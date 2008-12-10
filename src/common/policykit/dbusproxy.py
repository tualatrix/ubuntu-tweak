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
    INTERFACE = "com.ubuntu_tweak.Mechanism"

    try:
        __system_bus = dbus.SystemBus()
        __proxy = __system_bus.get_object('com.ubuntu_tweak.Mechanism', '/Tweak', INTERFACE)
    except dbus.exceptions.DBusException:
        __proxy = None

    def set_liststate(self, state):
        self.__proxy.SetListState(state, dbus_interface = self.INTERFACE)

    def get_liststate(self):
        return self.__proxy.GetListState(dbus_interface = self.INTERFACE)

    def set_entry(self, url, distro, comps, name, enabled):
        return self.__proxy.SetSourcesList(url, distro, comps, name, enabled, dbus_interface = self.INTERFACE)

    def add_aptkey(self, key):
        self.__proxy.AddAptKey(key, dbus_interface = self.INTERFACE)

    def get_proxy(self):
        return self.__proxy

    def clean_apt_cache(self):
        try:
            return self.__proxy.CleanAptCache(dbus_interface = self.INTERFACE)
        except:
            return 'error'

    def delete_file(self, path):
        try:
            return self.__proxy.DeleteFile(path, dbus_interface = self.INTERFACE)
        except:
            return 'error'

    def edit_file(self, path, content):
        try:
            return self.__proxy.EditFile(path, content, dbus_interface = self.INTERFACE)
        except:
            return 'error'

    def exit(self):
        self.__proxy.Exit(dbus_interface = self.INTERFACE)

proxy = DbusProxy()

if __name__ == '__main__':
    print proxy
