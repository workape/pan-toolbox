#!/usr/bin/env python3
"""
Convert policies from XML sheet

This script reads an excel sheet in a compatible format and uploads it to Panorama via API.
Best used with Lab in a box Panorama VMs to validate config before using in production/pre-production.

CAVEATS:
address, address-group, service and other objects may need manual creation if
they don"t already exist on the firewall.

"""
__author__ = "Fahad Yousuf <fyousuf@paloaltonetworks.com>"

import openpyxl
import argparse
from pandevice import panorama, policies, objects
import pprint

pp = pprint.PrettyPrinter(indent=2)

def parse_args():
    parser = argparse.ArgumentParser(description="Convert policies from XML sheet")
    parser.add_argument("-i", "--input-file",  type=str, help="Input excel sheet (xls or xlsx)")
    parser.add_argument("-d", "--device", type=str, help="Panorama Hostname or IP")
    parser.add_argument("-dg", "--devicegroup", type=str, help="Device Group in Panorama")
    parser.add_argument("-u", "--api_username", type=str, help="Username used to generate API Key")
    parser.add_argument("-p", "--api_password", type=str, help="Password for API creation")
    args = parser.parse_args()
    if (args.input_file !=None):
        return args
    else:
        parser.print_help()
        return None

def create_service(servicename, pan):
    """
    Takes a service name string in format tcp-NNNN or udp-NNNN
    and creates a corresponding service object in the provided
    panorama object.
    """
    try:
        protocol, port = servicename.split('-')
        svc = objects.ServiceObject(
            name=servicename,
            protocol = protocol,
            destination_port = port,
        )
        pan.add(svc)
        svc.create()
    except:
        print("Error creating service named %s. Check name format" % servicename )
        raise

def get_policy_rows(sheet, offset=0):
    return list(sheet.rows)[offset:]

def get_pan_devtree(hostname="", api_username="", api_password=""):
    print("Attempting connection to %s" % hostname)
    pan = panorama.Panorama(hostname=hostname, api_username=api_username, api_password=api_password)
    # Get all Device Groups
    dgs = panorama.DeviceGroup.refreshall(pan, add=True)
    # Get all ServiceObjects, ServiceGroups, AddressObjects and AddressGroups
    objects.ServiceGroup.refreshall(pan, add=True)
    objects.ServiceObject.refreshall(pan, add=True)
    objects.AddressGroup.refreshall(pan, add=True)
    objects.AddressObject.refreshall(pan, add=True)
    for dg in dgs:
        policies.PreRulebase.refreshall(dg, add=True)
    print("Device information successfully refreshed")
    return dgs, pan


if __name__ == "__main__":
    args = parse_args()
    if args == None:
        exit(1)
    wb = openpyxl.reader.excel.load_workbook(args.input_file)
    dgs, pan = get_pan_devtree(args.device, api_username=args.api_username, api_password=args.api_password)
    
    service_objs = list()
    for obj in pan.children:
        if type(obj) == objects.ServiceObject:
            service_objs.append(obj)

    target_dg = None
    for dg in dgs:
        if dg.name == args.devicegroup:
            target_dg = dg
        else:
            print("DG Name is: %s" % dg.name)
    # Create Policies 
    for i, row in enumerate(get_policy_rows(wb['Sheet'], offset=1)):
        print("Working on row# %d" % i)
        #Truncate name if it is greater than 32 chars
        name = row[0].value+'-'+str(i)
        if len(name) > 31:
            offset = len(name)-31
            name = name[offset:]
            if name[0] == '-':
                name = name[1:]
        sources = [sa.strip() for sa in row[2].value.split(";")]
        while '' in sources: sources.remove('')
        destinations = [da.strip() for da in row[4].value.split(";")]
        while '' in destinations: destinations.remove('')
        apps = [app.strip() for app in row[5].value.split(";")]
        while '' in apps: apps.remove('')
        services = [srv.strip() for srv in row[6].value.split(";")]
        while '' in services: services.remove('')
        pdict = {
            'name': name,
            'fromzone': [str(row[1].value)], 
            'source': sources, 
            "tozone":  [str(row[3].value) ],
            "destination": destinations, 
            "application": apps,
            "service": services,
            "action": row[7].value.lower(),
            "type": "universal",
            "description": ("Policy tuning rule id %s" % i)
        }
        
        p = policies.SecurityRule(**pdict)
        # Find the PreRulebase in the dg
        for child in target_dg.children:
            if type(child) == policies.PreRulebase:
                pre_rb = child
        pre_rb.add(p)
        print("Creating rule %s" % pdict['name'])
        try:
            for service in services:
                if not (service in ['any', 'application-default']) and not (service in [o.name for o in service_objs]):
                    print("Service %s not found in existing services %s" % (service, [o.name for o in service_objs]))
                    print("Creating service from name")
                    create_service(service, pan)
            p.create()
        except:
            print("Error creating rule %s " % pdict['name'])
            pp.pprint(pdict)
            raise
