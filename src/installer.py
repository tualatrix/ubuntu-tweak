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
from common.utils import *
from common.widgets import TweakPage
from common.widgets.dialogs import InfoDialog
from common.appdata import get_app_logo, get_app_describ
from xdg.DesktopEntry import DesktopEntry

try:
    from common.package import package_worker, PackageInfo
    DISABLE = False
except ImportError:
    DISABLE = True

DESKTOP_DIR = '/usr/share/app-install/desktop/'
ICON_DIR = os.path.join(DATA_DIR, 'applogos')

(
    COLUMN_INSTALLED,
    COLUMN_ICON,
    COLUMN_PKG,
    COLUMN_NAME,
    COLUMN_DESC,
    COLUMN_DISPLAY,
    COLUMN_CATE,
) = range(7)

(
    CATE_ID,
    CATE_NAME,
    CATE_ICON,
) = range(3)

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

def create_cate(*items):
    new = []
    for i, item in enumerate(items):
        list = [i]
        list.extend(item)
        new.append(list)
    return new

CATES_DATA = create_cate(P2P, Image, Sound, Video, Text, IM, Internet, FTP, Desktop, Disk, Develop, Emulator, Mail)

APPS = \
{
    'agave': Image,
    'amule': P2P,
    'amarok-nightly': Sound,
    'anjuta': Develop,
    'audacious': Sound,
    'audacity': Sound,
    'avant-window-navigator': Desktop,
    'avant-window-navigator-trunk': Desktop,
    'avidemux': Video,
    'azureus': P2P,
    'banshee': Sound,
    'blueman': P2P,
    'backintime-gnome': Desktop,
    'backintime-kde4': Desktop,
    'cairo-dock': Desktop,
    'chmsee': Text,
    'christine': Sound,
    'chromium-browser': Internet,
    'compizconfig-settings-manager': Desktop,
    'codeblocks': Develop,
    'devhelp': Develop,
    'deluge-torrent': P2P,
    'eclipse': Develop,
    'emesene': IM,
    'empathy': IM,
    'eioffice-personal': Text,
    'exaile': Sound,
    'filezilla': FTP,
    'pcmanfm': Desktop,
    'galaxium': IM,
    'gajim': IM,
    'geany': Develop,
    'gftp': FTP,
    'ghex': Text,
    'gmail-notify': Mail,
    'gnote': Text,
    'gnome-do': Desktop,
    'gnome-globalmenu': Desktop,
    'gnome-colors': Desktop,
    'googleearth': Internet,
    'google-gadgets': Desktop,
    'google-chrome-unstable': Internet,
    'gparted': Disk,
    'gpicview': Image,
    'gtk-recordmydesktop': Video,
    'gwibber': Internet,
    'gtg': Text,
    'isomaster': Disk,
    'inkscape': Image,
    'ibus': Text,
    'ibus-pinyin': Text,
    'ibus-table': Text,
    'kino': Video,
    'lastfm': Internet,
    'leafpad': Text,
    'liferea': Internet,
    'mail-notification': Mail,
    'meld': Text,
    'mirage': Image,
    'miro': Video,
    'midori': Internet,
    'moovida': Sound,
    'monodevelop': Develop,
    'mplayer': Video,
    'netbeans': Develop,
    'nautilus-dropbox': Internet,
    'opera': Internet,
    'playonlinux': Emulator,
    'picasa': Image,
    'screenlets': Desktop,
    'specto': Desktop,
    'shutter': Image,
    'skype': IM,
    'smplayer': Video,
    'soundconverter': Sound,
    'stardict': Desktop,
    'synapse': IM,
    'spicebird': Internet,
    'tasque': Desktop,
    'terminator': Emulator,
    'transmission-gtk': P2P,
    'ubudsl': Internet,
    'ubuntu-restricted-extras': Desktop,
    'virtualbox-ose': Emulator,
    'virtualbox-3.0': Emulator,
    'vlc': Video,
    'vmware-player': Emulator,
    'wine': Emulator,
    'wine-doors': Emulator,
    'xbmc': Desktop,
}

