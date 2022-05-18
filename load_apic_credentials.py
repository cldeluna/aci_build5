#!/usr/bin/python -tt
# load_apic_credentials
# Claudia
# aci_fabric_buildout
__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = "Revision: 1.0 $"
__date__ = "11/2/2016-8:00 AM"
__copyright__ = "Copyright (c) 2015 Claudia de Luna"
__license__ = "Python"

import sys
import re
import os
import argparse


def load_credentials(credentials_file):
    # Open and parse credentials file (credentials.py by default)
    cred_dict = {}
    creds = False
    try:
        with open(credentials_file) as f:
            content = f.readlines()
            content = [l.strip() for l in content]

            for line in content:
                if "#" not in line and len(line) > 0:
                    line = line.replace('"', '')
                    line_split = line.split('=')
                    cred_dict[line_split[0].strip()] = line_split[1].strip()
        creds = cred_dict


    except IOError:
        print("File Error")

    return creds


# Provided main() calls the above functions
def main():
    # Take path argument and list all text files
    """
    This script loads a credentials file which is a text file in the format KEY = VALUE and returns a dictionary of
    the APIC credentials. Specifically URL, LOGIN, and PASSWORD
    """
    credentials = load_credentials(load_credential_options.filename)

    if not credentials:
        # Problem opening the file
        print("There was a problem opening the Credentials file " +  load_credential_options.filename + "!")
        sys.exit('Aborting program Execution')
    else:
        for key in credentials.keys():
            print(credentials[key])


# Standard call to the main() function.
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Load ACI APIC Credentials", epilog="Usage: python load_apic_credentials.py or python load_apic_credentials.py -f 'somefile.txt' ")
    parser.add_argument('-f', '--filename', help='Option used to pass a credentials file other than the default "credentias.py"',
                        default='credentials.py')

    load_credential_options = parser.parse_args()

    main()

