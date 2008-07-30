#!/usr/bin/env python

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

import os
import dbus
import gettext

class DbusProxy:
    INTERFACE = "com.ubuntu_tweak.Mechanism"

    try:
        system_bus = dbus.SystemBus()
        proxy = system_bus.get_object('com.ubuntu_tweak.Mechanism', '/Tweak', INTERFACE)
    except dbus.exceptions.DBusException:
        proxy = None

    @classmethod
    def set_liststate(self, state):
        self.proxy.SetListState(state, dbus_interface = self.INTERFACE)

    @classmethod
    def get_liststate(self):
        return self.proxy.GetListState(dbus_interface = DbusProxy.INTERFACE)

    @classmethod
    def set_entry(self, url, distro, comps, name, enabled):
        return self.proxy.SetSourcesList(url, distro, comps, name, enabled, dbus_interface = self.INTERFACE)

    @classmethod
    def add_aptkey(self, key):
        self.proxy.AddAptKey(key, dbus_interface = self.INTERFACE)

    @classmethod
    def exit(self):
        self.proxy.Exit(dbus_interface = DbusProxy.INTERFACE)
