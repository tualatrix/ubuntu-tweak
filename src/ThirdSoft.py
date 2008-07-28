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
import time
import thread
import subprocess
import gobject
import gettext
import apt_pkg

from Constants import *
from Factory import Factory
from Settings import BoolSetting
from PolicyKit import PolkitButton, DbusProxy
from Widgets import ListPack, TweakPage, Colleague, Mediator, MessageDialog, GconfCheckButton
from aptsources.sourceslist import SourceEntry, SourcesList
from PolicyKit import PolkitButton

(
    COLUMN_ENABLED,
    COLUMN_URL,
    COLUMN_DISTRO,
    COLUMN_COMPS,
    COLUMN_LOGO,
    COLUMN_NAME,
    COLUMN_COMMENT,
    COLUMN_KEY,
) = range(8)

(
    ENTRY_URL,
    ENTRY_DISTRO,
    ENTRY_COMPS,
    ENTRY_NAME,
    ENTRY_COMMENT,
    ENTRY_LOGO,
    ENTRY_KEY,
) = range(7)

SOURCES_DATA = [
    ['http://ppa.launchpad.net/awn-core/ubuntu', 'hardy', 'main', 'AWN', _('Fully customisable dock-like window navigator'), 'awn.png'],
    ['http://deb.opera.com/opera/', 'lenny', 'non-free', 'Opera', _('The Opera Web Browser'), 'opera.png', 'opera.gpg'],
    ['http://download.skype.com/linux/repos/debian', 'stable', 'non-free', 'Skype', _('A VoIP software'), 'skype.png'],
    ['http://playonlinux.botux.net/', 'hardy', 'main', 'PlayOnLinux', _('Play windows games on your Linux'), 'playonlinux.png', 'pol.gpg'],
    ['http://ppa.launchpad.net/stemp/ubuntu', 'hardy', 'main', 'Midori', _('Webkit based lightweight web browser'), 'midori.png'],
    ['http://ppa.launchpad.net/fta/ubuntu', 'hardy', 'main', 'Firefox', _('Development Version of Mozilla Firefox 3.0/3.1, 4.0'), 'firefox.png'],
    ['http://ppa.launchpad.net/compiz/ubuntu', 'hardy', 'main', 'Compiz Fusion', _('Development version of Compiz Fusion'), 'compiz-fusion.png'],
    ['http://repository.cairo-dock.org/ubuntu', 'hardy', 'cairo-dock', 'Cairo Dock', _('A true dock for linux'), 'cairo-dock.png'],
    ['http://ppa.launchpad.net/do-core/ubuntu', 'hardy', 'main', 'GNOME Do', _('Do things as quickly as possible'), 'gnome-do.png'],
    ['http://ppa.launchpad.net/banshee-team/ubuntu', 'hardy', 'main', 'Banshee', _('Audio Management and Playback application'), 'banshee.png'],
    ['http://ppa.launchpad.net/googlegadgets/ubuntu', 'hardy', 'main', 'Google gadgets', _('Platform for running Google Gadgets on Linux'), 'gadgets.png'],
    ['http://ppa.launchpad.net/lidaobing/ubuntu', 'hardy', 'main', 'chmsee', _('A chm file viewer written in GTK+'), 'chmsee.png'],
    ['http://ppa.launchpad.net/kubuntu-members-kde4/ubuntu', 'hardy', 'main', 'KDE 4', _('K Desktop Environment 4.1'), 'kde4.png'],
    ['http://ppa.launchpad.net/tualatrix/ubuntu', 'hardy', 'main', 'Ubuntu Tweak', _('Tweak ubuntu to what you like'), 'ubuntu-tweak.png'],
    ['http://ppa.launchpad.net/gilir/ubuntu', 'hardy', 'main', 'Screenlets', _('A framework for desktop widgets'), 'screenlets.png'],
    ['http://wine.budgetdedicated.com/apt', 'hardy', 'main', 'Wine', _('A compatibility layer for running Windows programs'), 'wine.png', 'wine.gpg'],
    ['http://ppa.launchpad.net/lxde/ubuntu', 'hardy', 'main', 'LXDE', _('Lightweight X11 Desktop Environment:GPicView, PCManFM'), 'lxde.png'],
    ['http://ppa.launchpad.net/gnome-terminator/ubuntu', 'hardy', 'main', 'Terminator', _('Multiple GNOME terminals in one window'), 'terminator.png'],
    ['http://ppa.launchpad.net/gscrot/ubuntu', 'hardy', 'main', 'GScrot', _('A powerful screenshot tool'), 'gscrot.png'],
#    ['http://packages.medibuntu.org/', 'hardy', 'free non-free', 'Medibuntu', _('Multimedia, Entertainment and Distraction In Ubuntu'), 'medibuntu.png', 'medibuntu.gpg'],
#    ['http://ppa.launchpad.net/reacocard-awn/ubuntu/', 'hardy', 'main', 'AWN Trunk', _('Play windows games on your Linux')],
#    ['http://ppa.launchpad.net/bearoso/ubuntu', 'hardy', 'main', 'snes9x-gtk', _('Hello World')],
]

