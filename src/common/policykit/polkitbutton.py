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

import os
import gtk
import dbus
import gobject
from common.config import TweakSettings

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

    def get_authenticated(self):
        return self.result

    def do_authenticate(self):
        if TweakSettings.get_power_user():
            self.__class__.result = 1
            self.emit('changed', 1)
            return
        policykit = self.session_bus.get_object('org.freedesktop.PolicyKit.AuthenticationAgent', '/')
        xid = self.widget.get_toplevel().window.xid

        if self.__class__.result:
            self.emit('changed', 1)
            return

        try:
            granted = policykit.ObtainAuthorization('com.ubuntu-tweak.daemon', dbus.UInt32(xid), dbus.UInt32(os.getpid()))
        except dbus.exceptions.DBusException:
            self.emit('changed', 0)
        else:
            self.__class__.result = granted

            if self.__class__.result == 1:
                self.emit('changed', 1)
            else:
                self.emit('changed', 0)

class PolkitButton(gtk.Button):
    __gsignals__ = {
        'changed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_INT,)),
    }

    def __init__(self):
        super(PolkitButton, self).__init__()

        self.set_label(_('_Unlock'))
        image = gtk.image_new_from_stock(gtk.STOCK_DIALOG_AUTHENTICATION, gtk.ICON_SIZE_BUTTON)
        self.set_image(image)

        self.action = PolkitAction(self)
        self.action.connect('changed', self.on_action_changed)
        self.connect('clicked', self.on_button_clicked)

    def on_button_clicked(self, widget):
        self.action.authenticate()

    def on_action_changed(self, widget, action):
        if action:
            self.change_button_state()

        self.emit('changed', self.action.get_authenticated())

    def change_button_state(self):
        image = gtk.image_new_from_stock(gtk.STOCK_YES, gtk.ICON_SIZE_BUTTON)
        self.set_image(image)
        self.set_sensitive(False)
