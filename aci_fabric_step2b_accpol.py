#!/usr/bin/python -tt
# Project: python
# Filename: aci_fabric_step2b_accpol
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
##### STEP 2b Fabric Access Policies                #####
#########################################################

#########################################################
##### FABRIC > Access Policies > Interface Policies #####
#########################################################

def link_payload(name, desc, speed, autoneg, status):

    if not status:

        payload = {
            "fabricHIfPol": {
                "attributes": {
                    "dn": "uni/infra/hintfpol-" + name,
                    "name": name,
                    "descr": aci_fabric_build_utilities.slash_replace(desc),
                    "linkDebounce": "100",
                    # Valid Values = "100M"  "1G"  "10G"  "25G"  "40G"  "100G"
                    "speed": speed,
                    # Valid Values = "off" "on"
                    "autoNeg": autoneg,
                    # "rn": "hintfpol-40G",
                    "status": "created"
                },
                "children": []
            }
        }

    else:
        payload = {
            "fabricHIfPol": {
                "attributes": {
                    "dn": "uni/infra/hintfpol-" + name,
                    "status": "deleted"
                },
                "children": []
            }
        }
    return payload


def cdp_payload(name, desc, adminSt, status):

    if not status:
        payload = {
            "cdpIfPol": {
                "attributes": {
                    "dn": "uni/infra/cdpIfP-" + name,
                    "name": name,
                    "descr": aci_fabric_build_utilities.slash_replace(desc),
                    # Valid values = enabled, disabled
                    "adminSt": adminSt,
                    #"rn": "cdpIfP-CDP_OFF",
                    "status": "created"
                },
                "children": []
            }
        }
    else:
        payload = {
            "cdpIfPol": {
                "attributes": {
                    "dn": "uni/infra/cdpIfP-" + name,
                    "status": "deleted"
                },
                "children": []
            }
        }
    return payload



def lldp_payload(name, desc, rxSt, txSt, status):

    if not status:

        payload = {
            "lldpIfPol": {
                "attributes": {
                    "dn": "uni/infra/lldpIfP-" + name,
                    "name": name,
                    "descr": aci_fabric_build_utilities.slash_replace(desc),
                    # Valid values = enabled, disabled
                    "adminRxSt": rxSt,
                    "adminTxSt": txSt,
                    #"rn": "lldpIfP-LLDP_Off",
                    "status": "created"
                },
                "children": []
            }
        }
    else:
        payload = {
            "lldpIfPol": {
                "attributes": {
                    "dn": "uni/infra/lldpIfP-" + name,
                    "status": "deleted"
                },
                "children": []
            }
        }
    return payload

def lacp_payload(name, desc, mode, status):


    if not status:
        payload = {
            "lacpLagPol": {
                "attributes": {
                    "dn": "uni/infra/lacplagp-" + name,
                    "ctrl": "fast-sel-hot-stdby,graceful-conv,susp-individual",
                    "name": name,
                    "descr": aci_fabric_build_utilities.slash_replace(desc),
                    # Valid valuse = "off" "active" "passive" "mac-pin" "mac-pin-nicload"
                    "mode": mode,
                    #"rn": "lacplagp-PortChannel_LACPACTIVE",
                    "status": "created"
                },
                "children": []
            }
        }
    else:
        payload = {
            "lacpLagPol": {
                "attributes": {
                    "dn": "uni/infra/lacplagp-" + name,
                    "status": "deleted"
                },
                "children": []
            }
        }
    return payload

def mcp_payload(name, desc, adminSt, status):


    if not status:
        payload = {
            "mcpIfPol": {
                "attributes": {
                    "dn": "uni/infra/mcpIfP-" + name,
                    "name": name,
                    # Valid Values = "disabled" "enabled"
                    "adminSt": adminSt,
                    "descr": aci_fabric_build_utilities.slash_replace(desc)
                    #"ownerKey": "",
                    #"ownerTag": ""
                }
            }

        }
    else:
        payload = {
            "mcpIfPol": {
                "attributes": {
                    "dn": "uni/infra/mcpIfP-" + name,
                    "status": "deleted"
                }
            }

        }
    return payload