class UpdateCacheDialog:
    """This class is modified from Software-Properties"""
    def __init__(self, parent):
        self.parent = parent

        self.dialog = gtk.MessageDialog(parent, buttons = gtk.BUTTONS_YES_NO)
        self.dialog.set_markup(_('<b><big>The information about available software is out-of-date</big></b>\n\nTo install software and updates from newly added or changed sources, you have to reload the information about available software.\n\nYou need a working internet connection to continue.'))

    def update_cache(self, window_id, lock):
        """start synaptic to update the package cache"""
        try:
            apt_pkg.PkgSystemUnLock()
        except SystemError:
            pass
        cmd = []
        if os.getuid() != 0:
            cmd = ['/usr/bin/gksu',
                   '--desktop', '/usr/share/applications/synaptic.desktop',
                   '--']
        
        cmd += ['/usr/sbin/synaptic', '--hide-main-window',
               '--non-interactive',
               '--parent-window-id', '%s' % (window_id),
               '--update-at-startup']
        subprocess.call(cmd)
        lock.release()

    def run(self):
        """run the dialog, and if reload was pressed run synaptic"""
        res = self.dialog.run()
        self.dialog.hide()
        if res == gtk.RESPONSE_YES:
            self.parent.set_sensitive(False)
            lock = thread.allocate_lock()
            lock.acquire()
            t = thread.start_new_thread(self.update_cache,
                                       (self.parent.window.xid, lock))
            while lock.locked():
                while gtk.events_pending():
                    gtk.main_iteration()
                    time.sleep(0.05)
            self.parent.set_sensitive(True)
        return res

class SourcesView(gtk.TreeView, Colleague):
    def __init__(self, mediator):
        gtk.TreeView.__init__(self)
        Colleague.__init__(self, mediator)

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
                gobject.TYPE_STRING,
                gtk.gdk.Pixbuf,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING)

        return model

    def __add_column(self):
        renderer = gtk.CellRendererToggle()
        renderer.connect('toggled', self.on_enable_toggled)
        column = gtk.TreeViewColumn(' ', renderer, active = COLUMN_ENABLED)
        column.set_sort_column_id(COLUMN_ENABLED)
        self.append_column(column)

        column = gtk.TreeViewColumn(_('Third Party Sources'))
        column.set_sort_column_id(COLUMN_NAME)
        column.set_spacing(5)
        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, pixbuf = COLUMN_LOGO)

        renderer = gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.set_attributes(renderer, markup = COLUMN_COMMENT)

        self.append_column(column)

    def update_model(self):
        for entry in SOURCES_DATA:
            enabled = False
            url = entry[ENTRY_URL]
            comps = entry[ENTRY_COMPS]
            distro = entry[ENTRY_DISTRO]
            logo = gtk.gdk.pixbuf_new_from_file(os.path.join(DATA_DIR, 'aptlogos', entry[ENTRY_LOGO]))
            name = entry[ENTRY_NAME]
            comment = entry[ENTRY_COMMENT]
            try:
                key = os.path.join(DATA_DIR, 'aptkeys', entry[ENTRY_KEY])
            except IndexError:
                key = ''

            for source in self.list:
                if url in source.str() and source.type == 'deb':
                    enabled = not source.disabled

            self.model.append((
                enabled,
                url,
                distro,
                comps,
                logo,
                name,
                '<b>%s</b>\n%s' % (name, comment),
                key,
                ))

    def on_enable_toggled(self, cell, path):
        iter = self.model.get_iter((int(path),))

        enabled = self.model.get_value(iter, COLUMN_ENABLED)
        url = self.model.get_value(iter, COLUMN_URL)
        distro = self.model.get_value(iter, COLUMN_DISTRO)
        name = self.model.get_value(iter, COLUMN_NAME)
        comps = self.model.get_value(iter, COLUMN_COMPS)
        key = self.model.get_value(iter, COLUMN_KEY)

        if key:
            self.proxy.add_aptkey(key)

        result = self.proxy.set_entry(url, distro, comps, name, not enabled)

        if result == 'enabled':
            self.model.set(iter, COLUMN_ENABLED, True)
        else:
            self.model.set(iter, COLUMN_ENABLED, False)
            
        self.state_changed(cell)
   
