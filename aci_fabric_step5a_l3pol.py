#!/usr/bin/python -tt
# Project: python
# Filename: aci_fabric-step5a_l3pol.py
# Claudia
# PyCharm

from __future__ import absolute_import, division, print_function

__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = "Revision: 1.0 $"
__date__ = "10/9/2016-6:04 AM"
__copyright__ = "Copyright (c) 2015 Claudia de Luna"
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




#########################################################################################################
####################################### Layer 3 Constructs #############################################
#########################################################################################################

def l3extout_ospf_payload(name, desc, tn, area, areatype, vrf, l3outdom, status):

    if not status:
        payload = {

            "l3extOut": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/out-" + name,
                    "name": name,
                    "descr": desc,
                    #"rn": "out-External_Routed_L3Out",
                    "status": "created, modified"
                },
                "children": [{
                    "ospfExtP": {
                        "attributes": {
                            "dn": "uni/tn-" + tn + "/out-" + name + "/ospfExtP",
                            "areaId": area,
                            # areaType = regular,
                            "areaType": areatype,
                            #"rn": "ospfExtP",
                            "status": "created, modified"
                        },
                        "children": []
                    }
                },
                    {
                        "l3extRsEctx": {
                            "attributes": {
                                "tnFvCtxName": vrf,
                                "status": "created,modified"
                            },
                            "children": []
                        }
                    },
                    {
                        "l3extRsL3DomAtt": {
                            "attributes": {
                                "tDn": "uni/l3dom-" + l3outdom,
                                "status": "created"
                            },
                            "children": []
                        }
                    }]
            }
        }

    else:
        payload = {
            "l3extOut": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/out-" + name,
                    "name": name,
                    "status": "deleted"
                },
            }
        }
    return payload


