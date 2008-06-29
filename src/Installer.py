#!/usr/bin/env python

import os
import gtk
import gettext
import gobject

from Widgets import TweakPage, MessageDialog
from xdg.DesktopEntry import DesktopEntry

try:
    import apt_pkg
    from PackageWorker import PackageWorker, PackageInfo, update_apt_cache
    DISABLE = False
except ImportError:
    DISABLE = True

DESKTOP_DIR = '/usr/share/app-install/desktop/'
ICON_DIR = 'applogos'

(
    COLUMN_INSTALLED,
    COLUMN_ICON,
    COLUMN_NAME,
    COLUMN_DESC,
    COLUMN_DISPLAY,
    COLUMN_CATE,
) = range(6)

P2P = _("P2P")
Image = _("Image")
Sound = _("Sound")
Video = _("Video")
Text = _("Text")
Internet = _("Internet")
FTP = _("FTP Transform")
Desktop = _("Desktop")
Disk = _("Disk")
Develop = _("Develop")
Virtual = _("Virtual")
Mail = _("Main")

data = \
(
    ("agave", _("A colorscheme designer for GNOME"), Image),
    ("amule", _("Client for the eD2k and Kad networks, like eMule."), P2P),
    ("anjuta", _("Integrated Development Environment for GNOME"), Develop),
    ("audacious", _("A skinned multimedia player for many platforms."), Sound),
    ("avant-window-navigator", _("Fully customisable dock-like window navigator for GNOME."), Desktop),
    ("azureus", _("Java based BitTorrent client."), P2P),
    ("banshee", _("GTK# based Audio Management and Playback application."), Sound),
    ("chmsee", _("A chm file viewer written in GTK+."), Text),
    ("compizconfig-settings-manager", _("Advanced Desktop Effects Settings Manager for Compiz Fusion."), Desktop),
    ("devhelp", _("An API documentation browser for GNOME."), Develop),
    ("deluge-torrent", _("Deluge is a Bittorrent client, created using Python and GTK+."), P2P),
    ("eclipse", _("Extensible Tool Platform and Java IDE."), Develop),
    ("emesene", _("A client for the Windows Live Message network."), Internet),
    ("eva", _("KDE IM client using Tencent QQ's protocol"), Internet),
    ("exaile", _("GTK+ based flexible audio player, similar to Amarok."), Sound),
    ("filezilla", _("gFTP is a multithreaded FTP client"), FTP),
    ("gftp", _("gFTP is a multithreaded FTP client"), FTP),
    ("ghex", _("GNOME Hex editor for files"), Text),
    ("gmail-notify", _("Notify the arrival of new mail on Gmail"), Mail),
    ("gnomebaker", _("CD tools"), Disk),
    ("gnome-do", _("CD tools"), Desktop),
    ("googleearth", _("ddd"), Internet),
    ("gparted", _("GNOME partition editor"), Disk),
    ("gpicview", _("lightweight image viewer"), Image),
    ("gtk-recordmydesktop", _("Graphical frontend for recordmydesktop"), Video),
    ("isomaster", _("A graphical CD image editor"), Disk),
    ("lastfm", _("a music player for Last.fm personalized radio"), Internet),
    ("leafpad", _("GTK+ based simple text editor"), Text),
    ("mail-notification", _("mail notification in system tray"), Mail),
    ("meld", _("adcal tool to diff and merge files"), Text),
    ("mirage", _("A fast and simple GTK+ Image Viewer"), Image),
    ("monodevelop", _("Develop .NET applications in an Integrated Development Environment"), Develop),
    ("mplayer", _("The Ultimate Movie Player For Linux - Medibuntu package"), Video),
    ("netbeans", _("NetBeans Integrated Development Environment for Java, C/C++, Ruby, UML, etc."), Develop),
    ("rar", _("ddd"), Desktop),
    ("screenlets", _("ddd"), Desktop),
    ("smplayer", _("ddd"), Video),
    ("stardict", _("ddd"), Desktop),
    ("virtualbox", _("ddd"), Virtual),
    ("vlc", _("ddd"), Video),
    ("vmware-player", _("ddd"), Virtual),
    ("wine", _("ddd"), Virtual),
)

