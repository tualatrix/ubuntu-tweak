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
import gconf
import gettext

try:
    from common.package import PackageWorker, AptCheckButton, update_apt_cache
    DISABLE = False
except ImportError:
    DISABLE = True

from common.factory import Factory
from common.widgets import ListPack, TablePack, TweakPage
from common.widgets.dialogs import InfoDialog

class Nautilus(TweakPage):
    """Nautilus Settings"""
    def __init__(self):
        TweakPage.__init__(self)

        button = Factory.create("gconfcheckbutton", _("Show advanced permissions on Permissions tab of File Property"), "show_advanced_permissions")

        box = ListPack(_("File Browser"), (button, )) 
        self.pack_start(box, False, False, 0)

        hbox = gtk.HBox(False, 5)
        label = gtk.Label(_("Default thumbnail icon Size"))
        hbox.pack_start(label, False, False, 0)

        client = gconf.client_get_default()
        init_size = client.get_int("/apps/nautilus/icon_view/thumbnail_size")
        adjust = gtk.Adjustment(init_size, 16, 512, 16, 16)
        spinbutton = gtk.SpinButton(adjust)
        spinbutton.connect("value-changed", self.spinbutton_value_changed_cb)
        hbox.pack_end(spinbutton, False, False, 0)
        box.vbox.pack_start(hbox, False, False, 0)

        box = ListPack(_("CD Burner"), (
            Factory.create("gconfcheckbutton", _("Enable BurnProof technology"), "burnproof"),
            Factory.create("gconfcheckbutton", _("Enable OverBurn"), "overburn"),
        ))
        self.pack_start(box, False, False, 0)

        if not DISABLE:
            update_apt_cache(True)
            self.packageWorker = PackageWorker()

            self.nautilus_terminal = AptCheckButton(_('Nautilus with Open Terminal'), 'nautilus-open-terminal')
            self.nautilus_terminal.connect('toggled', self.colleague_changed)
            self.nautilus_root = AptCheckButton(_('Nautilus with Root Privileges'), 'nautilus-gksu')
            self.nautilus_root.connect('toggled', self.colleague_changed)
            self.nautilus_wallpaper = AptCheckButton(_('Nautilus with Wallpaper'), 'nautilus-wallpaper')
            self.nautilus_wallpaper.connect('toggled', self.colleague_changed)
            box = ListPack(_("Nautilus Extensions"), (
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

        state = self.packageWorker.perform_action(widget.get_toplevel(), to_add, to_rm)

        if state == 0:
            self.button.set_sensitive(False)
            InfoDialog(_("Update Successfully!")).launch()
        else:
            InfoDialog(_("Update Failed!")).launch()

        update_apt_cache()

    def colleague_changed(self, widget):
        if self.nautilus_terminal.get_state() != self.nautilus_terminal.get_active() or\
                self.nautilus_root.get_state() != self.nautilus_root.get_active() or\
                self.nautilus_wallpaper.get_state() != self.nautilus_wallpaper.get_active():
                    self.button.set_sensitive(True)
        else:
            self.button.set_sensitive(False)

if __name__ == "__main__":
    from utility import Test
    Test(Nautilus)
