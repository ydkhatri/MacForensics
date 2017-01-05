# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Parse the microsoftRegistrationDB.reg database on OSX
# Copyright (C) 2016  Yogesh Khatri <yogesh@swiftforensics.com>
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
# Script Name  : Read_OfficeRegDB.py
# Author       : Yogesh Khatri
# Last Updated : 8/30/2016
# Purpose/Usage: This script parses the file 'microsoftRegistrationDB.reg' found at
#                /Users/research/Library/Group Containers/xxxx.Office/MicrosoftRegistrationDB.reg
#                on mac OSX systems. This is an sqlite database which represents the
#                same data as is available at HKCU\Software\Microsoft\Office in the 
#                registry on a windows system.
#
#                Output will be a Plist file and a CSV file in the provided folder. The 
#                plist output is provided so we can view the tree visually in any plist
#                plist parser application, somewhat similar to viewing it in windows 
#                registry.
#
#                Usage:
#                Read_OfficeRegDB.py <path to microsoftRegistrationDB.reg> <output folder>
#                Example: Read_OfficeRegDB.py  c:\microsoftRegistrationDB.reg c:\output
#
# Requirements:  Python 3 and biplist
#                biplist can be installed with a simple 'pip install biplist' command"
# 
# Send bugs and feedback to yogesh@swiftforensics.com
# 

import sqlite3
import sys
from biplist import *
import datetime
import binascii
import struct
import os
import codecs

def GetStringUtcFromFileTimeTS(val):
    t = GetUtcFromFileTimeTS(val)
    if t != None:
        return str(t)
    return ''

def GetUtcFromFileTimeTS(val):
    if type (val) == bytes:
        # Reverse order of bytes (read as little endian)
        try:
            windate = struct.unpack('<Q', val)[0]
            t = datetime.datetime(1601,1,1) + datetime.timedelta(microseconds=windate / 10.)
            return t
        except Exception as ex:
            print ("Error converting timestamp value, value was : " + str(val))
            pass
    return None

def GetStringRepresentation(value, valuetype = None):
    s = ''
    if value == None:
        return s
    if valuetype == 3:  # REG_BINARY
        s = binascii.hexlify(value).decode("ascii").upper() # For python3!
    else:
        s = str(value)
    return s

# ONLY 1,3,4,11 have been seen so far.
def GetStringValueType(valuetype):
    s = ''
    if valuetype == None or valuetype == '':
        return s
    elif valuetype == 1: s = "REG_SZ"
    elif valuetype == 3: s = "REG_BINARY"
    elif valuetype == 4: s = "REG_DWORD"
    elif valuetype == 11: s = "REG_QWORD"
    elif valuetype == 2: s = "REG_EXPAND_SZ"
    elif valuetype == 5: s = "REG_DWORD_BIG_ENDIAN"
    elif valuetype == 6: s = "REG_LINK"
    elif valuetype == 7: s = "REG_MULTI_SZ"
    elif valuetype == 8: s = "REG_RESOURCE_LIST"
    elif valuetype == 9: s = "REG_FULL_RESOURCE_DESCRIPTOR"
    elif valuetype == 10: s = "REG_RESOURCE_REQUIREMENTS_LIST"
    else:
        s = str(value)
    return s

def GetBranch(plist, key):
    path = key.split("\\")
    subkey = plist
    for item in path:
        temp = subkey.get(item, None)
        if temp == None:
            subkey.update( { item : {} } )
            subkey = subkey[item]
        elif type(temp) != dict:
            # Sometimes, this happens, HKCU\Path\Var is a key having values in it AND Var is also a value in HKCU\Path
            # Perhaps this is the (Default) value stored this way.
            subkey.update( { item : { "(Default)" : temp } } )
            subkey = subkey[item]
        else:
            subkey = temp
    return subkey

def CreatePListFromData(data):
    # plist = {'HKCU':  
    #             {'SOFTWARE' : 
    #                 {'MICROSOFT' : 
    #                     {'OFFICE' : 
    #                         {'xx..xx': 
    #                             {'Application':'PowerPoint',
    #                             'FileName':'Environmental disasters.pptx'
    #                             } 
    #                         } 
    #                     } 
    #                 } 
    #             },
    #             'LastWriteTimeUTC':"2016-04-03 12:34:56",
    #         }

    plist = {'Software': {} }

    try:
        for row in data:
            id = row['id']
            ts = GetUtcFromFileTimeTS(row['keyLastWriteTime'])
            key = row['key']
            vname = row['valueName']
            vtype = row['valueType'] 
            value = row['value'] #GetStringRepresentation(row['value'], row['valueType'])
            if value == None: value = ''
            branch = GetBranch(plist, key)
            if ts != None: branch.update( {'LastWriteTimeUTC': ts })
            if vname and len(vname) > 0:
                # Check if there is not already a subkey by that name, else it will get overwritten
                subkey = branch.get(vname, None)
                if subkey == None:  # All good, no such subkey
                    branch.update( { vname : value } )
                else: 
                    # Found same name being used! Deal with it!
                    subkey.update( { "(Default)" : value } )
    except Exception as ex:
        print ('Error: Exception while trying to read cursor: ' + str(ex))
    return plist


