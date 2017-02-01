# Parse the Notifications db from mac OSX
#  (c) Yogesh Khatri - 2016- www.swiftforensics.com
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
# Script Name  : macNotifications.py
# Author       : Yogesh Khatri
# Last Updated : 1/4/2016
# Requirement  : Python (2 or 3) and biplist
#                biplist can be installed using the command 'pip install biplist' 
# 
# Purpose      : Parse the Notifications db found on mac OSX systems.
#                This database in OSX 10.8 is located at:
#                 /Users/<profile>/Library/Application Support/NotificationCenter/<GUID>.db
#                On Yosemite and higher, it is located at:
#                 /private/var/folders/<xx>/<yyyyyyy>/0/com.apple.notificationcenter/db
#                   where xx and yyyyyyy are random and differ for each user and
#                   installation of OSX
# Usage        : macNotifications.py  <path_to_database>  <output_file.csv>
#                Output is a tab-delimited file which can be viewed using Excel 
#                or any text/spreadsheet viewer. The output has the following
#                columns pulled from db tables and embedded plists blobs:
#                   Time	- Date and time in UTC
#                   Shown   - 1 = User was shown this message in a popup
#                   Bundle  - The official 'bundle', example: com.apple.appstore for the appstore app
#                   AppPath - Full path of application that sent notification
#                   UUID    - Unique ID
#                   Title   - Title of notification
#                   Message - Text of message
# Tested on    : OS X 10.8 - Mountain Lion to OS X 10.11 - El Capitan
#
# Send bugs and feedback to yogesh@swiftforensics.com
#


import codecs
import sqlite3
import sys
import os
import biplist
from biplist import *

def RemoveTabsNewLines(str):
    return str.replace("\t", " ").replace("\r", " ").replace("\n", "")
    
def ProcessNotificationDb(inputPath, outputPath):
    try:
        conn = sqlite3.connect(inputPath)
        print ("Opened database successfully");

        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT datetime(date_presented + 978307200, 'unixepoch') as time_utc, "
                                "datetime(date_presented + 978307200, 'unixepoch', 'localtime') as time, "
                                "actually_presented AS shown, "
                                "(SELECT bundleid from app_info WHERE app_info.app_id = presented_notifications.app_id)  AS bundle, "
                                "(SELECT last_known_path from app_loc WHERE app_loc.app_id = presented_notifications.app_id)  AS appPath, "
                                "(SELECT uuid from notifications WHERE notifications.note_id = presented_notifications.note_id) AS uuid, "
                                "(SELECT encoded_data from notifications WHERE notifications.note_id = presented_notifications.note_id) AS dataPlist "
                                "from presented_notifications ")

        # Print to file
        try:
            print ("Trying to create file '" + outputPath + "' for writing..")
            with codecs.open(outputPath, 'w', encoding='utf-16') as csv:
                csv.write ("Time\tShown\tBundle\tAppPath\tUUID\tTitle\tMessage\r\n")
                rowcount = 0
                for row in cursor:
                    rowcount += 1
                    title   = ''
                    message = ''
                    try:
                        plist = readPlistFromString(row['dataPlist'])
                        try:
                            title = RemoveTabsNewLines(plist['$objects'][2])
                        except:
                            pass
                        try:
                            message = RemoveTabsNewLines(plist['$objects'][3])
                        except:
                            pass
                        
                    except (InvalidPlistException, NotBinaryPlistException, Exception) as e:
                        print ("Invalid plist in table.", e )
                    try:
                        csv.write ('%s\t%s\t%s\t%s\t%s\t%s\t%s\r\n' %(row['time'], row['shown'], row['bundle'], row['appPath'], row['uuid'], title, message))
                    except Exception as ex:
                        print ("Error while writing to file, error details:\n", ex.args)
                print ("Finished processing! Wrote " + str(rowcount) + " rows of data.")
        except Exception as ex:
            print ("Failed to create file '" + outputPath + "' for writing. Is it locked? Perhaps a permissions issue")
            print ("Error details: " , ex.args)
        conn.close()
    except Exception as ex:
        print ("Failed to open database, is it a valid Notification DB? \nError details: ", ex.args)

## Main Program
usage = ("macNotifications.py - Parse the OSX Notifications database \n\n"
         "This script parses the notification database found at \n"
         "/Users/<profile>/Library/Application Support/NotificationCenter/<GUID>.db\n"
         " or for Yosemite onwards: \n"
         "/private/var/folders/<xx>/<yyyyyyy>/0/com.apple.notificationcenter/db\n\n"
         "Usage:\n"
         "macNotifications.py <path_to_db_file> <output.csv>\n"
         "Example: macNotifications.py  c:\\2676CFA4-F06E-4FFC-A48B-1C6457B2359D.db c:\\notifications.csv\n\n"
         "Output will be a tab-delimited file.\n\n"
         "Requirements: Python (2 or 3) and biplist\n"
         " biplist can be installed with a simple 'pip install biplist' command"
         )
         
print ("Using Python %i.%i" % (sys.version_info.major, sys.version_info.minor) )
if len(sys.argv) > 2:
    inputPath = sys.argv[1]
    outputPath = sys.argv[2]
    try:
        if os.path.exists(inputPath):
            ProcessNotificationDb(inputPath, outputPath)
        else:
            print("Error: Failed to find file at specified path. Path was : " + inputPath)
    except Exception as ex:
        print("Error: Unknown exception, error details are: " + ex.args)
else:
    print("Not enough arguments..")
    print(usage)

	
