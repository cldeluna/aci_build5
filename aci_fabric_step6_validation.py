#!/usr/bin/python -tt
# Project: python
# Filename: aic_fabric_step6_validation.py
# claud
# PyCharm

from __future__ import absolute_import, division, print_function

__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "9/9/2017"
__copyright__ = "Copyright (c) 2016 Claudia"
__license__ = "Python"

import sys
import json
import requests
import time
import argparse
import load_apic_credentials
import aci_fabric_build_utilities
import os
import transcript

requests.packages.urllib3.disable_warnings()

#Add support for all cipher suites
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS='ALL'
#Exclude use of pyopenssl (pyopenssl module may need to be installed first $pip install pyopenssl)
# requests.packages.urllib3.contrib.pyopenssl.extract_from_urllib3()


def get_query(get_key):
    get_query = {}
    get_query['tenant'] = '?query-target=subtree&target-subtree-class=fvTenant'
    get_query['aep'] = '/api/node/mo/uni/infra.json?query-target=subtree&target-subtree-class=infraAttEntityP'
    get_query['fault'] = '?query-target=subtree&target-subtree-class=faultInst'
    get_query['bgp_rr'] = '/api/node/mo/uni/fabric/bgpInstP-default/rr.json?query-target=subtree&target-subtree-class=bgpRRNodePEp'
    get_query['bd'] = '?query-target=subtree&target-subtree-class=fvBD'

    #GET URL: http://APIC-IP/api/mo/uni/tn-TENANT_NAME.json?query-target=subtree&target-subtree-class=fvCtx
    get_query['vrf'] = '?query-target=subtree&target-subtree-class=fvCtx'

    # http://APIC-IP/api/node/mo/uni.json?query-target=subtree&target-subtree-class=physDomP
    get_query['phydom'] = '?query-target=subtree&target-subtree-class=physDomP'

    #http://APIC-IP/api/node/mo/uni/infra.json?query-target=subtree&target-subtree-class=fvnsVlanInstP
    get_query['vlan_pool'] = '/api/node/mo/uni/infra.json?query-target=subtree&target-subtree-class=fvnsVlanInstP'

    #GET URL: http://APIC-IP/api/mo/uni/tn-TENANT_NAME.json?query-target=subtree&target-subtree-class=fvAEPg
    get_query['epg'] = '?query-target=subtree&target-subtree-class=fvAEPg'

    #GET URL: http://APIC-IP/api/mo/uni/tn-TENANT_NAME.json?query-target=subtree&target-subtree-class=vzBrCP
    get_query['contract'] = '?query-target=subtree&target-subtree-class=vzBrCP'

    # GET URL: http://APIC-IP/api/mo/uni/tn-TENANT_NAME.json?query-target=subtree&target-subtree-class=vzFilter
    get_query['filter'] = '?query-target=subtree&target-subtree-class=vzFilter'

    #GET URL: http://APIC-IP/api/mo/uni/tn-TENANT_NAME.json?query-target=subtree&target-subtree-class=l3extOut
    get_query['l3out'] = '?query-target=subtree&target-subtree-class=l3extOut'

    # GET URL: http://APIC-IP/api/node/mo/uni/fabric/funcprof.json?query-target=subtree&target-subtree-class=fabricPodPGrp
    get_query['fab_podpol'] = '/api/node/mo/uni/fabric/funcprof.json?query-target=subtree&target-subtree-class=fabricPodPGrp'

    # Helath core for a tenant
    # https://hostname/api/node/mo/uni/tn-TENANT_NAME.json?query-target=self&rsp-subtreeinclude=health

    # Statistics for a tenant
    # https://hostname/api/node/mo/uni/tn-TENANT_NAME.json?query-target=self&rsp-subtreeinclude=stats

    # Faults for a leaf node
    # https://hostname/api/node/mo/topology/pod-1/node-103.xml?query-target=self&rspsubtree-include=faults

    # Overall health of the fabric
    # REST :: https://172.16.96.2/api/node/class/fabricHealthTotal.json
    get_query['health_all'] = '/api/node/class/fabricHealthTotal.json'

    # List of all the devices within the fabric
    # REST :: https://172.16.96.2/api/node/class/topSystem.json
    # https://172.16.96.2/api/node/class/fabricNode.json
    get_query['topSystem'] = '/api/node/class/topSystem.json'
    get_query['fabricNode'] = '/api/node/class/fabricNode.json'


    # Description: A client endpoint attaching to the network.
    # Usage: The fvCEp class can be used to derive a list of end points attached to the fabric and the associated
    # ip/mac address and encapsulation for each object.
    #fvCEp REST :: https://172.16.96.2/api/node/class/fvCEp.json


    return get_query[get_key]

