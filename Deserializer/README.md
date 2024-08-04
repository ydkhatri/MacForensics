## Deserializer for ios/macos plists

This converts an NSKeyedArchive (NSKA) plist into a normal unserialized one, that can be easily read. 
#### Updates

- (Aug 2024) _The underlying library has also now been updated to process any plist, and recursively deserialize any elements that may be nested NSKA archvies within the plist._

- (Sep 2020) _This is now available for use as a library (installable via pip) [here](https://github.com/ydkhatri/nska_deserialize), if you need to use in your code. The script has been updated to use that library._


### Usage
```
C:\> Deserializer.exe sample.plist
```

For json output, use the `-j` option.
```
C:\> Deserializer.exe -j sample.plist
```

To process all plist files in a folder, simply provide a folder path instead of a file path:
```
C:\> Deserializer.exe C:\Samples\
```

The deserialized file will be stored in the same folder as source plist, and will have `_deserialized.plist` or `_deserialized.json` appended to its name.

You can also drag and drop a plist onto the exe.
![Screen Recording 2024-08-04 at 11 19 19 PM](https://github.com/user-attachments/assets/c165645b-4ac6-4989-a291-94b1bcb469dd)


### Download  
The compiled exe for windows is [here](https://github.com/ydkhatri/MacForensics/raw/master/Deserializer/deserializer.exe).

### Dependencies

This tool has a dependency on nska_deserialize library. Install via `pip3 install nska_deserialize`
