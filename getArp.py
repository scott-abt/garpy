#!/usr/bin/env python3
"""
Track ARP entries over time. Requires netmiko - 
https://github.com/ktbyers/netmiko
"""

import netmiko, sqlite3
from sys import exit
from getpass import getpass
from os import path

def main():

    arp_db = "arp.db"

    # Check for and set up the database
    if path.isfile(arp_db):
        pass
    else:
        # Create a new database
        create_db = input("Database does not exist. Create it now? (y/n): ")
        print(create_db)
        exit()

    # Receive a list of IP addresses to get ARP info from.

    # Check database for existing entry

    # Add new entry or update existing
    ## Entries: indx, IP, MAC, firstSeen, lastSeen, router
    ## Figure out a way to make indx unique per entry. Could have same ip
    ## multiple routers. Maybe hashing of some kind with ip/firstSeen/router
    exit()

if __name__ == "__main__":
    main()
