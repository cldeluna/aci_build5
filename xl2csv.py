#!/usr/bin/python -tt
# Project: python
# Filename: xl2csv
# claud
# PyCharm

from __future__ import absolute_import, division, print_function

__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "10/10/2017"
__copyright__ = "Copyright (c) 2016 Claudia"
__license__ = "Python"

import argparse
import xlrd
import csv
import time
import os


def short_name(full_tab_name):

    ftn = full_tab_name.lower()

    # Set the short name or prefix of the output CSV file
    # Set the proper script name so that the actual execution command can be printed out
    if "step1" in ftn:
        short_name = "step1"
        script_name = "aci_fabric_step1_mgmt.py"
    elif "step2a" in ftn:
        short_name = "step2a"
        script_name = "aci_fabric_step2a_fabpol.py"
    elif "step2b" in ftn:
        short_name = "step2b"
        script_name = "aci_fabric_step2b_accpol.py"
    elif "step3" in ftn:
        short_name = "step3"
        script_name = "aci_fabric_step3_tnpol.py"
    elif "fex" in ftn:
        short_name = "step4fex"
        script_name = "aci_fabric_step4_conpol-fex.py"
    elif "step4" in ftn:
        short_name = "step4"
        script_name = "aci_fabric_step4_conpol.py"
    elif "step5a" in ftn:
        short_name = "step5a"
        script_name = "aci_fabric_step5a_l3pol.py"
    elif "step5b" in ftn:
        short_name = "step5b"
        script_name = "aci_fabric_step5b_vmm.py"
    elif "step6" in ftn:
        short_name = "step6"
        script_name = "aci_fabric_step6_validation.py"
    else:
        short_name = ftn
        script_name = "unknown"

    return short_name, script_name

def csv_from_excel(excel_file):
    workbook = xlrd.open_workbook(excel_file)
    all_worksheets = workbook.sheet_names()
    execution_cmds = []
    # print(all_worksheets)

    # Create a Log file
    filename_base = excel_file.split(".")[0]
    timestr = time.strftime("%Y%m%d-%H%M%S")
    log_filename = filename_base + "-Command-Run-Cheatsheet.txt"
    log_file = open(log_filename, 'w')
    msg = "Excel to CSV {}\n".format(time.ctime())
    print(msg)
    log_file.write(msg)

    for worksheet_name in all_worksheets:

        if "step" in worksheet_name.lower():
            # print(worksheet_name)
            worksheet = workbook.sheet_by_name(worksheet_name)
            # Make sure the worksheet has content
            if worksheet.nrows == 0:
                continue
            shortname, scriptname = short_name(worksheet_name)
            s = str(arguments.xlfile).strip()
            s = s.split(".xlsx")
            suffix = s[0]
            # print(suffix)

            with open('{}-{}.csv'.format(shortname,suffix), 'w') as your_csv_file:
                # print(dir(your_csv_file))
                # wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)
                wr = csv.writer(your_csv_file)
                for rownum in range(worksheet.nrows):
                    row = []
                    temp_row = worksheet.row_values(rownum)
                    # print(worksheet.row_values(rownum))
                    # print(type(worksheet.row_values(rownum)))
                    for item in range(0, len(worksheet.row_values(rownum))):
                        if type(temp_row[item]) == int or type(temp_row[item]) == float:
                            row.append(int(temp_row[item]))
                        else:
                            row.append(temp_row[item])

                    # wr.writerow([unicode(entry).encode("utf-8") for entry in worksheet.row_values(rownum)])
                    wr.writerow([str(entry) for entry in row])
                msg = "Saved {} CSV payload file to {}".format(shortname.upper(), your_csv_file.name)
                print(msg)
                log_file.write(msg + "\n")
                if shortname == 'step6':
                    execution_cmds.append("python {} QA_DIR -a #Validation script has no payload but requires a "
                                          "directory for the Validation log file".format(scriptname))
                elif shortname == 'step5a':
                    execution_cmds.append("python {} {} -3 -4 -5 -6 #Use -a only for specific transit routing "
                                          "needs.".format(scriptname, your_csv_file.name))
                elif not scriptname == 'unknown':
                    execution_cmds.append("python {} {} -a ".format(scriptname, your_csv_file.name))
                else:
                    pass

    msgs = [
        "\nCommon Execution Commands:",
        "Tip: Use the python scriptname.py -h option for help and details on running each script.",
        "Tip: In many cases the -f specific_credentials.txt is also used.",
        "Tip: Copy the relevant command(s) when ready to commence a fabric build or validation.\n"
    ]
    for msg in msgs:
        print(msg)
        log_file.write(msg + "\n")

    for line in execution_cmds:
        print(line)
        log_file.write(line + "\n")

    fullpath = os.path.join(os.getcwd(),log_filename)
    msg = "\nCommands saved in {}".format(fullpath)
    print(msg)
    log_file.write(msg + "\n")

    log_file.close()

def main():
    csv_from_excel(arguments.xlfile)

# Standard call to the main() function.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="EXCEL to CSV Script",
                                     epilog="Usage: ' python xl2csv payload_file.xlsx' ")

    parser.add_argument('xlfile', help='Excel File in local directory.  Each "Step" Tab will be saved to CSV.')
    # parser.add_argument('-a', '--all', help='Execute all exercises in week 4 assignment', action='store_true',
    #                     default=False)
    arguments = parser.parse_args()
    # print(arguments)
    main()


