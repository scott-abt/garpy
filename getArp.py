#!/usr/bin/env python3
"""
Track ARP entries over time.
"""

import netmiko, sqlite3, hashlib, sys, os
import csv
from getpass import getpass
from DEVICE_LIST import DEVICES
from datetime import datetime

def GetCreds():
    """Return the username and password as a list."""

    _username = input("Router username: ")
    _password = getpass("Password for {}: ".format(_username))
    return [_username, _password]

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
        try:
            self.ssh = netmiko.ConnectHandler(**self.router_dict)
        except netmiko.ssh_exception.NetMikoAuthenticationException:
            raise
        except Exception as e:
            raise

        if self.router_dict['device_type'] == 'juniper':
            self.arp_table = self.ssh.send_command_expect('show arp no-resolve')
        else:
            print("{} is not Juniper.".format(self.router_dict['device_type']))

    def __str__(self):
        return self.arp_table

def main():
    arp_db = "arp.db"
    username, password = GetCreds()

    # Check for and set up the database
    if not os.path.isfile(arp_db):
        # Create a new database
        create_db = input("Database does not exist. Create it now? (y/n): ")

        if create_db.lower() == "y":
            con = sqlite3.connect(arp_db)
            cur = con.cursor()
            cur.execute("create table arp_entry(indx, IP, MAC, firstSeen, lastSeen, router)")
            cur.execute('create unique index entries on arp_entry (indx)')
            con.commit()
            con.close()
        else:
            sys.exit()

    # Receive a list of router IP addresses to get ARP info from.
    con = sqlite3.connect(arp_db)
    cur = con.cursor()

    now_datetime = datetime.now()
    now_timestamp = now_datetime.timestamp()
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
            if "Total" in mac or "MAC" in mac:
                continue
            else:
                string_to_encode = mac + ip + device['ip']
                encoded_str = string_to_encode.encode()
                indxr = Indexer(encoded_str)

            # Try to add new entry
            try:
                cur.execute("INSERT INTO arp_entry VALUES (?,?,?,?,?,?)", [str(indxr), ip, mac, now_timestamp, now_timestamp, device['ip']])
                con.commit()
            except sqlite3.IntegrityError:
                # Update the lastSeen value.
                cur.execute("UPDATE arp_entry SET lastSeen = ? WHERE indx = ?", [now_timestamp, str(indxr)])
                con.commit()
            except Exception as e:
                raise
    sys.exit()

if __name__ == "__main__":
    main()
