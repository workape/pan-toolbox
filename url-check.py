#!/usr/bin/env python

import requests
import lxml.etree
import argparse
import sys
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
    parser.add_argument('-d', '--debug', type=bool, default=False, help='Enable Debugging for additional Outputs')
    parser.add_argument('-c', '--cname', type=bool, default=False, help='Enable CNAME/Recursion on domain')
    args = parser.parse_args()
    return parser, args


def url_query(fw, api_key, urls_in, urls_out, debug, cname):
    resp_out = open(urls_out, 'a')
    with open(urls_in, 'r') as urls_file:
        for url in urls_file:
            if url.strip() != '':
                test_headers = {'type': 'op', 'key': api_key, 'cmd': '<test><url-info-cloud>' + requests.utils.requote_uri(str(url.strip())) + '</url-info-cloud></test>'}
                if debug:
                    print '***Request to API***'
                    print 'URL: https://%s/api' % fw
                    print 'Parameters:'
                    print test_headers
                    print '***End API Request\n\n'
                url_req = requests.get('https://%s/api' % fw, params=test_headers, verify=False)
                if debug:
                    print '***Response from API***'
                    print url_req.content
                    print '***End API Response\n\n'
                if url_req.status_code is requests.codes.ok:
                    resp_root = lxml.etree.fromstring(url_req.content)
                    if resp_root.xpath('//result') is not None:            
                        for x in resp_root.xpath('//result')[0].text.split():
                            if not x.startswith('BM:'):
                                if cname:
                                    if debug:
                                        print '***Data in //result xpath: %s' % x
                                    if ',' in x:
                                        y = x.split(',')
                                        print y[0], y[-1]
                                        resp_out.write('%s,%s\n' % (y[0], y[-1]))
                                else:
                                    if debug:
                                        print '***Data in //result xpath: %s' % x
                                    if ',' in x:
                                        y = x.split(',')
                                        print url, y[-1]
                                        resp_out.write('%s,%s\n' % (url.strip(), y[-1]))
                                    break
                        else:
                            print 'Caught an error '
                else:
                    sys.exit('API Connection to %s returned %s' % (fw, url_req.status_code))


def control():
    url_parser, url_args = parse_args()
    url_query(url_args.fw, url_args.api_key, url_args.urls_in, url_args.urls_out, url_args.debug, url_args.cname)


if __name__ == '__main__':
    control()
