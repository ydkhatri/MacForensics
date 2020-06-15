## Deserializer for ios/macos plists

This converts an NSKeyedArchive plist into a normal unserialized one, that can be easily read. 

Usage:
```
C:\> Deserializer.exe sample.plist
```
The deserialized plist will be stored in the same folder as source plist, and will have `_deserialized.plist` appended to its name.

Download the compiled exe for windows  [here](https://github.com/ydkhatri/MacForensics/raw/master/Deserializer/deserializer.exe).

### Dependencies

This tool has a dependency on [plistutils](https://github.com/strozfriedberg/plistutils) and [ccl_bplist](https://github.com/cclgroupltd/ccl-bplist). 
Use the supplied **ccl_bplist.py** and install **plistutils** with pip.
```
pip install plistutils
```
