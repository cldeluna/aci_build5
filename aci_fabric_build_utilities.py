#!/usr/bin/python -tt
# Project: python
# Filename: aci_fabric_build_utilities
# claud
# PyCharm

from __future__ import absolute_import, division, print_function

__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "4/30/2017"
__copyright__ = "Copyright (c) 2016 Claudia"
__license__ = "Python"

import sys
import re
import os
import argparse
import json
import csv
import time


#########################################################
################### UTILITIES ###########################
#########################################################

# status is set by the -x --xdelete argument to False for deletion
# Read: If (delete) not true create payload else (delete) IS true and remove

def template_payload(name, desc, protocol, uname, upwd, ip, status):

    if not status:
        payload = {

        }
    else:
        payload = {

        }
    return payload



# BASIC File Open Utility

def basic_file_open(fname):

    try:

        fh = open(fname)

    except IOError:
        # Problem opening the file
        print("There was a problem opening the file " + fname + "!")
        sys.exit('Aborting program Execution')

    return fh


def get_input(prompt = "Enter Value: "):
    '''
    Function for user input for both Python2 and Python3
    :param prompt: 
    :return: 
    '''

    try:
        user_input = raw_input(prompt)
    except NameError:
        user_input = input(prompt)

    return user_input


def debug_print_var(name, value):
    print("DEBUG==>  Variable: " + name + "\tValue = " + value)


def slash_replace(str):
    new_str = str.replace("/","-")
    new_string = re.sub('[^a-zA-Z0-9\n\.]', ' ', new_str)
    # print str
    # print new_str
    return new_string


def csv2json(filename):
    # Take path argument and list all text files
    """
    This script takes a CSV dump of a JSON OBJECTS tab in the ACI Object Naming Workbook and
    converts it to a json file that can be used by the aci_fabric_xxx scripts.

    """

    top_level_list = []
    top_level_dict = {}
    temp_dict = {}
    interim_dict = {}
    temp_list = []
    after_start = False
    keys = []


    try:

        with open(filename) as csv_file:

            print("Converting CSV file " + filename + " to JSON.")

            reader = csv.reader(csv_file)
            for row in reader:
                # If not an empty row
                if row:
                    if row[0] and not re.search('^#',row[0].strip()):

                        if row[0] == "key_start":

                            # print(row[0])
                            # print(row[1])
                            top_level_key = row[1].strip()
                            top_level_dict[top_level_key] = {}

                            row.remove(top_level_key)
                            row.remove('key_start')

                            keys = row
                            after_start = True

                            continue
                        if after_start:
                            column_headings = row
                            after_start = False
                            continue
                        if row[0] == "key_end":

                            interim_dict[top_level_key.strip()]=temp_list

                            top_level_list.append(interim_dict.copy())

                            keys = ""
                            temp_dict = {}
                            temp_list = []
                            interim_dict = {}
                            continue
                        for i in range(0, len(keys)):

                            if keys[i].strip():
                                temp_dict[keys[i].strip()]=row[i].strip()

                        temp_list.append(temp_dict.copy())

        print("Total number of policy sections generated in file: " + str(len(top_level_list)))
        for line in top_level_list:
            print(line.keys())


        # Save to JSON file of the same name
        filename_base = filename.split(".")[0]
        json_filename = filename_base + ".json"

        with open(json_filename, 'w') as jsonfile:
            json.dump(top_level_list, jsonfile)

        print("JSON Output has been saved to the file: " + json_filename)
        print("="*20 + "Payload Load Complete\n\n")

    except IOError:
        # Problem opening the file
        print("There was a problem opening the file " + filename + "!")
        sys.exit('Aborting program Execution')

    return top_level_list


def print_header(apic, user, action, logfile):
    print("\n")
    print("*" * 50)
    logfile.write("\n")
    logfile.write("*" * 50 + "\n")
    if not action:
        text = "User " + user + " Creating Configuration on APIC " + apic
        print(text)
        logfile.write(text + "\n")
    else:
        text = "User " + user + " Removing Configuration on APIC " + apic
        print(text)
        logfile.write(text + "\n")
    print("*" * 50)
    print("\n")
    logfile.write("*" * 50)
    logfile.write("\n")


def print_qa_header(apic, user, action, logfile):
    print("\n")
    print("*" * 50)
    logfile.write("\n")
    logfile.write("*" * 50 + "\n")
    text = "User " + user + " Validating Configuration on APIC " + apic
    print(text)
    logfile.write(text + "\n")
    print("*" * 50)
    print("\n")
    logfile.write("*" * 50)
    logfile.write("\n")


def pluck_payload(json_data, key):
    data = ''
    for jlist in json_data:
        if key in jlist.keys():
            data = jlist[key]
            # print list['vlan']
    return data


