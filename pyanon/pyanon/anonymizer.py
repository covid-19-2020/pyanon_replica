git status"""
---------------------------------------------------
Author: Nick Hopewell <nicholas.hopewell@cic.gc.ca>

Description
-----------
See README.
---------------------------------------------------
"""
import os, json
from typing import Dict, Union, Optional, List, Any
import pyanon.pyanon.anonymizer_h as anons

class Anonymizer:
    """
    This class masks and unmasks a pandas dataframe
    and stores a key with the mappings between these values.
    """
    def __init__(self):

        self._key = {
                'col_map' : {
                    },
                'rev_col_map' : {
                    }, 
                'val_map' : {                    
                    }, 
                'rev_val_map' : {
                    }, 
                'col_order' : None
            }
        self._key_directory: str = None
        self._key_id: Union[int, str] = None
        self._cols_dropped: List[str] = None

    @property
    def key(self):
        return self._key

    @key.setter
    def key(seld, new: Dict):
        self._key = new       

    @property
    def cols_dropped(self):
        return self._cols_dropped
    
    @cols_dropped.setter
    def cols_dropped(self, cols_list):
        self._cols_dropped = cols_list

    def encode_data(self, dataframe, mask_continuous=False,
            drop_zero_variance=True, drop_keys=False, 
            build_val_map=False, permute_rows=True,
            permute_columns=True):
        """
        masks a pandas dataframe

        Notes
        -----
        Must build code dict if you want to reverse masked data
        """
        # optionally stores zero variance cols and keys
        cols_dropped = []
        # zero variance means each row has same value. No variance = no model.
        if drop_zero_variance:
            for c in dataframe.columns:
                n_unique = dataframe[c].nunique()
                if n_unique == 1:
                    cols_dropped.append(c)
                    dataframe.drop(c, axis = 1)
        # if you wont need keys to join later, just drop them
        if drop_keys:
            n_rows = dataframe.shape[0]
            for c in dataframe.columns:
                n_unique = dataframe[c].nunique()
                if n_unique == n_rows:
                    cols_dropped.append(c)
                    dataframe.drop(c, axis = 1)
        # update self if user drops any cols
        if any( (drop_zero_variance, drop_keys) ):
            self.cols_dropped = cols_dropped

        if permute_columns:
            self.key['col_order'] = list(dataframe.columns)

        # conv objects to cats for easy encoding
        anons.strings_to_cats(dataframe)
        # set col maps
        (
            self._key['col_map'], self._key['rev_col_map']
         ) = anons.build_col_dict(dataframe)
        # map new names to df
        dataframe.rename(
            columns = self._key['col_map'], inplace = True)
        if build_val_map:
            # get val maps
            (
                self._key['val_map'], self._key['rev_val_map']
             )  = anons.build_value_dict(dataframe)
        # map to codes
        dataframe = anons.cat_to_code(dataframe, self._key['rev_val_map'],
                    permute_rows=permute_rows, 
                    permute_columns=permute_columns)
        

        return dataframe
        
    def decode_data(self, masked_dataframe):
        """unmasks a masked pandas dataframe"""

        order = []

        for col in self._key['col_order']:
            order.append(self._key['col_map'][col])

        masked_dataframe = masked_dataframe.reindex(
            columns=order)

        masked_dataframe.rename(
            columns = self._key['rev_col_map'], inplace = True)

        anons.reverse_coded_values(masked_dataframe, self._key['val_map'])

        dataframe = masked_dataframe.reindex(range(len(masked_dataframe)))

        return dataframe

    def decode_rules(self, masked_rules, dump_directory=None):
        """reverses masked models rules back to original state"""
        raise NotImplementedError

    def dump_key(self, key_id, directory):
        """dumps a encoding key to a directory as json"""
        file_path = os.path.join(directory, f'{key_id}.json')
        
        with open(file_path, 'w') as f:
            json.dump(self._key, f, indent=4)

    def retrieve_key(self, key_id, directory):
        """loads a json file containing an encoding key
        into memory"""
        file_path = os.path.join(directory, f'{key_id}.json')       
        
        with open(file_path, 'r') as f:
            key = json.load(f)

        self._key = key
