#!/usr/bin/python -tt
# Project: python
# Filename: aci_fabric_step1_mgmt
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
##### STEP 1 Fabric Discovery                       #####
#########################################################


# status is set by the -x --xdelete argument to False for deletion
# Read: If (delete) not true create payload else (delete) IS true and remove

def fab_discovery_payload(name, serial, nodeid, pod, role, status):

    if not status:
        payload = {
            "fabricNodeIdentP": {
                "attributes": {
                    "dn": "uni/controller/nodeidentpol/nodep-" + serial,
                    "serial": serial,
                    "nodeId": str(nodeid),
                    "podId": str(pod),
                    "name": name,
                    #"role": "leaf", "spine", "unknown"
                    "role": role,
                    "status": "created,modified"
                },
                "children": []
            }
        }
    else:
        payload = {
            "fabricNodeIdentP": {
                "attributes": {
                    "dn": "uni/controller/nodeidentpol/nodep-N5768TEST",
                    "status": "deleted"
                },
            }
        }
    return payload


def fab_decommission_payload(name, serial, nodeid, pod, role, status):

    if not status:
        payload = {
            "fabricRsDecommissionNode": {
                "attributes": {
                    "dn": "uni/fabric/outofsvc/rsdecommissionNode-[topology/pod-" + str(pod) + "/node-" + str(nodeid)+ "]",
                    # "tDn": "topology/pod-" + str(pod) + "/node-" + str(nodeid),
                    "status": "created,modified",
                    "removeFromController": "true"
                },
                "children": []
            }
        }
    else:
        pass
    return payload



#########################################################
##### STEP 1 Fabric Management                      #####
#########################################################

#########################################################
##### TENANTS > mmt > Node Management Addresses > Static#
#########################################################

# Tenants > mgmt > Node Management EPGS > Out-of-Band EPG - default
# Associate the common/default Contract as a Provided Out-of_Band Contract to remove
# "Not Associated with Management Zone" Configuration Issue

def oob_mgmt_prov_payload(oobepg, status):

    if not status:
        payload = {
            "mgmtRsOoBProv": {
                "attributes": {
                    "dn": "uni/tn-mgmt/mgmtp-default/oob-" + oobepg + "/rsooBProv-" + oobepg,
                    "tnVzOOBBrCPName": "default",
                    "status": "created,modified"
                },
                "children": []
            }
        }
    else:
        payload = {
            "mgmtRsOoBProv": {
                "attributes": {
                    "dn": "uni/tn-mgmt/mgmtp-default/oob-" + oobepg + "/rsooBProv-" + oobepg,
                    #"tnVzOOBBrCPName": "default",
                    "status": "deleted"
                },
                "children": []
            }
        }
    return payload


# mgmt > IP Address Pools
def mgmt_ip_pool_payload(mgmtippool, gw, addrmask, status):

    if not status:
        payload = {
            "fvnsAddrInst": {
                "attributes": {
                    "dn": "uni/tn-mgmt/addrinst-" + mgmtippool,
                    "name": mgmtippool,
                    "addr": gw + "/" + addrmask,
                    #"rn": "addrinst-OOB-IPAddr-POOL",
                    "status": "created"
                },
            }
        }
    else:
        payload = {
            "fvnsAddrInst": {
                "attributes": {
                    "dn": "uni/tn-mgmt/addrinst-" + mgmtippool,
                    "status": "deleted"
                },
            }
        }
    return payload


# mgmt > IP Address Pool Entries
def mgmt_ip_pool_entry_payload(mgmtippool, ip, status):

    if not status:
        payload = {
            "fvnsUcastAddrBlk": {
                "attributes": {
                    "dn": "uni/tn-mgmt/addrinst-" + mgmtippool + "/fromaddr-[" + ip + "]-toaddr-[" + ip + "]",
                    "from": ip,
                    "status": "created",
                    "to": ip,
                    #"rn": "fromaddr-[10.1.10.201]-toaddr-[10.1.10.201]"
                },
            }
        }
    else:
        payload = {
            "fvnsUcastAddrBlk": {
                "attributes": {
                    "dn": "uni/tn-mgmt/addrinst-" + mgmtippool + "/fromaddr-[" + ip + "]-toaddr-[" + ip + "]",
                    "status": "deleted",
                },
            }
        }
    return payload