def print_post_result(action, response, item, logfile):

    print("=" * 20 + "POST Action: " + action + " POST Object: " + item)
    logfile.write("=" * 20 + "POST Action: " + action + " POST Object: " + item + "\n")
    rd = response.__dict__

    rd_dict = json.loads(rd['_content'])

    texts = "Status Code: " + str(rd['status_code'])
    textr = "Reason: " + rd['reason']
    print(texts)
    print(textr)
    logfile.write(texts + "\n")
    logfile.write(textr + "\n")
    if rd['reason'] != "OK":

        texte = "\t Error Text: " + rd_dict['imdata'][0]['error']['attributes']['text']
        print(texte)
        logfile.write(texte + "\n")
    print("=" * 40)
    logfile.write("=" * 40)
    logfile.write("\n")

def print_post_result_log(action, response, item, logfile, errorlistofdict):


    post_action = "POST Action: " + action + " POST Object: " + item
    print("=" * 20 + post_action)
    logfile.write("=" * 20 + post_action + "\n")
    rd = response.__dict__

    rd_dict = json.loads(rd['_content'])
    rd_dict['post_action'] = post_action

    texts = "Status Code: " + str(rd['status_code'])
    textr = "Reason: " + rd['reason']
    print(texts)
    print(textr)
    logfile.write(texts + "\n")
    logfile.write(textr + "\n")
    if rd['reason'] != "OK":

        texte = "\t Error Text: " + rd_dict['imdata'][0]['error']['attributes']['text']
        print(texte)
        logfile.write(texte + "\n")
        errorlistofdict.append(rd_dict)
    print("=" * 40)
    logfile.write("=" * 40)
    logfile.write("\n")

def print_debug_data(response):
    print("\n")
    print("=" * 40)
    rd = response.__dict__
    # print("RESPONSE OBJECT TYPE:  " + str(type(rd)))
    print(rd.keys())
    # print("_CONTENT OBJECT TYPE:  " + str(type(rd['_content'])))
    # print rd['_content']
    rd_dict = json.loads(rd['_content'])
    # print type(rd_dict)
    print(len(rd_dict))
    print(rd['status_code'])
    print(rd['reason'])
    if rd['reason'] != "OK":

        print("\t key: imdata0errorAttributesText: "),
        print(rd_dict['imdata'][0]['error']['attributes']['text'])
    print("=" * 40)
    for key, value in rd.items():
        print(key + " ==> " + str(value))

def payload_size(json_payload,fh):

    payload_totals_dict = {}
    t = 0

    for line in json_payload:
        x = sum(len(v) for v in line.items())
        k = line.keys()

        # print(x)
        # print(k)
        # print(dir(k))
        # list(e.keys())[0]
        key = list(line.keys())[0]
        t = t + x

        payload_totals_dict[key] = x
    payload_totals_dict['total_objects'] = t
    #print(payload_totals_dict)

    print("Payload Size Processed:")
    fh.write("\nPayload Size Processed:\n")
    for k,v in payload_totals_dict.items():
        if "total_objects" not in k:
            #textt = "\t" + k + " => \t\t" + str(v)
            textt = "{:>25} ==> {:30}".format(k,str(v))
            print(textt)
            fh.write(textt + "\n")
    print("Total Objects in Payload  ==> {}".format(payload_totals_dict['total_objects']))
    fh.write("Total Objects in Payload  ==> " + str(payload_totals_dict['total_objects']))
    return payload_totals_dict

def allowed_encap_split(string):

    numeric_list = []
    # print(string)

    # If it is a range of numbers x-y
    if "-" in string:
        r = string.split("-")
        if len(r) == 2:
            for x in range(int(r[0]),int(r[1])+1):
                numeric_list.append(x)
        else:
            print("ERROR: Allowed Encapsulation looks to be a range but has more than 2 values!")
            numeric_list = False

    # If it is a list of numbers separated by a comma
    elif "," in string:
        x = string.split(",")
        for val in x:
            numeric_list.append(int(val))

    # If it is a list of numbers separated by a space
    elif " " in string:
        x = string.split()
        for val in x:
            numeric_list.append(int(val))

    # If it is a valid single number
    elif int(string):
        x = int(string)
        numeric_list.append(x)

    else:
        print("ERROR: Unknown delimiter in allowed encapsulation string. Valid delimeters are ',', ' ', or '-' for a range of valid values!")
        numeric_list = False

    return(numeric_list)


def main():
    print("ACI Fabric Buildout Utilities to be used with Step 1 - 6 Buildout Scripts")

    a1 = '1136 1138 1140 1141 1142 1143 1147 1148 1151 1160 1162 1166 1168 1170 1172 1176 1182 1184'
    a2 = '1136, 1138,  1140,  1141 '
    a3 = "1 - 4"

    allowed_encap_split(a1)


def get_current_time():
    try:
        start_time = time.clock()
    except Exception as e:
        print(f"Time Exception is {e}")
        start_time = time.process_time()
    return start_time

# Standard call to the main() function.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="ACI build out functions for aci_fabric_buildout.  "
                                                 "This module is not typically called explicityly.  "
                                                 "All the aci_fabric_setXX modules import this module.",
                                     epilog="Usage: ' python aci_fabric_build_utilities' ")
    arguments = parser.parse_args()
    main()


