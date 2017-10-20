#!/usr/bin/env python

import requests
import argparse
requests.packages.urllib3.disable_warnings()


'''
    This is a quick script to grab a backup a firewall with a known API key.  Next iteration will pull a username and
    password as needed to gen the API key on it's own for use.  This was a quick script though used out of a private
    server with cron to pull these.

    - Tighe Schlottog tschlottog@paloaltonetworks.com
'''


def parse_args():
    parser = argparse.ArgumentParser(description='Quick Backup of onboard firewall configuration')
    parser.add_argument('-fw', type=str, help='IP Address of Firewall')
    parser.add_argument('-k', '--api_key', type=str, help='API Key with access to Firewall')
    parser.add_argument('-out', type=str, help='Output file where the configuration should be written')
    parser.add_argument('-fwlist', type=str, help='CSV file of firewalls to backup')
    args = parser.parse_args()
    return parser, args


def pull_backup(fw, api_key, outfile):
    config_out = open(outfile, 'w')
    backup_headers = {'type': 'export', 'key': api_key, 'category': 'configuration'}
    backup_req = requests.get('https://%s/api' % fw, params=backup_headers, verify=False)
    config_out.write(backup_req.content)
    config_out.close()


def pull_firewalllist(fwlist):
    with open(fwlist, 'r') as fwdata:
        for line in fwdata:
            (fw, apikey) = line.split(',')
            pull_backup(fw, apikey, '%s.cfg' % fw.replace('.', '_'))


def control():
    backup_parser, backup_args = parse_args()
    if backup_args.fw and backup_args.api_key and backup_args.out:
        pull_backup(backup_args.fw, backup_args.api_key, backup_args.out)
    elif backup_args.fwlist:
        pull_firewalllist(backup_args.fwlist)
    else:
        backup_parser.print_help()


if __name__ == '__main__':
    control()