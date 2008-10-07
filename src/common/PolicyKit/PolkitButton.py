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

class PolkitButton(gtk.Button):
    action = 0
    error = 0
    __gsignals__ = {
            'authenticated': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()),
            'failed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()),
            }

    def __init__(self):
        gtk.Button.__init__(self)

        self.set_label(_('_Unlock'))
        image = gtk.image_new_from_stock(gtk.STOCK_DIALOG_AUTHENTICATION, gtk.ICON_SIZE_BUTTON)
        self.set_image(image)

        self.connect("clicked", self.on_button_clicked)

    def on_button_clicked(self, widget):
        xid = widget.get_toplevel().window.xid
        thread.start_new_thread(self.obtain_authorization, (xid,))

    def obtain_authorization(self, xid):
        policykit = dbus.SessionBus().get_object('org.freedesktop.PolicyKit.AuthenticationAgent', '/')

        if self.__class__.action:
            self.change_button_state()
            self.emit('authenticated')
            return

        try:
            granted = policykit.ObtainAuthorization('com.ubuntu-tweak.mechanism', dbus.UInt32(xid), dbus.UInt32(os.getpid()))
        except dbus.exceptions.DBusException:
            self.error = -1
            self.emit('failed')
        else:
            self.__class__.action = granted

            if self.__class__.action == 1:
                self.change_button_state()
                self.emit('authenticated')
            else:
                self.emit('failed')

    def change_button_state(self):
        image = gtk.image_new_from_stock(gtk.STOCK_YES, gtk.ICON_SIZE_BUTTON)
        self.set_image(image)
        self.set_sensitive(False)
