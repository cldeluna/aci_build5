#!/usr/bin/python -tt
# Project: python
# Filename: aci_fabric_step5b_vmm
# claud
# PyCharm

from __future__ import absolute_import, division, print_function

__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "4/30/2017"
__copyright__ = "Copyright (c) 2016 Claudia"
__license__ = "Python"

import argparse
import sys
import json
import requests
import time
import argparse
import load_apic_credentials
import aci_fabric_build_utilities
import aci_fabric_step2b_accpol
import csv
import re

requests.packages.urllib3.disable_warnings()



#########################################################
##### STEP 5B MM Domain                            #####
#########################################################

#########################################################
##### VMM > VMware                                #######
#########################################################


def  vmw_vmmcreds_payload(vmm_name, cred_name, desc, usr, pwd, status):


    if not status:
        payload = {
            "vmmUsrAccP": {
                "attributes": {
                    "dn": "uni/vmmp-VMware/dom-" + vmm_name + "/usracc-" + cred_name,
                    "name": cred_name,
                    "descr": desc,
                    "usr": usr,
                    "pwd": pwd,
                    "status": "created"
                },
                "children": []
            }
        }
    else:
        #
        payload = {
            "vmmUsrAccP": {
                "attributes": {
                    "dn": "uni/vmmp-VMware/dom-" + vmm_name + "/usracc-" + cred_name,
                    "status": "deleted"
                },
                "children": []
            }
        }
    return payload

## vmw_vcenter_payload (name,vmm_name,cred_name,ip,dvsversion,dc_name,stats , status):

def vmw_vcenter_payload (name, vmm_name, cred_name, ip, dvsversion, dc_name,stats , status):


    if not status:
        payload = {
            "vmmCtrlrP": {
                "attributes": {
                    "dn": "uni/vmmp-VMware/dom-" + vmm_name + "/ctrlr-" + name,
                    "name": name,
                    "hostOrIp": ip,
                    "dvsVersion": str(dvsversion),
                    "rootContName": dc_name,
                    "statsMode": stats,
                    "status": "created"
                },
                "children": [{
                    "vmmRsAcc": {
                        "attributes": {
                            "tDn": "uni/vmmp-VMware/dom-" + vmm_name + "/usracc-" + cred_name,
                            "status": "created"
                        },
                        "children": []
                    }
                }]
            }
        }
    else:
        #
        payload = {
            "vmmCtrlrP": {
                "attributes": {
                    "dn": "uni/vmmp-VMware/dom-" + vmm_name + "/ctrlr-" + name,
                    "status": "deleted"
                },
            }
        }
    return payload


def vmw_vmm_payload(name,delimeter,secdom,vmmpool,override_lagpol,overrid_lldppol, status):

    if not status:
        payload = {

            "vmmDomP": {
                "attributes": {
                    "dn": "uni/vmmp-VMware/dom-" + name,
                    "name": name,
                    "delimiter": delimeter,
                    "status": "created"
                },
                "children": [{
                    "aaaDomainRef": {
                        "attributes": {
                            "dn": "uni/vmmp-VMware/dom-" + name + "/domain-" + secdom,
                            "name": secdom,
                            "status": "created"
                        },
                        "children": []
                    }
                },
                {
                    "infraRsVlanNs": {
                        "attributes": {
                            "tDn": "uni/infra/vlanns-[" + vmmpool + "]-dynamic",
                            "status": "created"
                        },
                        "children": []
                    }
                },
                {
                    "vmmVSwitchPolicyCont": {
                        "attributes": {
                            "dn": "uni/vmmp-VMware/dom-" + name + "/vswitchpolcont",
                            "status": "created,modified"
                        },
                        "children": [{
                            "vmmRsVswitchOverrideLacpPol": {
                                "attributes": {
                                    "tDn": "uni/infra/lacplagp-" + override_lagpol,
                                    "status": "created,modified"
                                },
                                "children": []
                            }
                        },
                        {
                            "vmmRsVswitchOverrideLldpIfPol": {
                                "attributes": {
                                    "tDn": "uni/infra/lldpIfP-" + overrid_lldppol,
                                    "status": "created,modified"
                                },
                                "children": []
                            }
                        }]
                    }
                }]
            }
        }
    else:
        #
        payload = {
            "vmmDomP": {
                "attributes": {
                    "dn": "uni/vmmp-VMware/dom-" + name,
                    "status": "deleted"
                },
            }
        }
    return payload
