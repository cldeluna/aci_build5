#!/usr/bin/python -tt
# xlsjson.py
# Claudia
# ACI_Configuration
__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = "Revision: 1.0 $"
__date__ = "10/1/2016-5:43 PM"
__copyright__ = "Copyright (c) 2015 Claudia de Luna"
__license__ = "Python"

import sys
import re
import os
import csv
import json



def debug_print_var(name,value):
    print("DEBUG==>  Variable: " + name + "\tValue = " + value )


# Provided main() calls the above functions
def main():
    # Take path argument and list all text files
    """
    This script takes a CSV dump of a JSON OBJECTS tab in the ACI Object Naming Workbook and
    converts it to a json file that can be used by the aci_fabric_xxx scripts.
    :return:
    """

    script, filename = sys.argv
    #debug_print_var("script", script)
    #debug_print_var("filename", filename)

    top_level_list = []
    top_level_dict = {}
    temp_dict = {}
    interim_dict = {}
    temp_list = []
    after_start = False
    keys = []

    print("Converting CSV file " + filename + " to JSON.")

    with open(filename) as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            # If not an empty row
            if row:
                if row[0] and not re.search('^#',row[0].strip()):
                    #print row
                    #debug_print_var("len(row)",str(len(row)))
                    if row[0] == "key_start":
                        #print row[0].strip()
                        top_level_key = row[1].strip()
                        top_level_dict[top_level_key] = {}
                        #debug_print_var("top_level_key", top_level_key)
                        row.remove(top_level_key)
                        row.remove('key_start')
                        # for i in range(len(row)):
                        #     print i,
                        #     print row[i]
                        keys = row
                        after_start = True
                        #raw_input("Press Enter to continue...")
                        continue
                    if after_start:
                        column_headings = row
                        #debug_print_var("column_headings", str(column_headings))
                        # if len(column_headings) <> len(keys):
                        #     print "Extra column headings > ",
                        #     print len(column_headings)
                        after_start = False
                        continue
                    if row[0] == "key_end":
                        #print "**********************KEY END PROCESSING "
                        interim_dict[top_level_key]=temp_list
                        #print interim_dict.keys()
                        top_level_list.append(interim_dict.copy())
                        #print top_level_list
                        #raw_input("Press Enter to continue...")
                        #Reset variables
                        keys = ""
                        temp_dict = {}
                        temp_list = []
                        interim_dict = {}
                        continue
                    for i in range(0, len(keys)):
                        # print i,
                        # print keys[i],
                        # print row[i]
                        temp_dict[keys[i].strip()]=row[i].strip()
                        #print temp_dict
                    #debug_print_var("temp_dict",str(temp_dict))
                    temp_list.append(temp_dict.copy())
                    #debug_print_var("temp_list",str(temp_list))
                    #debug_print_var("len(temp_list)", str(len(temp_list)))
                    #print len(temp_list)

                    #raw_input("Press Enter to continue...")
                    #debug_print_var("top_level_key", top_level_key)
                    #temp_list.append(temp_dict)

    #print json.dumps(top_level_list, indent = 4)
    print("Total number of policy sections generated in file: " + str(len(top_level_list)))
    for line in top_level_list:
        print(line.keys())

    # print top_level_list[0]['link']
    # print "\n"
    # print top_level_list[1]['cdp']

    # Save to JSON file of the same name
    filename_base = filename.split(".")[0]
    json_filename = filename_base + ".json"

    with open(json_filename, 'w') as jsonfile:
        json.dump(top_level_list, jsonfile)

    print("JSON Output has been saved to the file: " + json_filename)


# Standard call to the main() function.
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('\nUsage: xls2json.py.py <filename>\nExample: python xls2json.py.py "aci-constructs.csv"\n')
        sys.exit()
    else:
        main()