def l3extnodep_ospf_payload(name, desc, tn, l3extout, ospfintprof, rtrid1, rtrid2, node1, node2, rtrlo, pod, status):

    if not status:
        payload = {
            "l3extLNodeP": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/out-" + l3extout + "/lnodep-" + name,
                    "name": name,
                    #"desc": desc,
                    #"rn": "lnodep-ExtL3OutNodeProfile",
                    "status": "created"
                },
                "children": [{
                    "l3extLIfP": {
                        "attributes": {
                            "dn": "uni/tn-" + tn + "/out-" + l3extout + "/lnodep-" + name + "/lifp-" + ospfintprof,
                            "name": ospfintprof,
                            "descr": "OSPF Interface Profile",
                            #"rn": "lifp-ExtL3Out_OSPF_IntProf",
                            "status": "created"
                        },
                        "children": [{
                            "ospfIfP": {
                                "attributes": {
                                    "dn": "uni/tn-" + tn + "/out-" + l3extout + "/lnodep-" + name + "/lifp-" + ospfintprof + "/ospfIfP",
                                    #"rn": "ospfIfP",
                                    "status": "created"
                                },
                                "children": []
                            }
                        }]
                    }
                },
                    {
                        "l3extRsNodeL3OutAtt": {
                            "attributes": {
                                "dn": "uni/tn-" + tn + "/out-" + l3extout + "/lnodep-" + name + "/rsnodeL3OutAtt-[topology/pod-" + pod + "/node-" + node1 + "]",
                                "tDn": "topology/pod-" + pod + "/node-" + node1,
                                "rtrId": rtrid1,
                                # Router ID Loopback for BGP = True, for other protocols = false
                                "rtrIdLoopBack": rtrlo,
                                "rn": "rsnodeL3OutAtt-[topology/pod-" + pod + "/node-" + node1 + "]",
                                "status": "created"
                            },
                            "children": [{
                                "l3extInfraNodeP": {
                                    "attributes": {
                                        "fabricExtCtrlPeering": "false",
                                        "status": "created"
                                    },
                                    "children": []
                                }
                            }]
                        }
                    },
                    {
                        "l3extRsNodeL3OutAtt": {
                            "attributes": {
                                "dn": "uni/tn-" + tn + "/out-" + l3extout + "/lnodep-" + name + "/rsnodeL3OutAtt-[topology/pod-" + pod + "/node-" + node2 + "]",
                                "tDn": "topology/pod-" + pod + "/node-" + node2,
                                "rtrId": rtrid2,
                                # Router ID Loopback for BGP = True, for other protocols = false
                                "rtrIdLoopBack": rtrlo,
                                "rn": "rsnodeL3OutAtt-[topology/pod-" + pod + "/node-" + node2 + "]",
                                "status": "created"
                            },
                            "children": [{
                                "l3extInfraNodeP": {
                                    "attributes": {
                                        "fabricExtCtrlPeering": "false",
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
            "l3extLNodeP": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/out-" + l3extout + "/lnodep-" + name,
                    "status": "deleted"
                },
            }
        }
    return payload


def l3out_routedint_payload(name, desc, tn, l3extout, ospfintprof, node, int, mtu, ip, mask, conntype, mode, encap, pod, status):

    # type = l3-port (Routed Interface), sub-interface (Routed Sub-Interface), ext-svi (SVI)

    if not status:

        if conntype.lower() == "l3-port":
            payload = {
                "l3extRsPathL3OutAtt": {
                    "attributes": {
                        "dn": "uni/tn-" + tn + "/out-" + l3extout + "/lnodep-" + name + "/lifp-" + ospfintprof +
                        "/rspathL3OutAtt-[topology/pod-" + pod + "/paths-" + node + "/pathep-[eth" + int + "]]",
                        "ifInstT": conntype,
                        "descr": desc,
                        "addr": ip + "/" + str(mask),
                        "mtu": mtu,
                        # "tDn": "topology/pod-1/paths-101/pathep-[eth1/1]",
                        # "rn": "rspathL3OutAtt-[topology/pod-1/paths-101/pathep-[eth1/1]]",
                        "status": "created"
                    },
                    "children": []
                }
            }

        elif conntype.lower() == "sub-interface":
            payload = {
                "l3extRsPathL3OutAtt": {
                    "attributes": {
                        "dn": "uni/tn-" + tn + "/out-" + l3extout + "/lnodep-" + name + "/lifp-" + ospfintprof +
                        "/rspathL3OutAtt-[topology/pod-" + pod + "/paths-" + node + "/pathep-[eth" + int + "]]",
                        "ifInstT": conntype,
                        "descr": desc,
                        "addr": ip + "/" + str(mask),
                        "mtu": mtu,
                        "encap": "vlan-" + str(encap),
                        # "tDn": "topology/pod-1/paths-101/pathep-[eth1/1]",
                        # "rn": "rspathL3OutAtt-[topology/pod-1/paths-101/pathep-[eth1/1]]",
                        "status": "created"
                    },
                    "children": []
                }
            }

        elif conntype.lower() == "ext-svi":
            payload = {
                "l3extRsPathL3OutAtt": {
                    "attributes": {
                        "dn": "uni/tn-" + tn + "/out-" + l3extout + "/lnodep-" + name + "/lifp-" + ospfintprof +
                        "/rspathL3OutAtt-[topology/pod-" + pod + "/paths-" + node + "/pathep-[eth" + int + "]]",
                        "ifInstT": conntype,
                        "descr": desc,
                        "addr": ip + "/" + str(mask),
                        "mtu": mtu,
                        "encap": "vlan-" + str(encap),
                        # mode: Valid Values "native" for 802.1P, "untagged" for Access, "regular" for Trunk
                        "mode": mode,
                        # "tDn": "topology/pod-1/paths-101/pathep-[eth1/1]",
                        # "rn": "rspathL3OutAtt-[topology/pod-1/paths-101/pathep-[eth1/1]]",
                        "status": "created"
                    },
                    "children": []
                }
            }

        else:
            print(
                "ERROR in Routed Interface function connection type. Valid types are 'l3-port', 'sub-interface', 'ext-svi'.")
            sys.exit('Aborting program Execution')

    else:

        payload = {
            "l3extRsPathL3OutAtt": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/out-" + l3extout + "/lnodep-" + name + "/lifp-" + ospfintprof +
                          "/rspathL3OutAtt-[topology/pod-" + pod + "/paths-" + node + "/pathep-[eth" + int + "]]",
                    # "mac": "00:22:BD:F8:19:FF",
                    # "ifInstT": "l3-port",
                    # "descr": desc,
                    # "addr": + ip.strip() + "/" + mask.strip(),
                    # "mtu": mtu,
                    # # "tDn": "topology/pod-1/paths-101/pathep-[eth1/1]",
                    # # "rn": "rspathL3OutAtt-[topology/pod-1/paths-101/pathep-[eth1/1]]",
                    "status": "deleted"
                },
                "children": []
            }
        }
    return payload



def l3epg_payload(name, desc, tn, l3extout, extip, extipmask, status):

    if not status:
        payload = {

            "l3extInstP": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/out-" + l3extout + "/instP-" + name,
                    "name": name,
                    "descr": desc,
                    "rn": "instP-ExtL3Out-Networks-EPG",
                    "status": "created"
                },
                "children": [{
                    "l3extSubnet": {
                        "attributes": {
                            "dn": "uni/tn-" + tn + "/out-" + l3extout + "/instP-" + name +
                                  "/extsubnet-[" + extip + "/" + extipmask + "]",
                            "ip": extip + "/" + str(extipmask),
                            "aggregate": "",
                            #"rn": "extsubnet-[0.0.0.0/0]",
                            "status": "created"
                        },
                        "children": []
                    }
                }]
            }

        }

    else:
        payload = {

            "l3extInstP": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/out-" + l3extout + "/instP-" + name,
                    "name": name,
                    "descr": desc,
                    "rn": "instP-ExtL3Out-Networks-EPG",
                    "status": "deleted"
                },
            }

        }
    return payload