def ParseRegistrationDBFile(inputPath, outputPath):

    try:
        plistPath = os.path.join(outputPath, "officeregdb.plist")
        csvPath   = os.path.join(outputPath, "officeregdb.csv")
    except Exception as ex:
        print ("Error: Failed to create output paths : " + outputPath + " Error: " + str(ex))

    conn = None
    try:
        conn = sqlite3.connect(inputPath)
        print ("Opened database successfully: ", inputPath)

        conn.row_factory = sqlite3.Row
        try:
            query = str("SELECT  t2.node_id as id, t2.write_time as keyLastWriteTime, path as key, HKEY_CURRENT_USER_values.name as valueName, HKEY_CURRENT_USER_values.value as value, HKEY_CURRENT_USER_values.type as valueType from ( "
                    " WITH RECURSIVE "
                    "   under_software(path, name, node_id, write_time) AS ( "
                    "     VALUES('Software','',1, 0) "
                    "     UNION ALL "
                    "     SELECT under_software.path || '\\' || HKEY_CURRENT_USER.name, HKEY_CURRENT_USER.name, HKEY_CURRENT_USER.node_id, HKEY_CURRENT_USER.write_time "
                    "       FROM HKEY_CURRENT_USER JOIN under_software ON HKEY_CURRENT_USER.parent_id=under_software.node_id "
                    "       ORDER BY 1 "
                    "   ) "
                    " SELECT name, path, write_time, node_id FROM under_software "
                    " ) as t2 LEFT JOIN HKEY_CURRENT_USER_values on HKEY_CURRENT_USER_values.node_id=t2.node_id ")
            cursor = conn.execute(query)
            data = cursor.fetchall()
            # Print to file
            print (" Creating file " + csvPath + " for writing")
            try:
                with codecs.open(csvPath, 'w', encoding='utf-16') as csv:
                    csv.write("ID\tKeyLastWriteTimeUTC\tKey\tValueName\tValue\tValueType\r\n")
                    for row in data:
                        csv.write ('%d\t%s\t%s\t%s\t%s\t%s\r\n' % (row['id'], GetStringUtcFromFileTimeTS(row['keyLastWriteTime']), 
                                    GetStringRepresentation(row['key']), GetStringRepresentation(row['valueName']), 
                                    GetStringRepresentation(row['value'],row['valueType']), GetStringValueType(row['valueType'])))
                    print (" CSV written out successfully to " + csvPath)
            except Exception as ex:
                print ("Error writing to csv: ", ex.args )

            print (" Creating file " + plistPath + " for writing") 
            try:
                plist = CreatePListFromData(data)
                writePlist(plist, plistPath)
                print (" Plist written out successfully to " + plistPath)
            except (InvalidPlistException, NotBinaryPlistException) as ex:
                print ("Error creating the plist: ", ex.args )

        except Exception as ex:
            print ("Error: Failed to execute query, error was : " + str(ex))
    except Exception as ex:
        print ("Error: Failed to open database : " + inputPath + " Error: " + str(ex))

    if conn:
        conn.close()


## Program starts here ##

usage = ("Read_OfficeRegDB.py \n\n"
         "This script parses the file 'microsoftRegistrationDB.reg' found at \n"
         "/Users/research/Library/Group Containers/xxxx.Office/MicrosoftRegistrationDB.reg\n\n"
         "Usage:\n"
         "Read_OfficeRegDB.py <path to microsoftRegistrationDB.reg> <output folder>\n"
         "Example: Read_OfficeRegDB.py  c:\\microsoftRegistrationDB.reg c:\\output\n\n"
         "Output will be a Plist file and a CSV file in the provided folder.\n\n"
         "Requirements: Python 3 and biplist\n"
         " biplist can be installed with a simple 'pip install biplist' command"
         )

if len(sys.argv) > 2:
    inputPath = sys.argv[1]
    outputPath = sys.argv[2]
    try:
        if os.path.exists(inputPath):
            if os.path.isdir(outputPath): # Check output path provided
                ParseRegistrationDBFile(inputPath, outputPath)
            else: # Either path does not exist or it is not a folder
                if os.path.isfile(outputPath):
                    print("Error: There is already a file existing by that name. Cannot create folder : " + outputPath)
                else: # Try creating folder
                    try:
                        os.makedirs(outputPath)
                        ParseRegistrationDBFile(inputPath, outputPath)
                    except Exception as ex:
                        print("Error: Cannot create output folder : " + outputPath + "\nError Details: " + ex.args)
        else:
            print("Error: Failed to find file at specified path. Path was : " + inputPath)
    except Exception as ex:
        print("Error: Unknown exception, error details are: " + ex.args)
else:
    print("Not enough arguments..")
    print(usage)