class AppView(gtk.TreeView):
    __gsignals__ = {
        'changed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_INT,))
    }

    def __init__(self):
        gtk.TreeView.__init__(self)

        self.to_add = []
        self.to_rm = []
        self.filter = None

        model = self.__create_model()
        self.__add_columns()
        self.set_model(model)

        self.set_rules_hint(True)
        self.set_search_column(COLUMN_NAME)

        self.show_all()

    def __create_model(self):
        model = gtk.ListStore(
                        gobject.TYPE_BOOLEAN,
                        gtk.gdk.Pixbuf,
                        gobject.TYPE_STRING,
                        gobject.TYPE_STRING,
                        gobject.TYPE_STRING,
                        gobject.TYPE_STRING,
                        gobject.TYPE_STRING)

        model.set_sort_column_id(COLUMN_NAME, gtk.SORT_ASCENDING)

        return model

    def __add_columns(self):
        renderer = gtk.CellRendererToggle()
        renderer.connect('toggled', self.on_install_toggled)
        column = gtk.TreeViewColumn(' ', renderer, active = COLUMN_INSTALLED)
        column.set_sort_column_id(COLUMN_INSTALLED)
        self.append_column(column)

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
        self.append_column(column)

    def update_model(self, apps, cates=None):
        '''apps is a list to iter pkgname,
        cates is a dict to find what the category the pkg is
        '''
        model = self.get_model()
        model.clear()

        icon = gtk.icon_theme_get_default()

        for pkgname in apps:
            if cates:
                category = cates[pkgname][0]
            else:
                category = 0

            pixbuf = get_app_logo(pkgname)

            try:
                package = PackageInfo(pkgname)
                is_installed = package.check_installed()
                appname = package.get_name()
                desc = get_app_describ(pkgname)
            except KeyError:
                continue

            if self.filter == None:
                if pkgname in self.to_add or pkgname in self.to_rm:
                    model.append((not is_installed,
                            pixbuf,
                            pkgname,
                            appname,
                            desc,
                            '<span foreground="#ffcc00"><b>%s</b>\n%s</span>' % (appname, desc),
                            category))
                else:
                    model.append((is_installed,
                            pixbuf,
                            pkgname,
                            appname,
                            desc,
                            '<b>%s</b>\n%s' % (appname, desc),
                            category))
            else:
                if self.filter == category:
                    if pkgname in self.to_add or pkgname in self.to_rm:
                        model.append((not is_installed,
                                pixbuf,
                                pkgname,
                                appname,
                                desc,
                                '<span foreground="#ffcc00"><b>%s</b>\n%s</span>' % (appname, desc),
                                category))
                    else:
                        model.append((is_installed,
                                pixbuf,
                                pkgname,
                                appname,
                                desc,
                                '<b>%s</b>\n%s' % (appname, desc),
                                category))

    def on_install_toggled(self, cell, path):
        model = self.get_model()

        iter = model.get_iter((int(path),))
        is_installed = model.get_value(iter, COLUMN_INSTALLED)
        pkgname = model.get_value(iter, COLUMN_PKG)
        appname = model.get_value(iter, COLUMN_NAME)
        desc = model.get_value(iter, COLUMN_DESC)

        is_installed = not is_installed
        if is_installed:
            if pkgname in self.to_rm:
                self.to_rm.remove(pkgname)
                model.set(iter, COLUMN_DISPLAY, '<b>%s</b>\n%s' % (appname, desc))
            else:
                self.to_add.append(pkgname)
                model.set(iter, COLUMN_DISPLAY, '<span foreground="#ffcc00"><b>%s</b>\n%s</span>' % (appname, desc))
        else:
            if pkgname in self.to_add:
                self.to_add.remove(pkgname)
                model.set(iter, COLUMN_DISPLAY, '<b>%s</b>\n%s' % (appname, desc))
            else:
                self.to_rm.append(pkgname)
                model.set(iter, COLUMN_DISPLAY, '<span foreground="#ffcc00"><b>%s</b>\n%s</span>' % (appname, desc))

        model.set(iter, COLUMN_INSTALLED, is_installed)

        self.emit('changed', len(self.to_add) + len(self.to_rm))

