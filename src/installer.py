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
import gettext
import gobject
import pango

from common.consts import *
from common.appdata import *
from common.utils import *
from common.widgets import TweakPage
from common.widgets.dialogs import InfoDialog
from xdg.DesktopEntry import DesktopEntry

try:
    from common.package import PackageWorker, PackageInfo, update_apt_cache
    DISABLE = False
except ImportError:
    DISABLE = True

DESKTOP_DIR = '/usr/share/app-install/desktop/'
ICON_DIR = os.path.join(DATA_DIR, 'applogos')

(
    COLUMN_INSTALLED,
    COLUMN_ICON,
    COLUMN_NAME,
    COLUMN_DESC,
    COLUMN_DISPLAY,
    COLUMN_CATE,
) = range(6)

P2P = (_('File-Sharing Clients'), 'p2p.png')
Image = (_('Image Tools'), 'image.png')
Sound = (_('Sound Tools'), 'sound.png')
Video = (_('Video Tools'), 'video.png')
Text = (_('Text Tools'), 'text.png')
IM = (_('Instant Messengers'), 'im.png')
Internet = (_('Internet Tools'), 'internet.png')
FTP = (_('FTP Tools'), 'ftp.png')
Desktop = (_('Desktop Tools'), 'desktop.png')
Disk = (_('CD/Disk Tools'), 'cd.png')
Develop = (_('Development'), 'develop.png')
Emulator = (_('Emulators'), 'emulator.png')
Mail = (_('E-mail Tools'), 'mail.png')

CATES_DATA = (P2P, Image, Sound, Video, Text, IM, Internet, FTP, Desktop, Disk, Develop, Emulator, Mail)

data = \
(
    ('agave', Image),
    ('amule', P2P),
    ('amarok-nightly', Sound),
    ('anjuta', Develop),
    ('audacious', Sound),
    ('audacity', Sound),
    ('avant-window-navigator', Desktop),
    ('avant-window-navigator-trunk', Desktop),
    ('avidemux', Video),
    ('azureus', P2P),
    ('banshee', Sound),
    ('blueman', P2P),
    ('cairo-dock', Desktop),
    ('chmsee', Text),
    ('chromium-browser', Internet),
    ('compizconfig-settings-manager', Desktop),
    ('codeblocks', Develop),
    ('devhelp', Develop),
    ('deluge-torrent', P2P),
    ('eclipse', Develop),
    ('emesene', IM),
    ('empathy', IM),
    ('eioffice-personal', Text),
    ('exaile', Sound),
    ('filezilla', FTP),
    ('pcmanfm', Desktop),
    ('galaxium', IM),
    ('gajim', IM),
    ('geany', Develop),
    ('gftp', FTP),
    ('ghex', Text),
    ('gmail-notify', Mail),
    ('gnome-do', Desktop),
    ('gnome-globalmenu', Desktop),
    ('googleearth', Internet),
    ('google-gadgets', Desktop),
    ('gparted', Disk),
    ('gpicview', Image),
    ('gscrot', Image),
    ('gtk-recordmydesktop', Video),
    ('gwibber', Internet),
    ('gtg', Text),
    ('isomaster', Disk),
    ('inkscape', Image),
    ('ibus', Text),
    ('ibus-pinyin', Text),
    ('ibus-table', Text),
    ('kino', Video),
    ('lastfm', Internet),
    ('leafpad', Text),
    ('liferea', Internet),
    ('mail-notification', Mail),
    ('meld', Text),
    ('mirage', Image),
    ('miro', Video),
    ('midori', Internet),
    ('monodevelop', Develop),
    ('mplayer', Video),
    ('netbeans', Develop),
    ('nautilus-dropbox', Internet),
    ('opera', Internet),
    ('playonlinux', Emulator),
    ('screenlets', Desktop),
    ('shutter', Image),
    ('skype', IM),
    ('smplayer', Video),
    ('soundconverter', Sound),
    ('stardict', Desktop),
    ('synapse', IM),
    ('tasque', Desktop),
    ('terminator', Emulator),
    ('transmission-gtk', P2P),
    ('ubuntu-restricted-extras', Desktop),
    ('virtualbox-ose', Emulator),
    ('vlc', Video),
    ('vmware-player', Emulator),
    ('wine', Emulator),
    ('wine-doors', Emulator),
    ('xbmc', Desktop),
)

