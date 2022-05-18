#!/usr/bin/python -tt
# Project: python
# Filename: aci_fabric_step3_tnpol
# claud
# PyCharm

from __future__ import absolute_import, division, print_function

__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "4/30/2017"
__copyright__ = "Copyright (c) 2016 Claudia"
__license__ = "Python"


import sys
import json
import requests
import time
import argparse
import load_apic_credentials
import aci_fabric_build_utilities
import re

requests.packages.urllib3.disable_warnings()


#########################################################
##### STEP 3 Tenant Network & Application Policies  #####
#########################################################

#########################################################
##### TENANT >                                      #####
#########################################################
def createtn_payload(name, desc, vrf, secdom, status):

    if not status:
        payload = {
            "fvTenant": {
                "attributes": {
                    "dn": "uni/tn-" + name,
                    "name": name,
                    "descr": aci_fabric_build_utilities.slash_replace(desc),
                    "status": "created"
                },
                "children": [
                    {
                        "aaaDomainRef": {
                            "attributes": {
                                "dn": "uni/tn-" + name + "/domain-" + secdom,
                                "name": secdom,
                                "status": "created"
                            },
                            "children": []
                        }
                    },
                    {
                        "fvRsTenantMonPol": {
                            "attributes": {
                                "tnMonEPGPolName": "default",
                                "status": "created,modified"
                            },
                            "children": []
                        }
                    }]
            }
        }
    else:
        payload = {
            "fvTenant": {
                "attributes": {
                    "dn": "uni/tn-" + name,
                    # "name": "My_Tenant-TN",
                    # "descr": "This is my tenant",
                    # "rn": "tn-My_Tenant-TN",
                    "status": "deleted"
                },

            }
        }
    return payload


def ctx_payload(name, desc, tenant, enfctrl, enfctrldir, status):

    if not status:
        payload = {
            "fvCtx": {
                "attributes": {
                    "dn": "uni/tn-" + tenant + "/ctx-" + name,
                    "name": name,
                    "descr": aci_fabric_build_utilities.slash_replace(desc),
                    # Valid Values = "enforced" "unenforced"
                    "pcEnfPref": enfctrl,
                    # Valid Values = "egress" "ingress"
                    "pcEnfDir": enfctrldir,
                    "status": "created"
                },
                "children": [{
                    "fvRsCtxToEpRet": {
                        "attributes": {
                            "tnFvEpRetPolName": "default",
                            "status": "created,modified"
                        },
                        "children": []
                    }
                },
                    {
                        "fvRsCtxMonPol": {
                            "attributes": {
                                "tnMonEPGPolName": "default",
                                "status": "created,modified"
                            },
                            "children": []
                        }
                    },
                    {
                        "fvRsCtxToExtRouteTagPol": {
                            "attributes": {
                                "tnL3extRouteTagPolName": "default",
                                "status": "created,modified"
                            },
                            "children": []
                        }
                    }]
            }
        }
    else:
        payload = {
            "fvCtx": {
                "attributes": {
                    "dn": "uni/tn-" + tenant + "/ctx-" + name,
                    "status": "deleted"
                },
            }
        }
    return payload


def bd_payload(name, desc, tn, vrf, arpflood, unkmacu, limit, unicastrtr, status):

    if not status:
        payload = {
            "fvBD": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/BD-" + name,
                    #"mac": "00:22:BD:F8:19:FF",
                    "name": name,
                    "descr": aci_fabric_build_utilities.slash_replace(desc),
                    # Valid Values = "true" "false" Use true for custom
                    "arpFlood": arpflood.lower(),
                    # Valid Values = "flood" "proxy" Use flood for custom
                    "unkMacUcastAct": unkmacu,
                    "limitIpLearnToSubnets": limit,
                    "unicastRoute": unicastrtr,
                    "status": "created"
                },
                "children": [{
                    "fvRsCtx": {
                        "attributes": {
                            "tnFvCtxName": vrf,
                            "status": "created,modified"
                        },
                        "children": []
                    }
                },
                    {
                        "fvRsBdToEpRet": {
                            "attributes": {
                                "tnFvEpRetPolName": "default",
                                "status": "created,modified"
                            },
                            "children": []
                        }
                    },
                    {
                        "fvRsIgmpsn": {
                            "attributes": {
                                "tnIgmpSnoopPolName": "default",
                                "status": "created,modified"
                            },
                            "children": []
                        }
                    }]
            }
        }
    else:
        payload = {
            "fvBD": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/BD-" + name,
                    "status": "deleted"
                },
            }
        }
    return payload


