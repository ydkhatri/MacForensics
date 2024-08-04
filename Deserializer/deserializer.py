#
# Plist Deserializer, from NSKeyedArchive to normal plist 
# Copyright (c) 2018-2024  Yogesh Khatri <yogesh@swiftforensics.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You can get a copy of the complete license here:
#  <http://www.gnu.org/licenses/>.
#
# Script Name  : DeSerializer.py
# Author       : Yogesh Khatri
# Last Updated : August 04 2024
# Purpose      : NSKeyedArchive plists (such as .SFL2 files) are stored as 
#                serialized data, which is machine readable but not human
#                readable. This script will convert NSKeyedArchive binary 
#                plists into normal plists.
# Usage        : deserializer.py input_plist_path
#                Output will be saved in same location with _deserialised.plist 
#                appended to filename.
# Requirements : 
#                Python3.x
#                nska_deserialize (Get it with pip3 install nska_deserialize)
#
# Note: This will not work with python 2.xx

import nska_deserialize as nd
import os
import sys

usage = rf"""
Deserializer version {nd.get_version()}  (c) Yogesh Khatri 2018-2024
This tool converts an NSKeyedArchive plist into a normal deserialized one
using the nska_deserialize library: 
  https://github.com/ydkhatri/nska_deserialize

  Usage  : deserializer.exe [-j] input_plist_path
  Example: deserializer.exe C:\test\com.apple.preview.sfl2
           deserializer.exe -j  C:\test\screentime.plist

The -j option will also create a json file as output.
If successful, the resulting plist or json file will be created in the same folder
and will have _deserialized appended to its name.

If input path is a folder, this will attempt to deserialize all .plist file 
found in that folder (not recursive). Won't process plists without the extension.

"""

def main():
    create_json = False
    create_plist = True

    if len(sys.argv) == 1:
        print(usage)
        return
    
    elif len(sys.argv) == 2:
        input_path = sys.argv[1]

    elif len(sys.argv) > 2:
        if sys.argv[1].lower() == '-h':
            print(usage)
            return
        elif sys.argv[1].lower() == '-j':
            create_json = True
            input_path = sys.argv[2]
        elif os.path.exists(sys.argv[1]):
            input_path = sys.argv[1]
        else:
            print(f"Error, unrecognized input {sys.argv[1]}")
            return

    if not os.path.exists(input_path):
        print(f"Error, input_file \"{input_path}\" does not exist! Check file path!")
        print(usage)
        return
    
    input_paths = []
    if os.path.isdir(input_path):
        print("Input path is a folder, will deserialise all .plist files found")
        for name in os.listdir(input_path):
            if name.lower().endswith('.plist'):
                input_paths.append(os.path.join(input_path, name))
    else:
        input_paths.append(input_path)

    for path in input_paths:
        print(f"Reading file .. {path}")
        with open(path, 'rb') as f:
            try:
                print("Trying to deserialize...")
                deserialized_plist = nd.deserialize_plist(f, True) # Get Deserialized plist
            except (nd.DeserializeError, 
                    nd.biplist.NotBinaryPlistException, 
                    nd.biplist.InvalidPlistException,
                    nd.plistlib.InvalidFileException,
                    nd.ccl_bplist.BplistError, 
                    ValueError, 
                    TypeError, OSError, OverflowError) as ex:
                # These are all possible errors from libraries imported
                print('Had exception: ' + str(ex))
                print('Please send the offending plist my way to\n yogesh@swiftforensics.com')
                deserialized_plist = None

            if deserialized_plist:
                output_path_plist = path + '_deserialized.plist'
                output_path_json  = path + '_deserialized.json'

                if create_json:
                    print(f"Writing out .. {output_path_json}")
                    nd.write_plist_to_json_file(deserialized_plist, output_path_json)
                if create_plist:
                    print(f"Writing out .. {output_path_plist}")
                    nd.write_plist_to_file(deserialized_plist, output_path_plist)
    return

if __name__ == "__main__":
    main()