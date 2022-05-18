#!/usr/bin/python -tt
# Project: python
# Filename: aci_fabric_step4_fexconpol
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
import re
import load_apic_credentials
import aci_fabric_build_utilities
import aci_fabric_step4_conpol

requests.packages.urllib3.disable_warnings()



##############################################################################################################
################## STEP 4 Fabric Access Policies for Specific Connectivity to Hosts FEX ######################
##############################################################################################################

# Physical Domains created in accpol_base
# AEP created in accpol_base

# Interface Policies > Policy Groups > Leaf Policy Groups
#   AccessIntPolGrp
#   PCIntPolGrp
#   vPCIntPolGrp

# Fabric > Access Policies > Interface Policies > Policy Groups > Leaf Policy Groups <Right Click Options>
# Create Leaf Access Port Policy Group

# AccIntPolGrp_payload(name, desc, aep, spdPol, cdpPol, mcpPol, lldpPol, status)
# def accIntPolGrp_payload(name, desc, aep, spdPol, cdpPol, mcpPol, lldpPol, status):
#
#     if not status:
#         payload = {
#             "infraAccPortGrp": {
#                 "attributes": {
#                     "dn": "uni/infra/funcprof/accportgrp-" + name,
#                     "name": name,
#                     "descr": aci_fabric_build_utilities.slash_replace(desc),
#                     #"rn": "accportgrp-" + name,
#                     "status": "created"
#                 },
#                 "children": [{
#                     "infraRsAttEntP": {
#                         "attributes": {
#                             "tDn": "uni/infra/attentp-" + aep,
#                             "status": "created,modified"
#                         },
#                         "children": []
#                     }
#                 },
#                     {
#                         "infraRsHIfPol": {
#                             "attributes": {
#                                 "tnFabricHIfPolName": spdPol,
#                                 "status": "created,modified"
#                             },
#                             "children": []
#                         }
#                     },
#                     {
#                         "infraRsCdpIfPol": {
#                             "attributes": {
#                                 "tnCdpIfPolName": cdpPol,
#                                 "status": "created,modified"
#                             },
#                             "children": []
#                         }
#                     },
#                     {
#                         "infraRsMcpIfPol": {
#                             "attributes": {
#                                 "tnMcpIfPolName": mcpPol,
#                                 "status": "created,modified"
#                             },
#                             "children": []
#                         }
#                     },
#                     {
#                         "infraRsLldpIfPol": {
#                             "attributes": {
#                                 "tnLldpIfPolName": lldpPol,
#                                 "status": "created,modified"
#                             },
#                             "children": []
#                         }
#                     }]
#                 }
#             }
#
#
#
#     else:
#         payload = {
#             "infraAccPortGrp": {
#                 "attributes": {
#                     "dn": "uni/infra/funcprof/accportgrp-" + name,
#                     "status": "deleted"
#                 },
#             }
#         }
#     return payload
#
#
# # vpcIntPolGrp_payload(name, desc, aep, spdPol, cdpPol, mcpPol, lldpPol, lacpPol, status)
# def vpcIntPolGrp_payload(name, lagt, desc, aep, spdPol, cdpPol, mcpPol, lldpPol, lacpPol, status):
#
#     if not status:
#         payload = {
#             "infraAccBndlGrp": {
#                 "attributes": {
#                     "dn": "uni/infra/funcprof/accbundle-" + name,
#                     "lagT": lagt,
#                     "name": name,
#                     "descr": aci_fabric_build_utilities.slash_replace(desc),
#                     "ownerKey": "",
#                     "ownerTag": "",
#                     "status": "created"
#                 },
#                 "children": [
#                     {
#                         "infraRsL2IfPol": {
#                             "attributes": {
#                                 "tnL2IfPolName": ""
#                             }
#                         }
#                     },
#                     {
#                         "infraRsHIfPol": {
#                             "attributes": {
#                                 "tnFabricHIfPolName": spdPol
#                             }
#                         }
#                     },
#                     {
#                         "infraRsL2PortSecurityPol": {
#                             "attributes": {
#                                 "tnL2PortSecurityPolName": ""
#                             }
#                         }
#                     },
#                     {
#                         "infraRsQosPfcIfPol": {
#                             "attributes": {
#                                 "tnQosPfcIfPolName": ""
#                             }
#                         }
#                     },
#                     {
#                         "infraRsMonIfInfraPol": {
#                             "attributes": {
#                                 "tnMonInfraPolName": ""
#                             }
#                         }
#                     },
#                     {
#                         "infraRsStpIfPol": {
#                             "attributes": {
#                                 "tnStpIfPolName": ""
#                             }
#                         }
#                     },
#                     {
#                         "infraRsQosSdIfPol": {
#                             "attributes": {
#                                 "tnQosSdIfPolName": ""
#                             }
#                         }
#                     },
#                     {
#                         "infraRsAttEntP": {
#                             "attributes": {
#                                 "tDn": "uni/infra/attentp-" + aep
#                             }
#                         }
#                     },
#                     {
#                         "infraRsMcpIfPol": {
#                             "attributes": {
#                                 "tnMcpIfPolName": mcpPol
#                             }
#                         }
#                     },
#                     {
#                         "infraRsLacpPol": {
#                             "attributes": {
#                                 "tnLacpLagPolName": lacpPol
#                             }
#                         }
#                     },
#                     {
#                         "infraRsQosDppIfPol": {
#                             "attributes": {
#                                 "tnQosDppPolName": ""
#                             }
#                         }
#                     },
#                     {
#                         "infraRsQosIngressDppIfPol": {
#                             "attributes": {
#                                 "tnQosDppPolName": ""
#                             }
#                         }
#                     },
#                     {
#                         "infraRsQosEgressDppIfPol": {
#                             "attributes": {
#                                 "tnQosDppPolName": ""
#                             }
#                         }
#                     },
#                     {
#                         "infraRsStormctrlIfPol": {
#                             "attributes": {
#                                 "tnStormctrlIfPolName": ""
#                             }
#                         }
#                     },
#                     {
#                         "infraRsLldpIfPol": {
#                             "attributes": {
#                                 "tnLldpIfPolName": lldpPol
#                             }
#                         }
#                     },
#                     {
#                         "infraRsFcIfPol": {
#                             "attributes": {
#                                 "tnFcIfPolName": ""
#                             }
#                         }
#                     },
#                     {
#                         "infraRsCdpIfPol": {
#                             "attributes": {
#                                 "tnCdpIfPolName": cdpPol
#                             }
#                         }
#                     }
#                 ]
#             }
#         }
#
#     else:
#         payload = {
#             "infraAccBndlGrp": {
#                 "attributes": {
#                     "dn": "uni/infra/funcprof/accbundle-" + name,
#                     "status": "deleted"
#                 },
#             }
#         }
#     return payload
#