def bdnet_payload(ip, mask, desc, tn, bd, scope, status):

    if not status:
        payload = {
            "fvSubnet": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/BD-" + bd + "/subnet-[" + ip + "/" + mask + "]",
                    "ip": ip + "/" + mask,
                    # Valid values = public, private
                    "scope": scope,
                    "descr": aci_fabric_build_utilities.slash_replace(desc),
                    "ctrl": "",
                    "name": "",
                    "preferred": "no",
                    "virtual": "no",
                    "status": "created"
                },
                "children": []
            }
        }
    else:
        payload = {
            "fvSubnet": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/BD-" + bd + "/subnet-[" + ip + "/" + mask + "]",
                    "status": "deleted"
                },
            }
        }
    return payload


def ap_payload(name, desc, tn, status):

    if not status:
        payload = {
            "fvAp": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/ap-" + name,
                    "name": name,
                    "descr": aci_fabric_build_utilities.slash_replace(desc),
                    "status": "created"
                },
                "children": []
            }
        }
    else:
        payload = {
            "fvAp": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/ap-" + name,
                    "status": "deleted"
                },
            }
        }
    return payload


def epg_payload(name, desc, tn, anp, bd, status):

    if not status:
        payload = {
            "fvAEPg": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/ap-" + anp + "/epg-" + name,
                    "name": name,
                    "descr": aci_fabric_build_utilities.slash_replace(desc),
                    # Valid Values: enforced, unenforced
                    "pcEnfPref": "unenforced",
                    "status": "created"
                },
                "children": [{
                    "fvRsBd": {
                        "attributes": {
                            "tnFvBDName": bd,
                            "status": "created,modified"
                        },
                        "children": []
                    }
                }]
            }
        }
    else:
        payload = {
            "fvAEPg": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/ap-" + anp + "/epg-" + name,
                    "status": "deleted"
                },
            }
        }
    return payload


# Provided Contract
def provcondef_payload(name, tn, anp, epg, status):

    if not status:
        payload = {
            "fvRsProv": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/ap-" + anp + "/epg-" + epg + "/rsprov-" + name,
                    "matchT": "AtleastOne",
                    "prio": "unspecified",
                    "tnVzBrCPName": "" + name,
                    "status": "created,modified"
                }
            }
        }
    else:
        payload = {
            "fvRsProv": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/ap-" + anp + "/epg-" + epg + "/rsprov-" + name,
                    "status": "deleted"
                },
            }
        }
    return payload


# Consumed Contract
def conscondef_payload(name, tn, anp, epg, status):

    if not status:
        payload = {
            "fvRsCons": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/ap-" + anp + "/epg-" + epg + "/rscons-" + name,
                    "prio": "unspecified",
                    "tnVzBrCPName": "" + name,
                    "status": "created,modified"
                }
            }
        }
    else:
        payload = {
            "fvRsCons": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/ap-" + anp + "/epg-" + epg + "/rscons-" + name,
                    "status": "deleted"
                },
            }
        }
    return payload


def contractdef_payload(name, scope, tn, subject, status):
    if status:
        payload = {
            "vzBrCP": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/brc-" + name,
                    "name": name,
                    # Valid Values: application-profile,context(vrf),tenant,global
                    "scope": scope,
                    "rn": "/brc-" + name,
                    "status": "created"
                },
                "children": [{
                    "vzSubj": {
                        "attributes": {
                            "dn": "uni/tn-" + tn + "/brc-" + name + "/subj-" + subject,
                            "name": subject,
                            "rn": "subj-" + subject,
                            "status": "created,modified"
                        },

                        "children": [{
                            "vzRsSubjFiltAtt": {
                                "attributes": {
                                    "status": "created,modified",
                                    "tnVzFilterName": "default",
                                    "directives": "none"
                                },
                                "children": []
                            }
                        }
                        ]
                    }
                }
                ]

            }
        }
    else:
        payload = {
            "vzBrCP": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/brc-" + name,
                    "status": "deleted"
                },
            }
        }
    return payload


