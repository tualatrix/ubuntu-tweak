#!/usr/bin/env python
# coding: utf-8

import os
import sys
import pygtk
pygtk.require('2.0')
import gtk
import gconf
import socket
import gobject

from Constants import *
from SystemInfo import SystemInfo
from xmlrpclib import ServerProxy, Error

client = gconf.client_get_default()
server = ServerProxy("http://ubuntu-tweak.appspot.com/xmlrpc")
#server = ServerProxy('http://127.0.0.1:8080/xmlrpc')

def CheckVersion():
    try:
        version = server.version()
    except Error, e:
        print "Error:", e
    except socket.gaierror:
        print "Bad Network!"
    else:
        client.set_string('/apps/ubuntu-tweak/update', version)

def SubmitCurrent():
    current = client.get_string('/apps/ubuntu-tweak/current')
    if Version != current:

        distro = SystemInfo.distro
        locale = os.getenv("LANG")
        platform = os.uname()[-1]

        try:
            result = server.putinfo(Version, distro, locale, platform)
        except Error, e:
            print "Error:", e
        else:
            if result:
                client.set_string('/apps/ubuntu-tweak/current', Version)

if __name__ == "__main__":
    CheckVersion()
