#!/usr/bin/python -tt
# Project: python
# Filename: aci_contract_log_analysis
# claud
# PyCharm


__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "7/15/2017"
__copyright__ = "Copyright (c) 2016 Claudia"
__license__ = "Python"

import json
import requests
import argparse
import aci_fabric_build_utilities
import re
import collections
import csv

requests.packages.urllib3.disable_warnings()


def some_function():
    pass


def main():

    '''

    Sample Log record from ACI

            "eventRecord": {
            "attributes": {
                "affected": "topology/pod-1/node-201/sys",
                "cause": "transition",
                "changeSet": "",
                "childAction": "",
                "code": "E4204936",
                "created": "2017-07-15T12:10:20.773-07:00",
                "descr": " %ACLLOG-5-ACLLOG_PKTLOG: CName: MC-ITD01-PublicSafety-TN:MC-ITD01-PublicSafety-VRF(VXLAN:
                2752512), VlanType: FD_VLAN, Vlan-Id: 16, SMac: 0x00505695c1b3, DMac:0x0022bdf819ff, SIP: 198.18.11.40,
                DIP: 8.8.8.8, SPort: 42575, DPort: 53, Src Intf: port-channel2, Proto: 17, PktLen: 79 ",
                "dn": "subj-[topology/pod-1/node-201/sys]/rec-4294978845",
                "id": "4294978845",
                "ind": "special",
                "modTs": "never",
                "severity": "info",
                "status": "",
                "trig": "manual",
                "txId": "3696360",
                "user": "internal"
            }
        }
    },

    :return:
    '''

    # aci_fabric_build_utilities.get_input("Press Enter to continue....")

    file_handle = aci_fabric_build_utilities.basic_file_open(arguments.payload_file)

    with file_handle:
        print(file_handle)
        json_data = json.load(file_handle)

    # print(json.dumps(json_data, indent=4))

    # for k, v in json_data.iteritems():
        # print("Key is: {} | Value is: {} | Value Type is: {}\n".format(k,v,type(v)))
        # print("Key is: {} |  Value Type is: {}\n".format(k, type(v)))

    print("Length of imdata is: {}".format(len(json_data['imdata'])))


    protocol_file = aci_fabric_build_utilities.basic_file_open('protocol-numbers-1.csv')

    protocol_dict = csv.DictReader(protocol_file)


    print(protocol_dict)
    for k in protocol_dict.__iter__():
        print(k)

    aci_fabric_build_utilities.get_input("Press Enter to continue....")

    tmp_list = []
    tmp_tuples = []



    # For each event payload in the log file
    for line in json_data['imdata']:
        tmp_dict = {}
        protocol_desc = ''
        #print("eventRecord > attributes: {}".format(line['eventRecord']['attributes']))

        event = line['eventRecord']['attributes']

        # If the event payload is an ACL Log Event, process it
        if re.search("%ACLLOG-", event['descr']):

            line = re.sub(r'%ACLLOG-5-ACLLOG_PKTLOG:','', event['descr'])

            descr = line.strip().split(",")
            # print("Desription: {}".format(descr))

            # Parsing of the Descr line in the ACI output
            for item in descr:
                i = item.split(":")
                # If there are two elements the first is the key and the second is the value
                if len(i) == 2:
                    tmp_dict[i[0].strip()] = i[1].strip()
                # the first element in th split has ":" in it and needs special parsing to pull out the Tenant,
                # VRF, and VXLAN ID
                else:
                    cname = i[1].strip() + ":" + i[2].strip() + ":" + i[3].strip()
                    tmp_dict[i[0].strip()] = cname
                    tmp_dict['tn'] = i[1].strip()
                    tmp_dict['vrf'] = re.sub(r'\(VXLAN','',i[2].strip())
                    tmp_dict['vxlan'] = re.sub(r'\)','',i[3].strip())


            # If source or destination is using an ephemeral port set it to 65535 for easier counting
            if int(tmp_dict['SPort']) > 49151:
                source_port = 65535
            else:
                source_port = int(tmp_dict['SPort'])

            if int(tmp_dict['DPort']) > 49151:
                dest_port = 65535
            else:
                dest_port = int(tmp_dict['DPort'])

            # Protocol Lookup
            #proto_desc = [p['Protocol'] for p in protocol_dict.__iter__() if tmp_dict['Proto'] in p['Protocol']]

            #print("tmp dict proto: {}".format(tmp_dict['Proto']))



            for p in protocol_dict.__iter__():
                # print(p)
                #print("p proto: {}".format(p['Decimal']))
                #aci_fabric_build_utilities.get_input("Press Enter to continue....")
                print(p['Decimal'])
                print(tmp_dict['Proto'])
                if p['Decimal'].strip() == tmp_dict['Proto'].strip():
                    print(p['Protocol'])
                    protocol_desc = p['Protocol']
                    print(protocol_desc)

            #print("protocol: {}".format(proto_desc))


            # print(proto_desc)
            # Definte the tuple to be used as a "key"
            tmp_tuple = (tmp_dict['tn'],tmp_dict['vrf'], tmp_dict['vxlan'],tmp_dict['Vlan-Id'],tmp_dict['SIP'],
                         source_port,tmp_dict['DIP'],dest_port,tmp_dict['Proto'],protocol_desc)
            # tmp_tuple = (tmp_dict['vxlan'],tmp_dict['SIP'],tmp_dict['SPort'],tmp_dict['DIP'],tmp_dict['DPort'],
            #              tmp_dict['Proto'])
            # print(tmp_tuple)
            # print(protocol_desc)

            tmp_dict['key'] = tmp_tuple
            tmp_tuples.append(tmp_tuple)
            # print("Desription: {}".format(descr))
            # print("Temp Dict: {}".format(tmp_dict))

            tmp_list.append(tmp_dict)


    print("\n\n")

    tcount = collections.Counter(tmp_tuples)

    for k,v in tcount.items():
        print("key: {} \t count: {}".format(k,v))
    print(len(tcount))

    print()
    print("**** More than 10 hits! ****")
    for k,v in tcount.items():
        if v > 10:
            print("key: {} \t count: {}".format(k,v))
            #print(k[8])




    print("Items in Temp List: {}".format(len(tmp_list)))


    print("Total items in imdata: {}".format(len(json_data['imdata'])))
    print("Total ACL LOG lines: {}".format(len(tmp_list)))










# Standard call to the main() function.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script Description",
                                     epilog="Usage: ' python aci_contract_log_analysis' ")

    parser.add_argument('payload_file', help='Name of the JSON payload file to use in this script.')

    parser.add_argument('-a', '--all', help='Execute all exercises in week 4 assignment', action='store_true',
                        default=False)
    arguments = parser.parse_args()
    main()


