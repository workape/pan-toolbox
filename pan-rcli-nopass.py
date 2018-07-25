#!/usr/bin/env python
import paramiko
import sys
from datetime import datetime
import argparse

__author__ = 'Tighe Schlottog || workape<at>gmail<dot>com'

def parse_args():
    '''
    This function will parse the command line arguments passed in via ARGV.
    :return:
    '''
    parser = argparse.ArgumentParser(description='Script to remotely execute CLI commands on Palo Alto Networks firewalls')
    parser.add_argument('-fw', '--firewall', type=str, help='IP address of remote Firewall')
    parser.add_argument('-u', '--user', type=str, help='Remote Firewall Username')
    parser.add_argument('-p', '--password', type=str, help='Remote Firewall Password')
    parser.add_argument('-cmd', type=str, help='Remote Command to be run surrounded by double quotes.  For example "show system info".')
    parser.add_argument('-cf', '--command_file', type=str, help='Read commands to be executed remotely from a defined file')
    parser.add_argument('-stdout', dest='stdout', action='store_true', help='Output command data to STDOUT')
    parser.add_argument('-debug', dest='debug', action='store_true', help='Enable additional debugging')
    parser.set_defaults(stdout=False, debug=False)
    parser.add_argument('-f', '--file', type=str, help='Output command data to named file')
    args = parser.parse_args()

    return parser, args


def parse_command_file(command_file):
    '''
    This function will parse the lines of the command file, excluding the comment lines starting with #, based on the
    newline character and return a list for use in other functions.
    :param command_file: This is the name/location of the command file pulled in from the CLI.
    :return: Returns a dict of the non-comment command lines from the file.
    '''
    commands = []
    with open(command_file, 'r') as cf:
        for line in cf.read().split('\n'):
            if not line.startswith('#'):
                commands.append(line)
    return commands


def setup_conn(fw_ip, username, password):
    '''
    This function will set up the SSH connection via Paramiko's SSH Client.
    :param fw_ip: IP address of the firewall that is being connected too.
    :param username: Username used to log into the firewall.
    :param password: Password used to log into the firewall.
    :return:  Returns the connection handler for use in other functions.
    '''
    print fw_ip, username, password
    test_conn = paramiko.SSHClient()
    test_conn.load_system_host_keys()
    test_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print 'Connecting to firewall'
        test_conn.connect(fw_ip, username=username, password=password)
    except:
        print 'Unable to connect to firewall, please check your settings'
        sys.exit(1)

    return test_conn  # Paramiko SSH Handler


def execute_remote_command(ssh_con, cmds, cmd_args):
    '''
    This function will invoke a Paramiko shell and execute commands in a remote manner.

    It will search for two ending prompt conditions the '>' which is the standard prompt and the ':'
    which is the prompt used for passwords.

    :param ssh_con: This is the Paramiko SSH connection handler which is handed into the system.
    :param cmd: This is the command which will be executed in the Paramiko SSH Shell
    :param cmd_args: These are the CLI arguments to cehck for debugging, file destination, etc.
    :return: It will return a string of the data that is pulled back from the results of the command.
    '''
    if cmd_args.file:
        cmd_out = open(cmd_args.file, 'a+')
    ssh_shell = ssh_con.invoke_shell()
    while not ssh_shell.recv_ready():
        pass
    ssh_shell.send('set cli pager off\n')
    while not ssh_shell.recv_ready():
        pass
    for cmd in cmds:
        if len(cmd) > 0:
            if cmd[-1] != '\n':
                cmd += '\n'
            if cmd_args.debug:
                print 'Sending "%s" to remote firewall' % cmd
            ssh_shell.send(cmd)
            prompt_search = ''
            results_data = ''
            while prompt_search not in ['>', ':']:
                results_data += ssh_shell.recv(4096).replace('\r', '')
                prompt_search = results_data.strip()[-1]
            if cmd_args.file:
                cmd_out.write(results_data)
            if cmd_args.stdout:
                print results_data
    if cmd_args.debug:
        print 'All commands executed'

def main():
    cmd_parser, cmd_args = parse_args()

    if cmd_args.file:
        cmd_out = open(cmd_args.file, 'a+')
        cmd_out.write('---------> %s <---------\n' % datetime.now().strftime('%Y/%m/%d@%H:%M:%S'))
        cmd_out.close()
    if cmd_args.command_file:
        cmds = parse_command_file(cmd_args.command_file)
    else:
        cmds = [ cmd_args.cmd ]
    if cmd_args.debug:
        print 'Setting up SSH connection'
    cmd_handler = setup_conn(cmd_args.firewall, cmd_args.user, cmd_args.password)
    if cmd_args.debug:
        print 'Successfully set up SSH connection and received connection handler back'

    execute_report_command(cmd_handler, cmds, cmd_args)


if __name__ == '__main__':
    main()