def epgsubnet_payload(tn,l3out,l3epg,extip, extmask, scope, status):

    if not status:
        payload = {
            "l3extSubnet": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/out-" + l3out + "/instP-" + l3epg + "/extsubnet-[" + extip + "/" + extmask + "]",
                    "ip": extip + "/" + extmask,
                    # Valid Values =  export-rtctrl, import-security
                    "scope": scope,
                    "aggregate": "",
                    #"rn": "extsubnet-[10.150.0.192/29]",
                    "status": "created"
                },
            }
        }
    else:
        payload = {
            "l3extSubnet": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/out-" + l3out + "/instP-" + l3epg + "/extsubnet-[" + extip + "/" + extmask + "]",
                    "status": "deleted"
                },
            }
        }
    return payload



def iproutep_payload(tn, l3out, l3nodeprof, node, extip, extmask, pod, status):

    if not status:
        payload = {
            "ipRouteP": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/out-" + l3out + "/lnodep-" + l3nodeprof + "/rsnodeL3OutAtt-[topology/pod-" + pod + "/node-" + node + "]/rt-[" + extip + "/" + extmask + "]",
                    "ip": extip + "/" + extmask,
                    #"rn": "rt-[10.150.27.0/24]",
                    "status": "created"
                },
            }
        }
    else:
        payload = {
            "ipRouteP": {
                "attributes": {
                    "dn": "uni/tn-" + tn + "/out-" + l3out + "/lnodep-" + "/rsnodeL3OutAtt-[topology/pod-" + pod + "/node-" + node + "]/rt-[" + extip + "/" + extmask + "]",
                    "status": "deleted"
                },
            }
        }
    return payload

def ipnexthopp_payload(tn, l3out, l3nodeprof, node, extip, extmask, nexthop, pod, status):

    if not status:
        payload = {
            "ipNexthopP": {
                "attributes": {
                    # "dn": "uni/tn-common/out-LBS_RoutedOut/lnodep-LBS_RoutedOut_NodeProf/
                    # rsnodeL3OutAtt-[topology/pod-1/node-201]/rt-[10.150.27.0/24]/nh-[10.150.0.196]",
                    "dn": "uni/tn-" + tn + "/out-" + l3out + "/lnodep-" + l3nodeprof +
                          "/rsnodeL3OutAtt-[topology/pod-" + pod + "/node-" + node + "]/rt-[" + extip + "/" + extmask + "]/nh-[" + nexthop + "]",
                    "nhAddr": nexthop,
                    #"rn": "nh-[10.150.0.196]",
                    "status": "created"
                },
            }
        }
    else:
        payload = {

        }
    return payload


