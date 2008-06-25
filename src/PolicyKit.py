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

import pygtk
pygtk.require("2.0")
import gtk
import os
import gettext
import dbus

from Constants import *
from Widgets import ListPack

gettext.install(App, unicode = True)

class PolkitButton(gtk.Button):
    action = 0

    def __init__(self):
        gtk.Button.__init__(self)

        self.set_label(_('_Unlock'))
        image = gtk.image_new_from_stock(gtk.STOCK_DIALOG_AUTHENTICATION, gtk.ICON_SIZE_BUTTON)
        self.set_image(image)

        self.connect("clicked", self.on_button_clicked)

    def on_button_clicked(self, widget):
        win = widget.get_toplevel()
        xid = win.window.xid
        policykit = dbus.SessionBus().get_object('org.freedesktop.PolicyKit.AuthenticationAgent', '/')

        granted = policykit.ObtainAuthorization('com.ubuntu-tweak.tweak', dbus.UInt32(xid), dbus.UInt32(os.getpid()))

        self.action = granted

        if self.action == 1:
            image = gtk.image_new_from_stock(gtk.STOCK_YES, gtk.ICON_SIZE_BUTTON)
            self.set_image(image)
            self.set_sensitive(False)
