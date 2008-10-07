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
import gconf

from common.Consts import *
from common.Widgets import TweakPage
from common.Factory import Factory

computer_icon = \
{
    "label" : _("Show \"Computer\" icon on desktop"),
    "rename" : _("Rename the \"Computer\" icon: "),
    "visible" : "computer_icon_visible",
    "name" : "computer_icon_name",
    "icon" : "gnome-fs-client"
}

home_icon = \
{
    "label" : _("Show \"Home\" icon on desktop"),
    "rename" : _("Rename the \"Home\" icon: "),
    "visible" : "home_icon_visible",
    "name" : "home_icon_name",
    "icon" : "gnome-fs-home"
}
    
trash_icon = \
{
    "label" : _("Show \"Trash\" icon on desktop"),
    "rename" : _("Rename the \"Trash\" icon: "),
    "visible" : "trash_icon_visible",
    "name" : "trash_icon_name",
    "icon" : "gnome-fs-trash-empty"
}

desktop_icon = (computer_icon, home_icon, trash_icon)

class DesktopIcon(gtk.VBox):
    def __init__(self, item):
        gtk.VBox.__init__(self)

        self.show_button = Factory.create("gconfcheckbutton", item["label"], item["visible"])
        self.show_button.connect('toggled', self.colleague_changed)
        self.pack_start(self.show_button, False, False, 0)

        self.show_hbox = gtk.HBox(False, 10)
        self.pack_start(self.show_hbox, False, False, 0)

        if not self.show_button.get_active():
            self.show_hbox.set_sensitive(False)

        icon = gtk.image_new_from_icon_name(item["icon"], gtk.ICON_SIZE_DIALOG)
        self.show_hbox.pack_start(icon, False, False, 0)

        self.rename_button = Factory.create("strgconfcheckbutton", item["rename"], item["name"])
        self.rename_button.connect('toggled', self.colleague_changed)
        vbox = gtk.VBox(False, 5)
        self.show_hbox.pack_start(vbox, False, False, 0)
        vbox.pack_start(self.rename_button, False, False, 0)

        self.entry = Factory.create("gconfentry", item["name"])
        self.entry.connect('focus-out-event', self.entry_focus_out)
        if not self.rename_button.get_active():
            self.entry.set_sensitive(False)
        vbox.pack_start(self.entry, False, False, 0)

    def entry_focus_out(self, widget, event):
        self.entry.get_gsetting().set_string(self.entry.get_text())

    def colleague_changed(self, widget):
        self.show_hbox.set_sensitive(self.show_button.get_active())
        active = self.rename_button.get_active()
        if active:
            self.entry.set_sensitive(True)
            self.entry.grab_focus()
        else:
            self.entry.set_sensitive(False)
            self.entry.get_gsetting().unset()
            self.entry.set_text(_("Unset"))

class Icon(TweakPage):
    """Desktop Icon settings"""

    def __init__(self):
        TweakPage.__init__(self, _("Desktop Icon settings"))

        self.show_button = Factory.create("gconfcheckbutton", _("Show desktop icons"), "show_desktop")
        self.show_button.connect('toggled', self.colleague_changed)
        self.pack_start(self.show_button, False, False, 10)

        self.show_button_box = gtk.HBox(False, 10)
        self.pack_start(self.show_button_box, False, False,0)

        if not self.show_button.get_active():
            self.show_button_box.set_sensitive(False)

        label = gtk.Label(" ")
        self.show_button_box.pack_start(label, False, False, 0)

        vbox = gtk.VBox(False, 5)
        self.show_button_box.pack_start(vbox, False, False, 0)

        client = gconf.client_get_default()
        for item in desktop_icon:
            vbox.pack_start(DesktopIcon(item), False, False, 0)

        button = Factory.create("gconfcheckbutton", _("Show \"Network\" icon on desktop"), "network_icon_visible")
        vbox.pack_start(button, False, False, 0)

        button = Factory.create("gconfcheckbutton", _("Show Mounted Volumes on desktop"), "volumes_visible")
        vbox.pack_start(button, False, False, 0)

        button = Factory.create("gconfcheckbutton", _("Use Home Folder as the desktop(Logout for changes to take effect)"), "desktop_is_home_dir")
        vbox.pack_start(button, False, False, 0)

    def colleague_changed(self, widget):
        self.show_button_box.set_sensitive(self.show_button.get_active())

if __name__ == "__main__":
    from Utility import Test
    Test(Icon)
