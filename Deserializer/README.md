## Deserializer for ios/macos plists

This converts an NSKeyedArchive plist into a normal unserialized one, that can be easily read. 

Usage:
```
C:\> Deserializer.exe sample.plist
```
The deserialized plist will be stored in the same folder as source plist, and will have `_deserialized.plist` appended to its name.
