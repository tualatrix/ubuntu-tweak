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
import gconf
import gettext

try:
    import apt_pkg
    from PackageWorker import PackageWorker, AptCheckButton, update_apt_cache
    DISABLE = False
except ImportError:
    DISABLE = True

from Constants import *
from Factory import Factory
from Widgets import ListPack, TablePack, Mediator, MessageDialog

gettext.install(App, unicode = True)

class Nautilus(gtk.VBox, Mediator):
    """Nautilus Settings"""
    def __init__(self, parent = None):
        gtk.VBox.__init__(self)
        self.main_window = parent

        button = Factory.create("gconfcheckbutton", _("Show advanced Permissions on File Property pages"), "show_advanced_permissions")

        box = ListPack(_("<b>Settings for Nautilus behavior</b>"), (button, )) 
        self.pack_start(box, False, False, 0)

        hbox = gtk.HBox(False, 5)
        label = gtk.Label(_("Default Thumbnail Icon Size"))
        hbox.pack_start(label, False, False, 0)

        client = gconf.client_get_default()
        spinbutton = gtk.SpinButton(gtk.Adjustment(client.get_int("/apps/nautilus/icon_view/thumbnail_size"), 16, 512, 16, 16, 16))
        spinbutton.connect("value-changed", self.spinbutton_value_changed_cb)
        hbox.pack_end(spinbutton, False, False, 0)
        box.vbox.pack_start(hbox, False, False, 0)

        box = ListPack(_("<b>CD Burner</b>"), (
            Factory.create("gconfcheckbutton", _("Enable BurnProof technology"), "burnproof"),
            Factory.create("gconfcheckbutton", _("Enable OverBurn"), "overburn"),
        ))
        self.pack_start(box, False, False, 0)

        if not DISABLE:
            self.packageWorker = PackageWorker()

            self.nautilus_terminal = AptCheckButton(_("Nautilus with Open Terminal"), 'nautilus-open-terminal', self)
            self.nautilus_root = AptCheckButton(_("Nautilus with Root"), 'nautilus-gksu', self)
            self.nautilus_wallpaper = AptCheckButton(_("Nautilus with Wallpaper"), 'nautilus-wallpaper', self)
            box = ListPack(_("<b>Nautilus Extensions</b>"), (
                self.nautilus_terminal,
                self.nautilus_root,
                self.nautilus_wallpaper,
            ))

            self.button = gtk.Button(stock = gtk.STOCK_APPLY)
            self.button.connect("clicked", self.on_apply_clicked, box)
            self.button.set_sensitive(False)
            hbox = gtk.HBox(False, 0)
            hbox.pack_end(self.button, False, False, 0)

            box.vbox.pack_start(hbox, False, False, 0)

            self.pack_start(box, False, False, 0)

    def spinbutton_value_changed_cb(self, widget, data = None):
        widget.set_increments(widget.get_value(), widget.get_value())
        client = gconf.client_get_default()
        client.set_int("/apps/nautilus/icon_view/thumbnail_size", int(widget.get_value()))

    def on_apply_clicked(self, widget, box):
        to_add = []
        to_rm = []

        for widget in box.items:
            if widget.get_active():
                to_add.append(widget.pkgname)
            else:
                to_rm.append(widget.pkgname)

        self.packageWorker.perform_action(self.main_window, to_add, to_rm)

        self.button.set_sensitive(False)
        dialog = MessageDialog(_("Update Successfully!"), buttons = gtk.BUTTONS_OK)
        dialog.run()
        dialog.destroy()

        update_apt_cache()

    def colleague_changed(self):
        if self.nautilus_terminal.get_state() != self.nautilus_terminal.get_active() or\
                self.nautilus_root.get_state() != self.nautilus_root.get_active() or\
                self.nautilus_wallpaper.get_state() != self.nautilus_wallpaper.get_active():
                    self.button.set_sensitive(True)
        else:
            self.button.set_sensitive(False)

if __name__ == "__main__":
    from Utility import Test
    Test(Nautilus)
