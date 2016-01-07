#!/usr/bin/env python

import paramiko, sys, getpass

# logging
paramiko.util.log_to_file('getArp.log')

# hostname
user = ''
host = ''

if len(sys.argv) > 1:
    host = sys.argv[1]
    user = sys.argv[2]
else:
    default_username = getpass.getuser()
    host = input('Hostname: ')
    user = input('Username [{0}]: '.format(default_username))

if len(user) == 0:
    user = default_username

password = getpass.getpass()

print(user)