class Installer(TweakPage):
    def __init__(self):
        TweakPage.__init__(self, 
                _('Add/Remove Applications'),
                _('A simple but more effecient method for finding and installing popular packages than the default Add/Remove.'))

        self.package_worker = package_worker

        vbox = gtk.VBox(False, 8)
        self.pack_start(vbox)

        hbox = gtk.HBox(False, 0)
        vbox.pack_start(hbox, False, False, 0)

        combobox = self.create_category()
        self.update_cate_model()
        combobox.set_active(0)
        combobox.connect('changed', self.on_category_changed)
        hbox.pack_end(combobox, False, False, 0)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        vbox.pack_start(sw)

        # create tree view
        self.treeview = AppView()
        self.treeview.update_model(APPS.keys(), APPS)
        self.treeview.connect('changed', self.on_app_status_changed)
        sw.add(self.treeview)

        # button
        hbox = gtk.HBox(False, 0)
        vbox.pack_end(hbox, False ,False, 0)

        self.button = gtk.Button(stock = gtk.STOCK_APPLY)
        self.button.connect('clicked', self.on_apply_clicked)
        self.button.set_sensitive(False)
        hbox.pack_end(self.button, False, False, 0)

        self.show_all()

    def create_category(self):
        self.cate_model = gtk.ListStore(gobject.TYPE_INT,
                                gobject.TYPE_STRING,
                                gtk.gdk.Pixbuf)

        combobox = gtk.ComboBox(self.cate_model)
        textcell = gtk.CellRendererText()
        pixbufcell = gtk.CellRendererPixbuf()
        combobox.pack_start(pixbufcell, False)
        combobox.pack_start(textcell, True)
        combobox.add_attribute(textcell, 'text', CATE_NAME)
        combobox.add_attribute(pixbufcell, 'pixbuf', CATE_ICON)

        return combobox

    def update_cate_model(self):
        self.cate_model.clear()

        iter = self.cate_model.append()
        self.cate_model.set(iter, 
                CATE_ID, 0,
                CATE_NAME, _('All Categories'),
                CATE_ICON, gtk.gdk.pixbuf_new_from_file(os.path.join(DATA_DIR, 'appcates', 'all.png')))

        for item in CATES_DATA:
            iter = self.cate_model.append()
            self.cate_model.set(iter, 
                    CATE_ID, item[0],
                    CATE_NAME, item[1],
                    CATE_ICON, gtk.gdk.pixbuf_new_from_file(os.path.join(DATA_DIR, 'appcates', item[2])))

    def on_category_changed(self, widget, data = None):
        index = widget.get_active()
        if index:
            liststore = widget.get_model()
            iter = liststore.get_iter(index)
            self.treeview.filter = liststore.get_value(iter, 1)
        else:
            self.treeview.filter = None

        self.treeview.update_model(APPS.keys(), APPS)

    def deep_update(self):
        package_worker.update_apt_cache(True)
        self.treeview.update_model(APPS.keys(), APPS)

    def normal_update(self):
        self.treeview.update_model(APPS.keys(), APPS)

    def on_apply_clicked(self, widget, data = None):
        to_rm = self.treeview.to_rm
        to_add = self.treeview.to_add
        self.package_worker.perform_action(widget.get_toplevel(), to_add, to_rm)

        package_worker.update_apt_cache(True)

        done = package_worker.get_install_status(to_add, to_rm)

        if done:
            self.button.set_sensitive(False)
            InfoDialog(_('Update Successful!')).launch()
        else:
            InfoDialog(_('Update Failed!')).launch()

        self.treeview.to_add = []
        self.treeview.to_rm = []
        self.treeview.update_model(APPS.keys(), APPS)

    def on_app_status_changed(self, widget, i):
        if i:
            self.button.set_sensitive(True)
        else:
            self.button.set_sensitive(False)

if __name__ == '__main__':
    from utility import Test
    Test(Installer)
