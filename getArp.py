#!/usr/bin/env python3
"""
Track ARP entries over time.
"""

import netmiko, sqlite3, hashlib, sys, os
import csv
from getpass import getpass
from DEVICE_LIST import DEVICES

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
#        self.ssh = netmiko.ConnectHandler(**router_dict)
        if self.router_dict['device_type'] == 'juniper':
#            self.arp_table = self.ssh.send_command_expect('show arp no-resolve')
            print("JUNIPER")
        else:
            print(self.router_dict['device_type'])

    def __str__(self):
        return self.arp_table

def main():
    arp_db = "arp.db"

    username = input("Router username: ")
    password = getpass("Password for {}: ".format(username))


    # Check for and set up the database
    if not os.path.isfile(arp_db):
        # Create a new database
        create_db = input("Database does not exist. Create it now? (y/n): ")
        arp_db = input("Please name your database file. Default is arp.db: ")

        if create_db.lower() == "y":
            con = sqlite3.connect(arp_db)
            con.execute('create table arp_entry(indx, IP, MAC, firstSeen,\
                         lastSeen, router)')
        else:
            sys.exit()

    # Receive a list of router IP addresses to get ARP info from.
    for device in DEVICES:
        # Get the arp table
        device['username'] = username
        device['password'] = password
        arp_table = Arper(device)

        # parse the table as csv
        ## Create helper function here checking for device type.
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