# Fabric > Access Policies > Interface Policies > Policy Groups > Leaf Policy Groups <Right Click Options>
# Create Leaf Interface Profile
# IntProf_payload(name, desc, intPolGrp, intSel, fromPort, toPort, status)
#
# def IntProf_payload(conntype, name, desc, intPolGrp, intSel, fromPort, toPort, status):
#
#     #"tDn": "uni/infra/funcprof/accportgrp-" + intPolGrp,
#     #"tDn": "uni/infra/funcprof/accbundle-MyTestvPC-IntPolGrp",
#
#     if conntype.lower() == "acc":
#         tdn = "uni/infra/funcprof/accportgrp-" + intPolGrp
#     elif conntype.lower() == "vpc" or conntype.lower() == "dpo":
#         tdn = "uni/infra/funcprof/accbundle-" + intPolGrp
#     else:
#         print("ERROR in Interface Profile function connection type. Valid types are 'acc', 'vpc', 'dpo', 'fex'.")
#         sys.exit('Aborting program Execution')
#
#
#     if not status:
#         payload = {
#             "infraAccPortP": {
#                 "attributes": {
#                     "dn": "uni/infra/accportprof-" + name,
#                     "name": name,
#                     "descr": aci_fabric_build_utilities.slash_replace(desc),
#                     #"rn": "accportprof-ESX-EDGE-L201-P25-P32-IntProf",
#                     "status": "created,modified"
#                 },
#                 "children": [{
#                     "infraHPortS": {
#                         "attributes": {
#                             "dn": "uni/infra/accportprof-" + name + "/hports-" + intSel + "-typ-range",
#                             "name": intSel,
#                             #"rn": "hports-ESX-EDGE-L201-P25-P32-IntSel-typ-range",
#                             "status": "created,modified"
#                         },
#                         "children": [{
#                             "infraPortBlk": {
#                                 "attributes": {
#                                     "dn": "uni/infra/accportprof-" + name + "/hports-" + intSel + "-typ-range/portblk-block2",
#                                     "fromPort": str(fromPort),
#                                     "toPort": str(toPort),
#                                     # "name": "block2",
#                                     # "rn": "portblk-block2",
#                                     "status": "created,modified"
#                                 },
#                                 "children": []
#                             }
#                         },
#                             {
#                                 "infraRsAccBaseGrp": {
#                                     "attributes": {
#                                         "tDn": tdn,
#                                         "status": "created,modified"
#                                     },
#                                     "children": []
#                                 }
#                             }]
#                     }
#                 }]
#             }
#         }
#     else:
#         payload = {
#             "infraAccPortP": {
#                 "attributes": {
#                     "dn": "uni/infra/accportprof-" + name,
#                     "status": "deleted"
#                 },
#                 "children": []
#             }
#         }
#     return payload



