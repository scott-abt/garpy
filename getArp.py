#!/usr/bin/env python3
"""
Track ARP entries over time. Requires netmiko - 
https://github.com/ktbyers/netmiko
"""

import netmiko, sqlite3, hashlib, sys, os
import csv
from getpass import getpass
from IP_LIST import IP_LIST

class Indexer:
    """Create a unique index for each entry"""
    def __init__(self, encoded_string):
        self.hasher = hashlib.sha1()
        self.hasher.update(encoded_string)
        self.digest = self.hasher.hexdigest()
        
    def __str__(self):
        return self.digest

class Arper:
    def __init__(self, router_dict):
        self.router_dict = router_dict
        self.ssh = netmiko.ConnectHandler(**router_dict)
        self.arp_table = self.ssh.send_command_expect('show arp no-resolve')

    def __str__(self):
        return self.arp_table

def main():
    arp_db = "arp.db"

    username = input("Router username: ")
    password = getpass("Password for {}: ".format(username))

    JUNIPER_SWITCH = {
        'device_type':          'juniper',
        'ip':                   '',
        'username':             username,
        'password':             password,
        'verbose':              False,
    }

    # Check for and set up the database
    if not os.path.isfile(arp_db):
        # Create a new database
        create_db = input("Database does not exist. Create it now? (y/n): ")
        if create_db.lower() == "y":
            con = sqlite3.connect("arp.db")
            con.execute('create table arp_entry(indx, IP, MAC, firstSeen,\
                         lastSeen, router)')
        else:
            sys.exit()

    # Receive a list of router IP addresses to get ARP info from.
    ## Imported from IP_LIST.py
    for router_ip in IP_LIST:
        # Get the arp table
        JUNIPER_SWITCH['ip'] = router_ip
        JUNIPER_SWITCH['username'] = username
        JUNIPER_SWITCH['password'] = password
        arp_table = Arper(JUNIPER_SWITCH)

        # parse the table as csv
        csvreader = csv.reader(arp_table.arp_table.splitlines(), delimiter='\t')
        for row in csvreader:
            if not row:
                continue
            splitrow = row[0].rsplit()
            mac = splitrow[0]
            ip = splitrow[1]
            if "Total" in mac:
                continue
            else:
                string_to_encode = mac + ip + router_ip
                encoded_str = string_to_encode.encode()
                indxr = Indexer(encoded_str)

            # Check database for existing entry

            

        # Add new entry or update existing
        ## Entries: indx, IP, MAC, firstSeen, lastSeen, router
        ## Figure out a way to make indx unique per entry. Could have same ip
        ## multiple routers. Maybe hashing of some kind with IP/MAC/router

    sys.exit()

if __name__ == "__main__":
    main()
