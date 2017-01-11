#!/usr/bin/env python

import requests
import lxml.etree
import argparse
requests.packages.urllib3.disable_warnings()

'''
    url-check.py - 2017 Tighe Schlottog

    This script will pull in data from a text file and then utilize it querying the URL Cloud w/PANDB.
'''


def parse_args():
    parser = argparse.ArgumentParser(description='Query URL Cloud to determine the category of URLs.')
    parser.add_argument('-fw', type=str, help='IP Address of Firewall for querying', required=True)
    parser.add_argument('-k', '--api_key', type=str, help='API Key with access to Firewall', required=True)
    parser.add_argument('-ui', '--urls_in', type=str, help='Input file containing a list of URLS for querying', required=True)
    parser.add_argument('-uo', '--urls_out', type=str, help='Output file where the URL and category are written in CSV', required=True)
    args = parser.parse_args()
    return parser, args


def url_query(fw, api_key, urls_in, urls_out):
    resp_out = open(urls_out, 'a')
    with open(urls_in, 'r') as urls_file:
        for url in urls_file:
            test_headers = {'type': 'op', 'key': api_key, 'cmd': '<test><url-info-cloud>' + url + '</url-info-cloud></test>'}
            url_req = requests.get('https://%s/api' % fw, params=test_headers, verify=False)
            resp_root = lxml.etree.fromstring(url_req.content)
            for x in resp_root.xpath('//result')[0].text.split():
                if ',' in x:
                    y = x.split(',')
                    print y[0], y[-1]
                    resp_out.write('%s,%s\n' % (y[0], y[-1]))


def control():
    url_parser, url_args = parse_args()
    url_query(url_args.fw, url_args.api_key, url_args.urls_in, url_args.urls_out)


if __name__ == '__main__':
    control()