# Fabric > Access Policies > Interface Policies > Policy Groups > Leaf Policy Groups <Right Click Options>
# Create FEX Host Interface Profile
# FexHifProf_payload(name, desc, intPolGrp, intSel, fromPort, toPort, fexId status)

def FexHifProf_payload(conntype, name, desc, intPolGrp, intSel, fromPort, toPort, fexId, status):

    if not status:
        payload = {
            "infraFexP": {
              "attributes":{
                "dn":"uni/infra/fexprof-" + intPolGrp,
                "name":intPolGrp,
                "descr": "Host interfaces on " + aci_fabric_build_utilities.slash_replace(desc),
                "rn":"fexprof-" + intPolGrp,
                "status":"created,modified"
              },
              "children":[{
                "infraFexBndlGrp": {
                  "attributes":{
                    "dn":"uni/infra/fexprof-" + intPolGrp + "/fexbundle-" + intPolGrp,
                    "name":intPolGrp,
                    "rn":"fexbundle-" + intPolGrp,
                    "status":"created,modified"
                  },
                  "children":[]}
            }]}
        }

    else:

        payload = {
        "infraInfra":{
            "attributes":{
              "dn":"uni/infra",
              "status":"modified"
            },
            "children":[{
                "infraFexP":{
                    "attributes":{
                    "dn":"uni/infra/fexprof-" + intPolGrp,
                    "status":"deleted"
                },
                "children":[]}
            }]}
        }

    return payload



# Fabric > Access Policies > Interface Policies > Policy Groups > Leaf Policy Groups <Right Click Options>
# Create Leaf Interface Profile
# FexNifProf_payload(name, desc, intPolGrp, intSel, fromPort, toPort, fexId, status)