def bdl3out_payload(tn, bd, l3out, status):

    if not status:
        payload = {
            "fvRsBDToOut": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/BD-" + bd + "/rsBDToOut-" + l3out,
                    "tnL3extOutName": l3out,
                    "status": "created,modified"
                }
            }
        }
    else:
        payload = {
            "fvRsBDToOut": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/BD-" + bd + "/rsBDToOut-" + l3out,
                    "status": "deleted"
                }
            }
        }
    return payload



##### MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN #####

# Provided main() calls the above functions
def main():
    """
    This script creates BD and Subnets in the common tenant and ANP, EPGs in a separate tenant that use the BDs
    created in the common tenant.

    The data currently comes from the IP Address Allocations workbook Columns Z - AF and is formatted via
    Mr. Data Converter
    https://shancarter.github.io/mr-data-converter/

    The credentials.py file is used for credentials.

    """

    # define non 200 response dictionary for items that failed to apply
    error_list = []

    # set variable filename to the json file passed as the first argument
    filename = arguments.payload_file

    # Set to "True" to delete the objects defined in this script on the APIC by passing -x
    # default is "False"
    object_status_delete = arguments.xdelete

    action_text = "Adding" if not object_status_delete else "Removing"

    start_time = aci_fabric_build_utilities.get_current_time()

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
    print("\n===========  Running ACI STEP 3: Configure Tenant & Application Constructs ===========")
    print("===========                    With the following options                     ===========")
    log_file.write("\n===========  Running ACI STEP 3: Configure Tenant & Application Constructs ===========")
    log_file.write("\n===========                    With the following options                     ===========\n")
    for key, value in args_dict.items():
        txt = '{:15} : {:10}'.format(key,str(value))
        print(txt)
        log_file.write(txt + "\n")

    if arguments.all or arguments.tenant or arguments.vrf or arguments.bd or arguments.subnet or arguments.anp \
            or arguments.epg or arguments.prov or arguments.cons or arguments.l3out:
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
  

    # Configure Tenant
    # the -t option creates a tenant and security domain for that tenant.
    # key: tnpol

    if arguments.all or arguments.tenant:

        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'createtn')

        for line in data:
            # createtn_payload(name, desc, vrf, secdom, status)
            payload = createtn_payload(line['name'], line['desc'], line['vrf'],  line['secdom'], object_status_delete)
            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} Tenant & SecDom Policy", resp, line['name'],
                                                             log_file, error_list)

    # Configure VRF/Private Network
    # the -v option creates a vrf for any tenant including common
    # key: ctx

    if arguments.all or arguments.vrf:

        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'ctx')

        for line in data:
            # ctx_payload(name, desc, tenant, enfctrl, enfctrldir, status)
            payload = ctx_payload(line['name'], line['desc'], line['tenant'], line['enfctrl'],
                                  line['enfctrldir'], object_status_delete)
            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} VRF/Private Network", resp, line['name'],
                                                             log_file, error_list)

    # Configure Bridge Domain
    # key: bd

    if arguments.all or arguments.bd:

        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'bd')

        for line in data:
            #bd_payload(name, desc, tn, vrf, arpflood, unkmacu, limit, unicastrtr, status)
            payload = bd_payload(line['name'], line['desc'], line['tn'], line['vrf'],
                                  line['arpflood'], line['unkmacu'], line['limit'], line['unicastrtr'],
                                  object_status_delete)
            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} Bridge Domain", resp, line['name'],
                                                             log_file, error_list)

    # Configure Bridge Domain Subnet(s)
    # key: bdnet

    if arguments.all or arguments.subnet:

        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'bdnet')

        for line in data:
            # bdnet_payload(ip, mask, desc, tn, bd, scope, status)
            payload = bdnet_payload(line['ip'], str(line['mask']), line['desc'], line['tn'], line['bd'], line['scope'], object_status_delete)
            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} Bridge Domain subnet(s)", resp,
                                                             line['ip'] +"/" + str(line['mask']),
                                                             log_file, error_list)

    # Configure Application Network Profile (AP)
    # key: ap

    if arguments.all or arguments.anp:

        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'anp')

        for line in data:
            # ap_payload(name, desc, tn, status)
            payload = ap_payload(line['name'], line['desc'], line['tn'], object_status_delete)
            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} Application Network Profile", resp, line['name'],
                                                             log_file, error_list)

    # Configure End Point Group (EPG)
    # key: epg

    if arguments.all or arguments.epg:

        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'epg')

        for line in data:
            # epg_payload(name, desc, tn, anp, bd, status)
            payload = epg_payload(line['name'], line['desc'], line['tn'], line['anp'], line['bd'], object_status_delete)
            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} End Point Group (EPG)", resp, line['name'],
                                                             log_file, error_list)

    # Configure EPG Provider Contract
    # key: provcondef

    if arguments.all or arguments.prov:

        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'provcondef')

        for line in data:
            # provcondef_payload(name, tn, anp, epg, status)
            payload = provcondef_payload(line['name'], line['tn'], line['anp'], line['epg'], object_status_delete)
            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} EPG Provider Contract", resp,
                                                             line['name'] + " " + line['epg'],
                                                             log_file, error_list)

    # Configure EPG consumer Contract
    # key: conscondef

    if arguments.all or arguments.cons:

        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'conscondef')

        for line in data:
            # conscondef_payload(name, tn, anp, epg, status)
            payload = conscondef_payload(line['name'], line['tn'], line['anp'], line['epg'], object_status_delete)
            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} EPG Consumer Contract", resp,
                                                             line['name'] + " " + line['epg'],
                                                             log_file, error_list)

    # Configures Contract
    # key: contractdef
    if arguments.all or arguments.ctr:

        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'contractdef')

        print(data)

        for line in data:
            # contractdef_payload(name, scope, tn, subject, status)
            payload = contractdef_payload(line['name'], line['scope'], line['tn'], line['subject'], object_status_delete)
            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} Contracts", resp,
                                                     line['name'] + " " + line['tn'], log_file, error_list)


    # Configure Bridge Domain L3Out Association
    # key: bdl3out

    if arguments.all or arguments.l3out:

        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'bdl3out')

        for line in data:
            # bdl3out_payload(tn, bd, l3out, status)
            payload = bdl3out_payload(line['tn'], line['bd'], line['l3out'], object_status_delete)
            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} Bridge Domain L3Out Association", resp,
                                                             line['bd'] + " L3Out association => " + line['l3out'],
                                                             log_file, error_list)



    ############ END of PROCESSING #######################
    # End - Calculate time of execution
    delta_time = str(aci_fabric_build_utilities.get_current_time() - start_time)
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

    #Configure Logical Network Constructs

    parser = argparse.ArgumentParser(description="ACI STEP 3: Configure Tenant Network & Application Constructs",
                                     epilog="Usage: aci_fabric_step3_tnpol.py 'my_payload.csv' -a to create and -a -x to delete")

    parser.add_argument('payload_file', help='Name of the payload file to use in this script.')

    parser.add_argument('-x', '--xdelete',
                        help='True to remove/delete/reset configuration and False to create (default) action unless -x is used',
                        action='store_true',
                        default=False)

    parser.add_argument('-a', '--all', help='Execute all object CRUD sections. Without this argument nothing will execute.',
                        action='store_true', default=False)

    parser.add_argument('-t', '--tenant', help='Execute Tenant function', action='store_true',default=False)
    parser.add_argument('-v', '--vrf', help='Execute VRF function', action='store_true', default=False)
    parser.add_argument('-b', '--bd', help='Execute Bridge Domain function', action='store_true', default=False)
    parser.add_argument('-s', '--subnet', help='Execute Subnet function', action='store_true', default=False)
    parser.add_argument('-n', '--anp', help='Execute Application Network Profile function', action='store_true', default=False)
    parser.add_argument('-e', '--epg', help='Execute End Point Group function', action='store_true', default=False)
    parser.add_argument('-p', '--prov', help='Execute Provider Contract function', action='store_true', default=False)
    parser.add_argument('-o', '--cons', help='Execute Consumer Contract function', action='store_true', default=False)
    parser.add_argument('-r', '--ctr', help='Execute Contract function', action='store_true', default=False)
    parser.add_argument('-3', '--l3out', help='Execute L3 Out Association to BD function', action='store_true', default=False)

    parser.add_argument('-f', '--filename',
                        help='Option used to pass a credentials file other than the default "credentias.py"',
                        default='credentials.py')

    arguments = parser.parse_args()
    #print arguments

    main()
