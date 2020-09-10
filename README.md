# MacForensics

Repository of scripts for processing various artifacts from macOS (formerly OSX).

Artifact | Script Name | Description
-------- | ----------- | ------------
Darwin folders | darwin_path_generator.py | DARWIN_USER_ folders name generation algorithm (those seemingly random folder names under /var/folders/)
Deserialize NSKeyedArchive plists | Deserializer/deserializer.py<br>Deserializer/deserializer.exe | Converts NSKeyedArchive plists to normal (human-readable) plists (Code + compiled exe for windows)  
Domain (Active Directory) | Domain_Info/Read_ConfigProfiles.py | Reads user profile information for AD domain users from the ConfigProfiles.binary file
DotUnderscore ._ files | DotUnderscore_macos.bt | An 010 template for parsing extended attribute files that begin with ._
Ktx to Png convertor | IOS_KTX_TO_PNG/ios_ktx2png.py<br>IOS_KTX_TO_PNG/ios_ktx2png.exe | Convert ios created KTX texture images (like app snapshots) to PNG (Code + compiled exe for windows)  
Notifications | macNotifications.py | Parse Mac Notifications db
Office reg file | Read_OfficeRegDB.py | Parse MS Office created sqlite db (microsoftRegistrationDB.reg)
