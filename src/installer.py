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
import urllib
import gettext
import gobject
import pango

from common.consts import *
from common.utils import *
from common.widgets import TweakPage
from common.widgets.dialogs import ErrorDialog, InfoDialog, QuestionDialog
from common.widgets.utils import ProcessDialog
from common.network.parser import Parser
from common.appdata import get_app_logo, get_app_describ
from xdg.DesktopEntry import DesktopEntry

try:
    from common.package import package_worker, PackageInfo
    DISABLE = False
except ImportError:
    DISABLE = True

DESKTOP_DIR = '/usr/share/app-install/desktop/'
ICON_DIR = os.path.join(DATA_DIR, 'applogos')
REMOTE_APP_DATA = os.path.expanduser('~/.ubuntu-tweak/apps/data/apps.json')
REMOTE_CATE_DATA = os.path.expanduser('~/.ubuntu-tweak/apps/data/cates.json')
REMOTE_DATA_DIR = os.path.expanduser('~/.ubuntu-tweak/apps/data')
REMOTE_LOGO_DIR = os.path.expanduser('~/.ubuntu-tweak/apps/logos')

(
    COLUMN_INSTALLED,
    COLUMN_ICON,
    COLUMN_PKG,
    COLUMN_NAME,
    COLUMN_DESC,
    COLUMN_DISPLAY,
    COLUMN_CATE,
) = range(7)

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

APP_DATA = \
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
    ('christine', Sound),
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
    ('gnote', Text),
    ('gnome-do', Desktop),
    ('gnome-globalmenu', Desktop),
    ('gnome-colors', Desktop),
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
    ('moovida', Sound),
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
    ('ubudsl', Internet),
    ('ubuntu-restricted-extras', Desktop),
    ('virtualbox-ose', Emulator),
    ('virtualbox-3.0', Emulator),
    ('vlc', Video),
    ('vmware-player', Emulator),
    ('wine', Emulator),
    ('wine-doors', Emulator),
    ('xbmc', Desktop),
)

class LogoHandler:
    def __init__(self, dir):
        self.dir = dir
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)

    def save_logo(self, name, url):
        data = urllib.urlopen(url).read()
        f = open(os.path.join(self.dir, '%s.png' % name), 'w')
        f.write(data)
        f.close()

    def get_logo(self, name):
        path = os.path.join(self.dir, '%s.png' % name)

        return gtk.gdk.pixbuf_new_from_file(path)

    def is_exists(self, name):
        return os.path.exists(os.path.join(self.dir, '%s.png' % name))

class FetchingDialog(ProcessDialog):
    def __init__(self, parent, caller):
        self.caller = caller
        self.done = False
        self.message = None
        self.user_action = False

        super(FetchingDialog, self).__init__(parent=parent)
        self.set_dialog_lable(_('Fetching online data...'))

    def process_data(self):
        import time
        self.caller.model.clear()
        for item in self.caller.get_items():
            time.sleep(1)

            try:
                pkgname, category, pixbuf, desc, appname, is_installed = self.caller.parse_item(item)
            except IOError:
                self.message = _('Network is error')
                break
            except KeyError:
                continue

            self.caller.model.append((is_installed,
                    pixbuf,
                    pkgname,
                    appname,
                    desc,
                    '<b>%s</b>\n%s' % (appname, desc),
                    category))

            if self.user_action == True:
                break

        self.done = True

    def on_timeout(self):
        self.pulse()

        if not self.done:
            return True
        else:
            self.destroy()