def get_tenants(post_url, cookies):

    t_list = []
    tenantQuery = get_query('tenant')

    response = requests.get(post_url + tenantQuery, cookies=cookies, verify=False).json()['imdata']
    # print(response)
    # print(str(len(response)))
    # print(type(response))

    for line in response:
        # print(line)
        # print(str(len(line)))
        # print(type(line))

        # print(line['fvTenant']['attributes']['name'])
        t_list.append(line['fvTenant']['attributes']['name'])

    return t_list

def get_tenant_based_query(url,cookies,query_txt,arg,obj_class):

    ##### CONTRACTS #####
    # GET URL: http://APIC-IP/api/mo/uni/tn-TENANT_NAME.json?query-target=subtree&target-subtree-class=vzBrCP

    #    post_url = APIC_URL + '/api/node/mo/uni.json'
    p_url = url + '/api/node/mo/uni.json'
    tn_list = []
    obj_dict = {}
    obj_listofdict = []
    objQuery = get_query(query_txt)
    if arg:
        if arg.upper() == 'ALL':
            tn_list = get_tenants(p_url, cookies)
        else:
            tn_list.append(arg.strip())
    else:
        tn_list = get_tenants(p_url, cookies)

    for tn in tn_list:
        print(tn)
        obj_list = []
        obj_dict = {}
        get_url = url + '/api/mo/uni/tn-' + tn.strip() + '.json'
        response = requests.get(get_url + objQuery, cookies=cookies, verify=False).json()['imdata']

        for line in response:
            obj_list.append(line[obj_class]['attributes']['name'])

        #print("obj_list = ".format(obj_list))
        obj_dict[tn] = obj_list

        obj_listofdict.append(obj_dict[tn])
        print(obj_listofdict)

    return obj_dict


def get_custom_query(url,cookies,query_txt):

    ##### CUSTOM QUERY #####
    counter  = 0
    response = requests.get(url + query_txt.strip(), cookies=cookies, verify=False).json()['imdata']
    print('====CUSTOM QUERY {} ====\n'.format(query_txt))
    split_query = query_txt.split('/')
    sq = split_query[-1]
    if "=" in sq:
        oc = sq.split('=')
        obj_class = oc[-1]
    elif "." in sq:
        oc = sq.split('.')
        obj_class = oc[0]
    else:
        obj_class = sq
    print("Split = {}".format(split_query))
    print(sq)
    print(obj_class)
    #
    print(response)
    print(str(len(response)))
    print(type(response))
    #
    for line in response:
        counter += 1
        print('-'*len(line[obj_class]['attributes']['dn']))
        print(line[obj_class]['attributes']['dn'])
        for k,v in (line[obj_class]['attributes']).iteritems():
            print("\t{}. {:33s} ==> \t {:<36}".format(counter,k.strip(),v.strip()))
    # #
    # # print("\nTotal Fabric Topology Health {} = {}".format(response[0]['fabricHealthTotal']['attributes']['dn'],response[0]['fabricHealthTotal']['attributes']['cur']))
    # # print("\nTotal Fabric Pod Health {} = {}".format(response[1]['fabricHealthTotal']['attributes']['dn'],response[1]['fabricHealthTotal']['attributes']['cur']))
    #
    print("\nTotal Items in Response = {}".format(counter))