class ThirdSoft(TweakPage, Mediator):
    def __init__(self):
        TweakPage.__init__(self, 
                _('Third Party Softwares Sources'), 
                _('You can always follow the latest version of an application.\nAnd new applications can be installed through Add/Remove.'))

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.pack_start(sw)

        self.treeview = SourcesView(self)
        self.treeview.set_sensitive(False)
        self.treeview.set_rules_hint(True)
        sw.add(self.treeview)

        hbox = gtk.HBox(False, 0)
        self.pack_end(hbox, False, False, 5)

        un_lock = PolkitButton()
        un_lock.connect('authenticated', self.on_polkit_action)
        hbox.pack_end(un_lock, False, False, 5)

        self.refresh_button = gtk.Button(stock = gtk.STOCK_REFRESH)
        self.refresh_button.set_sensitive(False)
        self.refresh_button.connect('clicked', self.on_refresh_button_clicked)
        hbox.pack_end(self.refresh_button, False, False, 5)

    def on_polkit_action(self, widget):
        gtk.gdk.threads_enter()
        if widget.action == 1:
            self.treeview.set_sensitive(True)
            WARNING_KEY = '/apps/ubuntu-tweak/disable_thidparty_warning'

            if not BoolSetting(WARNING_KEY).get_bool():
                dialog = MessageDialog(_('<b><big>Warning</big></b>\n\nIt is possible security rish to use packages from third party sources. Please be careful.'), type = gtk.MESSAGE_WARNING, buttons = gtk.BUTTONS_OK)
                vbox = dialog.get_child()
                hbox = gtk.HBox()
                vbox.pack_start(hbox, False, False, 0)
                checkbutton = GconfCheckButton(_('Never show this dialog'), WARNING_KEY)
                hbox.pack_end(checkbutton, False, False, 0)
                hbox.show_all()

                dialog.run()
                dialog.destroy()
        elif widget.error == -1:
            dialog = MessageDialog(_('<b><big>Could not authenticate</big></b>\n\nAn unexpected error has occurred.'), type = gtk.MESSAGE_ERROR, buttons = gtk.BUTTONS_CLOSE)
            dialog.run()
            dialog.destroy()

        gtk.gdk.threads_leave()

    def colleague_changed(self):
        self.refresh_button.set_sensitive(True)
    
    def on_refresh_button_clicked(self, widget):
        dialog = UpdateCacheDialog(widget.get_toplevel())
        res = dialog.run()
        self.treeview.proxy.set_liststate('normal')
        widget.set_sensitive(False)

        dialog = gtk.MessageDialog(buttons = gtk.BUTTONS_OK)
        dialog.set_markup(_('<b><big>The software information is up-to-date now</big></b>.\n\nYou need to restart Ubuntu Tweak if you want to install the new applications through Add/Remove.'))
        dialog.run()
        dialog.destroy()

if __name__ == '__main__':
    from Utility import Test
    gtk.gdk.threads_init()
    Test(ThirdSoft)
