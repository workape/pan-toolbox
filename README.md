## Palo Alto Networks Toolbox

This will be a repository of scripts written to handle some checks and other things on
on the Palo Alto Networks firewalls.  

### url-check.py
This script will query the PANDB cloud with data from a flat text file and return the
categories in a CSV.  This is a CLI executed script that utilizes argparse, requests,
and the lxml library.

### pan-rcli.py
This script will allow you to execute commands on a remote Palo Alto Networks firewall
and then read back the responses.  You can feed it either a single command or a text
file of commands.  It should be noted that the commands are executed as is, there is no 
logic in place to check the validity of the commands.

### pan-qb.py
This script will perform a quick backup of a firewall where there is a known API key to
make life easier.  If anyone wants to update it to auto-gen an API key from a fed username
and password.