# mgmt > Managemd Node Connectivity Group
def oob_node_conngrp_payload(mgmtgrppol, mgmtippool, status):

    if not status:
        payload = {
            "mgmtGrp": {
                "attributes": {
                    "dn": "uni/infra/funcprof/grp-" + mgmtgrppol,
                    "name": mgmtgrppol,
                    "status": "created,modified"
                },
                "children": [{
                    "mgmtOoBZone": {
                        "attributes": {
                            "dn": "uni/infra/funcprof/grp-" + mgmtgrppol + "/oobzone",
                            "rn": "oobzone",
                            "status": "created"
                        },
                        "children": [{
                            "mgmtRsOoB": {
                                "attributes": {
                                    "tDn": "uni/tn-mgmt/mgmtp-default/oob-default",
                                    "status": "created"
                                },
                                "children": []
                            }
                        },
                            {
                                "mgmtRsAddrInst": {
                                    "attributes": {
                                        "tDn": "uni/tn-mgmt/addrinst-" + mgmtippool,
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
            "mgmtGrp": {
                "attributes": {
                    "dn": "uni/infra/funcprof/grp-" + mgmtgrppol,
                    "name": "OOB-NodeConnGrp",
                    "rn": "grp-OOB-NodeConnGrp",
                    "status": "deleted"
                },
                # "children": [{
                #     "mgmtOoBZone": {
                #         "attributes": {
                #             "dn": "uni/infra/funcprof/grp-OOB-NodeConnGrp/oobzone",
                #             "rn": "oobzone",
                #             "status": "created"
                #         },
                #         "children": [{
                #             "mgmtRsOoB": {
                #                 "attributes": {
                #                     "tDn": "uni/tn-mgmt/mgmtp-default/oob-default",
                #                     "status": "created"
                #                 },
                #                 "children": []
                #             }
                #         },
                #             {
                #                 "mgmtRsAddrInst": {
                #                     "attributes": {
                #                         "tDn": "uni/tn-mgmt/addrinst-OOB-IPAddr-POOL",
                #                         "status": "created"
                #                     },
                #                     "children": []
                #                 }
                #             }]
                #     }
                # }]
            }
        }
    return payload


def oobstnode_payload(node,oobepg,addr,addrmask,gw,v6addr,v6addrmask,v6gw,pod, status):

    # status is set by the -x --xdelete argument to False for deletion
    # Read: If (delete) not true create payload else (delete) IS true and remove

    if not status:
        payload = {
            "mgmtRsOoBStNode": {
                "attributes": {
                    "dn": "uni/tn-mgmt/mgmtp-default/oob-" + oobepg + "/rsooBStNode-[topology/pod-" + str(pod)
                          + "/node-" + node + "]",
                    "addr": addr + "/" + addrmask,
                    "gw": gw,
                    "v6Addr": v6addr + "/" + v6addrmask,
                    "v6Gw": v6gw,
                    "status": "created"
                },
                "children": []
            }
        }
    else:
        payload = {
            "mgmtRsOoBStNode": {
                "attributes": {
                    # "uni/tn-mgmt/mgmtp-default/oob-default/rsooBStNode-[topology/pod-1/node-101]",
                    "dn": "uni/tn-mgmt/mgmtp-default/oob-" + oobepg + "/rsooBStNode-[topology/pod-"
                          + str(pod) + "/node-" + node + "]",
                    "status": "deleted"
                },
            }
        }
    return payload




###############################
##### ADMIN Import/Export #####
###############################

def remote_loc_payload(name, desc, protocol, uname, upwd, ip, status):
    port_dict = {"scp": "22", "sftp": "22", "ftp": "21"}
    if not status:
        payload = {
            "fileRemotePath": {
                "attributes": {
                    "dn": "uni/fabric/path-" + name,
                    "remotePort": port_dict[protocol],
                    "name": name,
                    "descr": aci_fabric_build_utilities.slash_replace(desc),
                    # Valid values = "ftp" "scp" "sftp"
                    "protocol": protocol,
                    "userName": uname,
                    "userPasswd": upwd,
                    "host": ip
                    # "rn": "path-cdl-remote-loc",
                    # "status": "created"
                },
                "children": []
            }
        }

    else:
        payload = {
            "fileRemotePath": {
                "attributes": {
                    "dn": "uni/fabric/path-" + name,
                    "remotePort": port_dict[protocol],
                    # "name": name,
                    # "descr": desc,
                    # # Valid values = "ftp" "scp" "sftp"
                    # "protocol": protocol,
                    # "userName": uname,
                    # "userPasswd": upwd,
                    # "host": ip
                    # # "rn": "path-cdl-remote-loc",
                    "status": "deleted"
                },
                "children": []
            }
        }

    return payload


def export_pol_payload(name, desc, adminSt, format, trigger, remote_path, status):

    if not status:
        payload = {
                "configExportP": {
                    "attributes": {
                        "dn": "uni/fabric/configexp-" + name,
                        "name": name,
                        "descr": aci_fabric_build_utilities.slash_replace(desc),
                        #Valid Values = "triggered" NOte: can't send  empty string
                        "adminSt": adminSt,
                        #Valid Values = "xml" "json"
                         "format": format,
                        #"rn": "configexp-CDL_export-pol",
                        #"status": "created"
                    },
                    "children": [{
                        "configRsExportScheduler": {
                            "attributes": {
                                #Valid Values = "EveryEightHours" "ConstSchedP" "ConstCatSchedP" Any existing name
                                "tnTrigSchedPName": trigger,
                                "status": "created,modified"
                            },
                            "children": []
                        }
                    },
                    {
                        "configRsRemotePath": {
                            "attributes": {
                                # Valid Values = Any existing name
                                "tnFileRemotePathName": remote_path,
                                "status": "created,modified"
                            },
                            "children": []
                        }
                    }]
                }
            }

    else:
        payload = {
            "configExportP": {
                "attributes": {
                    "dn": "uni/fabric/configexp-" + name,
                    "status": "deleted"
                },
                "children": []
            }
        }

    return payload



# ADMIN > AAA > Security Management > Local Users

def aaa_localuser_payload(status, uname="ddadmin", desc="Temporary DD Admin Account", pwd="didata123",
                          fname="Dimension",lname="Data",phone="123-456-7890", email="dd@didata.com", udomain="all"):

    # udomain = User Domain Valid values "all", custom built

    if not status:
        payload = {

            "aaaUser": {
                "attributes": {
                    "dn": "uni/userext/user-" + uname,
                    "descr": aci_fabric_build_utilities.slash_replace(desc),
                    "name": uname,
                    "pwd": pwd,
                    "firstName": fname,
                    "lastName": lname,
                    "phone": phone,
                    "email": email,
                    "status": "created"
                },
                "children": [{
                    "aaaUserDomain": {
                        "attributes": {
                            "dn": "uni/userext/user-" + uname + "/userdomain-" + udomain,
                            "name": udomain,
                            "status": "created,modified"
                        },
                        "children": [{
                            "aaaUserRole": {
                                "attributes": {
                                    "dn": "uni/userext/user-" + uname + "/userdomain-" + udomain + "/role-aaa",
                                    "name": "aaa",
                                    "privType": "writePriv",
                                    "rn": "role-aaa",
                                    "status": "created,modified"
                                },
                                "children": []
                            }
                        },
                            {
                                "aaaUserRole": {
                                    "attributes": {
                                        "dn": "uni/userext/user-" + uname + "/userdomain-" + udomain + "/role-access-admin",
                                        "name": "access-admin",
                                        "privType": "writePriv",
                                        "rn": "role-access-admin",
                                        "status": "created,modified"
                                    },
                                    "children": []
                                }
                            },
                            {
                                "aaaUserRole": {
                                    "attributes": {
                                        "dn": "uni/userext/user-" + uname + "/userdomain-" + udomain + "/role-admin",
                                        "name": "admin",
                                        "privType": "writePriv",
                                        "rn": "role-admin",
                                        "status": "created,modified"
                                    },
                                    "children": []
                                }
                            },
                            {
                                "aaaUserRole": {
                                    "attributes": {
                                        "dn": "uni/userext/user-" + uname + "/userdomain-" + udomain + "/role-fabric-admin",
                                        "name": "fabric-admin",
                                        "privType": "writePriv",
                                        "rn": "role-fabric-admin",
                                        "status": "created,modified"
                                    },
                                    "children": []
                                }
                            },
                            {
                                "aaaUserRole": {
                                    "attributes": {
                                        "dn": "uni/userext/user-" + uname + "/userdomain-" + udomain + "/role-nw-svc-admin",
                                        "name": "nw-svc-admin",
                                        "privType": "writePriv",
                                        "rn": "role-nw-svc-admin",
                                        "status": "created,modified"
                                    },
                                    "children": []
                                }
                            },
                            {
                                "aaaUserRole": {
                                    "attributes": {
                                        "dn": "uni/userext/user-" + uname + "/userdomain-" + udomain + "/role-nw-svc-params",
                                        "name": "nw-svc-params",
                                        "privType": "writePriv",
                                        "rn": "role-nw-svc-params",
                                        "status": "created,modified"
                                    },
                                    "children": []
                                }
                            },
                            {
                                "aaaUserRole": {
                                    "attributes": {
                                        "dn": "uni/userext/user-" + uname + "/userdomain-" + udomain + "/role-ops",
                                        "name": "ops",
                                        "privType": "writePriv",
                                        "rn": "role-ops",
                                        "status": "created,modified"
                                    },
                                    "children": []
                                }
                            },
                            {
                                "aaaUserRole": {
                                    "attributes": {
                                        "dn": "uni/userext/user-" + uname + "/userdomain-" + udomain + "/role-read-all",
                                        "name": "read-all",
                                        "privType": "writePriv",
                                        "rn": "role-read-all",
                                        "status": "created,modified"
                                    },
                                    "children": []
                                }
                            },
                            {
                                "aaaUserRole": {
                                    "attributes": {
                                        "dn": "uni/userext/user-" + uname + "/userdomain-" + udomain + "/role-tenant-admin",
                                        "name": "tenant-admin",
                                        "privType": "writePriv",
                                        "rn": "role-tenant-admin",
                                        "status": "created,modified"
                                    },
                                    "children": []
                                }
                            },
                            {
                                "aaaUserRole": {
                                    "attributes": {
                                        "dn": "uni/userext/user-" + uname + "/userdomain-" + udomain + "/role-tenant-ext-admin",
                                        "name": "tenant-ext-admin",
                                        "privType": "writePriv",
                                        "rn": "role-tenant-ext-admin",
                                        "status": "created,modified"
                                    },
                                    "children": []
                                }
                            },
                            {
                                "aaaUserRole": {
                                    "attributes": {
                                        "dn": "uni/userext/user-" + uname + "/userdomain-" + udomain + "/role-vmm-admin",
                                        "name": "vmm-admin",
                                        "privType": "writePriv",
                                        "rn": "role-vmm-admin",
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

            "aaaUser": {
                "attributes": {
                    "dn": "uni/userext/user-" + uname,
                    # "descr": "Mission San Juan Bautista, June 24, 1797",
                    # "name": "Juan",
                    # "pwd": "Bautista",
                    # "firstName": "Juan",
                    # "lastName": "Bautista",
                    # "phone": "123-456-7890",
                    # "email": "juan@mission.com",
                    # "rn": "user-Juan",
                    "status": "deleted"
                },
            }
        }
    return payload

def fabdeploypol_payload(show, status):

    if not status:
        payload = {
            "fabricDeployPol": {
                "attributes": {
                    "childAction": "",
                    "descr": "",
                    "dn": "uni/fabric/deploypol-default",
                    "lcOwn": "local",
                    "modTs": "2017-09-10T14:38:13.344+00:00",
                    "name": "default",
                    "nameAlias": "",
                    "ownerKey": "",
                    "ownerTag": "",
                    "showUsageWarn": yes,
                    "status": "",
                    "uid": "0"
                }
            }
        }
    else:
        payload = {
            "fabricDeployPol": {
                "attributes": {
                    "childAction": "",
                    "descr": "",
                    "dn": "uni/fabric/deploypol-default",
                    # "lcOwn": "local",
                    # "modTs": "2017-09-10T14:38:13.344+00:00",
                    "name": "default",
                    # "nameAlias": "",
                    # "ownerKey": "",
                    # "ownerTag": "",
                    "showUsageWarn": "no",
                    # "status": "",
                    # "uid": "0"
                }
            }
        }
    return payload


##### MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN #####

# Provided main() calls the above functions
def main():
    """
    This script takes a CSV payload file, turns it into JSON, and configures management constructes in the 
    mgmt tenant starting wtih:
    1. Static Node IP assignments on the OOB Management Network
    
    # -x Remote Location (Future)
    # -x Export Policy (Future)
    
    """
    # define non 200 response dictionary for items that failed to apply
    error_list = []

    # set variable filename to the CSV file passed as the first argument
    filename = arguments.payload_file

    # Set to "True" to delete the objects defined in this script on the APIC by passing -x
    # default is "False"
    object_status_delete = arguments.xdelete

    action_text = "Adding" if not object_status_delete else "Removing"

    start_time = time.time()

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
    print("\n===========Running ACI STEP 1: Configure Node Management => Static Node===========")
    print("===========                   With the following options                  ===========")
    log_file.write("\n===========Running ACI STEP 1: Configure Node Management => Static Node===========")
    log_file.write("\n===========               With the following options                   ===========\n")
    for key, value in args_dict.items():
        txt = '{:15} : {:10}'.format(key,str(value))
        print(txt)
        log_file.write(txt + "\n")


    if arguments.all or arguments.remoteloc or arguments.export or arguments.fabdiscovery or arguments.localuser \
            or arguments.oobmgmt or arguments.warnings:
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
    #print("len of json_payload is {}".format(len(json_payload)))

    ##### FABRIC DISCOVERY #####

    # Configure Fabric Discovery
    # key: fab_discovery
    if arguments.all or arguments.fabdiscovery:
        # Configure Fabric Discovery
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'fab_discovery')

        for line in data:
            if line:
                # fab_discovery_payload(name, serial, nodeid, pod, role, status):
                payload = fab_discovery_payload(line['name'], line['serial'], line['nodeid'], line['pod'],
                                                line['role'], object_status_delete)

                resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
                # aci_fabric_build_utilities.print_debug_data(resp)
                aci_fabric_build_utilities.print_post_result_log("Configure Fabric Discovery Pod ",
                                                                 resp, line['name'], log_file, error_list)

    if arguments.decomm:
        # Decomission Fabric Discovery
        # WARNING:  This decomissions all devices in the fabric discovery payload
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'fab_discovery')

        for line in data:
            if line:
                # fab_decommission_payload(name, serial, nodeid, pod, role, status):
                payload = fab_decommission_payload(line['name'], line['serial'], line['nodeid'], line['pod'],
                                                line['role'], object_status_delete)

                resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
                # aci_fabric_build_utilities.print_debug_data(resp)
                aci_fabric_build_utilities.print_post_result_log("Decommission Fabric Nodes ",
                                                                 resp, line['name'], log_file, error_list)



    # Configure Out of Band Static Nodes
    # key: oobstnode
    if arguments.all or arguments.oobmgmt:
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'oobstnode')

        # Configure default contract on default EPG
        payload = oob_mgmt_prov_payload(data[0]['oobepg'], object_status_delete)
        resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
        aci_fabric_build_utilities.print_post_result_log(f"{action_text} OOB Management Provider Contract for Default EPG ",
                                                     resp, data[0]['oobepg'], log_file, error_list)

        # Configure Management IP Pool
        # mgmt_ip_pool_payload(name, gw, addrmask, status)
        payload = mgmt_ip_pool_payload(data[0]['mgmtippool'], data[0]['gw'], data[0]['addrmask'], object_status_delete)
        resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
        aci_fabric_build_utilities.print_post_result_log(f"{action_text} OOB Management IP Pool ",
                                                     resp, data[0]['mgmtippool'], log_file, error_list)

        # Configure Management Node Connectivity Group
        # def oob_node_conngrp_payload(mgmtgrppol, mgmtippool, status):
        payload = oob_node_conngrp_payload(data[0]['mgmtgrppol'], data[0]['mgmtippool'], object_status_delete)
        resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
        aci_fabric_build_utilities.print_post_result_log(f"{action_text} OOB Management Node Connectivity Gropu ",
                                                     resp, data[0]['mgmtgrppol'], log_file, error_list)

        for line in data:
            # mgmt_ip_pool_entry_payload(mgmtippool, ip, status):
            payload = mgmt_ip_pool_entry_payload(line['mgmtippool'], line['addr'], object_status_delete)
            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} OOB Management IP Address Pool Entry ",
                                                             resp, line['addr'], log_file, error_list)

            # oobstnode_payload(node,oobepg,addr,addrmask,gw,v6addr, v6addrmask,v6gw, pod, status)
            payload = oobstnode_payload(line['node'], line['oobepg'], line['addr'], line['addrmask'], line['gw'],
                                        line['v6addr'], line['v6addrmask'], line['v6gw'], line['pod'],
                                        object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # aci_fabric_build_utilities.print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} OOB Management for node ", resp, line['node'],
                                                             log_file, error_list)


    # Configure Remote Location for Export
    # key: remote_loc
    if arguments.all or arguments.remoteloc:
        # Configure Remote Location
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'remote_loc')

        for line in data:
            # remote_loc_payload(name, desc, protocol, uname, upwd, ip)
            payload = remote_loc_payload(line['name'], line['desc'], line['protocol'], line['uname'], line['upwd'],
                                        line['ip'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # aci_fabric_build_utilities.print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(f"{action_text} Remote Location for Backup ", resp, line['name'],
                                                             log_file, error_list)

    if arguments.all or arguments.export:
        # Configure Export Policy
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'export_pol')

        for line in data:
            if line:
                # export_pol_payload(name, desc, adminSt, format, trigger, remote_path, status):
                payload = export_pol_payload(line['name'], line['desc'], line['adminSt'], line['format'],
                                             line['trigger'],
                                             line['remote_path'], object_status_delete)

                resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
                # aci_fabric_build_utilities.print_debug_data(resp)
                aci_fabric_build_utilities.print_post_result_log(f"{action_text} Export Policy ", resp, line['name'],
                                                                 log_file, error_list)


    if arguments.all or arguments.localuser:
        # Configure Local User with full Admin rights
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'aaa_localuser')

        for line in data:
            if line:
                # aaa_localuser_payload(uname="ddadmin", desc="Temporary DD Admin Account", pwd="didata123",
                # fname="Dimension", lname="Data", phone="123-456-7890", email="dd@didata.com",
                # udomain="all", status):

                payload = aaa_localuser_payload(object_status_delete, line['uname'], line['desc'], line['pwd'], line['fname'],
                                             line['lname'], line['phone'], line['email'], line['udomain'])

                resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
                # aci_fabric_build_utilities.print_debug_data(resp)
                aci_fabric_build_utilities.print_post_result_log(f"{action_text} Local User ", resp,
                                                                 line['uname'],
                                                                 log_file, error_list)

    if arguments.all or arguments.warnings:
        # Configure Fabric to show warnings on Modify/Delete
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'fabdeploypol')

        for line in data:
            if line:
                # def fabdeploypol_payload(show, status):

                payload = fabdeploypol_payload(object_status_delete, line['show'])

                resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
                # aci_fabric_build_utilities.print_debug_data(resp)
                aci_fabric_build_utilities.print_post_result_log(f"{action_text} Fabric to show warnings on Modify/Delete ", resp,
                                                                 line['show'], log_file, error_list)



    ############ END of PROCESSING #######################
    # End - Calculate time of execution
    delta_time = str(time.time() - start_time)
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

    # Configure Node Management in mgmt Tenant

    parser = argparse.ArgumentParser(description="ACI STEP 1: Configure Fabric Discovery and Node Management in mgmt Tenant",
                                     epilog="Usage: aci_fabric_step1_mgmt.py 'my_payload.csv' -a to create and -a -x to delete")

    parser.add_argument('payload_file', help='Name of the CSV payload file to use in this script.')

    parser.add_argument('-x', '--xdelete',
                        help='True to remove/delete/reset configuration and False to create (default) action unless -x is used',
                        action='store_true',
                        default=False)

    parser.add_argument('-a', '--all', help='Execute all object CRUD sections. Without this argument nothing will execute.',
                        action='store_true', default=False)

    parser.add_argument('-d', '--fabdiscovery', help='Fabric Discovery', action='store_true',default=False)

    parser.add_argument('-o', '--oobmgmt', help='Out of Band Management', action='store_true',default=False)

    parser.add_argument('-l', '--localuser', help='Local User', action='store_true',default=False)

    parser.add_argument('-r', '--remoteloc', help='Remote Locations', action='store_true',default=False)

    parser.add_argument('-e', '--export', help='Configuration Export', action='store_true',default=False)

    parser.add_argument('-w', '--warnings', help='Fabric Deploy Show Warnings', action='store_true',default=False)

    parser.add_argument('-c', '--decomm', help='Decommission Nodes - WARNING this decommissions all nodes in the '
                                               'discovery payload! It will NOT be run with the -a option.  '
                                               'This must be called with just the -c option.',
                        action='store_true', default=False)

    parser.add_argument('-f', '--filename',
                        help='Option used to pass a credentials file other than the default "credentias.py"',
                        default='credentials.py')

    arguments = parser.parse_args()
    #print arguments
    main()


