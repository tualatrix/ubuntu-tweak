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

from ubuntutweak.modules  import TweakModule
from ubuntutweak.common.consts import *
from ubuntutweak.common.factory import WidgetFactory

computer_icon = \
{
    "label" : _('Show "Computer" icon on desktop'),
    "rename" : _('Rename'),
    "visible" : "computer_icon_visible",
    "name" : "computer_icon_name",
    "icon" : "gnome-fs-client"
}

home_icon = \
{
    "label" : _('Show "Home Folder" icon on desktop'),
    "rename" : _('Rename'),
    "visible" : "home_icon_visible",
    "name" : "home_icon_name",
    "icon" : "gnome-fs-home"
}
    
trash_icon = \
{
    "label" : _('Show "Trash" icon on desktop'),
    "rename" : _('Rename'),
    "visible" : "trash_icon_visible",
    "name" : "trash_icon_name",
    "icon" : "gnome-fs-trash-empty"
}

desktop_icon = (computer_icon, home_icon, trash_icon)

class DesktopIcon(gtk.VBox):
    def __init__(self, item):
        gtk.VBox.__init__(self)

        self.show_button = WidgetFactory.create("GconfCheckButton", 
                                                label = item["label"], 
                                                key = item["visible"])
        self.show_button.connect('toggled', self.colleague_changed)
        self.pack_start(self.show_button, False, False, 0)

        self.show_hbox = gtk.HBox(False, 10)
        self.pack_start(self.show_hbox, False, False, 0)

        if not self.show_button.get_active():
            self.show_hbox.set_sensitive(False)

        icon = gtk.image_new_from_icon_name(item["icon"], gtk.ICON_SIZE_DIALOG)
        self.show_hbox.pack_start(icon, False, False, 0)

        self.rename_button = WidgetFactory.create("StrGconfCheckButton", 
                                                  label = item["rename"], 
                                                  key = item["name"])
        self.rename_button.connect('toggled', self.colleague_changed)
        vbox = gtk.VBox(False, 5)
        self.show_hbox.pack_start(vbox, False, False, 0)
        vbox.pack_start(self.rename_button, False, False, 0)

        self.entry = WidgetFactory.create("GconfEntry", key = item["name"])
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

class Icon(TweakModule):
    __title__ = _('Desktop Icon settings')
    __desc__ = _('Change your desktop icons behavir')
    __icon__ = 'user-desktop'
    __url__ = 'http://ubuntu-tweak.com'
    __category__ = 'desktop'

    def __init__(self):
        TweakModule.__init__(self)

        self.show_button = WidgetFactory.create("GconfCheckButton",
                                                label = _("Show desktop icons"),
                                                key = "show_desktop")
        self.show_button.connect('toggled', self.colleague_changed)
        self.add_start(self.show_button, False, False, 0)

        self.show_button_box = gtk.HBox(False, 12)
        self.add_start(self.show_button_box, False, False, 0)

        if not self.show_button.get_active():
            self.show_button_box.set_sensitive(False)

        label = gtk.Label(" ")
        self.show_button_box.pack_start(label, False, False, 0)

        vbox = gtk.VBox(False, 6)
        self.show_button_box.pack_start(vbox, False, False, 0)

        for item in desktop_icon:
            vbox.pack_start(DesktopIcon(item), False, False, 0)

        button = WidgetFactory.create("GconfCheckButton", 
                                      label = _("Show \"Network\" icon on desktop"), 
                                      key = "network_icon_visible")
        vbox.pack_start(button, False, False, 0)

        button = WidgetFactory.create("GconfCheckButton", 
                                      label = _("Show mounted volumes on desktop"),
                                      key = "volumes_visible")
        vbox.pack_start(button, False, False, 0)

        button = WidgetFactory.create("GconfCheckButton",
                                      label = _('Use "Home Folder" as desktop (Logout for changes to take effect)'),
                                      key = "desktop_is_home_dir")
        vbox.pack_start(button, False, False, 0)

    def colleague_changed(self, widget):
        self.show_button_box.set_sensitive(self.show_button.get_active())