# api/node/mo/uni/infra/stormctrlifp-DC-StormControl-IntPol.jsonpayload{
# By default, storm control is not enabled in the ACI fabric

# status is set by the -x --xdelete argument to False for deletion
# Read: If (delete) not true create payload else (delete) IS true and remove

def stormctl_payload(name, desc, rate, burstRate, status):

    """
    method: POSTurl: https: //172.30.254.11/api/node/mo/uni/infra/stormctrlifp-some7575.jsonpayload{
    "stormctrlIfPol": {
        "attributes": {
            "dn": "uni/infra/stormctrlifp-some7575",
            "name": "some7575",
            "descr": "7575",
            "rate": "75",
            "burstRate": "75",
            "rn": "stormctrlifp-some7575",
            "status": "created"
        },
        "children": []
    }
}
    :param name:
    :param desc:
    :param rate:
    :param burstRate:
    :param status:
    :return:
    """

    if not status:
        payload = {
            "stormctrlIfPol": {
                "attributes": {
                    "dn": "uni/infra/stormctrlifp-" + name,
                    "name": name,
                    "descr": aci_fabric_build_utilities.slash_replace(desc),
                    "rate": rate,
                    "burstRate": burstRate,
                    "status": "created"
                },
                "children": []
            }

        }
    else:
        payload = {
            "stormctrlIfPol": {
                "attributes": {
                    "dn": "uni/infra/stormctrlifp-" + name,
                    "status": "deleted"
                },
                "children": []
            }

        }
    return payload



#########################################################
##### FABRIC > Access Policies > Switch Policies ########
#########################################################



# FABRIC > Access Policies > Switch Policies > Policies > VPC Domain
def vpcdomain_payload(name, desc, status):

    if not status:
        payload = {
            "vpcInstPol": {
                "attributes": {
                    "dn": "uni/fabric/vpcInst-" + name,
                    "name": name,
                    "descr": aci_fabric_build_utilities.slash_replace(desc)
                    # Next two came from API Inspector
                    #"rn": "vpcInst-vpc-domain-leaf101-102",
                    #"status": "created"
                    # Next 3 came from Save As via GUI on object
                    #"deadIntvl": "200"
                    #"ownerKey": "",
                    #"ownerTag": ""
                }
            }
        }
    else:
        payload = {
            "vpcInstPol": {
                "attributes": {
                    "dn": "uni/fabric/vpcInst-" + name,
                    "status": "deleted"
                }
            }
        }

    return payload

# FABRIC > Access Policies > Switch Policies > Policies > Virtual Port Channel default
# Updates description only
def fabricProtPol_payload(name, desc):

    payload = {
        "fabricProtPol": {
            "attributes": {
                "dn": "uni/fabric/protpol",
                "descr": aci_fabric_build_utilities.slash_replace(desc)
            },
            "children": []
        }

    }
    return payload