def main():
    """
    This script will query an APIC for objects

    - Fabric Health
    - Fabric Devices
    - Tenants
    - VRFs
    - Bridge Domains
    - ANPs
    - EPGS
    - Contracts
    - Fabric Policies
    - Fabric Access Policies
    - Faults

    """

    # set variable filename to the json file passed as the first argument
    filename = arguments.project

    # Set to "True" to delete the objects defined in this script on the APIC by passing -x
    # default is "False"
    object_status_delete = False

    action_text = "Verification and QA"

    start_time = time.time()

    # Create a Log file for configuration session
    filename_base = filename
    timestr = time.strftime("%Y%m%d-%H%M%S")
    log_filename = filename_base + "-" + action_text.upper() + "-" + timestr + ".log"
    log_file = open(log_filename, 'w')

    # Create Directory for show output based on the Project Name
    path = os.path.join("./", arguments.project.strip())
    #print path
    if not os.path.exists(path):
        os.makedirs(path)
        print("Created directory: " + path)

    # Create logfile for the discovery run in same directory as the resulting show commands
    logfilename = arguments.project.strip() + "-logfile.log"
    logfilename = os.path.join(path, logfilename)
    transcript.start(logfilename)

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
    print("\n===========Running ACI STEP 6: Verification Script===========")
    print("===========      With the following options       ===========")
    log_file.write("\n===========Running ACI STEP 6:  Verification Script===========")
    log_file.write("\n===========       With the following option       ===========\n")
    for key, value in args_dict.items():
        txt = '{:15} : {:10}'.format(key,str(value))
        print(txt)
        log_file.write(txt + "\n")

    if arguments.all or arguments.tenants  or arguments.faults or arguments.aeps or arguments.bds or arguments.phydoms \
            or arguments.vlan_pools or arguments.network_vrf or arguments.epgs or arguments.contracts \
            or arguments.filters or arguments.fab_podpol or arguments.l3out or arguments.health_all\
            or arguments.nodes or arguments.custom:
        aci_fabric_build_utilities.print_qa_header(APIC_URL, APIC_USER, object_status_delete, log_file)

    else:
        print("\nNo executable arguments passed.  Use the -h option for help.")

    ##################################################################################################################

    ##### FABRIC #####

    ##### Fabric Nodes #####
    if arguments.all or arguments.nodes:
        counter  = 0
        response = requests.get(APIC_URL + get_query('topSystem'), cookies=cookies, verify=False).json()['imdata']
        print('====FABRIC DOMAIN {} ====\n'.format((response[0]['topSystem']['attributes']['fabricDomain'])))
        print('\n----FABRIC NODES----\n')
        # print(response)
        # print(str(len(response)))
        # print(type(response))
        #
        # print(str(len(response[0]['fabricHealthTotal']['attributes'])))
        # print((response[0]['fabricHealthTotal']['attributes']))

        for line in response:
            counter += 1
            print('-'*len(line['topSystem']['attributes']['name']))
            print(line['topSystem']['attributes']['name'])
            for k,v in (line['topSystem']['attributes']).items():
                print("\t{}. {:33s} ==> \t {:<36}".format(counter,k.strip(),v.strip()))
        #
        # print("\nTotal Fabric Topology Health {} = {}".format(response[0]['fabricHealthTotal']['attributes']['dn'],response[0]['fabricHealthTotal']['attributes']['cur']))
        # print("\nTotal Fabric Pod Health {} = {}".format(response[1]['fabricHealthTotal']['attributes']['dn'],response[1]['fabricHealthTotal']['attributes']['cur']))

        print("\nTotal Devices in Fabric = {}".format(counter))

        response = requests.get(APIC_URL + get_query('fabricNode'), cookies=cookies, verify=False).json()['imdata']
        # print(response)
        # print(str(len(response)))
        # print(type(response))



    ##### TOTAL FABRIC HEALTH #####

    if arguments.all or arguments.health_all:
        print('\n----TOTAL FABRIC HEALTH----\n')
        counter  = 0
        response = requests.get(APIC_URL + get_query('health_all'), cookies=cookies, verify=False).json()['imdata']
        # print(response)
        # print(str(len(response)))
        # print(type(response))
        #
        # print(str(len(response[0]['fabricHealthTotal']['attributes'])))
        # print((response[0]['fabricHealthTotal']['attributes']))

        for line in response:
            counter += 1
            print('-'*len(line['fabricHealthTotal']['attributes']['cur']))
            print(line['fabricHealthTotal']['attributes']['cur'])
            for k,v in (line['fabricHealthTotal']['attributes']).items():
                print("\t{}. {:33s} ==> \t {:<36}".format(counter, k.strip(), v.strip()))

        print("\nTotal Fabric Topology Health {} = {}".format(response[0]['fabricHealthTotal']['attributes']['dn'],response[0]['fabricHealthTotal']['attributes']['cur']))
        print("\nTotal Fabric Pod Health {} = {}".format(response[1]['fabricHealthTotal']['attributes']['dn'],response[1]['fabricHealthTotal']['attributes']['cur']))


    ##### AEP #####

    if arguments.all or arguments.aeps:
        print('\n----AEPs----\n')
        counter  = 0
        response = requests.get(APIC_URL + get_query('aep'), cookies=cookies, verify=False).json()['imdata']
        # print(f"response: \n {response}\n")
        # print(f"response length: {str(len(response))}\n")
        # print(f"response type: {type(response)}\n")

        #
        # print(str(len(response[0]['infraAttEntityP']['attributes'])))
        # print((response[0]['infraAttEntityP']['attributes']))

        for line in response:
            # print(line)
            # print(str(len(line)))
            # print(type(line))
            counter += 1

            # 13 items int the attributes dictionary
            #print(str(len(line['infraAttEntityP']['attributes'])))

            #print('\t' + '-'*len(line['infraAttEntityP']['attributes']['name']))
            print('\t' + line['infraAttEntityP']['attributes']['name'])
            # for k,v in (line['infraAttEntityP']['attributes']).iteritems():
            #     print("\t{}. {:33s} ==> \t {:<36}".format(counter,k.strip(),v.strip()))

        print("\nTotal AEPs in Fabric = {}".format(counter))


    ##### Physical Domains #####

    if arguments.all or arguments.phydoms:
        obj_list = []
        objQuery = get_query('phydom')

        response = requests.get(post_url + objQuery, cookies=cookies, verify=False).json()['imdata']
        # print(response)
        # print(str(len(response)))
        # print(type(response))

        for line in response:
            # print(line)
            # print(str(len(line)))
            # print(type(line))

            #print(line['fvTenant']['attributes']['name'])
            obj_list.append(line['physDomP']['attributes']['name'])

        print('\n----PHYSICAL DOMAINS----\n')
        for o in obj_list:
            print("\t{}".format(o))
        print('\nTotal Physical Domains in Fabric = {}'.format(len(obj_list)))


    ##### VLAN Pools #####

    if arguments.all or arguments.vlan_pools:
        print('\n----VLAN POOLS----\n')
        counter  = 0
        response = requests.get(APIC_URL + get_query('vlan_pool'), cookies=cookies, verify=False).json()['imdata']
        # print(response)
        # print(str(len(response)))
        # print(type(response))
        #
        # print(str(len(response[0]['infraAttEntityP']['attributes'])))
        # print((response[0]['infraAttEntityP']['attributes']))

        for line in response:
            # print(line)
            # print(str(len(line)))
            # print(type(line))
            counter += 1

            # 13 items int the attributes dictionary
            #print(str(len(line['infraAttEntityP']['attributes'])))

            #print('-'*len(line['fvnsVlanInstP']['attributes']['name']))
            print("Vlan Pool: {} \t Allocation Mode: {}".format(line['fvnsVlanInstP']['attributes']['name'],
                                                                line['fvnsVlanInstP']['attributes']['allocMode']))

            # for k,v in (line['fvnsVlanInstP']['attributes']).iteritems():
            #     print("\t{}. {:33s} ==> \t {:<36}".format(counter,k.strip(),v.strip()))

        print("\nTotal Vlan Pools in Fabric = {}".format(counter))

    ##### FABRIC POD POLICY GROUP #####

    if arguments.all or arguments.fab_podpol:
        print('\n----FABRIC POD POLICY GROUP----\n')
        counter  = 0
        response = requests.get(APIC_URL + get_query('fab_podpol'), cookies=cookies, verify=False).json()['imdata']
        # print(response)
        # print(str(len(response)))
        # print(type(response))
        #
        # print(str(len(response[0]['infraAttEntityP']['attributes'])))
        # print((response[0]['infraAttEntityP']['attributes']))

        for line in response:
            # print(line)
            # print(str(len(line)))
            # print(type(line))
            counter += 1

            # 13 items int the attributes dictionary
            #print(str(len(line['infraAttEntityP']['attributes'])))

            #print('-'*len(line['fvnsVlanInstP']['attributes']['name']))
            print("Fabric Pod Policy Group: {}".format(line['fabricPodPGrp']['attributes']['name']))
            #print(line['fabricPodPGrp']['attributes'])

            # for k,v in (line['fvnsVlanInstP']['attributes']).iteritems():
            #     print("\t{}. {:33s} ==> \t {:<36}".format(counter,k.strip(),v.strip()))

        print("\nTotal Fabric Pod Policy Group = {}".format(counter))



    ##### Tenants #####

    if arguments.all or arguments.tenants:
        tenant_list = get_tenants(post_url, cookies)
        print(tenant_list)

        print('\n----TENANTS----\n')
        for t in tenant_list:
            print("\t{}".format(t))
        print('\nTotal Tenants = {}'.format(len(tenant_list)))


    ##### Bridge Domains #####
    #http://APIC-IP/api/mo/uni/tn-TENANT_NAME.json?query-target=subtree&target-subtree-class=fvBD

    if arguments.all or arguments.bds:
        tn_list = []
        objQuery = get_query('bd')
        if arguments.bds:
            if arguments.bds.upper() == 'ALL':
                tn_list = get_tenants(post_url, cookies)
            else:
                tn_list.append(arguments.bds.strip())
        else:
            tn_list = get_tenants(post_url, cookies)

        for tn in tn_list:
            bd_list = []
            get_url = APIC_URL + '/api/mo/uni/tn-' + tn.strip() + '.json'
            response = requests.get(get_url + objQuery, cookies=cookies, verify=False).json()['imdata']
            print(f"response: \n {response}\n")
            print(f"response length: {str(len(response))}\n")
            print(f"response type: {type(response)}\n")

            for line in response:
                # print(line)
                # print(str(len(line)))
                # print(type(line))

                #print(line['fvBD']['attributes']['name'])
                bd_list.append(line['fvBD']['attributes']['name'])

            print('\n----BRIDGE DOMAINS for TENANT {}----\n'.format(tn))
            for t in bd_list:
                print("\t{}".format(t))
            print('\nTotal Bridge Domains for Tenant {} = {}'.format(tn,len(bd_list)))

    ##### VRFs #####
    # GET URL: http://APIC-IP/api/mo/uni/tn-TENANT_NAME.json?query-target=subtree&target-subtree-class=fvCtx

    if arguments.all or arguments.network_vrf:
        tn_list = []
        objQuery = get_query('vrf')
        if arguments.network_vrf:
            if arguments.network_vrf.upper() == 'ALL':
                tn_list = get_tenants(post_url, cookies)
            else:
                tn_list.append(arguments.network_vrf.strip())
        else:
            tn_list = get_tenants(post_url, cookies)

        for tn in tn_list:
            vrf_list = []
            get_url = APIC_URL + '/api/mo/uni/tn-' + tn.strip() + '.json'
            response = requests.get(get_url + objQuery, cookies=cookies, verify=False).json()['imdata']
            # print(response)
            # print(str(len(response)))
            # print(type(response))

            for line in response:
                # print(line)
                # print(str(len(line)))
                # print(type(line))

                # print(line['fvBD']['attributes']['name'])
                vrf_list.append(line['fvCtx']['attributes']['name'])

            print('\n----VRFs for TENANT {}----\n'.format(tn))
            for v in vrf_list:
                print("\t{}".format(v))
            print('\nTotal VRFs for Tenant {} = {}'.format(tn, len(vrf_list)))

    ##### EPGs #####
    # GET URL: http://APIC-IP/api/mo/uni/tn-TENANT_NAME.json?query-target=subtree&target-subtree-class=fvAEPg

    if arguments.all or arguments.epgs:
        tn_list = []
        objQuery = get_query('epg')
        if arguments.epgs:
            if arguments.epgs.upper() == 'ALL':
                tn_list = get_tenants(post_url, cookies)
            else:
                tn_list.append(arguments.epgs.strip())
        else:
            tn_list = get_tenants(post_url, cookies)

        for tn in tn_list:
            epg_list = []
            get_url = APIC_URL + '/api/mo/uni/tn-' + tn.strip() + '.json'
            response = requests.get(get_url + objQuery, cookies=cookies, verify=False).json()['imdata']
            # print(response)
            # print(str(len(response)))
            # print(type(response))

            for line in response:
                # print(line)
                # print(str(len(line)))
                # print(type(line))

                # print(line['fvBD']['attributes']['name'])
                epg_list.append(line['fvAEPg']['attributes']['name'])

            print('\n----EPGs for TENANT {}----\n'.format(tn))
            for e in epg_list:
                print("\t{}".format(e))
            print('\nTotal EPGs for Tenant {} = {}'.format(tn, len(epg_list)))

    ##### CONTRACTS #####
    # GET URL: http://APIC-IP/api/mo/uni/tn-TENANT_NAME.json?query-target=subtree&target-subtree-class=vzBrCP

    if arguments.all or arguments.contracts:
        tn_list = []
        objQuery = get_query('contract')
        if arguments.contracts:
            if arguments.contracts.upper() == 'ALL':
                tn_list = get_tenants(post_url, cookies)
            else:
                tn_list.append(arguments.contracts.strip())
        else:
            tn_list = get_tenants(post_url, cookies)

        for tn in tn_list:
            contract_list = []
            get_url = APIC_URL + '/api/mo/uni/tn-' + tn.strip() + '.json'
            response = requests.get(get_url + objQuery, cookies=cookies, verify=False).json()['imdata']

            for line in response:
                contract_list.append(line['vzBrCP']['attributes']['name'])

            print('\n----CONTRACTs for TENANT {}----\n'.format(tn))
            for c in contract_list:
                print("\t{}".format(c))
            print('\nTotal Contracts for Tenant {} = {}'.format(tn, len(contract_list)))


    #get_tenant_based_query(post_url, cookies,query_txt,arg,obj_class)

    ##### FILTERS #####
    # GET URL: http://APIC-IP/api/mo/uni/tn-TENANT_NAME.json?query-target=subtree&target-subtree-class=vzFilter

    if arguments.all or arguments.filters:
        tn_list = []
        objQuery = get_query('filter')
        if arguments.filters:
            if arguments.filters.upper() == 'ALL':
                tn_list = get_tenants(post_url, cookies)
            else:
                tn_list.append(arguments.filters.strip())
        else:
            tn_list = get_tenants(post_url, cookies)

        for tn in tn_list:
            object_list = []
            get_url = APIC_URL + '/api/mo/uni/tn-' + tn.strip() + '.json'
            response = requests.get(get_url + objQuery, cookies=cookies, verify=False).json()['imdata']

            for line in response:
                object_list.append(line['vzFilter']['attributes']['name'])

            print('\n----FILTERSs for TENANT {}----\n'.format(tn))
            for o in object_list:
                print("\t{}".format(o))
            print('\nTotal Filters for Tenant {} = {}'.format(tn, len(object_list)))




    ##### L3 Out #####
    # GET URL: http://APIC-IP/api/mo/uni/tn-TENANT_NAME.json?query-target=subtree&target-subtree-class=l3extOut

    if arguments.all or arguments.l3out:
        tn_list = []
        objQuery = get_query('l3out')
        if arguments.contracts:
            if arguments.l3out.upper() == 'ALL':
                tn_list = get_tenants(post_url, cookies)
            else:
                tn_list.append(arguments.l3out.strip())
        else:
            tn_list = get_tenants(post_url, cookies)

        for tn in tn_list:
            l3out_list = []
            get_url = APIC_URL + '/api/mo/uni/tn-' + tn.strip() + '.json'
            response = requests.get(get_url + objQuery, cookies=cookies, verify=False).json()['imdata']

            for line in response:
                l3out_list.append(line['l3extOut']['attributes']['name'])

            print('\n----Routed L3 Out for TENANT {}----\n'.format(tn))
            for l in l3out_list:
                print("\t{}".format(l))
            print('\nTotal Routed L3 Out for Tenant {} = {}'.format(tn, len(l3out_list)))

    ##### Faults #####

    if arguments.all or arguments.faults:
        print('\n----FAULTS----\n')
        fault_count = 0
        response = requests.get(post_url + get_query('fault'), cookies=cookies, verify=False).json()['imdata']
        # print(response)
        # print(str(len(response)))
        # print(type(response))

        for line in response:
            # print(line)
            # print(str(len(line)))
            # print(type(line))

            print("\t\t" + "-"*20)
            for k,v in (line['faultInst']['attributes']).items():
                #print("\t{} ==> \t {}".format(k, v))
                print("\t{:>25s} ==> \t {:<30}".format(k.strip(), v.strip()))
                fault_count += 1

        print('\nTotal Faults = {}'.format(fault_count))

    ##### CUSTOM QUERY #####

    if arguments.custom:
        get_custom_query(APIC_URL,cookies,arguments.custom)


