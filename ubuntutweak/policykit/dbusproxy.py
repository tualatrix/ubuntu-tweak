#!/usr/bin/python

# Ubuntu Tweak - PyGTK based desktop configuration tool
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
import logging

log = logging.getLogger("DbusProxy")

def show_message():
    from ubuntutweak.widgets.dialogs import ErrorDialog
    message = _('The daemon of Ubuntu Tweak doesn\'t start correctly, that means some '
            'advanced features may not work.\n'
            'If you want to help developer to debug, try to run "<b>sudo ubuntu-tweak-daemon</b>" under terminal.')
    ErrorDialog(message).launch()

class DbusProxy:
    INTERFACE = "com.ubuntu_tweak.daemon"

    try:
        __system_bus = dbus.SystemBus()
        __proxy = __system_bus.get_object('com.ubuntu_tweak.daemon', '/com/ubuntu_tweak/daemon')
    except Exception, e:
        __proxy = None

    def __getattr__(self, name):
        try:
            return self.__proxy.get_dbus_method(name, dbus_interface=self.INTERFACE)
        except Exception, e:
            log.error(e)
            return show_message

    def get_proxy(self):
        return self.__proxy

proxy = DbusProxy()

if __name__ == '__main__':
    print proxy