# Updates the protection groups in the default VPC object
def vpcdefault_payload(name, pair_id, node_1, node_2, vpc_domain, status):
    # This configures the default Virtual Port Channel object in
    # Fabric > Access Policies > Switch Policies > Virtual Port Channel default
    # name = Explicit VPC Protection Group Name
    # which refrences the Domain Policy, the explicit switches, and the logical pair ID

    # text = "uni/fabric/protpol/expgep-" + name + "/nodepep-" + node_1
    # print("TEXT >>>> " + text)
    #
    # text = "uni/fabric/protpol/expgep-" + name + "/nodepep-" + node_2
    # print("TEXT >>>> " + text)

    if not status:

        payload = {
            "fabricExplicitGEp": {
                "attributes": {
                    "dn": "uni/fabric/protpol/expgep-" + name,
                    "id": pair_id,
                    "name": name,
                    #"rn": "expgep-vpc-explicit-prot-grp",
                    "status": "created"
                },
                "children": [{
                    "fabricNodePEp": {
                        "attributes": {
                            "dn": "uni/fabric/protpol/expgep-" + name + "/nodepep-" + node_1,
                            "id": node_1,
                            "status": "created"
                            # "rn": "nodepep-" + node_1
                        },
                        "children": []
                    }
                },
                {
                    "fabricNodePEp": {
                        "attributes": {
                            "dn": "uni/fabric/protpol/expgep-" + name + "/nodepep-" + node_2,
                            "id": node_2,
                            "status": "created"
                            #"rn": "nodepep-" + node_2
                        },
                        "children": []
                    }
                },
                {
                    "fabricRsVpcInstPol": {
                        "attributes": {
                            "tnVpcInstPolName": vpc_domain,
                            "status": "created,modified"
                        },
                        "children": []
                    }
                }]
            }
        }
    else:
        payload = {
            "fabricExplicitGEp": {
                "attributes": {
                    "dn": "uni/fabric/protpol/expgep-" + name,
                    "status": "deleted"
                },
                "children": [{
                    "fabricNodePEp": {
                        "attributes": {
                            "dn": "uni/fabric/protpol/expgep-" + name + "/nodepep-" + node_1,
                            "status": "deleted"
                        },
                        "children": []
                    }
                },
                {
                    "fabricNodePEp": {
                        "attributes": {
                            "dn": "uni/fabric/protpol/expgep-" + name + "/nodepep-" + node_2,
                            "status": "deleted"
                        },
                        "children": []
                    }
                },
                {
                    "fabricRsVpcInstPol": {
                        "attributes": {
                            "tnVpcInstPolName": vpc_domain,
                            "status": "deleted"
                        },
                        "children": []
                    }
                }]
            }
        }
    return payload



