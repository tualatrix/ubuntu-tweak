#!/usr/bin/python
# TODO remove it in the future or add as a feature

import os
import sys
import glob

codename = os.popen('lsb_release -cs').read().strip()
SOUCES_LIST = '/etc/apt/sources.list'

if os.getuid() != 0:
    print("You need to be root to execute this script")
    sys.exit(1)

print("Check the PPA list...")
for sourceslist in glob.glob('/etc/apt/*-%s.list' % codename):
    print("Found ppa source file: %s" % sourceslist)
    data = open(sourceslist).read()

    print("Merge the source to %s" % SOUCES_LIST)
    file_path = open(SOUCES_LIST, 'a')
    file_path.write(data)
    file_path.close()

    print("Delete the ppa source file: %s\n" % sourceslist)
    os.remove(sourceslist)

print("Your apt sources is clean now")