class Installer(TweakPage):
    def __init__(self, parent = None):
        TweakPage.__init__(self)
        self.main_window = parent
        update_apt_cache(True)

        self.to_add = []
        self.to_rm = []
        self.packageWorker = PackageWorker()

        self.set_title(_("Install the common used applications"))
        self.set_description(_("You can install applications form this easily interface."))

        vbox = gtk.VBox(False, 8)
        self.pack_start(vbox)

        hbox = gtk.HBox(False, 0)
        vbox.pack_start(hbox, False, False, 0)

        combobox = gtk.combo_box_new_text()
        combobox.append_text(_("All Category"))
        temp = []
        for item in data:
            cate = item[-1]
            if cate not in temp:
                combobox.append_text(cate)
                temp.append(cate)
        del temp
        combobox.set_active(0)
        combobox.connect("changed", self.on_category_changed)
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
        self.button.connect("clicked", self.on_apply_clicked)
        self.button.set_sensitive(False)
        hbox.pack_end(self.button, False, False, 0)

        self.show_all()

    def on_category_changed(self, widget, data = None):
        if widget.get_active():
            self.filter = widget.get_active_text()
        else:
            self.filter = None

        self.update_model()

    def update_model(self):
        self.model.clear()

        icon = gtk.icon_theme_get_default()

        for item in data:
            try:
                iconpath = os.path.join(ICON_DIR, item[0] + ".png")
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

            if self.filter == None:
                if item[0] in self.to_add or item[0] in self.to_rm:
                    self.model.append((not is_installed,
                            pixbuf,
                            appname,
                            desc,
                            "<span foreground='#ffcc00'><b>%s</b>\n%s</span>" % (disname, desc),
                            item[-1]))
                else:
                    self.model.append((is_installed,
                            pixbuf,
                            appname,
                            desc,
                            "<b>%s</b>\n%s" % (disname, desc),
                            item[-1]))
            else:
                if self.filter == item[-1]:
                    if appname in self.to_add or appname in self.to_rm:
                        self.model.append((not is_installed,
                                pixbuf,
                                appname,
                                desc,
                                "<span foreground='#ffcc00'><b>%s</b>\n%s</span>" % (disname, desc),
                                item[-1]))
                    else:
                        self.model.append((is_installed,
                                pixbuf,
                                appname,
                                desc,
                                "<b>%s</b>\n%s" % (disname, desc),
                                item[-1]))
        
    def on_install_toggled(self, cell, path):
        iter = self.model.get_iter((int(path),))
        is_installed = self.model.get_value(iter, COLUMN_INSTALLED)
        appname = self.model.get_value(iter, COLUMN_NAME)
        disname = PackageInfo(appname).get_name()
        desc = self.model.get_value(iter, COLUMN_DESC)
        display = self.model.get_value(iter, COLUMN_DISPLAY)

        print is_installed
        print appname

        is_installed = not is_installed
        if is_installed:
            if appname in self.to_rm:
                self.to_rm.remove(appname)
                self.model.set(iter, COLUMN_DISPLAY, "<b>%s</b>\n%s" % (disname, desc))
            else:
                self.to_add.append(appname)
                self.model.set(iter, COLUMN_DISPLAY, "<span foreground='#ffcc00'><b>%s</b>\n%s</span>" % (disname, desc))
        else:
            if appname in self.to_add:
                self.to_add.remove(appname)
                self.model.set(iter, COLUMN_DISPLAY, "<b>%s</b>\n%s" % (disname, desc))
            else:
                self.to_rm.append(appname)
                self.model.set(iter, COLUMN_DISPLAY, "<span foreground='#ffcc00'><b>%s</b>\n%s</span>" % (disname, desc))

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
        treeview.append_column(column)

        # column for application
        column = gtk.TreeViewColumn('Application')
        column.set_spacing(5)
        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, pixbuf = COLUMN_ICON)

        renderer = gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.add_attribute(renderer, "markup", COLUMN_DISPLAY)
        treeview.append_column(column)
        
        self.filter = None
        self.update_model()
        treeview.set_model(self.model)

        return treeview

    def on_apply_clicked(self, widget, data = None):
        state = self.packageWorker.perform_action(self.main_window, self.to_add, self.to_rm)

        if state == 0:
            self.button.set_sensitive(False)
            dialog = MessageDialog(_("Update Successfully!"), buttons = gtk.BUTTONS_OK)
        else:
            dialog = MessageDialog(_("Update Failed!"), buttons = gtk.BUTTONS_OK)
        dialog.run()
        dialog.destroy()

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
