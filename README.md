#Palo Alto Networks Toolbox

##url-check.py
This script will query the PANDB cloud with data from a flat text file and return the
categories in a CSV.  This is a CLI executed script that utilizes argparse, requests,
and the lxml library.

##pan-rcli.py
This script will allow you to execute commands on a remote Palo Alto Networks firewall
and then read back the responses.  You can feed it either a single command or a text
file of commands.  It should be noted that the commands are executed as is, there is no 
logic in place to check the validity of the commands.