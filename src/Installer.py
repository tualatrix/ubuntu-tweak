#!/usr/bin/env python

import os
import gtk
import gettext
import gobject

from common.Constants import *
from common.Widgets import TweakPage, InfoDialog
from xdg.DesktopEntry import DesktopEntry

InitLocale()

try:
    from common.PackageWorker import PackageWorker, PackageInfo, update_apt_cache
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

P2P = (_('P2P Clients'), 'p2p.png')
Image = (_('Image Tools'), 'image.png')
Sound = (_('Sound Tools'), 'sound.png')
Video = (_('Video Tools'), 'video.png')
Text = (_('Text Tools'), 'text.png')
IM = (_('Instant Messenger'), 'im.png')
Internet = (_('Internet Tools'), 'internet.png')
FTP = (_('FTP Tools'), 'ftp.png')
Desktop = (_('Desktop Tools'), 'desktop.png')
Disk = (_('CD/Disk Tools'), 'cd.png')
Develop = (_('Development Kit'), 'develop.png')
Emulator = (_('Emulators'), 'emulator.png')
Mail = (_('E-mail Tools'), 'mail.png')

CATES_DATA = (P2P, Image, Sound, Video, Text, IM, Internet, FTP, Desktop, Disk, Develop, Emulator, Mail)

data = \
(
    ('agave', _('A color scheme designer'), Image),
    ('amule', _('Client for the eD2k and Kad networks'), P2P),
    ('anjuta', _('GNOME IDE for C/C++, Java, Python'), Develop),
    ('audacious', _('A skinned multimedia player for many platforms'), Sound),
    ('audacity', _('Record and edit audio files'), Sound),
    ('avant-window-navigator', _('Fully customisable dock-like window navigator'), Desktop),
    ('avidemux', _('A free video editor'), Video),
    ('azureus', _('BitTorrent client written in Java'), P2P),
    ('banshee-1', _('Audio Management and Playback application'), Sound),
    ('cairo-dock', _('A true dock for linux'), Desktop),
    ('chmsee', _('A chm file viewer written in GTK+'), Text),
    ('compizconfig-settings-manager', _('Advanced Desktop Effects Settings Manager'), Desktop),
    ('devhelp', _('An API documentation browser for GNOME.'), Develop),
    ('deluge-torrent', _('A Bittorrent client written in PyGTK'), P2P),
    ('eclipse', _('Extensible Tool Platform and Java IDE'), Develop),
    ('emesene', _('A client for the Windows Live Message network'), IM),
    ('eva', _('KDE IM client using Tencent QQ protocol'), IM),
    ('exaile', _('GTK+ based flexible audio player, similar to Amarok'), Sound),
    ('filezilla', _('File transmission via ftp, sftp and ftps'), FTP),
    ('pcmanfm', _('An extremly fast and lightweight file manager'), Desktop),
    ('gajim', _('A GTK+ jabber client'), IM),
    ('geany', _('A fast and lightweight IDE'), Develop),
    ('gftp', _('A multithreaded FTP client'), FTP),
    ('ghex', _('GNOME Hex editor'), Text),
    ('gmail-notify', _('Notify the arrival of new mail on Gmail'), Mail),
    ('gnome-do', _('Do things as quickly as possible'), Desktop),
    ('googleearth', _('Let you fly anywhere to view the earth'), Internet),
    ('google-gadgets', _('Platform for running Google Gadgets on Linux'), Desktop),
    ('gparted', _('GNOME partition editor'), Disk),
    ('gpicview', _('Lightweight image viewer'), Image),
    ('gscrot', _('A powerful screenshot tool'), Image),
    ('gtk-recordmydesktop', _('Graphical frontend for recordmydesktop'), Video),
    ('isomaster', _('A graphical CD image editor'), Disk),
    ('kino', _('Non-linear editor for Digital Video data'), Video),
    ('lastfm', _('A music player for Last.fm personalized radio'), Internet),
    ('leafpad', _('GTK+ based simple text editor'), Text),
    ('liferea', _('Feed aggregator for GNOME'), Internet),
    ('mail-notification', _('mail notification in system tray'), Mail),
    ('meld', _('adcal tool to diff and merge files'), Text),
    ('mirage', _('A fast and simple GTK+ Image Viewer'), Image),
    ('midori', _('Webkit based lightweight web browser'), Internet),
    ('monodevelop', _('Develop .NET applications.'), Develop),
    ('mplayer', _('The Ultimate Movie Player For Linux'), Video),
    ('netbeans', _('IDE for Java, C/C++, Ruby, UML, etc.'), Develop),
    ('opera', _('The Opera Web Browser'), Internet),
    ('playonlinux', _('Run your Windows programs on Linux'), Emulator),
    ('screenlets', _('A framework for desktop widgets'), Desktop),
    ('skype', _('A VoIP software'), IM),
    ('smplayer', _('A great MPlayer front-end, written in QT4'), Video),
    ('soundconverter', _('Convert audio files into other formats'), Sound),
    ('stardict', _('An international dictionary'), Desktop),
    ('terminator', _('Multiple GNOME terminals in one window'), Emulator),
    ('ubuntu-restricted-extras', _('Commonly used restricted packages'), Desktop),
    ('virtualbox', _('A feature rich, high performance virtualization software'), Emulator),
    ('vlc', _('Read, capture, broadcast your multimedia streams'), Video),
    ('vmware-player', _('VMware Player can play virtual machines created by VMware'), Emulator),
    ('wine', _('A compatibility layer for running Windows programs'), Emulator),
)

class Installer(TweakPage):
    def __init__(self):
        TweakPage.__init__(self, 
                _('Install the widely used applications'),
                _('You can install applications by using this simple interface.'))

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
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
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
            try:
                iconpath = os.path.join(ICON_DIR, item[0] + '.png')
                pixbuf = gtk.gdk.pixbuf_new_from_file(iconpath)
            except gobject.GError:
                pixbuf = icon.load_icon(gtk.STOCK_MISSING_IMAGE, 32, 0)

            try:
                appname = item[0]
                package = PackageInfo(appname)
                is_installed = package.check_installed()
                disname = package.get_name()
                desc = item[1]
            except KeyError:
                continue

            category = item[-1][0]

            if self.filter == None:
                if item[0] in self.to_add or item[0] in self.to_rm:
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
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'markup', COLUMN_DISPLAY)
        treeview.append_column(column)
        
        self.filter = None
        self.update_model()
        treeview.set_model(self.model)

        return treeview

    def on_apply_clicked(self, widget, data = None):
        state = self.packageWorker.perform_action(widget.get_toplevel(), self.to_add, self.to_rm)

        if state == 0:
            self.button.set_sensitive(False)
            InfoDialog(_('Update Successfully!')).launch()
        else:
            InfoDialog(_('Update Failed!')).launch()

        update_apt_cache()
        self.to_add = []
        self.to_rm = []
        self.update_model()

    def colleague_changed(self):
        if self.to_add or self.to_rm:
            self.button.set_sensitive(True)
        else:
            self.button.set_sensitive(False)

if __name__ == '__main__':
    from Utility import Test
    Test(Installer)