# Standard call to the main() function.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script Description",
                                     epilog="Usage: ' python aic_fabric_step6_validation.py' project")


    parser.add_argument('project', help='Name of the project for this script. This is used to create a logfile.')

    parser.add_argument('-a', '--all', help='Execute all Queries', action='store_true',
                        default=False)

    parser.add_argument('-e', '--aeps', help='Query Fabric for AEPs', action='store_true',
                        default=False)

    parser.add_argument('-p', '--phydoms', help='Query Fabric for Physical Domains', action='store_true',
                        default=False)

    parser.add_argument('-v', '--vlan_pools', help='Query Fabric for Vlan Pools', action='store_true',
                        default=False)

    parser.add_argument('-o', '--fab_podpol', help='Query Fabric Pod Policy Group', action='store_true',
                        default=False)

    parser.add_argument('-t', '--tenants', help='Query Fabric for Tenants', action='store_true',
                        default=False)

    parser.add_argument('-u', '--faults', help='Query Fabric for faults', action='store_true',
                        default=False)

    parser.add_argument('-1', '--health_all', help='Query Fabric for Total Overall Health', action='store_true',
                        default=False)

    parser.add_argument('-2', '--nodes', help='Query Fabric for all Nodes', action='store_true',
                        default=False)

    parser.add_argument('-b', '--bds', help='Query Fabric for Bridge Domains within a Tenant (use "ALL" for all Tenants)')

    parser.add_argument('-g', '--epgs', help='Query Fabric for EPGs within a Tenant (use "ALL" for all Tenants)')

    parser.add_argument('-c', '--contracts', help='Query Fabric for Contracts within a Tenant (use "ALL" for all Tenants)')

    parser.add_argument('-i', '--filters', help='Query Fabric for Filters within a Tenant (use "ALL" for all Tenants)')

    parser.add_argument('-n', '--network_vrf', help='Query Fabric for VRF (Network or Context) within a Tenant (use "ALL" for all Tenants)')

    parser.add_argument('-3', '--l3out', help='Query Fabric for Routed L3 Out within a Tenant (use "ALL" for all Tenants)')

    parser.add_argument('-m', '--custom', help='Query Fabric with a custom REST call. Example: -c "/api/node/class/fvCEp.json" to query a list of end points attached to the fabric.')

    parser.add_argument('-f', '--filename', help='Option used to pass a credentials file other than the default "credentias.py"',
                        default='credentials.py')

    arguments = parser.parse_args()
    main()