def FexNifProf_payload(conntype, name, desc, intPolGrp, intSel, fromPort, toPort, fexId, status):

    if not status:
        payload = {
            "infraAccPortP": {
                "attributes": {
                    "dn": "uni/infra/accportprof-" + name,
                    "name": name,
                    "descr": "Network interfaces to " + aci_fabric_build_utilities.slash_replace(desc),
                    #"rn": "accportprof-ESX-EDGE-L201-P25-P32-IntProf",
                    "status": "created,modified"
                },
                "children": [{
                    "infraHPortS": {
                        "attributes": {
                            "dn": "uni/infra/accportprof-" + name + "/hports-" + intSel + "-typ-range",
                            "name": intSel,
                            #"rn": "hports-ESX-EDGE-L201-P25-P32-IntSel-typ-range",
                            "status": "created,modified"
                        },
                        "children": [{
                            "infraPortBlk": {
                                "attributes": {
                                    "dn": "uni/infra/accportprof-" + name + "/hports-" + intSel + "-typ-range/portblk-block2",
                                    "fromPort": str(fromPort),
                                    "toPort": str(toPort),
                                    "name": "block2",
                                    "rn": "portblk-block2",
                                    "status": "created,modified"
                                },
                                "children": []
                            }
                        },
                            {
                            "infraRsAccBaseGrp": {
                                "attributes": {
                                    "fexId": fexId,
                                    "tDn": "uni/infra/fexprof-" + intPolGrp + "/fexbundle-" + intPolGrp,
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
        payload = {
            "infraAccPortP": {
                "attributes": {
                    "dn": "uni/infra/accportprof-" + name,
                    "status": "deleted"
                },
                "children": []
            }
        }
    return payload
#
# # Add Interface Profile to Switch/Leaf Profile
# def add2swProf_payload(swProf, intProf, status):
#
#     if not status:
#         payload = {
#             "infraNodeP": {
#                 "attributes": {
#                     "dn": "uni/infra/nprof-" + swProf,
#                     "name": swProf,
#                     "status": "created,modified"
#                 },
#                 "children": [{
#                         "infraRsAccPortP": {
#                             "attributes": {
#                                 "tDn": "uni/infra/accportprof-" + intProf,
#                                 "status": "created,modified"
#                             },
#                             "children": []
#                         }
#                     }]
#             }
#
#         }
#
#     else:
#         payload = {
#             "infraNodeP": {
#                 "attributes": {
#                     "dn": "uni/infra/nprof-" + swProf,
#                     "name": swProf,
#                     # "rn": "nprof-LeafProf101",
#                     "status": "created,modified"
#                 },
#                 "children": [{
#                     "infraRsAccPortP": {
#                         "attributes": {
#                             "tDn": "uni/infra/accportprof-" + intProf,
#                             "status": "deleted"
#                         },
#                         "children": []
#                     }
#                 }]
#             }
#         }
#
#     return payload
#


# Add Interface Profile to FEX HIF Profile
def add2FexHif_payload(conntype, name, desc, intPolGrp, intSel, fromPort, toPort, status):

    #"tDn":"uni/infra/funcprof/accportgrp-1G-Server-IntPolGrp",
    if conntype.lower() == "acc":
        tdn = "uni/infra/funcprof/accportgrp-" + intPolGrp
    elif conntype.lower() == "vpc":
        tdn = "uni/infra/funcprof/accbundle-" + intPolGrp

    else:
        print("ERROR in Interface Profile function connection type. Valid types are 'acc', 'vpc', 'dpo', 'fex'.")
        sys.exit('Aborting program Execution')

    if not status:
        payload = {
          "infraHPortS":{
            "attributes":{
                "dn":"uni/infra/fexprof-" + name + "/hports-" + intSel + "-typ-range",
                "name": intSel,
                "descr": aci_fabric_build_utilities.slash_replace(desc),
                "rn":"hports-" + intSel + "-typ-range",
                "status":"created,modified"
              },
              "children":[{
                "infraPortBlk":{
                  "attributes":{
                    "dn":"uni/infra/fexprof-" + name + "/hports-" + intSel + "-typ-range/portblk-block2",
                    "fromPort": fromPort,
                    "toPort" :toPort,
                    "name":"block2",
                    #"rn":"portblk-block2",
                    "status":"created,modified"
                },
                "children":[]}}
                  ,{
                  "infraRsAccBaseGrp":{
                    "attributes":{
                      "tDn": tdn,
                      "status":"created,modified"
                      },
                      "children":[]}}]
          }
        }

    else:
        payload = {
          "infraHPortS":{
            "attributes":{
                "dn":"uni/infra/fexprof-" + name + "/hports-" + intSel + "-typ-range",
                "name": intSel,
                #'"rn":"hports-" + intSel + "-typ-range",
                "status":"deleted"
              },
              "children":[]
          }
        }

    return payload


#########################################################################################################
################### Tenant ANP EPG Host Connectivity Constructs (Dom & Static Path)######################
#########################################################################################################
#
#
#  # addDom2epg_payload(tn, anp, epg, phydom, status)
# def addDom2epg_payload(tn, anp, epg, phydom, encap, status):
#
#     if not status:
#         payload = {
#             "fvRsDomAtt": {
#                 "attributes": {
#                     "classPref": "encap",
#                     "delimiter": "",
#                     #"dn": "uni/tn-MC-ITD01-ITDSharedServices-TN/ap-Prod-ANP/epg-Vlan6-TCOM-Switch-EPG/rsdomAtt-[uni/phys-MC-ITD01-LegacyPhyDom]"
#                     "dn": "uni/tn-" + tn + "/ap-" + anp + "/epg-" + epg + "/rsdomAtt-[uni/phys-" + phydom + "]",
#                     "encap": "unknown",
#                     "instrImedcy": "immediate",
#                     "primaryEncap": "unknown",
#                     "resImedcy": "immediate",
#                     "status": "created"
#                 },
#                 "children": []
#             }
#         }
#     else:
#         payload = {
#             "fvRsDomAtt": {
#                 "attributes": {
#                     "dn": "uni/tn-" + tn + "/ap-" + anp + "/epg-" + epg + "/rsdomAtt-[uni/phys-" + phydom + "]",
#                     "status": "deleted"
#                 },
#                 "children": []
#             }
#         }
#     return payload

# This is the FEX static Path function from Warren...Needs to be merged with the staticPath module in conpol (Step4) main
def staticPathfex_payload(conntype, host, tn, anp, epg, pod, paths, extpaths, int, encap, mode, status):

    # conntype = acc (Access Interface), vpc (Virtual Port channel), dpo (Direct Port channel)

    if conntype.lower() == "acc":
        dn = "uni/tn-" + tn + "/ap-" + anp + "/epg-" + epg + "/rspathAtt-[topology/pod-" + str(pod) + "/paths-" + str(
            paths) + "/pathep-[eth" + int + "]]"
        # dn = "dn" + "uni/tn-" + tn + "/ap-" + anp + "/epg-" + epg + "/rspathAtt-[topology/pod-" + str(pod) + "/paths-" + str(paths) + "/pathep-[eth" + int + "]",
    elif conntype.lower() == "vpc" or conntype.lower() == "dpo":
        dn = "uni/tn-" + tn + "/ap-" + anp + "/epg-" + epg + "/rspathAtt-[topology/pod-" + str(pod) + "/protpaths-" + str(
            paths) + "/pathep-[" + host + "]]"
    elif conntype.lower() == "fex":
        dn = "uni/tn-" + tn + "/ap-" + anp + "/epg-" + epg + "/rspathAtt-[topology/pod-" + str(pod) + "/paths-" + str(
            paths) + "/extpaths-" + str(extpaths) + "/pathep-[eth" + int + "]]"
        #"tDn":"topology/pod-1/paths-101/extpaths-111/pathep-[eth1/1]",
    else:
        print("ERROR in Static Path function connection type. Valid types are 'acc', 'vpc', 'dpo', 'fex'.")
        sys.exit('Aborting program Execution')


    if not status:

        payload = {
            "fvRsPathAtt": {
                "attributes": {
                    "descr": "",
                    "dn": dn,
                    "encap": "vlan-" + str(encap),
                    "instrImedcy": "immediate",
                    # Valid Values "native" for 802.1P, "untagged" for Access, "regular" for Trunk
                    "mode": mode,
                    "primaryEncap": "unknown",
                    #"tDn": "topology/pod-1/paths-" + str(paths) + "/pathep-[eth" + intpolgrp + "]",
                    "status": "created,modified"
                }
            }
        }
    else:
        payload = {
            "fvRsPathAtt": {
                "attributes": {
                    "dn": dn,
                    "status": "deleted"
                }
            }
        }
    return payload


##### MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN #####

# Provided main() calls the above functions
def main():
    """
    This script takes a CSV file (passed as the first argument) of data (aci connectivity policy objects)
    and depending on the second argument configures/creates those objects or deletes them.
    The second argument should be "True" to create and "False" to delete.

    Assumptions:  the Switch Profiles, AEP, and Interface Policies have already been created with the aci_fabric_accpol_base.py script
    and the exact names are referenced in the payload for this script.

    - Interface Policy Group (IntPolGrp) references the already created Interface Policies and AEP
    - Interface Profile (IntProf) references the IntSel range, from and to ports and IntPolGrp
    - IntProf must be added to SwProf
    - Physical Domain must be added to EPG
    - For each EPG (Vlan) create static path binding for relevant interface

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

    # Create a Log file for configuration session
    filename_base = filename.split(".")[0]
    timestr = time.strftime("%Y%m%d-%H%M%S")
    log_filename = filename_base + "-" + action_text.upper() + "-" + timestr + ".log"
    log_file = open(log_filename, 'w')

    # USING NEW LOAD APIC CREDENTIALS SCRIPT
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
    print("\n===========Running ACI STEP 4 FEX: Configure User Access Constructs => FEX Access Policies===========")
    print("===========                       With the following options                        ===========")
    log_file.write("\n===========Running ACI STEP 4 FEX: Configure User Access Constructs => FEX Access Policies===========")
    log_file.write("\n===========                       With the following options                        ===========\n")
    for key, value in args_dict.items():
        txt = '{:15} : {:10}'.format(key,str(value))
        print(txt)
        log_file.write(txt + "\n")

    if arguments.all or arguments.add2swprof or arguments.intprof or arguments.vpcintpolgrp or arguments.dom2epg or arguments.accintpolgrp or arguments.staticpathfex:
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

    # Fabric > Access Policies > Interface Policies > Policy Groups > Leaf Policy Groups <Right Click Options>
    # Create Leaf Access Port Policy Group
    # key: accIntPolGrp

    if arguments.all or arguments.accintpolgrp:
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'accIntPolGrp')

        for line in data:
            # accIntPolGrp_payload(name, desc, aep, spdPol, cdpPol, mcpPol,lldpPol, status)
            payload = aci_fabric_step4_conpol.accIntPolGrp_payload(line['name'], line['desc'], line['aep'], line['spdPol'], line['cdpPol'], line['mcpPol'], line['lldpPol'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(action_text + " Access Port Interface Policy Group",
                                                             resp, line['name'], log_file, error_list)


    # Fabric > Access Policies > Interface Policies > Policy Groups > Leaf Policy Groups <Right Click Options>
    # Create VPC Interface Policy Group
    # key: vpcIntPolGrp

    if arguments.all or arguments.vpcintpolgrp:
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'vpcIntPolGrp')

        for line in data:
            # vpcIntPolGrp_payload(name, lagt, desc, aep, spdPol, cdpPol, mcpPol, lldpPol, lacpPol, status)
            payload = aci_fabric_step4_conpol.vpcIntPolGrp_payload(line['name'], line['lagt'], line['desc'], line['aep'], line['spdPol'],
                                           line['cdpPol'], line['mcpPol'], line['lldpPol'], line['lacpPol'],
                                           object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(action_text + " VPC/Po Interface Policy Group", resp,
                                                             line['name'], log_file, error_list)


    # Fabric > Access Policies > Interface Policies > Policy Groups > Leaf Policy Groups <Right Click Options>
    # Create Direct Port Channel Interface Policy Group
    # key: dpoIntPolGrp
    # Future


    # Fabric > Access Policies > Interface Policies > Policy Groups > Leaf Policy Groups <Right Click Options>
    # Create Leaf Interface Profile
    # key: IntProf

    if arguments.all or arguments.intprof:
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'IntProf')

        for line in data:
            # IntProf_payload(conntype, name, desc, intPolGrp, intSel, fromPort, toPort, status)
            payload = aci_fabric_step4_conpol.IntProf_payload(line['conntype'], line['name'], line['desc'],
                                                              line['intPolGrp'], line['intSel'],
                                                              line['fromPort'], line['toPort'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(action_text + " Leaf Interface Profile", resp,
                                                             line['name'], log_file, error_list)

    # Fabric > Access Policies > Interface Policies > Policy Groups > Leaf Policy Groups <Right Click Options>
    # Create Leaf Interface Profile
    # key: FexProf

    if arguments.all or arguments.fexprof:
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'FexProf')

        for line in data:
            # FexHifProf_payload(conntype, name, desc, intPolGrp, intSel, fromPort, toPort, fexId, status)
            payload = FexHifProf_payload(line['conntype'], line['name'], line['desc'], line['intPolGrp'],
                                         line['intSel'], line['fromPort'], line['toPort'], line['fexId'],
                                         object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result(action_text + " FEX Host Interface Profile", resp,
                                                         line['intPolGrp'], log_file)

        for line in data:
            # FexNifProf_payload(conntype, name, desc, intPolGrp, intSel, fromPort, toPort, fexId, status)
            payload = FexNifProf_payload(line['conntype'], line['name'], line['desc'], line['intPolGrp'],
                                         line['intSel'], line['fromPort'], line['toPort'], line['fexId'],
                                         object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result(action_text + " FEX Network Interface Profile", resp,
                                                         line['intPolGrp'], log_file)


    # Fabric > Access Policies > Interface Policies > Profiles > type:fex <Select HIF>
    # Add Selector and Profile to FEX Profile
    # key: Add2FexHif

    if arguments.all or arguments.add2fexhif:
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'add2FexHif')

        for line in data:
            # add2FexHif_payload(conntype, name, desc, intPolGrp, intSel, fromPort, toPort, status)
            payload = add2FexHif_payload(line['conntype'], line['name'], line['desc'], line['intPolGrp'],
                                         line['intSel'], line['fromPort'], line['toPort'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result(action_text + " FEX Profile", resp, line['desc'], log_file)


    # Add Interface Profile to Switch/Leaf Profile
    # key: add2swProf

    if arguments.all or arguments.add2swprof:
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'add2swProf')

        for line in data:
            #add2swProf_payload(swProf, intProf, status)
            payload = aci_fabric_step4_conpol.add2swProf_payload(line['swProf'], line['intProf'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            text = action_text + " Interface Profile " + line['intProf'] + " to Switch/Leaf Profile " + line['swProf']
            aci_fabric_build_utilities.print_post_result_log("", resp, text, log_file, error_list)



    # Add Physical Domain to EPG in Tenant and ANP
    # key: addDom2epg

    if arguments.all or arguments.dom2epg:
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'addDom2epg')

        for line in data:
            # addDom2epg_payload(tn, anp, epg, phydom, status)
            payload = aci_fabric_step4_conpol.addDom2epg_payload(line['tn'], line['anp'], line['epg'],
                                                                 line['phydom'], line['encap'],
                                                                 object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            text = action_text + " Physical Domain " + line['phydom'] + " to EPG " + line['epg'] + \
                   " in Tenant " + line['tn'] + " and ANP " + line['anp']
            aci_fabric_build_utilities.print_post_result_log("", resp, text, log_file, error_list)



    # Add Static Path Binding (Static Port) to each EPG for each relevant host
    # This uses two payloads, addDom2epg and staticPathfex
    # addDom2epg has the tn, anp, epg, and encap
    # staticPath has host, allowed_encap, paths, int, and mode (CdL original V2)
	# staticPath has host, allowed_encap, *pod*, paths, int, and mode (Warren Update)
    # staticPath_payload(conntype, tn, anp, epg, paths, int, encap, mode, status) (CdL original V2)
	# staticPath_payload(conntype, *host*, tn, anp, epg, *pod*, paths, int, encap, mode, status)
    # key: addDom2epg
    # key: staticPathfex

    if arguments.all or arguments.staticpathfex:

        epg_data = aci_fabric_build_utilities.pluck_payload(json_payload, 'addDom2epg')
        host_data = aci_fabric_build_utilities.pluck_payload(json_payload, 'staticPathfex')

        for line in epg_data:

            for host_int in host_data:
                # print(host_int)
                allowed_encap_numeric_list = aci_fabric_build_utilities.allowed_encap_split(host_int['allowed_encap'])
                # print(allowed_encap_numeric_list)nj
                # print(line['encap'])
                # raw_input("Pause...")
                # if line['encap'] in host_int['allowed_encap']:
                if int(line['encap']) in allowed_encap_numeric_list:
                    # text =  action_text + " Static Path Binding to EPG " + line['epg'] + " type " + host_int['conntype']\
                    #         + " on interface " + host_int['intpolgrp'] + " in mode " + host_int['mode'] +  " since " \
                    #         + line['encap'] + " is in allowed vlan list " + host_int['allowed_encap'] + "."
                    # staticPath_payload(conntype, tn, anp, epg, paths, intpolgrp, encap, mode, status) (CdL Original V2)
                    # payload = staticPath_payload(host_int['conntype'], line['tn'], line['anp'], line['epg'],
                    #                             host_int['paths'], host_int['intpolgrp'], line['encap'], host_int['mode'],
                    #                             object_status_delete)

                    text =  action_text + " Static Path Binding to EPG " + line['epg'] + " type " + host_int['conntype']\
                            + " on interface " + host_int['extpaths'] + " in pod " + host_int['pod'] \
                            + " in mode " + host_int['mode'] +  " since " \
                            + line['encap'] + " is in allowed vlan list " + host_int['allowed_encap'] + "."
                    #staticPath_payload(conntype, *host*, tn, anp, epg, paths, *extpaths*, int, encap, mode, status)
                    payload = staticPathfex_payload(host_int['conntype'], host_int['host'], line['tn'], line['anp'],
                                                 line['epg'], host_int['pod'], host_int['paths'], host_int['extpaths'],
                                                 host_int['int'], line['encap'], host_int['mode'], object_status_delete)


                    resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
                    #print_debug_data(resp)
                    aci_fabric_build_utilities.print_post_result_log("", resp, text, log_file, error_list)


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

    # - Interface Policy Group (IntPolGrp) references the already created Interface Policies and AEP
    # - Interface Profile (IntProf) references the IntSel range, from and to ports and IntPolGrp
    # - IntProf must be added to SwProf
    # - Physical Domain must be added to EPG
    # - For each EPG (Vlan) create static path binding for relevant interface

    parser = argparse.ArgumentParser(description="FEX ACI Fabric Connectivity Policies for FEX",
                                     epilog="Usage: aci_fabric_step4_conpol-fex.py 'my_payload.csv' -a to create and -a -x to delete" )

    parser.add_argument('payload_file', help='Name of the payload file to use in this script.')

    parser.add_argument('-x', '--xdelete',
                        help='True to remove/delete/reset configuration and False to create (default) action unless -x is used',
                        action='store_true',
                        default=False)

    parser.add_argument('-a', '--all', help='Execute all object CRUD sections. Without this argument nothing will execute.',
                        action='store_true', default=False)



    parser.add_argument('-g', '--accintpolgrp', help='Execute Interface Policy Group function', action='store_true', default=False)
    parser.add_argument('-v', '--vpcintpolgrp', help='Execute Interface Policy Group function', action='store_true', default=False)
    parser.add_argument('-o', '--dpointpolgrp', help='Execute Interface Policy Group function (Future)', action='store_true', default=False)
    parser.add_argument('-e', '--fexprof', help='Execute Fex Interface Profile function', action='store_true', default=False)
    parser.add_argument('-z', '--add2fexhif', help='Execute Fex HIF Profile function', action='store_true', default=False)
    parser.add_argument('-p', '--intprof', help='Execute Interface Profile function', action='store_true', default=False)
    parser.add_argument('-l', '--add2swprof', help='Execute IntProf to SwProf function', action='store_true', default=False)
    parser.add_argument('-d', '--dom2epg', help='Execute PhyDom to EPG function', action='store_true', default=False)
    parser.add_argument('-s', '--staticpathfex', help='Execute Static Path  Binding to EPG function', action='store_true', default=False)
    parser.add_argument('-f', '--filename', help='Option used to pass a credentials file other than the default "credentias.py"',
                        default='credentials.py')

    arguments = parser.parse_args()

    main()




