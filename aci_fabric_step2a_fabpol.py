#!/usr/bin/python -tt
# Project: python
# Filename: aci_fabric_step2a_fabpol
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
import csv
import re

requests.packages.urllib3.disable_warnings()



#########################################################
##### STEP 2a Fabric Policies                       #####
#########################################################

#########################################################
##### FABRIC > Fabric Policies > Monitoring Policies#####
#########################################################


#  Fabric > Fabric Policies > Monitoring Policies > Common Policy > Health Score Evaluation Policies
#       > Health Score Evaluation Policy
#       In the properties pane, Enable (Check) 'Ignore Acknowledged Faults' setting
#  Ignore Acknowledged Fault
def igackfault_payload(check, status):

    # status is set by the -x --xdelete argument to False for deletion
    # Read: If (delete) not true create payload else (delete) IS true and remove

    if not status:
        payload = {
            "healthEvalP": {
                "attributes": {
                    "dn": "uni/fabric/hsPols/hseval",
                    # Valid Values: true false
                    "ignoreAckedFaults": check
                },
                "children": []
            }
        }
    else:
        # Don't delete but set to
        payload = {
            "healthEvalP": {
                "attributes": {
                    "dn": "uni/fabric/hsPols/hseval",
                    "ignoreAckedFaults": "false"
                },
                "children": []
            }
        }
    return payload



#########################################################
##### FABRIC > Fabric Policies > PodPolicies #####
#########################################################

# Route Reflector Policies
def rrasn_payload(asn, status):
    if not status:
        payload = {
            "bgpAsP": {
                "attributes": {
                    "dn": "uni/fabric/bgpInstP-default/as",
                    "asn": str(asn),
                    "status": "created,modified"
                },
                "children": []
            }
        }
    else:
        # I this case ASN Number is set to  0 but lets try
        payload = {
            "bgpAsP": {
                "attributes": {
                    "dn": "uni/fabric/bgpInstP-default/as",
                    "asn": "1",
                    "status": "modified"
                },
                "children": []
            }
        }
    return payload

def rrdesc_payload(name, desc, status):
    if not status:
        payload = {
            "bgpInstPol": {
                "attributes": {
                    "dn": "uni/fabric/bgpInstP-default",
                    "descr": aci_fabric_build_utilities.slash_replace(desc)
                },
                "children": []
            }
        }
    else:
        payload = {
            "bgpInstPol": {
                "attributes": {
                    "dn": "uni/fabric/bgpInstP-default",
                    "descr": ""
                },
                "children": []
            }
        }
    return payload

def rrnode_payload(name, desc, status):
    if not status:
        payload = {
            "bgpRRNodePEp": {
                "attributes": {
                    "dn": "uni/fabric/bgpInstP-default/rr/node-" + name,
                    "id": name,
                    "descr": desc,
                    #"rn": "node-201",
                    "status": "created"
                },
                "children": []
            }
        }
    else:
        payload = {
            "bgpRRNodePEp": {
                "attributes": {
                    "dn": "uni/fabric/bgpInstP-default/rr/node-" + name,
                    "status": "deleted"
                },
                "children": []
            }
        }
    return payload


#########################################################
##### FABRIC > Fabric Policies > DATE & TIME ########
#########################################################

def ntppol_payload(name, desc, authSt, status):

    if not status:
        payload = {
            "datetimePol": {
                "attributes": {
                    "dn": "uni/fabric/time-"+ name,
                    "name": name,
                    # Valid Values = "enabled"  "disabled"
                    "authSt": authSt,
                    "descr": desc,
                    #"rn": "time-NTP_EMPTY",
                    "status": "created"
                },
                "children": []
            }
        }
    else:
        payload = {
            "datetimePol": {
                "attributes": {
                    "dn": "uni/fabric/time-" + name,
                    "status": "deleted"
                },
                "children": []
            }
        }
    return payload