#
# def vmw_vmm_aep_payload(name, aep, status):
#
#     if not status:
#         payload = {
#             "infraRsDomP": {
#                 "attributes": {
#                     "dn": "uni/vmmp-VMware/dom-" + name + "/rsdomP-[uni/infra/attentp-" + aep + "]",
#                     # "lcOwn": "local",
#                     # "modTs": "2018-01-02T16:07:21.622-05:00",
#                     "status": "",
#                     "tCl": "infraAttEntityP",
#                     "tDn": "uni/infra/attentp-" + aep
#                     # "status": "created,modified"
#                 }
#             }
#         }
#
#     else:
#         #
#         payload = {
#             "infraRtDomP": {
#                 "attributes": {
#                     "dn": "uni/vmmp-VMware/dom-" + name + "/rtdomP-[uni/infra/attentp-" + aep + "]",
#                     "status": "deleted"
#                 },
#             }
#         }
#
#     return payload


##### MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN #####

# Provided main() calls the above functions
def main():
    """
    This script takes a CSV file and converts it to a JSON Payload file to configure ACI VMM Domain for VMware

    """

    # define non 200 response dictionary for items that failed to apply
    error_list = []

    # set variable filename to the json file passed as the first argument
    filename = arguments.payload_file

    # Set to "True" to delete the objects defined in this script on the APIC by passing -x
    # default is "False"
    object_status_delete = arguments.xdelete

    action_text = "Adding" if not object_status_delete else "Removing"

    start_time = time.clock()

    # Create a Log file
    filename_base = filename.split(".")[0]
    timestr = time.strftime("%Y%m%d-%H%M%S")
    log_filename = filename_base + "-" + action_text.upper() + "-" + timestr + ".log"
    log_file = open(log_filename, 'w')

    # USING NEW LOAD APCI CREDENTIALS SCRIPT
    credentials = load_apic_credentials.load_credentials(arguments.filename)

    if not credentials:
        # Problem opening the file
        print("There was a problem opening the Credentials file " + arguments.filename + "!")
        sys.exit('Aborting program Execution')
    else:
        APIC_URL = credentials['URL']
        APIC_USER = credentials['LOGIN']
        APIC_PASS = credentials['PASSWORD']

    base_url = APIC_URL + '/api/'

    # create credentials structure
    name_pwd = {'aaaUser': {'attributes': {'name': APIC_USER, 'pwd': APIC_PASS}}}
    json_credentials = json.dumps(name_pwd)

    # log in to API
    login_url = base_url + 'aaaLogin.json'
    post_response = requests.post(login_url, data=json_credentials, verify=False)

    # get token from login response structure
    auth = json.loads(post_response.text)
    login_attributes = auth['imdata'][0]['aaaLogin']['attributes']
    auth_token = login_attributes['token']

    # create cookie array from token
    cookies = {}
    cookies['APIC-Cookie'] = auth_token

    post_url = APIC_URL + '/api/node/mo/uni.json'

    ##### Document Options for script Execution

    args_dict = vars(arguments)
    print("\n===========Running ACI STEP 5B: Configure Virtual Machine Manager (VMM)===========")
    print("===========                    With the following options                     ===========")
    log_file.write("\n===========Running ACI STEP 5B: Configure Virtual Machine Manager (VMM)===========")
    log_file.write("\n===========                    With the following options                     ===========\n")
    for key, value in args_dict.items():
        txt = '{:15} : {:10}'.format(key, str(value))
        print(txt)
        log_file.write(txt + "\n")

    if arguments.all or arguments.credentials or arguments.vcenter or arguments.vmware :
        aci_fabric_build_utilities.print_header(APIC_URL, APIC_USER, object_status_delete, log_file)

    else:
        print("\nNo executable arguments passed.  Use the -h option for help.")


    if arguments.all and arguments.xdelete:
        msg = "\n****You are about to remove all objects defined in the payload file " + filename + " from " + APIC_URL + "!"
        print(msg)
        confirmation1 = aci_fabric_build_utilities.get_input("\nPlease confirm that is the action you wish to take (Y/n): ")
        if confirmation1 == "Y":
            confirmation2 = aci_fabric_build_utilities.get_input("\n\tAre you certain (Y/n)? ")
            if confirmation2 != "Y":
                sys.exit("\nAborting Configuration Run at User request.")
        else:
            sys.exit("Aborting Configuration Run at User request.")

    ##### LOAD DATA #####

    #### Load JSON Payload

    json_payload = aci_fabric_build_utilities.csv2json(filename)


    ##### VMM POLICIES #####


    # Configure VMM Domain Skeleton
    # key: vmw_vmm
    if arguments.all or arguments.vmware:
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'vmw_vmm')

        for line in data:
            # Create VMM and tie to Creds and Controller
            #vmw_vmm_payload(name, delimeter, secdom, vmmpool, override_lagpol, overrid_lldppol, status):
            payload = vmw_vmm_payload(line['name'], line['delimeter'], line['secdom'], line['vmmpool'],
                                      line['override_lagpol'], line['override_lldppol'],
                                           object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log("Virtual Machine Manager (VMM)", resp, line['name'],
                                                             log_file, error_list)

        # Add AEP Association to VMM
        # aci_fabric_step2b_accpol
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'aep')

        for line in data:

            payload = aci_fabric_step2b_accpol.aep_payload(line['name'], line['desc'], line['dom'], line['domtype'],
                                                           object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log("VMM to AEP Association", resp, line['name'],
                                                             log_file, error_list)

    # Configure vCenter Credentials
    # key: vmw_vcenter
    if arguments.all or arguments.credentials:
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'vmw_vmmcreds')

        for line in data:
            # vmw_vmmcreds_payload(vmm_name, cred_name, desc, usr, pwd, status):
            payload = vmw_vmmcreds_payload(line['vmm_name'], line['cred_name'], line['desc'], line['usr'], line['pwd'],
                                           object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log("vCenter Credentials", resp, line['cred_name'],
                                                             log_file, error_list)


    # Configure vCenter Controller
    # key: vmw_vcenter
    if arguments.all or arguments.vcenter:
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'vmw_vcenter')

        for line in data:
            # # def vmw_vcenter_payload (name, vmm_name, cred_name, ip, dvsversion, dc_name,stats, status):
            payload = vmw_vcenter_payload(line['name'], line['vmm_name'], line['cred_name'], line['ip'],
                                           line['dvsversion'], line['dc_name'], line['stats'],
                                           object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log("vCenter Controller", resp, line['name'],
                                                             log_file, error_list)




    ############ END of PROCESSING #######################
    # End - Calculate time of execution
    delta_time = str(time.clock() - start_time)
    textt = "\nScript Execution Time (s): " + delta_time
    print(textt)
    log_file.write(textt + "\n")

    aci_fabric_build_utilities.payload_size(json_payload,log_file)

    # ERRORS
    if len(error_list) > 0:
        textt = "\n\nNumber of Errors in run: {}\n".format(len(error_list))
        print(textt)
        log_file.write(textt + "\n")
        for line in error_list:
            print(line['post_action'])
            log_file.write(line['post_action'] + "\n")
            print(line['imdata'][0]['error']['attributes']['text'] + "\n\n")
            log_file.write(line['imdata'][0]['error']['attributes']['text'] + "\n\n")
    else:
        textt = "\n\nRun Completed without any Errors!"
        print(textt)
        log_file.write(textt + "\n")

    print(textt)
    log_file.write(textt + "\n")

    log_file.close()

# Standard call to the main() function.
if __name__ == '__main__':
    # Configure Basic Fabric Constructs
    # -n NTP Fabric > Fabric Policies > Pod Policies > Policis > Date and time
    # -s SNMP (future)
    # -p Pod Policy
    # -r Route Reflector Fabric > Fabric Policies > Pod Policies > Communication > BGP Route Reflector default
    # -t Timezone
    # -i Ignore Acknowledged Fault

    parser = argparse.ArgumentParser(description="ACI STEP 5B: Configure ACI Virtual Machine Manager (VMM)",
                                     epilog="Usage: aci_fabric_step5b_vmm.py 'my_payload.csv' -a to create and -a -x to delete")

    parser.add_argument('payload_file', help='Name of the payload file to use in this script.')

    parser.add_argument('-x', '--xdelete',
                        help='True to remove/delete/reset configuration and False to create (default) action unless -x is used',
                        action='store_true',
                        default=False)

    parser.add_argument('-a', '--all',
                        help='Execute all object CRUD sections. Without this argument nothing will execute.',
                        action='store_true', default=False)

    parser.add_argument('-c', '--credentials', help='Execute Credentials Function', action='store_true',
                        default=False)
    parser.add_argument('-v', '--vcenter', help='Execute vCenter Controller Function', action='store_true',
                        default=False)
    parser.add_argument('-m', '--vmware', help='Execute vMware VMM Function including AEP Association using '
                                                'Step2B aep function.', action='store_true',
                        default=False)

    parser.add_argument('-f', '--filename',
                        help='Option used to pass a credentials file other than the default "credentias.py"',
                        default='credentials.py')

    arguments = parser.parse_args()
    # print arguments

    main()