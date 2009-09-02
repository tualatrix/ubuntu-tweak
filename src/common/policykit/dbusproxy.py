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

import dbus

class DbusProxy:
    INTERFACE = "com.ubuntu_tweak.daemon"

    __system_bus = dbus.SystemBus()

    def __init__(self, path):
        #TODO deal with exception
        self.path = path
        self.__object = self.__system_bus.get_object(self.INTERFACE, self.path)

    def __getattr__(self, name):
        return self.__object.get_dbus_method(name, dbus_interface=self.INTERFACE)

if __name__ == '__main__':
    print proxy