def ntpsrv_payload(name, desc, pref, policy, status):

    if not status:
        payload = {
            "datetimeNtpProv": {
                "attributes": {
                    "dn": "uni/fabric/time-"+ policy + "/ntpprov-" + name,
                    "name": name,
                    "descr": desc,
                    # Valid Values = "true"  "false"
                    "preferred": pref.lower(),
                    "status": "created"
                },
                "children": []
            }
        }
    else:
        payload = {
            "datetimeNtpProv": {
                "attributes": {
                    "dn": "uni/fabric/time-"+ policy + "/ntpprov-" + name,
                    "status": "deleted"
                },
                "children": []
            }
        }
    return payload


def podpolgrp_payload(name, desc, ntp, isis, coop, bgprr, mgt, snmp, status):

    if not status:
        payload = {
            "fabricPodPGrp": {
                "attributes": {
                    "dn": "uni/fabric/funcprof/podpgrp-" + name,
                    "name": name,
                    "descr": desc,
                    "status": "created"
                },
                "children": [{
                    "fabricRsTimePol": {
                        "attributes": {
                            "tnDatetimePolName": ntp,
                            "status": "created,modified"
                        },
                        "children": []
                    }
                },
                    {
                        "fabricRsPodPGrpIsisDomP": {
                            "attributes": {
                                "tnIsisDomPolName": isis,
                                "status": "created,modified"
                            },
                            "children": []
                        }
                    },
                    {
                        "fabricRsPodPGrpCoopP": {
                            "attributes": {
                                "tnCoopPolName": coop,
                                "status": "created,modified"
                            },
                            "children": []
                        }
                    },
                    {
                        "fabricRsPodPGrpBGPRRP": {
                            "attributes": {
                                "tnBgpInstPolName": bgprr,
                                "status": "created,modified"
                            },
                            "children": []
                        }
                    },
                    {
                        "fabricRsCommPol": {
                            "attributes": {
                                "tnCommPolName": mgt,
                                "status": "created,modified"
                            },
                            "children": []
                        }
                    },
                    {
                        "fabricRsSnmpPol": {
                            "attributes": {
                                "tnSnmpPolName": snmp,
                                "status": "created,modified"
                            },
                            "children": []
                        }
                    }]
            }
        }
    else:
        payload = {
            "fabricPodPGrp": {
                "attributes": {
                    "dn": "uni/fabric/funcprof/podpgrp-" + name,
                    "status": "deleted"
                },
                "children": []
            }
        }
    return payload