# FABRIC > Access Policies > Switch Policies > Policies > Profiles > Leaf Profiles
def leafprof_payload(name, desc, leafsel_name, frm_sw, to_sw, status):

    if not status:

        payload = {

            "infraNodeP": {
                "attributes": {
                    "dn": "uni/infra/nprof-" + name,
                    "name": name,
                    "descr": aci_fabric_build_utilities.slash_replace(desc),
                    #"rn": "nprof-TEST",
                    "status": "created,modified"
                },
                "children": [{
                    "infraLeafS": {
                        "attributes": {
                            "dn": "uni/infra/nprof-" + name + "/leaves-" + leafsel_name + "-typ-range",
                            "type": "range",
                            "name": leafsel_name,
                            #"rn": "leaves-TestLeafSelector-typ-range",
                            "status": "created"
                        },
                        "children": [{
                            "infraNodeBlk": {
                                "attributes": {
                                    "dn": "uni/infra/nprof-" + name + "/leaves-" + leafsel_name + "-typ-range/nodeblk-" +"node-" + frm_sw + "-" + to_sw,
                                    "from_": frm_sw,
                                    "to_": to_sw,
                                    "name": "node-" + frm_sw + "-" + to_sw,
                                    #"rn": "nodeblk-f7d61c9151db0e38",
                                    "status": "created"
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
            "infraNodeP": {
                "attributes": {
                    "dn": "uni/infra/nprof-" + name,
                    "status": "deleted"
                },
                "children": [{
                    "infraLeafS": {
                        "attributes": {
                            "dn": "uni/infra/nprof-" + name + "/leaves-" + leafsel_name + "-typ-range",
                            "status": "deleted"
                        },
                        "children": [{
                            "infraNodeBlk": {
                                "attributes": {
                                    "dn": "uni/infra/nprof-" + name + "/leaves-" + leafsel_name + "-typ-range/nodeblk-" + "node-" + frm_sw + "-" + to_sw,
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



#########################################################
##### FABRIC > Access Policies > Pools ########
#########################################################

# FABRIC > Access Policies > Pools > VLAN
def vlanpool_payload(name, desc, allocmode, vlan_desc, frm_vlan, to_vlan, status):
    if not status:
        payload = {
            "fvnsVlanInstP": {
                "attributes": {
                    "dn": "uni/infra/vlanns-[" + name + "]-" + allocmode,
                    "name": name,
                    "descr": aci_fabric_build_utilities.slash_replace(desc),
                    # Valid values = "static"  "dynamic"  "inherit"
                    "allocMode": allocmode,
                    "status": "created, modified"
                },
                "children": []
            }
        }
    else:
        payload = {
            "fvnsVlanInstP": {
                "attributes": {
                    "dn": "uni/infra/vlanns-[" + name + "]-" + allocmode,
                    "status": "deleted"
                },
                "children": []
            }
        }
    return payload

def vlan_payload(name, desc, poolallocmode, allocmode, vlan_desc, frm_vlan, to_vlan, status):
    # "dn": "uni/infra/vlanns-[testvmm]-dynamic/from-[vlan-3000]-to-[vlan-3099]"
    if not status:
        payload = {
            "fvnsEncapBlk": {
                "attributes": {
                    "dn": "uni/infra/vlanns-[" + name + "]-" + poolallocmode + "/from-[vlan-" + str(frm_vlan) + "]-to-[vlan-" + str(to_vlan) + "]",
                    "descr": aci_fabric_build_utilities.slash_replace(vlan_desc),
                    "from": "vlan-" + str(frm_vlan),
                    "to": "vlan-" + str(to_vlan),
                    "allocMode": allocmode,
                    #"rn": "from-[vlan-2009]-to-[vlan-2014]",
                    "status": "created"
                },
                "children": []
            }
        }
        #print("DN: " + "dn: uni/infra/vlanns-[" + name + "]-static/from-[vlan-" + str(frm_vlan) + "]-to-[vlan-" + str(to_vlan) + "]")

    else:
        #print "else"
        payload = {
            "fvnsEncapBlk": {
                "attributes": {
                    "dn": "uni/infra/vlanns-[" + name + "]-" + poolallocmode + "/from-[vlan-" + str(frm_vlan) + "]-to-[vlan-" + str(to_vlan) + "]",
                    "status": "deleted"
                },
                "children": []
            }
        }
    return payload




#######################################################################
##### FABRIC > Access Policies > Physical and External Domains ########
#######################################################################


def secdom_payload(name, desc, status):

    if not status:
        payload = {
            "aaaDomain": {
                "attributes": {
                    "dn": "uni/userext/domain-" + name,
                    "name": name,
                    "descr": aci_fabric_build_utilities.slash_replace(desc),
                    #"rn": "domain-LV1-SecDom",
                    "status": "created"
                },
                "children": []
            }
        }
    else:
        payload = {
            "aaaDomain": {
                "attributes": {
                    "dn": "uni/userext/domain-" + name,
                    "status": "deleted"
                },
                "children": []
            }
        }
    return payload


# phydom_payload(name, desc, secdom, pool, status )
def phydom_payload(name, desc, secdom, pool, status):

    if not status:
        payload = {
            "physDomP": {
                "attributes": {
                    "dn": "uni/phys-" + name,
                    "name": name,
                    #"rn": "phys-LV1-Common-ESX-PhyDom",
                    "status": "created, modified"
                },
                "children": [{
                    "aaaDomainRef": {
                        "attributes": {
                            "dn": "uni/phys-" + name + "/domain-" + secdom,
                            "name": secdom,
                            #"rn": "domain-LV1-SecDom",
                            "status": "created, modified"
                        },
                        "children": []
                    }
                },
                    {
                        "infraRsVlanNs": {
                            "attributes": {
                                "tDn": "uni/infra/vlanns-[" + pool + "]-static",
                                "status": "created, modified"
                            },
                            "children": []
                        }
                    }]
            }
        }
    else:
        payload = {
            "physDomP": {
                "attributes": {
                    "dn": "uni/phys-" + name,
                    "name": name,
                    #"rn": "phys-LV1-Common-ESX-PhyDom",
                    "status": "deleted"
                },
                "children": []
            }
        }
    return payload

#########################################################
##### FABRIC > Access Policies > Global Policies ########
#########################################################

# FABRIC > Access Policies > Global Policies > MCP Instance Policy default (enable the default behavior)
# This policy is disabled by default

def mcpdefault_payload(desc, adminSt, key, status):

    if not status:
        payload = {
            "mcpInstPol": {
                "attributes": {
                    "dn": "uni/infra/mcpInstP-default",
                    "descr": aci_fabric_build_utilities.slash_replace(desc),
                    "adminSt": "enabled",
                    "key": key
                },
                "children": []
            }
        }
    else:
        payload = {
            "mcpInstPol": {
                "attributes": {
                    "dn": "uni/infra/mcpInstP-default",
                    "descr": "",
                    "adminSt": "disabled"
                },
                "children": []
            }
        }
    return payload



# FABRIC > Access Policies > Global Policies >  Attachable Access Entity Profiles

def aep_payload(name, desc, dom, domtype, status):

    if not status:
        payload = {
            "infraInfra": {
                "attributes": {
                    "dn": "uni/infra",
                    "status": "created,modified"
                },
                "children": [{
                    "infraAttEntityP": {
                        "attributes": {
                            "dn": "uni/infra/attentp-" + name,
                            "name": name,
                            "descr": aci_fabric_build_utilities.slash_replace(desc),
                            #"rn": "attentp-LV1-ESX-AEP",
                            "status": "created,modified"
                        },
                        "children": [{
                            "infraRsDomP": {
                                "attributes": {
                                    "tDn": "uni/" + domtype + "-" + dom,
                                    "status": "created,modified"
                                },
                                "children": []
                            }
                        }]
                    }
                },
                    {
                        "infraFuncP": {
                            "attributes": {
                                "dn": "uni/infra/funcprof",
                                "status": "modified"
                            },
                            "children": []
                        }
                    }]

            }
        }
    else:
        payload = {
            "infraInfra": {
                "attributes": {
                    "dn": "uni/infra",
                    "status": "modified"
                },
                "children": [{
                    "infraAttEntityP": {
                        "attributes": {
                            "dn": "uni/infra/attentp-" + name,
                            "status": "deleted"
                        },
                        "children": []
                    }
                }]
            }
        }

    return payload



##l3outdom_payload(name, secdom, pool, status)
def l3outdom_payload(name, secdom, pool, status):

    if not status:
        payload = {
            "l3extDomP": {
                "attributes": {
                    "dn": "uni/l3dom-" + name,
                    "name": name,
                    # "rn": "l3dom-EXTERNAL_Routed_L3Out_Dom",
                    "status": "created"
                },
                "children": [{
                    "aaaDomainRef": {
                        "attributes": {
                            "dn": "uni/l3dom-" + name + "/domain-" + secdom,
                            "name": secdom,
                            # "rn": "domain-LAX01-SecDom",
                            "status": "created"
                        },
                        "children": []
                    }
                },
                    {
                        "infraRsVlanNs": {
                            "attributes": {
                                "tDn": "uni/infra/vlanns-[" + pool + "]-static",
                                "status": "created"
                            },
                            "children": []
                        }
                    }]
            }
        }

    else:
        payload = {
            "l3extDomP": {
                "attributes": {
                    "dn": "uni/l3dom-" + name,
                    "name": name,
                    # "rn": "l3dom-EXTERNAL_Routed_L3Out_Dom",
                    "status": "deleted"
                },
            }
        }
    return payload




# Enable the preservation of COS/dot1p Qos
# Fabric > Access > Global Policies > QOS Class Policies
def qos_preserve_payload(ctrl, status):


    if not status:
        payload = {
            "qosInstPol": {
                "attributes": {
                    "dn": "uni/infra/qosinst-default",
                    "ctrl": ctrl
                },
            }

        }
    else:
        payload = {
            "qosInstPol": {
                "attributes": {
                    "dn": "uni/infra/qosinst-default",
                    "ctrl": ctrl
                },
            }

        }

    return payload


##### MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN #####

# Provided main() calls the above functions
def main():
    """
    This script takes a CSV file (passed as the first argument) of data (aci objects)
    and depending on the second argument configures/creates those objects or deletes them.
    The second argument should be "True" to create and "False" to delete.
    :return:
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
    print("\n===========Running ACI STEP 2B: Configure Fabric Constructs => Access Policies===========")
    print("===========                    With the following options                     ===========")
    log_file.write("\n===========Running ACI STEP 2B: Configure Fabric Constructs => Access Policies===========")
    log_file.write("\n===========                    With the following options                     ===========\n")
    for key, value in args_dict.items():
        txt = '{:15} : {:10}'.format(key,str(value))
        print(txt)
        log_file.write(txt + "\n")


    if (
        arguments.all or arguments.link or arguments.cdp or arguments.lldp or arguments.lacp or arguments.stormcontrol
        or arguments.mcp or arguments.vpcdom or arguments.switch or arguments.vlanpool or arguments.vlan or arguments.mcpdefa
        or arguments.secdom or arguments.phydom or arguments.aep or arguments.l3outdom or arguments.qospreserve
        ):
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

    ##### FABRIC INTERFACE POLICIES #####

    # Lessons Learned: Never use "/" in comments or names
    # key: link

    if arguments.all or arguments.link:

        data = aci_fabric_build_utilities.pluck_payload(json_payload,'link')

        for line in data:
            # link_payload(name, desc, speed, autoneg, status)
            payload = link_payload(line['name'], line['desc'], line['speed'], line['autoneg'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            #print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} Link Interface Policies", resp, line['name'],
                                                             log_file, error_list)


    # key: cdp
    if arguments.all or arguments.cdp:
        data = aci_fabric_build_utilities.pluck_payload(json_payload,'cdp')

        for line in data:
            # cdp_payload(name, desc, adminSt)
            payload = cdp_payload(line['name'],line['desc'], line['adminSt'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} CDP Interface Policies", resp, line['name'],
                                                             log_file, error_list)


    #key: lldp
    if arguments.all or arguments.lldp:
        data = aci_fabric_build_utilities.pluck_payload(json_payload,'lldp')

        for line in data:
            # lldp_payload(name, desc, rxSt, txSt)
            payload = lldp_payload(line['name'],line['desc'], line['rxSt'], line['txSt'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} LLDP Interface Policies", resp, line['name'],
                                                             log_file, error_list)


    #key: lacp
    if arguments.all or arguments.lacp:
        data = aci_fabric_build_utilities.pluck_payload(json_payload,'lacp')

        for line in data:
            # lacp_payload(name, desc, mode)
            payload = lacp_payload(line['name'],line['desc'], line['mode'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} Port Channel Interface Policies", resp,
                                                             line['name'], log_file, error_list)



    #key: mcp
    if arguments.all or arguments.mcp:
        data = aci_fabric_build_utilities.pluck_payload(json_payload,'mcp')

        for line in data:
            # mcp_payload(name, desc, adminSt)
            payload = mcp_payload(line['name'],line['desc'], line['adminSt'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} MCP Interface Policies", resp, line['name'],
                                                             log_file, error_list)

    # key: stormctl
    if arguments.all or arguments.stormcontrol:
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'stormctl')

        for line in data:
            # def stormctl_payload(name, desc, rate, burstRate, status)
            payload = stormctl_payload(line['name'], line['desc'], line['rate'], line['burstRate'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} Storm Control Interface Policies", resp,
                                                             line['name'], log_file, error_list)

    ##### FABRIC Access Policies SWITCH POLICIES & VPC #####
    # Configure Switch Policies and vpc domains
    # Lesson learned - turn all integers into strings or pass as strings
    # Note: using same data for vpcdomain and vpcdefault functions

    # Configure vPC Domains for each leaf pair
    #key: vpc
    if arguments.all or arguments.vpcdom:
        data = aci_fabric_build_utilities.pluck_payload(json_payload,'vpc')

        for line in data:
            # vpcdomain_payload(name, desc)
            payload = vpcdomain_payload(line['vpc_domain'],line['desc'],object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} vPC Domains", resp, line['vpc_domain'],
                                                             log_file, error_list)

        # Configure default Virtual Port Channel Policy
        for line in data:
            # vpcdefault_payload(name, pair_id, node_1, node_2, vpc_domain)
            payload = vpcdefault_payload(line['prot_grp_name'],line['pair_id'],line['node_1'],line['node_2'],
                                         line['vpc_domain'],object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} default vPC Policy", resp, line['prot_grp_name'],
                                                         log_file, error_list)


    # Configure Leaf Profiles
    #key: switch
    if arguments.all or arguments.switch:
        data = aci_fabric_build_utilities.pluck_payload(json_payload,'switch')

        for line in data:
            # leafprof_payload(name, desc, leafsel_name, frm_sw, to_sw)
            payload = leafprof_payload(line['name'], line['desc'], line['leafsel_name'], line['frm_sw'], line['to_sw'],object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            #print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} Leaf Policies", resp, line['name'],
                                                             log_file, error_list)


    # Configure Vlan Pools (empty)
    #key: vlanpool
    if arguments.all or arguments.vlanpool:
        data = aci_fabric_build_utilities.pluck_payload(json_payload,'vlanpool')

        for line in data:
            # vlanpool_payload(name, desc, allocmode, vlan_desc, frm_vlan, to_vlan, status)
            payload = vlanpool_payload(line['name'], line['desc'], line['allocmode'], "", "", "", object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            #print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} Empty Vlan Pools", resp, line['name'],
                                                             log_file, error_list)

    #Configure VLANS
    #key: vlan
    if arguments.all or arguments.vlan:
        poolallocationtype = False
        vlanpool_data = aci_fabric_build_utilities.pluck_payload(json_payload, 'vlanpool')
        # print(vlanpool_data)

        data = aci_fabric_build_utilities.pluck_payload(json_payload,'vlan')


        for line in data:
            # print(line)
            poolallocationtype = False
            for vpline in vlanpool_data:
                # print("VPLINE: {}".format(vpline))
                if vpline['name'] == line['name']:
                    poolallocationtype = vpline['allocmode']

            # print(poolallocationtype)
            # raw_input("Pause...")

            if not poolallocationtype:
                print("ERROR: Cannot determine original Vlan Pool Allocation Type for vlan pool {}! Moving on to next item in list.".format(line['name']))
                continue


            # vlan_payload(name, desc, allocmode, vlan_desc, frm_vlan, to_vlan, status)
            payload = vlan_payload(line['name'], line['desc'], poolallocationtype, line['allocmode'], line['vlan_desc'],
                                       line['frm_vlan'], line['to_vlan'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            #print_debug_data(resp)
            vlans = str(line['frm_vlan']) + " - " + str(line['to_vlan'])
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} VLANs", resp, vlans, log_file, error_list)


    #Configure default MCP behavior to be enabled
    #key: set_default_mcp
    if arguments.all or arguments.mcpdefa:
        data = aci_fabric_build_utilities.pluck_payload(json_payload,'set_default_mcp')

        for line in data:
            #mcpdefault_payload(desc, adminSt, key, status)
            payload = mcpdefault_payload(line['desc'], line['adminSt'], line['key'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            #print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} default MCP behavior Policies", resp,
                                                             line['name'], log_file, error_list)

    #Configure Security Domain
    #key: secdom
    if arguments.all or arguments.secdom:
        data = aci_fabric_build_utilities.pluck_payload(json_payload,'secdom')

        for line in data:
            # secdom_payload(name, desc, status )
            payload = secdom_payload(line['name'], line['desc'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            #print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} Security Domain", resp, line['name'],
                                                             log_file, error_list)

    #Configure Physical Domain
    #key: phydom
    if arguments.all or arguments.phydom:
        data = aci_fabric_build_utilities.pluck_payload(json_payload,'phydom')

        for line in data:
            # phydom_payload(name, desc, secdom, pool, status )
            payload = phydom_payload(line['name'], line['desc'], line['secdom'], line['pool'],object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            #print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} Physical Domain", resp, line['name'],
                                                             log_file, error_list)


    #Configure External L3 Routed Outside Domain
    #key: l3outdom
    if arguments.all or arguments.l3outdom:
        data = aci_fabric_build_utilities.pluck_payload(json_payload,'l3outdom')

        for line in data:
            #l3outdom_payload(name, secdom, pool, status)
            payload = l3outdom_payload(line['name'], line['secdom'], line['pool'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            #print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} External Routed L3 Out Domain", resp,
                                                             line['name'], log_file, error_list)

    # Configure Attachable Entity Profile (AEP)
    # Valid for physical domains, L3 External Routed Outs
    # domtype = phys, l3dom
    # key: aep
    if arguments.all or arguments.aep:
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'aep')

        for line in data:
            # aep_payload(name, desc, phydom, status)
            # print(line)
            payload = aep_payload(line['name'], line['desc'], line['dom'], line['domtype'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} AEP", resp, line['name'],
                                                             log_file, error_list)

    # Enable/Disable the preservation of COS/dot1p Qos
    # key: qos_preserve
    if arguments.all or arguments.qospreserve:
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'qos_preserve')

        for line in data:
            # qos_preserve_payload(ctrl, status)

            ctrl = line['ctrl']

            if arguments.xdelete:
                if "none" in line['ctrl']:
                    ctrl = "dot1p-preserve"
                else:
                    ctrl = "none"

            payload = qos_preserve_payload(ctrl, object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} QoS COS Preservation", resp, line['ctrl'],
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

    # Configure Basic Fabric Access Policy Constructs
    # -k Link
    # -d CDP
    # -p LLDP
    # -l LACP
    # -m MCP
    # -v vPC Domain
    # -s Leaf (Switch) Profile
    # -o Vlan Pool
    # -n Vlan
    # -u MCP Default Enable
    # -y Security Domain
    # -i Physical Domain
    # -e AEP
    # -q QoS Preserve COS




    parser = argparse.ArgumentParser(description="ACI STEP 2B: Configure Fabric Constructs => Access Policies",
                                     epilog="Usage: aci_fabric_step2b_accpol.py 'my_payload.csv' -a to create and -a -x to delete")

    parser.add_argument('payload_file', help='Name of the payload file to use in this script.')

    parser.add_argument('-x', '--xdelete',
                        help='True to remove/delete/reset configuration and False to create (default) action unless -x is used',
                        action='store_true',
                        default=False)

    parser.add_argument('-a', '--all', help='Execute all object CRUD sections. Without this argument nothing will execute.',
                        action='store_true', default=False)

    parser.add_argument('-k', '--link', help='Execute Link Interface Policy function', action='store_true',
                        default=False)
    parser.add_argument('-d', '--cdp', help='Execute CDP Interface Policy function', action='store_true',
                        default=False)
    parser.add_argument('-p', '--lldp', help='Execute LLDP Interface Policy function', action='store_true', default=False)
    parser.add_argument('-l', '--lacp', help='Execute LACP Interface Policy function', action='store_true', default=False)

    parser.add_argument('-m', '--mcp', help='Execute MCP Interface Policy function', action='store_true', default=False)

    parser.add_argument('-t', '--stormcontrol', help='Execute StormControl Interface Policy function', action='store_true', default=False)

    parser.add_argument('-v', '--vpcdom', help='Execute vPC Domain Protection Group Policy function', action='store_true',
                        default=False)
    parser.add_argument('-s', '--switch', help='Execute Leaf/Switch Profile Policy function', action='store_true',
                        default=False)
    parser.add_argument('-o', '--vlanpool', help='Execute Vlan Pool Policy function', action='store_true', default=False)
    parser.add_argument('-n', '--vlan', help='Execute Vlan Policy function (note: VLAN Pool payload is required)', action='store_true', default=False)

    parser.add_argument('-u', '--mcpdefa', help='Execute MCP Default Policy function', action='store_true', default=False)

    parser.add_argument('-y', '--secdom', help='Execute Security Domain Policy function', action='store_true', default=False)

    parser.add_argument('-i', '--phydom', help='Execute Physical Domain Default Policy function', action='store_true', default=False)

    parser.add_argument('-3', '--l3outdom', help='Execute External L3 Routed Out function', action='store_true', default=False)

    parser.add_argument('-e', '--aep', help='Execute AEP Policy function', action='store_true', default=False)

    parser.add_argument('-q', '--qospreserve', help='QoS Preserve QoS Global Policy', action='store_true', default=False)

    parser.add_argument('-f', '--filename',
                        help='Option used to pass a credentials file other than the default "credentias.py"',
                        default='credentials.py')

    arguments = parser.parse_args()
    #print arguments

    main()
