## Application
Not intended for direct user use. Instead, the intention is to add this functionality to a pipeline where data can be masked on premisis before moving to the cloud and then decoded on premisis once it is read back. Another use-case is to mask the data off premisis before model rules are derived and then later decoding those rules on premisis.  


## API
```encode_data(dataframe) -> unmasked dataframe anonymized with sensitive data masked```  
Iterate through columns applying the appropriate transformations based on datatypes and storing mappings in a key (dict).
Can be done on premisis or in cloud (on prem if data secret).

```decode_data(masked_dataframe) -> masked dataframe reversed back to its original state```  
Allows masked data to be reversed to its original state by the user as long as they have access to the key.  
Should never be done off premisis with secret data. Can be done as data leaves cloud and is back on prem.  

```decode_rules(masked_rules, Optional[dump_directory]) -> masked model rules reversed back to human readable rules```  
User can choose to dump the rules to a file, else return decoded rules in pythoon session.

```dump_key(key_id, directory) -> none```  
Dumps the key mappings to a json file in the cwd by default.  

```retrieve_key(key_id, directory) -> key loaded into memory from a directory it was dumped to```  
This is private to the user and is never used off premisis. 