def hardcoded_payload( status ):

    if not status:
        payload = {
            "l3extOut": {
                "attributes": {
                    "dn": "uni/tn-common/out-NSX_Edge_RoutedOut",
                    "name": "NSX_Edge_RoutedOut",
                    "rn": "out-NSX_Edge_RoutedOut",
                    "status": "created"
                },
                "children": [{
                    "l3extLNodeP": {
                        "attributes": {
                            "dn": "uni/tn-common/out-NSX_Edge_RoutedOut/lnodep-NSX_Edge_RoutedOut-NodeProfile",
                            "name": "NSX_Edge_RoutedOut-NodeProfile",
                            "rn": "lnodep-NSX_Edge_RoutedOut-NodeProfile",
                            "status": "created"
                        },
                        "children": [{
                            "l3extLIfP": {
                                "attributes": {
                                    "dn": "uni/tn-common/out-NSX_Edge_RoutedOut/lnodep-NSX_Edge_RoutedOut-NodeProfile/lifp-NSX_Edge_RoutedOut-IntProf01",
                                    "name": "NSX_Edge_RoutedOut-IntProf01",
                                    "rn": "lifp-NSX_Edge_RoutedOut-IntProf01",
                                    "status": "created"
                                },
                                "children": [{
                                    "ospfIfP": {
                                        "attributes": {
                                            "dn": "uni/tn-common/out-NSX_Edge_RoutedOut/lnodep-NSX_Edge_RoutedOut-NodeProfile/lifp-NSX_Edge_RoutedOut-IntProf01/ospfIfP",
                                            "rn": "ospfIfP",
                                            "status": "created"
                                        },
                                        "children": []
                                    }
                                },
                                    {
                                        "l3extRsPathL3OutAtt": {
                                            "attributes": {
                                                "dn": "uni/tn-common/out-NSX_Edge_RoutedOut/lnodep-NSX_Edge_RoutedOut-NodeProfile/lifp-NSX_Edge_RoutedOut-IntProf01/rspathL3OutAtt-[topology/pod-1/paths-201/pathep-[eth1/25]]",
                                                "mac": "00:22:BD:F8:19:FF",
                                                "ifInstT": "ext-svi",
                                                "encap": "vlan-2012",
                                                "addr": "10.140.12.1/28",
                                                "mtu": "9000",
                                                "tDn": "topology/pod-1/paths-201/pathep-[eth1/25]",
                                                "rn": "rspathL3OutAtt-[topology/pod-1/paths-201/pathep-[eth1/25]]",
                                                "status": "created"
                                            },
                                            "children": []
                                        }
                                    },
                                    {
                                        "l3extRsPathL3OutAtt": {
                                            "attributes": {
                                                "dn": "uni/tn-common/out-NSX_Edge_RoutedOut/lnodep-NSX_Edge_RoutedOut-NodeProfile/lifp-NSX_Edge_RoutedOut-IntProf01/rspathL3OutAtt-[topology/pod-1/paths-201/pathep-[eth1/27]]",
                                                "mac": "00:22:BD:F8:20:FF",
                                                "ifInstT": "ext-svi",
                                                "encap": "vlan-2012",
                                                "addr": "10.140.12.1/28",
                                                "mtu": "9000",
                                                "tDn": "topology/pod-1/paths-201/pathep-[eth1/27]",
                                                "rn": "rspathL3OutAtt-[topology/pod-1/paths-201/pathep-[eth1/27]]",
                                                "status": "created"
                                            },
                                            "children": []
                                        }
                                    },
                                    {
                                        "l3extRsPathL3OutAtt": {
                                            "attributes": {
                                                "dn": "uni/tn-common/out-NSX_Edge_RoutedOut/lnodep-NSX_Edge_RoutedOut-NodeProfile/lifp-NSX_Edge_RoutedOut-IntProf01/rspathL3OutAtt-[topology/pod-1/paths-201/pathep-[eth1/29]]",
                                                "mac": "00:22:BD:F8:21:FF",
                                                "ifInstT": "ext-svi",
                                                "encap": "vlan-2012",
                                                "addr": "10.140.12.1/28",
                                                "mtu": "9000",
                                                "tDn": "topology/pod-1/paths-201/pathep-[eth1/29]",
                                                "rn": "rspathL3OutAtt-[topology/pod-1/paths-201/pathep-[eth1/29]]",
                                                "status": "created"
                                            },
                                            "children": []
                                        }
                                    },
                                    {
                                        "l3extRsPathL3OutAtt": {
                                            "attributes": {
                                                "dn": "uni/tn-common/out-NSX_Edge_RoutedOut/lnodep-NSX_Edge_RoutedOut-NodeProfile/lifp-NSX_Edge_RoutedOut-IntProf01/rspathL3OutAtt-[topology/pod-1/paths-201/pathep-[eth1/31]]",
                                                "mac": "00:22:BD:F8:22:FF",
                                                "ifInstT": "ext-svi",
                                                "encap": "vlan-2012",
                                                "addr": "10.140.12.1/28",
                                                "mtu": "9000",
                                                "tDn": "topology/pod-1/paths-201/pathep-[eth1/31]",
                                                "rn": "rspathL3OutAtt-[topology/pod-1/paths-201/pathep-[eth1/31]]",
                                                "status": "created"
                                            },
                                            "children": []
                                        }
                                    },
                                    {
                                        "l3extRsPathL3OutAtt": {
                                            "attributes": {
                                                "dn": "uni/tn-common/out-NSX_Edge_RoutedOut/lnodep-NSX_Edge_RoutedOut-NodeProfile/lifp-NSX_Edge_RoutedOut-IntProf01/rspathL3OutAtt-[topology/pod-1/paths-202/pathep-[eth1/25]]",
                                                "mac": "00:22:BD:F8:19:FF",
                                                "ifInstT": "ext-svi",
                                                "encap": "vlan-2013",
                                                "addr": "10.140.13.1/28",
                                                "mtu": "9000",
                                                "tDn": "topology/pod-1/paths-202/pathep-[eth1/25]",
                                                "rn": "rspathL3OutAtt-[topology/pod-1/paths-202/pathep-[eth1/25]]",
                                                "status": "created"
                                            },
                                            "children": []
                                        }
                                    },
                                    {
                                        "l3extRsPathL3OutAtt": {
                                            "attributes": {
                                                "dn": "uni/tn-common/out-NSX_Edge_RoutedOut/lnodep-NSX_Edge_RoutedOut-NodeProfile/lifp-NSX_Edge_RoutedOut-IntProf01/rspathL3OutAtt-[topology/pod-1/paths-202/pathep-[eth1/27]]",
                                                "mac": "00:22:BD:F8:20:FF",
                                                "ifInstT": "ext-svi",
                                                "encap": "vlan-2013",
                                                "addr": "10.140.13.1/28",
                                                "mtu": "9000",
                                                "tDn": "topology/pod-1/paths-202/pathep-[eth1/27]",
                                                "rn": "rspathL3OutAtt-[topology/pod-1/paths-202/pathep-[eth1/27]]",
                                                "status": "created"
                                            },
                                            "children": []
                                        }
                                    },
                                    {
                                        "l3extRsPathL3OutAtt": {
                                            "attributes": {
                                                "dn": "uni/tn-common/out-NSX_Edge_RoutedOut/lnodep-NSX_Edge_RoutedOut-NodeProfile/lifp-NSX_Edge_RoutedOut-IntProf01/rspathL3OutAtt-[topology/pod-1/paths-202/pathep-[eth1/29]]",
                                                "mac": "00:22:BD:F8:21:FF",
                                                "ifInstT": "ext-svi",
                                                "encap": "vlan-2013",
                                                "addr": "10.140.13.1/28",
                                                "mtu": "9000",
                                                "tDn": "topology/pod-1/paths-202/pathep-[eth1/29]",
                                                "rn": "rspathL3OutAtt-[topology/pod-1/paths-202/pathep-[eth1/29]]",
                                                "status": "created"
                                            },
                                            "children": []
                                        }
                                    },
                                    {
                                        "l3extRsPathL3OutAtt": {
                                            "attributes": {
                                                "dn": "uni/tn-common/out-NSX_Edge_RoutedOut/lnodep-NSX_Edge_RoutedOut-NodeProfile/lifp-NSX_Edge_RoutedOut-IntProf01/rspathL3OutAtt-[topology/pod-1/paths-202/pathep-[eth1/31]]",
                                                "mac": "00:22:BD:F8:22:FF",
                                                "ifInstT": "ext-svi",
                                                "encap": "vlan-2013",
                                                "addr": "10.140.13.1/28",
                                                "mtu": "9000",
                                                "tDn": "topology/pod-1/paths-202/pathep-[eth1/31]",
                                                "rn": "rspathL3OutAtt-[topology/pod-1/paths-202/pathep-[eth1/31]]",
                                                "status": "created"
                                            },
                                            "children": []
                                        }
                                    }]
                            }
                        },

                            {
                                "l3extRsNodeL3OutAtt": {
                                    "attributes": {
                                        "dn": "uni/tn-common/out-NSX_Edge_RoutedOut/lnodep-NSX_Edge_RoutedOut-NodeProfile/rsnodeL3OutAtt-[topology/pod-1/node-101]",
                                        "tDn": "topology/pod-1/node-101",
                                        "rtrId": "10.140.0.1",
                                        "rn": "rsnodeL3OutAtt-[topology/pod-1/node-101]",
                                        "status": "created"
                                    },
                                    "children": [{
                                        "l3extInfraNodeP": {
                                            "attributes": {
                                                "fabricExtCtrlPeering": "false",
                                                "status": "created"
                                            },
                                            "children": []
                                        }
                                    }]
                                }
                            },
                            {
                                "l3extRsNodeL3OutAtt": {
                                    "attributes": {
                                        "dn": "uni/tn-common/out-NSX_Edge_RoutedOut/lnodep-NSX_Edge_RoutedOut-NodeProfile/rsnodeL3OutAtt-[topology/pod-1/node-102]",
                                        "tDn": "topology/pod-1/node-102",
                                        "rtrId": "10.140.0.2",
                                        "rn": "rsnodeL3OutAtt-[topology/pod-1/node-102]",
                                        "status": "created"
                                    },
                                    "children": [{
                                        "l3extInfraNodeP": {
                                            "attributes": {
                                                "fabricExtCtrlPeering": "false",
                                                "status": "created"
                                            },
                                            "children": []
                                        }
                                    }]
                                }
                            }]
                    }
                },
                    {
                        "ospfExtP": {
                            "attributes": {
                                "dn": "uni/tn-common/out-NSX_Edge_RoutedOut/ospfExtP",
                                "areaId": "100",
                                "rn": "ospfExtP",
                                "status": "created"
                            },
                            "children": []
                        }
                    },
                    {
                        "l3extRsEctx": {
                            "attributes": {
                                "tnFvCtxName": "BDC-VRF-PN",
                                "status": "created,modified"
                            },
                            "children": []
                        }
                    },
                    {
                        "l3extRsL3DomAtt": {
                            "attributes": {
                                "tDn": "uni/l3dom-L3_Out-Dom",
                                "status": "created,modified"
                            },
                            "children": []
                        }
                    }]

            }
        }
    else:
        payload = {

        }
    return payload


##### MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN #####

# Provided main() calls the above functions
def main():
    """
    This script takes a CSV file (passed as the first argument) of data (aci external L3 out connectivity policy objects)
    and depending on the second argument configures/creates those objects or deletes them.

    Assumptions:  the Switch Profiles, AEP, and Interface Policies have already been created with the aci_fabric_step2b_accpol.py script
    and the exact names are referenced in the payload for this script.




    """
    # define non 200 response dictionary for items that failed to apply
    error_list = []

    # set variable filename to the CSV file passed as the first argument
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
    print("\n===========Running ACI STEP 5A: Layer 3 Constructs Tenant > Networking > External Routed Networks  ===========")
    print("===========                                  With the following options                              ===========")
    log_file.write("\n===========Running ACI STEP 5A: Layer 3 Constructs Tenant > Networking > External Routed Networks  ===========")
    log_file.write("\n===========                                 With the following options                             ===========\n")
    for key, value in args_dict.items():
        txt = '{:15} : {:10}'.format(key,str(value))
        print(txt)
        log_file.write(txt + "\n")

    if arguments.all or arguments.l3extout_ospf or arguments.l3extnodep_ospf or arguments.l3out_routedint \
            or arguments.l3epg or  arguments.epgsubnet or arguments.iproute or arguments.nexthop:
        aci_fabric_build_utilities.print_header(APIC_URL, APIC_USER, object_status_delete, log_file)
    else:
        print("\nNo executable arguments passed.  Use the -h option for help.")


    if (arguments.all or arguments.all or arguments.l3extout_ospf or arguments.l3extnodep_ospf
        or arguments.l3out_routedint or arguments.l3epg or  arguments.epgsubnet or arguments.iproute
        or arguments.nexthop) and arguments.xdelete:
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

    #####  EXTERNAL L3 ROUTED OUT #####


    # Create Main L3 Out OSPF
    # Tenant > Networking > External Routed Out
    # key: l3extout_ospf
    if arguments.all or arguments.l3extout_ospf:
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'l3extout_ospf')

        for line in data:
            # l3extout_ospf_payload(name, desc, tn, area, areatype, vrf, l3outdom, status):
            payload = l3extout_ospf_payload(line['name'], line['desc'], line['tn'], line['area'], line['areatype'],
                                        line['vrf'], line['l3outdom'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(action_text + " L3 Routed Out ", resp, line['name'],
                                                             log_file, error_list)




    # Create L3 Out Node Profile OSPF
    # Tenant > Networking > External Routed Out
    # key: l3extnodep_ospf

    if arguments.all or arguments.l3extnodep_ospf:
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'l3extnodep_ospf')

        for line in data:
            # l3extnodep_ospf_payload(name, desc, tn, l3extout, ospfintprof, rtrid1, rtrid2, node1, node2, rtrlo, status):
            payload = l3extnodep_ospf_payload(line['name'], line['desc'], line['tn'], line['l3extout'], line['ospfintprof'],
                                              line['rtrid1'], line['rtrid2'], line['node1'], line['node2'], line['rtrlo'],
                                              line['pod'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(action_text + " L3 Routed Out Node Profile ", resp,
                                                             line['name'], log_file, error_list)


    # Create L3 Out Node Routed Interface
    # Tenant > Networking > External Routed Out
    # key: l3out_routedint

    if arguments.all or arguments.l3out_routedint:
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'l3out_routedint')
        l3_details = ''
        for line in data:
            # l3out_routedint_payload(name, desc, tn, l3extout, ospfintprof, node, int, mtu, ip, mask, conntypes, mode, encap, status): Warren
            # l3out_routedint_payload(name, desc, tn, l3extout, ospfintprof, node, int, mtu, ip, mask, conntype, mode, encap, status): cdl
            payload = l3out_routedint_payload(line['name'], line['desc'], line['tn'], line['l3extout'],
                                              line['ospfintprof'], line['node'], line['int'], line['mtu'],
                                              line['ip'], line['mask'], line['conntype'], line['mode'], line['encap'],
                                              line['pod'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            if line['conntype'].strip() == 'l3-port':
                l3_details =  "{}: Connection Type is L3 Routed Interface with ip {}/{} using profile {} " \
                              "and L3 Out {} ".format(line['name'], line['ip'], line['mask'], line['ospfintprof'],
                                                      line['l3extout'])
            elif line['conntype'].strip() == 'sub-interface':
                l3_details =  "{}: Connection Type is L3 Routed Sub-Interface with ip {}/{} using profile {} " \
                              "and L3 Out {} ".format(line['name'], line['ip'], line['mask'], line['ospfintprof'],
                                                      line['l3extout'])
            elif line['conntype'].strip() == 'ext-svi':
                l3_details =  "{}: Connection Type is L3 SVI with ip {}/{} using profile {}, L3 Out {}, L2 mode {}, " \
                              "and encapsulation {} ".format(line['name'], line['ip'], line['mask'],
                                                             line['ospfintprof'], line['l3extout'], line['mode'],
                                                             line['encap'])
            else:
                print("ERROR!: Invalid L3 Out Connection Type! Value is {}. Valid values are l3-port | sub-interface | "
                      "ext-svi.".format(str(line['conntype'])))
            		
            aci_fabric_build_utilities.print_post_result_log(action_text + " L3 Routed Out - Details: ",
                                                             resp, l3_details, log_file, error_list)


    # Create L3 Out Node Network EPG
    # Tenant > Networking > External Routed Out
    # key: l3epg

    if arguments.all or arguments.l3epg:
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'l3epg')

        for line in data:
            # l3epg_payload(name, desc, tn, l3extout, extip, extipmask, status)
            payload = l3epg_payload(line['name'], line['desc'], line['tn'], line['l3extout'], line['extip'],
                                              line['extipmask'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(action_text + " L3 Out Node Network EPG ", resp,
                                                             line['name'], log_file, error_list)




    if arguments.all or arguments.epgsubnet:
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'epgsubnet')

        for line in data:
            #epgsubnet_payload(tn, l3out, l3epg, extip, extmask, scope, status)
            payload = epgsubnet_payload(line['tn'], line['l3out'], line['l3epg'], line['extip'], line['extmask'],
                                        line['scope'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(action_text + " L3 EPG Subnet", resp,
                                                             line['extip'], log_file, error_list)

    if arguments.all or arguments.iproute:
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'iproutep')

        for line in data:
            # iproutep_payload(tn, l3out, l3nodeprof, node, extip, extmask, status)
            payload = iproutep_payload(line['tn'], line['l3out'], line['l3nodeprof'], str(line['node']), line['extip'],
                                        line['extmask'], line['pod'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(action_text + " L3 IP Static route", resp,
                                                             line['extip'], log_file, error_list)

    if arguments.all or arguments.nexthop:
        data = aci_fabric_build_utilities.pluck_payload(json_payload, 'ipnexthopp')

        for line in data:
            #ipnexthopp_payload(tn, l3out, l3nodeprof, node, extip, extmask, nexthop, status)
            payload = ipnexthopp_payload(line['tn'], line['l3out'], line['l3nodeprof'], str(line['node']),
                                       line['extip'], line['extmask'],
                                       line['nexthop'], line['pod'], object_status_delete)

            resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies, verify=False)
            # print_debug_data(resp)
            aci_fabric_build_utilities.print_post_result_log(action_text + " L3 IP Static route Next Hop", resp,
                                                             line['extip'], log_file, error_list)


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

    parser = argparse.ArgumentParser(description="ACI External L3 Out Connectivity Policies",
                                     epilog="Usage: aci_fabric-step5a_l3pol.py 'my_payload.csv' -a                 \n\r"
                                            "Typical Usage: python aci_fabric_step5a_l3pol.py step5a.csv -3 -4 -5 -6" )

    parser.add_argument('payload_file', help='Name of the payload file to use in this script.')

    parser.add_argument('-x', '--xdelete',
                        help='True to remove/delete/reset configuration and False to create (default) action unless -x is used',
                        action='store_true', default=False)

    parser.add_argument('-a', '--all', help='Execute all object CRUD sections. Without this argument nothing will execute.',
                        action='store_true', default=False)

    parser.add_argument('-3', '--l3extout_ospf', help='Execute External Routed L3 Out OSPF function',
                        action='store_true', default=False)

    parser.add_argument('-4', '--l3extnodep_ospf', help='Execute External Routed L3 Out OSPF Node Profile function',
                        action='store_true', default=False)

    parser.add_argument('-5', '--l3out_routedint', help='Execute External Routed L3 Out Routed Interface function',
                        action='store_true', default=False)

    parser.add_argument('-6', '--l3epg', help='Execute External Routed L3 Out Network EPG function',
                        action='store_true', default=False)

    parser.add_argument('-e', '--epgsubnet', help='Execute EPG Subnet function', action='store_true', default=False)

    parser.add_argument('-r', '--iproute', help='Execute IP Static Route function', action='store_true', default=False)

    parser.add_argument('-n', '--nexthop', help='Execute Next Hop function', action='store_true', default=False)

    parser.add_argument('-f', '--filename', help='Option used to pass a credentials file other than the default "credentias.py"',
                        default='credentials.py')

    arguments = parser.parse_args()

    main()




