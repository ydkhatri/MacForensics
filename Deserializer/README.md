## Deserializer for ios/macos plists

This converts an NSKeyedArchive plist into a normal unserialized one, that can be easily read. 
#### _Update - This is now available for use as a library (installable via pip) [here](https://github.com/ydkhatri/nska_deserialize), if you need to use in your code._  

### Usage
```
C:\> Deserializer.exe sample.plist
```

For json output instead of plist, use the `-j` option
```
C:\> Deserializer.exe -j sample.plist
```

The deserialized file will be stored in the same folder as source plist, and will have `_deserialized.plist` or `_deserialized.json` appended to its name.

### Usage as a library
```python
import deserializer

input_path = 'c:\\nskeyedarchive.plist'
f = open(input_path, 'rb')
deserialised_plist = deserializer.process_nsa_plist(input_path, f)

# writing out the resulting plist to plist/json
deserializer.write_plist_to_file(deserialised_plist, 'c:\\nskeyedarchive_deserialized.plist')
deserializer.write_plist_to_json_file(deserialised_plist, 'c:\\nskeyedarchive_deserialized.json')
```

### Download  
The compiled exe for windows is [here](https://github.com/ydkhatri/MacForensics/raw/master/Deserializer/deserializer.exe).

### Dependencies

This tool has a dependency on biplist and [ccl_bplist](https://github.com/cclgroupltd/ccl-bplist). 
Use the supplied **ccl_bplist.py** as it is a modified version.
