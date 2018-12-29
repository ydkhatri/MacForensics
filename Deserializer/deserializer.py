#
# Plist Deserializer, from NSKeyedArchive to normal plist 
# Copyright (c) 2018  Yogesh Khatri <yogesh@swiftforensics.com>
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
# Last Updated : 12/29/2018
# Purpose      : NSKeyedArchive plists (such as .SFL2 files) are stored as 
#                serialized data, which is machine readable but not human
#                readable. This script will convert NSKeyedArchive binary 
#                plists into normal plists.
# Usage        : deserializer.py input_plist_path
#                Output will be saved in same location with _deserialised.plist 
#                appended to filename.
# Requirements : 
#                Python3.x
#                biplist (Get it with pip3 install biplist)
#                ccl_bplist
#
# Note: This will not work with python 2.xx

import biplist
import ccl_bplist
import os
import sys
import traceback

def recurseCreatePlist(plist, root):
    if isinstance(root, dict):
        for key, value in root.items():
            if key == '$class': 
                continue
            v = None
            if isinstance(value, list):
                v = []
                recurseCreatePlist(v, value)
            elif isinstance(value, dict):
                v = {}
                recurseCreatePlist(v, value)
            else:
                v = value
            plist[key] = v
    else: # must be list
        for value in root:
            v = None
            if isinstance(value, list):
                v = []
                recurseCreatePlist(v, value)
            elif isinstance(value, dict):
                v = {}
                recurseCreatePlist(v, value)
            else:
                v = value
            plist.append(v)

usage = '\r\nDeserializer.py   (c) Yogesh Khatri 2018 \r\n'\
        'This script converts an NSKeyedArchive plist into a normal deserialized one.\r\n\r\n'\
        'Usage: python.exe deserializer.py input_plist_path \r\n'\
        ' Example: deserializer.py com.apple.preview.sfl2 \r\n\r\n'\
        'If successful, the resulting plist will be created in the same folde and will have _unserialized appended to its name.\r\n'

def main():
    global usage
    if sys.version_info.major == 2:
        print('ERROR-This will not work with python2. Please run again with python3!')
        return
    argc = len(sys.argv)
    
    if argc < 2 or sys.argv[1].lower() == '-h':
        print(usage)
        return

    input_path = sys.argv[1]
    if not os.path.exists(input_path):
        print('Error, file does not exist! Check file path!\r\n')
        print(usage)
        return

    # All OK, process the file now
    try:
        f = open(input_path, 'rb')
        print('Reading file .. ' + input_path)
        ccl_bplist.set_object_converter(ccl_bplist.NSKeyedArchiver_common_objects_convertor)
        plist = ccl_bplist.load(f)
        ns_keyed_archiver_obj = ccl_bplist.deserialise_NsKeyedArchiver(plist, parse_whole_structure=True)
        root = ns_keyed_archiver_obj['root']

        print('Trying to deserialize binary plist ..')
        plist = {}
        recurseCreatePlist(plist, root)
        print('Writing it back out as .. ' + input_path + '_deserialized.plist')
        biplist.writePlist(plist, input_path + '_deserialized.plist')
        print('Done !')
    except Exception as ex:
        print('Had an exception (error)')
        traceback.print_exc()

if __name__ == "__main__":
    main()     