def podpol_payload(profname, grpname, status):

    if not status:

        if profname == "default":
            payload = {
                "fabricPodS": {
                    "attributes": {
                        "descr": "",
                        "dn": "uni/fabric/podprof-default/pods-default-typ-ALL",
                        "name": "default",
                        "nameAlias": "",
                        "ownerKey": "",
                        "ownerTag": "",
                        "type": "ALL",
                        "status": "created,modified"
                    },
                    "children": [
                        {
                            "fabricRsPodPGrp": {
                                "attributes": {
                                    "tDn": "uni/fabric/funcprof/podpgrp-"+grpname,
                                    "status": "created,modified"
                                }
                            }
                        }
                    ]
                }
            }
        else:

            payload = {

                "fabricPodP": {
                    "attributes": {
                        "dn": "uni/fabric/podprof-" + profname,
                        "status": "created,modified"
                    },
                    "children": [{
                        "fabricPodS": {
                            "attributes": {
                                "dn": "uni/fabric/podprof-" + profname + "/pods-default-typ-range",
                                "name": "default",
                                "status": "created",
                                "type": "range",
                                "rn": "pods-default-typ-range"
                            },
                            "children": [{
                                "fabricPodBlk": {
                                    "attributes": {
                                        "dn": "uni/fabric/podprof-" + profname + "/pods-default-typ-range/podblk-dfba4b9e4d568b2c",
                                        # "name": "dfba4b9e4d568b2c",
                                        # "rn": "podblk-dfba4b9e4d568b2c",
                                        "status": "created, modified"
                                    },
                                    "children": []
                                }
                            },
                                {
                                    "fabricRsPodPGrp": {
                                        "attributes": {
                                            "tDn": "uni/fabric/funcprof/podpgrp-" + grpname,
                                            "status": "created, modified"
                                        },
                                        "children": []
                                    }
                                }]
                        }
                    }]
                }

            }

    else:

        if not profname == "default":

            payload = {

                "fabricPodP": {
                    "attributes": {
                        "dn": "uni/fabric/podprof-" + profname,
                        "status": "deleted"
                    },
                    "children": []
                }
            }

        else:

            payload = {


                "fabricPodP": {
                    "attributes": {
                        "dn": "uni/fabric/podprof-" + profname,
                        "status": "modified"
                    },
                    "children": [{
                        "fabricPodS": {
                            "attributes": {
                                "dn": "uni/fabric/podprof-" + profname + "/pods-default-typ-range",
                                "name": "default",
                                "status": "deleted",
                                "type": "range",
                                "rn": "pods-default-typ-range"
                            },
                            "children": [{
                                "fabricPodBlk": {
                                    "attributes": {
                                        "dn": "uni/fabric/podprof-" + profname + "/pods-default-typ-range/podblk-dfba4b9e4d568b2c",
                                        # # "name": "dfba4b9e4d568b2c",
                                        # # "rn": "podblk-dfba4b9e4d568b2c",
                                        "status": "deleted"
                                    },
                                    "children": []
                                }
                            },
                                {
                                    "fabricRsPodPGrp": {
                                        "attributes": {
                                            "tDn": "uni/fabric/funcprof/podpgrp-" + grpname,
                                            "status": "deleted"
                                        },
                                        "children": []
                                    }
                                }]
                        }
                    }]
                }

            }



    return payload


def timezone_payload(format, desc, showOffset, tz, status):

    """
    method: POST url: https: //172.30.254.11/api/node/mo/uni/fabric/format-default.jsonpayload{
        "datetimeFormat": {
            "attributes": {
                "dn": "uni/fabric/format-default",
                "tz": "n240_America-New_York"
            },
            "children": []
        }

        displayFormat   = local | utc
        showOffset      = enabled | disabled
        tx =            = "n240_America-New_York",
    """

    if not status:
        payload = {
            "datetimeFormat": {
                "attributes": {
                    "childAction": "",
                    "descr": desc,
                    "displayFormat": format,
                    "dn": "uni/fabric/format-default",
                    # "lcOwn": "local",
                    # "modTs": "2017-08-13T08:51:59.720-04:00",
                    # "name": "default",
                    # "nameAlias": "",
                    # "ownerKey": "",
                    # "ownerTag": "",
                    "showOffset": showOffset,
                    "status": "",
                    "tz": tz,
                    # "uid": "0"
                },
            "children": []
            }
        }
    else:
        payload = {
            "datetimeFormat": {
                "attributes": {
                    "childAction": "",
                    "descr": "",
                    "displayFormat": "utc",
                    "dn": "uni/fabric/format-default",
                    "showOffset": "disabled",
                    "status": ""
                },
            "children": []
            }
        }
    return payload


#########################################################
## FABRIC > Fabric Policies > Policies > Geolocation ####
#########################################################

def geosite_payload(name, desc, status):

    if not status:

        payload = {
            "geoSite": {
                "attributes": {
                    "dn": "uni/fabric/site-"+ name,
                    "name": name,
                    "descr": desc,
                    # "rn": "site-New_GEO_SITE",
                    "status": "created"
                },
                "children": []
            }
        }

    else:

        payload = {
            "geoSite": {
                "attributes": {
                    "dn": "uni/fabric/site-"+ name,
                    "status": "deleted"
                },
                "children": []
            }
        }

    return payload



