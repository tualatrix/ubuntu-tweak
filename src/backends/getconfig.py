#!/usr/bin/python

# Ubuntu Tweak - PyGTK based desktop configure tool
#
# Copyright (C) 2007-2008 TualatriX <tualatrix@gmail.com>
#
# Ubuntu Tweak is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Ubuntu Tweak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ubuntu Tweak; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
import dbus
import dbus.glib
import dbus.service
import dbus.mainloop.glib
import gobject

INTERFACE = "com.ubuntu_tweak.daemon.getconfig"
PATH = "/com/ubuntu_tweak/daemon/getconfig"

class GetConfig(dbus.service.Object):
    def __init__ (self, bus):
        bus_name = dbus.service.BusName(INTERFACE, bus=bus)
        dbus.service.Object.__init__(self, bus_name, PATH)

    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='b')
    def is_exists(self, path):
        return os.path.exists(path)

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    GetConfig(dbus.SystemBus())

    mainloop = gobject.MainLoop()
    mainloop.run()
