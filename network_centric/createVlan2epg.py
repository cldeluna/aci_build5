#!/usr/bin/python -tt
# createTenant.py
# Claudia
# PyCharm
__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "1/19/16  1:10 PM"
__copyright__ = "Copyright (c) 2015 Claudia"
__license__ = "Python"

import sys
#import lxml.etree as etree
import acitoolkit.acitoolkit as ACI
import urllib3
import requests
import re




def extract_vlans(vlan_file):
    vl_fh = open(vlan_file,'r')
    vlans = vl_fh.readlines()
    #print vlans
    vlan_dict = {}
    row = 0
    for v in vlans:
        #print v
        vlan_row = v.split(',')
        #print "vlan_row", vlan_row
        if row > 1 and vlan_row[2] != "1":
            #print "in loop"
            vlan_dict[vlan_row[2]]=vlan_row[3]
        row += 1
    #print "****Vlan Dictionary", vlan_dict

    return vlan_dict


def apic_login(hostname, username, password):
    url = "https://" + hostname
    sess = LoginSession(url, username, password)
    modir = MoDirectory(sess)
    try:
        modir.login()
    except:
        print("Login error!")
        exit(1)
    return modir
pass


def apic_login_acitk(hostname,username,password):

    # Login to APIC
    url = "http://" + hostname
    print("url",url)
    session = ACI.Session(url, username, password)
    resp = session.login()
    if not resp.ok:
        print('%% Could not login to APIC')
        sys.exit(0)
    return session



def print_tenant(session):
    # Download all of the tenants
    #print "="*20 + "TENANT" + "="*20
    tenants = ACI.Tenant.get(session)
    tenant_list =[]
    #print "tenants", tenants
    for tenant in tenants:
        print(tenant.name)
        tenant_list.append(tenant.name)
    return tenant_list


def main():
    """
    This is the main function of the script. From here, other functions are called.
    This script will take in the IP and credentials for an APIC, a new Tenant name, and a filename of existing VLANS
    This script can be used when the initial ACI Policy will map EPGs to existing client vlans
    This script takes in a list of existing vlans and creates the Tenant and corresponding VRF,ANP, EPG, and BO
    based on naming best practice.

    This script configures one ANP, mapped to one EPG and its corresponding BD for each vlan.
    Each BD is a member of one VRF.

    """
    # Put relevant arguments passed to the script when the script was called in variables with east to understand names
    hostname, username, password, tenant_name, vlan_csv = sys.argv[1:]
    #print hostname
    #print username
    #print password
    #rint tenant_name
    #print vlan_csv

    # Initialize and empty dictionary to hold the ANP=>EPG key value pairs
    epg_anp_dict = {}

    print("\n\n" + "="*20 + 'Creating Application Network Profiles and End Point Groups for each existing Vlan.' + "="*20)
    print("="*10 + "Processing VLAN file " + vlan_csv +' for new Tenant ' + tenant_name + ' by user ' + username + " on APIC " + hostname + "="*10)

    # Call the extract_vlan function, pass it the filename provided in the command line
    # This function will return a dictionary of vlan_id keys and vlan_name values
    print("About to extract vlans from ",vlan_csv)
    vlans = extract_vlans(vlan_csv)
    # Now that we have a dictionary of our anp=>epg pairs, generat the ANP and EPG names to be configured in the APIC
    # Store those names in the epg_anp_dict dictionary for later use.
    for vlan_id,vlan_name in vlans.items():
        print(vlan_id, vlan_name)
        epg_name = "v"+vlan_id.strip()+"_"+vlan_name.upper().strip()+"_EPG"
        anp_name = "v"+vlan_id.strip()+"_"+vlan_name.upper().strip()+"_AppProfile"
        epg_anp_dict[anp_name]=epg_name
    #print epg_anp_dict

    print("="*10 + "Attempting to create Tenant " + tenant_name + ' by user ' + username + " on APIC " + hostname + "="*10)
    print("\n\tLogging in to APIC")
    # Establish a session to the apic whose parameters/credentials were passed as arguments on the command line
    apic_session = apic_login_acitk(hostname, username, password)

    # Call the print_tenant function which will return a list of all the tenants currently configured on the APIC
    # This list will be used to check to see if the tenant to be configured provided via an argument already exists
    tenants = print_tenant(apic_session)
    #print "modir ",modir
    #print "tenant_name ", tenant_name
    # If the tenant we are supposed to create already exists, primt a status message, print all the existing tenants, and exit the script.
    if tenant_name in tenants:

        print("\n\t Tenant <"+tenant_name+ "> already exists and does not need to be created.\n")
        for t in tenants:
            print("\t Tenant "+t + " exists.")

        delete = raw_input("\n**** Would you like to delete the existing tenant " + tenant_name + " (Yes/No)? ****: ")

        #print "delete", str(delete)

        if delete.lower().strip() == 'no':

            print("\t\n Exiting Script.\n")
            sys.exit()

        else:
            delete2 = raw_input("\n**** Are you absolutely sure you want to delete the existing tenant <" + tenant_name + "> (Yes/No)? ****: ")
            print("\nSorry, I still need to figure out how to delete a tenant.")
            tenant_name.mark_as_deleted()
            print("\t\nExiting Script.\n")
            sys.exit()

    # If the tenant does not exist, create it and create the corresponding VRF
    else:

        print("\n\tCreating Tenant " + tenant_name)
        #create_tenant(modir, tenant_name)
        # Create the tenant
        tenant = ACI.Tenant(tenant_name)

        #Configure a Private Network/VRF for the Tenant
        tenant_vrf = tenant_name + "_VRF"
        print("\n\tCreating Private Network\VRF " + tenant_vrf + " for Tenant " + tenant_name + "\n")
        context = ACI.Context(tenant_vrf, tenant)


    for anp, epg in epg_anp_dict.items():

        # Create the App Profile, Bridge Domain, and EPG
        bd_name = re.sub("_EPG","_BD",epg )
        #print "bd_name: ",bd_name

        print("\tCreating Application Profile " + anp + " with EPG " + epg + " and BD " + bd_name)
        aciapp = ACI.AppProfile(anp, tenant)
        aciepg = ACI.EPG(epg, aciapp)
        acibd = ACI.BridgeDomain(bd_name, tenant)

        #Add the BD to the context
        acibd.add_context(context)

        #Add the BD to the EPG
        aciepg.add_bd(acibd)

        # Push it all to the APIC
        resp = tenant.push_to_apic(apic_session)
        if not resp.ok:
            print('%% Error: Could not push configuration to APIC')
            print(resp.text)


    print("\nLogging out of APIC")
    #modir.logout()



# Standard call to the main() function.
if __name__ == '__main__':
    if len(sys.argv) != 6:
        print('\nUsage:python createVlan2epg.py <hostname> <username> <password> <tenant name> <vlan csv file> '
              '\nExample: python createVlan2epg.py "172.18.180.187" "admin" "TSNaci123" "CdL520" "belfast-get-vlan.csv"'
              '\n\nNote: Fill in.\n\n')
        sys.exit()
    else:
        urllib3.disable_warnings()
        requests.packages.urllib3.disable_warnings()
        main()
