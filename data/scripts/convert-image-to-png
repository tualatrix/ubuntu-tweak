#!/usr/bin/python

import os
import sys

def new_name(file):
    os.path.splitext(file)
    return '.'.join([os.path.splitext(file)[0],'png'])

files = sys.argv[1:]

for file in files:
    os.system('convert %s %s' % (file, new_name(file)))