class Installer(TweakPage):
    def __init__(self):
        TweakPage.__init__(self, 
                _('Add/Remove Applications'),
                _('A simple but more effecient method for finding and installing popular packages than the default Add/Remove.'))

        update_apt_cache(True)

        self.to_add = []
        self.to_rm = []
        self.packageWorker = PackageWorker()

        vbox = gtk.VBox(False, 8)
        self.pack_start(vbox)

        hbox = gtk.HBox(False, 0)
        vbox.pack_start(hbox, False, False, 0)

        combobox = self.create_category()
        combobox.set_active(0)
        combobox.connect('changed', self.on_category_changed)
        hbox.pack_end(combobox, False, False, 0)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        vbox.pack_start(sw)

        # create tree view
        treeview = self.create_treeview()
        treeview.set_rules_hint(True)
        treeview.set_search_column(COLUMN_NAME)
        sw.add(treeview)

        # button
        hbox = gtk.HBox(False, 0)
        vbox.pack_end(hbox, False ,False, 0)

        self.button = gtk.Button(stock = gtk.STOCK_APPLY)
        self.button.connect('clicked', self.on_apply_clicked)
        self.button.set_sensitive(False)
        hbox.pack_end(self.button, False, False, 0)

        self.show_all()

    def create_category(self):
        liststore = gtk.ListStore(gtk.gdk.Pixbuf,
                gobject.TYPE_STRING)

        iter = liststore.append()
        liststore.set(iter, 
                0, gtk.gdk.pixbuf_new_from_file(os.path.join(DATA_DIR, 'appcates', 'all.png')),
                1, _('All Categories'))

        for item in CATES_DATA:
            iter = liststore.append()
            liststore.set(iter, 
                    0, gtk.gdk.pixbuf_new_from_file(os.path.join(DATA_DIR, 'appcates', item[1])),
                    1, item[0])

        combobox = gtk.ComboBox(liststore)
        textcell = gtk.CellRendererText()
        pixbufcell = gtk.CellRendererPixbuf()
        combobox.pack_start(pixbufcell, False)
        combobox.pack_start(textcell, True)
        combobox.add_attribute(pixbufcell, 'pixbuf', 0)
        combobox.add_attribute(textcell, 'text', 1)

        return combobox

    def on_category_changed(self, widget, data = None):
        index = widget.get_active()
        if index:
            liststore = widget.get_model()
            iter = liststore.get_iter(index)
            self.filter = liststore.get_value(iter, 1)
        else:
            self.filter = None

        self.update_model()

    def update_model(self):
        self.model.clear()

        icon = gtk.icon_theme_get_default()

        for item in data:
            appname = item[0]
            category = item[-1][0] 

            try:
                iconpath = get_app_logo(appname)
                pixbuf = gtk.gdk.pixbuf_new_from_file(iconpath)
            except gobject.GError:
                pixbuf = icon.load_icon(gtk.STOCK_MISSING_IMAGE, 32, 0)

            try:
                package = PackageInfo(appname)
                is_installed = package.check_installed()
                disname = package.get_name()
                desc = get_app_describ(appname)
            except KeyError:
                continue

            if self.filter == None:
                if appname in self.to_add or appname in self.to_rm:
                    self.model.append((not is_installed,
                            pixbuf,
                            appname,
                            desc,
                            '<span foreground="#ffcc00"><b>%s</b>\n%s</span>' % (disname, desc),
                            category))
                else:
                    self.model.append((is_installed,
                            pixbuf,
                            appname,
                            desc,
                            '<b>%s</b>\n%s' % (disname, desc),
                            category))
            else:
                if self.filter == category:
                    if appname in self.to_add or appname in self.to_rm:
                        self.model.append((not is_installed,
                                pixbuf,
                                appname,
                                desc,
                                '<span foreground="#ffcc00"><b>%s</b>\n%s</span>' % (disname, desc),
                                category))
                    else:
                        self.model.append((is_installed,
                                pixbuf,
                                appname,
                                desc,
                                '<b>%s</b>\n%s' % (disname, desc),
                                category))

    def deep_update(self):
        update_apt_cache()
        self.update_model()
        
    def on_install_toggled(self, cell, path):
        iter = self.model.get_iter((int(path),))
        is_installed = self.model.get_value(iter, COLUMN_INSTALLED)
        appname = self.model.get_value(iter, COLUMN_NAME)
        disname = PackageInfo(appname).get_name()
        desc = self.model.get_value(iter, COLUMN_DESC)
        display = self.model.get_value(iter, COLUMN_DISPLAY)

        is_installed = not is_installed
        if is_installed:
            if appname in self.to_rm:
                self.to_rm.remove(appname)
                self.model.set(iter, COLUMN_DISPLAY, '<b>%s</b>\n%s' % (disname, desc))
            else:
                self.to_add.append(appname)
                self.model.set(iter, COLUMN_DISPLAY, '<span foreground="#ffcc00"><b>%s</b>\n%s</span>' % (disname, desc))
        else:
            if appname in self.to_add:
                self.to_add.remove(appname)
                self.model.set(iter, COLUMN_DISPLAY, '<b>%s</b>\n%s' % (disname, desc))
            else:
                self.to_rm.append(appname)
                self.model.set(iter, COLUMN_DISPLAY, '<span foreground="#ffcc00"><b>%s</b>\n%s</span>' % (disname, desc))

        self.model.set(iter, COLUMN_INSTALLED, is_installed)
        self.colleague_changed()

    def create_treeview(self):
        self.model = gtk.ListStore(
                        gobject.TYPE_BOOLEAN,
                        gtk.gdk.Pixbuf,
                        gobject.TYPE_STRING,
                        gobject.TYPE_STRING,
                        gobject.TYPE_STRING,
                        gobject.TYPE_STRING)
        treeview = gtk.TreeView()

        # column for is_installed toggles
        renderer = gtk.CellRendererToggle()
        renderer.connect('toggled', self.on_install_toggled)
        column = gtk.TreeViewColumn(' ', renderer, active = COLUMN_INSTALLED)
        column.set_sort_column_id(COLUMN_INSTALLED)
        treeview.append_column(column)

        # column for application
        column = gtk.TreeViewColumn('Applications')
        column.set_sort_column_id(COLUMN_NAME)
        column.set_spacing(5)
        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, pixbuf = COLUMN_ICON)

        renderer = gtk.CellRendererText()
        renderer.set_property('ellipsize', pango.ELLIPSIZE_END)
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'markup', COLUMN_DISPLAY)
        treeview.append_column(column)
        
        self.filter = None
        self.update_model()
        treeview.set_model(self.model)

        return treeview

    def on_apply_clicked(self, widget, data = None):
        self.packageWorker.perform_action(widget.get_toplevel(), self.to_add, self.to_rm)

        done = True
        update_apt_cache()

        for pkg in self.to_add:
            if not PackageInfo(pkg).check_installed():
                done = False
                break

        for pkg in self.to_rm:
            if PackageInfo(pkg).check_installed():
                done = False
                break

        if done:
            self.button.set_sensitive(False)
            InfoDialog(_('Update Successful!')).launch()
        else:
            InfoDialog(_('Update Failed!')).launch()

        self.to_add = []
        self.to_rm = []
        self.update_model()

    def colleague_changed(self):
        if self.to_add or self.to_rm:
            self.button.set_sensitive(True)
        else:
            self.button.set_sensitive(False)

if __name__ == '__main__':
    from utility import Test
    Test(Installer)
