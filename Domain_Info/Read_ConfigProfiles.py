# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Parse the ConfigProfiles.binary file on OSX to extract domain user info
#
# Copyright (C) 2017  Yogesh Khatri <yogesh@swiftforensics.com>
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
# Script Name  : Read_ConfigProfiles.py
# Author       : Yogesh Khatri
# Last Updated : 7/27/2017
# Purpose/Usage: This script parses the file 'ConfigProfiles.binary' found at
#                /private/var/db/ConfigurationProfiles/Store/ConfigProfiles.binary
#                on mac OSX systems. This file contains plists which contain
#                configuration information as well as domain user information for 
#                domain users that have logged into the system.
#
#                Output will be on the console.
#
#                Usage:
#                Read_ConfigProfiles.py  ConfigProfiles.reg
#                Example: Read_ConfigProfiles.py  c:\ConfigProfiles.binary
#
# Requirements:  Python (2 or 3) and ccl_bplist
# 
# Send bugs and feedback to yogesh@swiftforensics.com
# 

from __future__ import print_function
import ccl_bplist
import sys
import os
import tempfile
import struct

def GetProfileInfo(f):
    profiles = []
    ccl_bplist.set_object_converter(ccl_bplist.NSKeyedArchiver_common_objects_convertor)
    plist = ccl_bplist.load(f)
    ns_keyed_archiver_obj = ccl_bplist.deserialise_NsKeyedArchiver(plist, parse_whole_structure=True)
    md = ns_keyed_archiver_obj['mapData']

    for item in md:
        if md[item]['NSEntityName'] == 'MCX_Profile':
            profile_attribs = md[item]['NSAttributeValues']

            attributes = []
            attributes.append(profile_attribs[0]) # UUID if domain user, else name
            attributes.append(profile_attribs[1]) # user name
            attributes.append(profile_attribs[2]) # date first logged in (if domain user), else name
            # Not interpreting other attributes at this time!

            profiles.append(attributes)
    return profiles

usage = "Usage:\nRead_ConfigProfiles.py  ConfigProfiles.binary\n" 

if len(sys.argv) > 1:
    inputPath = sys.argv[1]
    try:
        with open(inputPath, 'rb') as configfile:
            configfile_size = os.path.getsize(inputPath)
            header = configfile.read(8)
            if header == b'CoreData':
                version = configfile.read(4)
                if (version != b'\x00\x00\x00\x01'): 
                    print('File version is different, this may not work! Trying.. ')
                configfile.seek(0x20) # jumping to 2nd plist's meta info
                plist_metadata = configfile.read(16)
                offset, size   = struct.unpack(">2Q", plist_metadata[0:16])
                configfile.seek(offset)
                data = configfile.read(size)
                if (offset > configfile_size) or ((offset + size) > configfile_size):
                    exit('Invalid data or file format changed, Exiting..')
                f = tempfile.SpooledTemporaryFile(max_size=size)
                f.write(data)
                f.seek(0)

                user_profiles = GetProfileInfo(f)
                i = 1
                if (len(user_profiles)) > 0:
                    user_profiles = sorted(user_profiles, key=lambda x: x[2], reverse=True)
                    print ("No.\tUUID\tDateFirstLoggedIn\tUser")
                    for p in user_profiles:
                        if len(p[0]) == 36: # Filter out non-domain items
                            print("%d\t%s\t%s\t%s" % (i, p[0], p[2], p[1]))
                            i += 1
                else:
                    print ('No user profile information found!')
            else:
                print('File does not appear to be in the correct format')
    except Exception as ex:
        print ('Error opening file: ' + str(ex))
else:
    print('Not enough parameters')
    print(usage)