def geobuilding_payload(site, name, desc, status):

    dn = f"uni/fabric/site-{site}/building-{name}"

    if not status:

        payload = {
            "geoBuilding": {
                "attributes": {
                    "dn": dn,
                    "name": name,
                    "descr": desc,
                    "status": "created"
                },
                "children": []
            }
        }

    else:

        payload = {
            "geoBuilding": {
                "attributes": {
                    "dn": dn,
                    "status": "deleted"
                },
                "children": []
            }
        }

    return payload


def geofloor_payload(site, bldg, name, desc, status):

    dn = f"uni/fabric/site-{site}/building-{bldg}/floor-{name}"

    if not status:

        payload = {
            "geoFloor": {
                "attributes": {
                    "dn": dn,
                    "name": name,
                    "descr": desc,
                    "status": "created"
                },
                "children": []
            }
        }

    else:

        payload = {
            "geoFloor": {
                "attributes": {
                    "dn": dn,
                    "status": "deleted"
                },
                "children": []
            }
        }

    return payload


def georoom_payload(site, bldg, flr, name, desc, status):

    dn = f"uni/fabric/site-{site}/building-{bldg}/floor-{flr}/room-{name}"

    if not status:

        payload = {
            "geoRoom": {
                "attributes": {
                    "dn": dn,
                    "name": name,
                    "descr": desc,
                    "status": "created"
                },
                "children": []
            }
        }

    else:

        payload = {
            "geoRoom": {
                "attributes": {
                    "dn": dn,
                    "status": "deleted"
                },
                "children": []
            }
        }

    return payload


def georow_payload(site, bldg, flr, room, name, desc, status):

    dn = f"uni/fabric/site-{site}/building-{bldg}/floor-{flr}/room-{room}/row-{name}"

    if not status:

        payload = {
            "geoRow": {
                "attributes": {
                    "dn": dn,
                    "name": name,
                    "descr": desc,
                    "status": "created"
                },
                "children": []
            }
        }

    else:

        payload = {
            "geoRow": {
                "attributes": {
                    "dn": dn,
                    "status": "deleted"
                },
                "children": []
            }
        }

    return payload


def georack_payload(site, bldg, flr, room, row, name, desc, status):

    dn = f"uni/fabric/site-{site}/building-{bldg}/floor-{flr}/room-{room}/row-{row}/rack-{name}"

    if not status:

        payload = {
            "geoRack": {
                "attributes": {
                    "dn": dn,
                    "name": name,
                    "descr": desc,
                    "status": "created"
                },
                "children": []
            }
        }

    else:

        payload = {
            "geoRack": {
                "attributes": {
                    "dn": dn,
                    "status": "deleted"
                },
                "children": []
            }
        }

    return payload


##### MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN #####

