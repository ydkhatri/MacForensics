## Deserializer for ios/macos plists

This converts an NSKeyedArchive plist into a normal unserialized one, that can be easily read. 

### Usage:
```
C:\> Deserializer.exe sample.plist
```

For json output instead of plist, use the `-j` option
```
C:\> Deserializer.exe -j sample.plist
```

The deserialized file will be stored in the same folder as source plist, and will have `_deserialized.plist` or `_deserialized.json` appended to its name.

### Download  
The compiled exe for windows is [here](https://github.com/ydkhatri/MacForensics/raw/master/Deserializer/deserializer.exe).

### Dependencies

This tool has a dependency on [ccl_bplist](https://github.com/cclgroupltd/ccl-bplist). 
Use the supplied **ccl_bplist.py** as it is a modified version.
