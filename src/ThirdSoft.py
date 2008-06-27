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
import dbus
import gconf
import gobject
import gettext
import apt_pkg

from Constants import *
from Factory import Factory
from PolicyKit import PolkitButton, DbusProxy
from Widgets import ListPack, TweakPage
from aptsources.sourceslist import SourceEntry, SourcesList
from PolicyKit import PolkitButton

gettext.install(App, unicode = True)

(
    COLUMN_ENABLED,
    COLUMN_URL,
    COLUMN_COMPS,
    COLUMN_COMMENT,
) = range(4)

(
    ENTRY_URL,
    ENTRY_COMPS,
    ENTRY_COMMENT,
) = range(3)

SOURCES_DATA = [
    ['http://ppa.launchpad.net/awn-testing/ubuntu', ['main'], _('<b>Avant Window Navigator</b>: webkit based light-weight browser')],
    ['http://ppa.launchpad.net/stemp/ubuntu', ['main'], _('<b>Midori</b>: webkit based light-weight browser')],
    ['http://ppa.launchpad.net/fta/ubuntu', ['main'], _('<b>Firefox</b>: The development firefox version')],
    ['http://ppa.launchpad.net/compiz/ubuntu', ['main'], _('<b>Compiz Fusion</b>: the development Compiz Fusion')],
    ['http://ppa.launchpad.net/do-core/ubuntu', ['main'], _('<b>GNOME Do</b>: dfsafdaf')],
    ['http://ppa.launchpad.net/banshee-team/ubuntu', ['main'], _('<b>Banshee</b>: music player')],
    ['http://ppa.launchpad.net/googlegadgets/ubuntu', ['main'], _('<b>Google gadgets</b>: Google desktopt tools')],
    ['http://ppa.launchpad.net/lidaobing/ubuntu', ['main'], _('<b>chmsee</b>: chm reader')],
    ['http://ppa.launchpad.net/kubuntu-members-kde4/ubuntu', ['main'], _('<b>KDE 4</b>')],
    ['http://ppa.launchpad.net/tualatrix/ubuntu', ['main'], _('Ubuntu Tweak')],
]

class SourcesView(gtk.TreeView):
    def __init__(self):
        gtk.TreeView.__init__(self)

        apt_pkg.init()
        self.list = SourcesList()
        self.proxy = DbusProxy()
        self.model = self.__create_model()
        self.set_model(self.model)
        self.__add_column()

        self.update_model()

    def __create_model(self):
        model = gtk.ListStore(
                gobject.TYPE_BOOLEAN,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING)

        return model

    def __add_column(self):
        renderer = gtk.CellRendererToggle()
        renderer.connect('toggled', self.on_enable_toggled)
        column = gtk.TreeViewColumn(' ', renderer, active = COLUMN_ENABLED)
        self.append_column(column)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Application', renderer, markup = COLUMN_COMMENT)
        self.append_column(column)

    def update_model(self):
        for entry in SOURCES_DATA:
            enabled = False
            url = entry[ENTRY_URL]
            comps = entry[ENTRY_COMPS]
            comment = entry[ENTRY_COMMENT]

            for source in self.list:
                if url in source.str() and source.type == 'deb':
                    print "found match!" 
                    print source.str()
                    enabled = not source.disabled

            self.model.append((
                enabled,
                url,
                comps,
                comment
                ))

    def on_enable_toggled(self, cell, path):
        iter = self.model.get_iter((int(path),))

        enabled = self.model.get_value(iter, COLUMN_ENABLED)
        url = self.model.get_value(iter, COLUMN_URL)
        comment = self.model.get_value(iter, COLUMN_COMMENT)

        result = self.proxy.proxy.SetSourcesList(url, comment, not enabled, dbus_interface = self.proxy.INTERFACE)

        if result == 'enabled':
            self.model.set(iter, COLUMN_ENABLED, True)
        else:
            self.model.set(iter, COLUMN_ENABLED, False)

class ThirdSoft(TweakPage):
    def __init__(self, parent = None):
        TweakPage.__init__(self)

        self.set_title(_("Added the Third-Party Softwares"))
        self.set_description(_("Always use the newest thrid-party softwares with Ubuntu Tweak!"))

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.pack_start(sw)

        self.treeview = SourcesView()
        self.treeview.set_sensitive(False)
        self.treeview.set_rules_hint(True)
        sw.add(self.treeview)

        hbox = gtk.HBox(False, 0)
        self.pack_end(hbox, False, False, 5)

        un_lock = PolkitButton()
        un_lock.connect("clicked", self.on_polkit_action)

        hbox.pack_end(un_lock, False, False, 0)

    def on_polkit_action(self, widget):
        if widget.action == 1:
            self.treeview.set_sensitive(True)

if __name__ == "__main__":
    from Utility import Test
    gtk.gdk.threads_init()
    Test(ThirdSoft)