# Provided main() calls the above functions
def main():
    """
    This script takes a json file (passed as the first argument) of data (aci fabric policy objects)
    and depending on the second argument configures/creates those objects or deletes them.
    The second argument should be "True" to create and "False" to delete.

    Configure Basic Fabric Constructs
    NTP Fabric > Fabric Policies > Pod Policies > Policis > Date and time
    SNMP
    Pod Policy
    Route Reflector Fabric > Fabric Policies > Pod Policies > Communication > BGP Route Reflector default
    Ignore Acknowledged Fault

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
    print("\n===========Running ACI STEP 2A: Configure Fabric Constructs => Fabric Policies===========")
    print("===========                    With the following options                     ===========")
    log_file.write("\n===========Running ACI STEP 2A: Configure Fabric Constructs => Fabric Policies===========")
    log_file.write("\n===========                    With the following options                     ===========\n")
    for key, value in args_dict.items():
        txt = '{:15} : {:10}'.format(key, str(value))
        print(txt)
        log_file.write(txt + "\n")

    if arguments.all or arguments.ntp or arguments.snmp or arguments.rr or arguments.iga or arguments.pod \
            or arguments.podgrp:
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


    ##### FABRIC POD POLICIES #####

    # Configure Route Reflector ASN
    # key: rrasn

    if arguments.all or arguments.rr:
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'rrasn')

        for line in data:
            # rrasn_payload(asn, status)
            payload = rrasn_payload(line['asn'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} Route Reflector ASN", resp, line['asn'],
                                                             log_file, error_list)

        # Configure Route Reflector Desc
        # key: rrdesc
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'rrdesc')

        for line in data:
            # rrdesc_payload(name, desc, status)
            payload = rrdesc_payload(line['name'], line['desc'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} Route Reflector Description", resp,
                                                             aci_fabric_build_utilities.slash_replace(line['desc']),
                                                             log_file, error_list)

        # Configure Route Reflector Nodes
        # key: rrnode
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'rrnode')

        for line in data:
            # rrnode_payload(name, desc, status)
            payload = rrnode_payload(line['name'], line['desc'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            #print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} Route Reflector Nodes", resp, line['name'],
                                                             log_file, error_list)

    # Configure NTP Policy
    # key: ntppol

    if arguments.all or arguments.ntp:

        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'ntppol')

        for line in data:
            # ntppol_payload(name, desc, authSt, status)
            payload = ntppol_payload(line['name'], line['desc'], line['authSt'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} NTP Policy to hold NTP Servers",
                                                             resp, line['name'],
                                                             log_file, error_list)

        # Configure NTP Servers
        # key: ntpsrv
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'ntpsrv')

        for line in data:
            # ntpsrv_payload(name, desc, pref, policy, status)
            payload = ntpsrv_payload(line['name'], line['desc'], line['pref'], line['policy'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} NTP Servers", resp, line['name'],
                                                             log_file, error_list)

    # Configure Pod Policy Group
    # key: podpolgrp

    if arguments.all or arguments.podgrp:

        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'podpolgrp')

        for line in data:
            # podpolgrp_payload(name, desc, ntp, isis , coop, bgprr, mgt, snmp, status)
            payload = podpolgrp_payload(line['name'], line['desc'], line['ntp'], line['isis'], line['coop'],
                                        line['bgprr'], line['mgt'], line['snmp'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} Pod Policy Group", resp, line['name'],
                                                             log_file, error_list)

    # Configure Pod Policy - Associate new group to default pod policy
    # key: podpol

    if arguments.all or arguments.pod:

        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'podpol')
        # print(data)

        for line in data:
            # podpol_payload(profname, grpname, status)
            payload = podpol_payload(line['profname'], line['grpname'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print(resp.__dict__)
            # x = resp.__dict__
            # print(x['_content'])
            #aci_fabric_build_utilities.print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} Pod Policy", resp, line['profname'],
                                                             log_file, error_list)

    # Configure timezone
    # key: timezone

    if arguments.all or arguments.timezone:

        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'timezone')

        for line in data:
            # def timezone_payload(format, desc, showOffset, tz, status):
            payload = timezone_payload(line['format'], line['desc'], line['showOffset'], line['tz'],
                                       object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result(f"{action_text} Set Timezone", resp, line['tz'],log_file)

    # Configure Ignore Acknowledged Fault
    # key: igackfault

    if arguments.all or arguments.iga:

        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'igackfault')

        for line in data:
            # def IgAckFault_payload(check, status)
            payload = igackfault_payload(line['check'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result(f"{action_text} Set Ignore Acknowledged Fault", resp, line['check'], log_file)

    #######################
    # Configure Geolocation
    # key: geosite

    if arguments.all or arguments.location:

        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'geosite')

        for line in data:
            # def geosite_payload(name, desc, status)
            payload = geosite_payload(line['name'], line['desc'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result(f"{action_text} Geolocation Site", resp, line['name'], log_file)

    # Configure Geolocation
    # key: geobuilding

    if arguments.all or arguments.location:

        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'geobuilding')

        for line in data:
            # def geobuilding_payload(site, name, desc, status):
            payload = geobuilding_payload(line['site'], line['name'], line['desc'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result(f"{action_text} Geolocation Building", resp, line['name'], log_file)

    # Configure Geolocation
    # key: geofloor

    if arguments.all or arguments.location:

        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'geofloor')

        for line in data:
            # def geofloor_payload(site, bldg, name, desc, status):
            payload = geofloor_payload(line['site'], line['bldg'], line['name'], line['desc'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result(f"{action_text} Geolocation Floor", resp, line['name'], log_file)

    # Configure Geolocation
    # key: georoom

    if arguments.all or arguments.location:

        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'georoom')

        for line in data:
            # def  georoom_payload(site, bldg, flr, name, desc, status):
            payload = georoom_payload(line['site'], line['bldg'], line['flr'], line['name'], line['desc'],
                                      object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result(f"{action_text} Geolocation Room", resp, line['name'], log_file)

    # Configure Geolocation
    # key: georow

    if arguments.all or arguments.location:

        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'georow')

        for line in data:
            # def  georow_payload(site, bldg, flr, room, name, desc, status):
            payload = georow_payload(line['site'], line['bldg'], line['flr'], line['room'], line['name'],
                                     line['desc'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result(f"{action_text} Geolocation Row(s)", resp, line['name'], log_file)

    # Configure Geolocation
    # key: georack

    if arguments.all or arguments.location:

        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'georack')

        for line in data:
            # def  georack_payload(site, bldg, flr, room, row, name, desc, status):
            payload = georack_payload(line['site'], line['bldg'], line['flr'], line['room'], line['row'], line['name'],
                                     line['desc'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result(f"{action_text} Geolocation Racks", resp, line['name'], log_file)

    ###################################################################################################################
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
    # Configure Basic Fabric Constructs
    # -n NTP Fabric > Fabric Policies > Pod Policies > Policis > Date and time
    # -s SNMP (future)
    # -p Pod Policy
    # -r Route Reflector Fabric > Fabric Policies > Pod Policies > Communication > BGP Route Reflector default
    # -t Timezone
    # -i Ignore Acknowledged Fault

    parser = argparse.ArgumentParser(description="ACI STEP 2A: Configure Fabric Constructs => Fabric Policies",
                                     epilog="Usage: aci_fabric_step2a.py 'my_payload.csv' -a to create and -a -x to delete")

    parser.add_argument('payload_file', help='Name of the payload file to use in this script.')

    parser.add_argument('-x', '--xdelete',
                        help='True to remove/delete/reset configuration and False to create (default) action unless -x is used',
                        action='store_true',
                        default=False)

    parser.add_argument('-a', '--all',
                        help='Execute all object CRUD sections. Without this argument nothing will execute.',
                        action='store_true', default=False)

    parser.add_argument('-n', '--ntp', help='Execute NTP Date and time Policy', action='store_true',
                        default=False)
    parser.add_argument('-t', '--timezone', help='Execute Date and Time Timezone Policy', action='store_true',
                        default=False)
    parser.add_argument('-s', '--snmp', help='Execute SNMP Policy (Future)', action='store_true',
                        default=False)
    parser.add_argument('-g', '--podgrp', help='Execute Pod Policy Group', action='store_true', default=False)
    parser.add_argument('-p', '--pod', help='Execute Pod Policy', action='store_true', default=False)
    parser.add_argument('-r', '--rr', help='Execute Route Reflector Policy (ASN, Description, Nodes)',
                        action='store_true', default=False)

    parser.add_argument('-i', '--iga', help='Execute Ignore Acknowledged Fault Policy', action='store_true',
                        default=False)

    parser.add_argument('-l', '--location', help='Execute GeoLocation Policies', action='store_true',
                        default=False)

    parser.add_argument('-f', '--filename',
                        help='Option used to pass a credentials file other than the default "credentias.py"',
                        default='credentials.py')

    arguments = parser.parse_args()
    # print arguments

    main()