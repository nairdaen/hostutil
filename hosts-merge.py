"""
Copyright (c) 2023 Adrian Ahuatzi Ayala
For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 
"""
#!/usr/bin/env python3
# Merge hosts from local and custom hosts file
# Skips localhost/hostname
# Sample usage:
# python hosts-merge.py --local-hosts auto merge --custom-hosts custom.txt

import argparse
import logging
import platform
import shutil
import socket

log_format = '[%(asctime)s] [%(levelname)s] - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)
log = logging.getLogger(__name__)

CUSTOM_MARKER_START = "# Following lines are appended by hosts-merge"
CUSTOM_SECTION_START = "# start|"
CUSTOM_SECTION_END = "# end|"

def read_file(filepath):
    log.info(f'Reading {filepath}')
    hosts = []
    with open(filepath, 'r') as hostsfile:
        for line in hostsfile:
            hosts.append(line.strip())

    return hosts

def write_file(filepath, content):
    log.info(f'Writing {filepath}')
    with open(filepath, 'w') as hostsfile:
        hostsfile.writelines('\n'.join(content))

def get_hostname():
    hostname = socket.gethostname()
    log.info(f'Hostname is {hostname}')
    return hostname

def combine_hosts(local_hosts, custom_hosts, skip_localhost=True):
    log.info(f'Combining hosts')
    combined_lines = []

    for local_line in local_hosts:
        if local_line.startswith(CUSTOM_MARKER_START):
            break
        log.info(f'Adding from local\t{local_line}')
        combined_lines.append(local_line)

    log.info(f'Adding\t{CUSTOM_MARKER_START}')
    combined_lines.append(CUSTOM_MARKER_START)

    hostname = get_hostname()

    for custom_line in custom_hosts:
        add = True
        if hostname in custom_line:
            tokens = custom_line.split()
            for t in tokens:
                if hostname == t and skip_localhost:
                    log.info(f'Skipping from custom {hostname}')
                    add = False
                break
        if add:
            log.info(f'Adding from custom \t{custom_line}')
            combined_lines.append(custom_line)

    return combined_lines

def remove_hosts(local_hosts, custom_name):
    log.info(f'Removing custom hosts section {custom_name}')

    lines = []
    skip_line = False

    for local_line in local_hosts:
        if local_line.startswith(CUSTOM_SECTION_START) and local_line.split('|')[1] == custom_name:
            log.info(f'Found start of section {custom_name}, will skip content.')
            skip_line = True

        if not skip_line:
            log.info(f'Adding from local\t{local_line}')
            lines.append(local_line)
        else:
            log.info(f'Skipping\t{local_line}')

        if local_line.startswith(CUSTOM_SECTION_END) and local_line.split('|')[1] == custom_name:
            log.info(f'Found end of section {custom_name}, will stop skipping content.')
            skip_line = False

    return lines

def backup_file(filename):
    backup = f'{filename}.bak'
    log.info(f'Saving copy of {filename} to {backup}')
    shutil.copyfile(filename, backup)

def main():
    valid_actions = ['merge', 'remove']

    parser = argparse.ArgumentParser(description='Merge hosts files')
    parser.add_argument('--local-hosts', dest='local_hosts', required=True, help='Full path to local hosts file')

    subparsers = parser.add_subparsers(help=f'Action to perform: {valid_actions}')
    merge_parser = subparsers.add_parser('merge', help='Merge two hosts files')
    remove_parser = subparsers.add_parser('remove', help='Remove a hosts section')

    merge_parser.add_argument('--custom-hosts', dest='custom_hosts', required=True, help='Full path to custom hosts file')
    merge_parser.set_defaults(action='merge')
    remove_parser.add_argument('--section', dest='custom_section', required=True, help='Name of the section to remove')
    remove_parser.set_defaults(action='remove')

    args = parser.parse_args()
    print(args)
    local = args.local_hosts
    action = args.action

    if local == 'auto':
        log.info('Auto detecting hosts location')
        osplatform = platform.system()

        if osplatform == 'Windows':
            local = 'C:\\Windows\\system32\\drivers\\etc\\hosts'
        elif osplatform == 'Linux':
            local = '/etc/hosts'
        elif osplatform == 'Haiku':
            local = '/system/settings/network/hosts'
        else:
            assert(False)
        log.info(f'Hosts set to {local}')

    if local and action == 'merge':
        custom_hosts = args.custom_hosts
        backup_file(local)

        local_lines = read_file(local)
        custom_lines = read_file(custom_hosts)

        combined = combine_hosts(local_lines, custom_lines)

        write_file(local, combined)
        log.info('Done')

    if local and action == 'remove':
        custom_section = args.custom_section
        backup_file(local)

        local_lines = read_file(local)

        lines = remove_hosts(local_lines, custom_section)

        write_file(local, lines)
        log.info('Done')

if __name__ == '__main__':
    main()