class Installer(TweakPage):
    def __init__(self):
        TweakPage.__init__(self, 
                _('Add/Remove Applications'),
                _('A simple but more effecient method for finding and installing popular packages than the default Add/Remove.'))

        if not os.path.exists(REMOTE_DATA_DIR):
            os.makedirs(REMOTE_DATA_DIR)
        if not os.path.exists(REMOTE_LOGO_DIR):
            os.makedirs(REMOTE_LOGO_DIR)
        self.app_logo_handler = LogoHandler(REMOTE_LOGO_DIR)
        self.app_data_parser = Parser(REMOTE_APP_DATA, 'package')

        self.to_add = []
        self.to_rm = []
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

        gobject.idle_add(self.on_idle_check)

    def on_idle_check(self):
        gtk.gdk.threads_enter()
        if self.check_update():
            dialog = QuestionDialog(_('New application data available, would you like to update?'))
            response = dialog.run()
            dialog.destroy()

            if response == gtk.RESPONSE_YES:
                dialog = FetchingDialog(self.get_toplevel(), self)

                if dialog.run() == gtk.RESPONSE_REJECT:
                    dialog.destroy()

                if dialog.message:
                    ErrorDialog(dialog.message).launch()

        gtk.gdk.threads_leave()

    def check_update(self):
        if os.path.exists(REMOTE_APP_DATA) and os.path.exists(REMOTE_CATE_DATA):
            return True
        else:
            return False

    def create_category(self):
        self.cate_model = gtk.ListStore(gtk.gdk.Pixbuf,
                gobject.TYPE_STRING)

        combobox = gtk.ComboBox(self.cate_model)
        textcell = gtk.CellRendererText()
        pixbufcell = gtk.CellRendererPixbuf()
        combobox.pack_start(pixbufcell, False)
        combobox.pack_start(textcell, True)
        combobox.add_attribute(pixbufcell, 'pixbuf', 0)
        combobox.add_attribute(textcell, 'text', 1)

        return combobox

    def update_cate_model(self):
        self.cate_model.clear()

        iter = self.cate_model.append()
        self.cate_model.set(iter, 
                0, gtk.gdk.pixbuf_new_from_file(os.path.join(DATA_DIR, 'appcates', 'all.png')),
                1, _('All Categories'))

        for item in CATES_DATA:
            iter = self.cate_model.append()
            self.cate_model.set(iter, 
                    0, gtk.gdk.pixbuf_new_from_file(os.path.join(DATA_DIR, 'appcates', item[1])),
                    1, item[0])

    def on_category_changed(self, widget, data = None):
        index = widget.get_active()
        if index:
            liststore = widget.get_model()
            iter = liststore.get_iter(index)
            self.filter = liststore.get_value(iter, 1)
        else:
            self.filter = None

        self.update_model()

    def get_app_logo(self, pkgname, url=None):
        if url and not self.app_logo_handler.is_exists(pkgname):
            self.app_logo_handler.save_logo(pkgname, url)

        if self.app_logo_handler.is_exists(pkgname):
            return self.app_logo_handler.get_logo(pkgname)
        else:
            return get_app_logo(pkgname)

    def get_app_describ(self, pkgname):
        try:
            if self.app_data_parser['pkgname'].has_key('summary'):
                return self.app_data_parser['pkgname']['summary']
        except:
            pass
        return get_app_describ(pkgname)

    def get_app_meta(self, pkgname):
        '''
        Meta data is App's display name and install status
        Need catch exception: KeyError
        '''
        package = PackageInfo(pkgname)
        return package.get_name(), package.check_installed()

    def get_items(self):
        if self.app_data_parser.items():
            return self.app_data_parser.items()

    def parse_item(self, item):
        '''
        If item[1] == tuple, so it's local data, or the remote data
        '''
        if type(item[1]) == tuple:
            pkgname = item[0]
            category = item[-1][0] 

            pixbuf = self.get_app_logo(pkgname)
            desc = self.get_app_describ(pkgname)

            appname, is_installed = self.get_app_meta(pkgname)
        elif type(item[1]) == dict:
            pkgname = item[0]
            pkgdata = item[1]
            appname = pkgdata['name']
            desc = pkgdata['summary']
            category = 1

            pixbuf = self.get_app_logo(pkgname, pkgdata['logo32'])
            appname, is_installed = self.get_app_meta(pkgname)

        return pkgname, category, pixbuf, desc, appname, is_installed

    def update_model(self):
        self.model.clear()

        icon = gtk.icon_theme_get_default()

        for item in APP_DATA:
            try:
                pkgname, category, pixbuf, desc, appname, is_installed = self.parse_item(item)
            except KeyError:
                continue

            if self.filter == None:
                if pkgname in self.to_add or pkgname in self.to_rm:
                    self.model.append((not is_installed,
                            pixbuf,
                            pkgname,
                            appname,
                            desc,
                            '<span foreground="#ffcc00"><b>%s</b>\n%s</span>' % (appname, desc),
                            category))
                else:
                    self.model.append((is_installed,
                            pixbuf,
                            pkgname,
                            appname,
                            desc,
                            '<b>%s</b>\n%s' % (appname, desc),
                            category))
            else:
                if self.filter == category:
                    if pkgname in self.to_add or pkgname in self.to_rm:
                        self.model.append((not is_installed,
                                pixbuf,
                                pkgname,
                                appname,
                                desc,
                                '<span foreground="#ffcc00"><b>%s</b>\n%s</span>' % (appname, desc),
                                category))
                    else:
                        self.model.append((is_installed,
                                pixbuf,
                                pkgname,
                                appname,
                                desc,
                                '<b>%s</b>\n%s' % (appname, desc),
                                category))

    def deep_update(self):
        package_worker.update_apt_cache(True)
        self.update_model()
        
    def on_install_toggled(self, cell, path):
        iter = self.model.get_iter((int(path),))
        is_installed = self.model.get_value(iter, COLUMN_INSTALLED)
        pkgname = self.model.get_value(iter, COLUMN_PKG)
        appname = self.model.get_value(iter, COLUMN_NAME)
        desc = self.model.get_value(iter, COLUMN_DESC)

        is_installed = not is_installed
        if is_installed:
            if pkgname in self.to_rm:
                self.to_rm.remove(pkgname)
                self.model.set(iter, COLUMN_DISPLAY, '<b>%s</b>\n%s' % (appname, desc))
            else:
                self.to_add.append(pkgname)
                self.model.set(iter, COLUMN_DISPLAY, '<span foreground="#ffcc00"><b>%s</b>\n%s</span>' % (appname, desc))
        else:
            if pkgname in self.to_add:
                self.to_add.remove(pkgname)
                self.model.set(iter, COLUMN_DISPLAY, '<b>%s</b>\n%s' % (appname, desc))
            else:
                self.to_rm.append(pkgname)
                self.model.set(iter, COLUMN_DISPLAY, '<span foreground="#ffcc00"><b>%s</b>\n%s</span>' % (appname, desc))

        self.model.set(iter, COLUMN_INSTALLED, is_installed)
        self.colleague_changed()

    def create_treeview(self):
        self.model = gtk.ListStore(
                        gobject.TYPE_BOOLEAN,
                        gtk.gdk.Pixbuf,
                        gobject.TYPE_STRING,
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
        self.package_worker.perform_action(widget.get_toplevel(), self.to_add, self.to_rm)

        package_worker.update_apt_cache(True)

        done = package_worker.get_install_status(self.to_add, self.to_rm)

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
