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

import pygtk
pygtk.require("2.0")
import gtk
import os
import thread
import gobject
import gettext
import dbus

class PolkitAction(gobject.GObject):
    """
    PolicyKit action, if changed return 0, means authenticate failed, 
    return 1, means authenticate successfully
    """
    result = 0
    session_bus = dbus.SessionBus()
    __gsignals__ = {
        'changed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_INT,)),
    }

    def __init__(self, widget):
        super(PolkitAction, self).__init__()

        self.widget = widget

    def authenticate(self):
        self.do_authenticate()
#        thread.start_new_thread(self.do_authenticate, ())

    def get_authenticated(self):
        return self.result

    def do_authenticate(self):
        policykit = self.session_bus.get_object('org.freedesktop.PolicyKit.AuthenticationAgent', '/')
        xid = self.widget.get_toplevel().window.xid

        if self.__class__.result:
            self.emit('changed', 1)
            return

        try:
            granted = policykit.ObtainAuthorization('com.ubuntu-tweak.mechanism', dbus.UInt32(xid), dbus.UInt32(os.getpid()))
        except dbus.exceptions.DBusException:
            self.emit('changed', 0)
        else:
            self.__class__.result = granted

            if self.__class__.result == 1:
                self.emit('changed', 1)
            else:
                self.emit('changed', 0)
