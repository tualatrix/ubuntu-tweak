#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
pygtk.require('2.0')
import os
import gtk
import sys
import gconf
import thread
import gobject

from Constants import *
from gnome import url_show
from Widgets import MessageDialog
from SystemInfo import GnomeVersion
from SystemInfo import SystemInfo

InitLocale()
DISABLE_HARDY = 'Mint' not in SystemInfo.distro and '8.04' not in SystemInfo.distro
GNOME = int(GnomeVersion.minor)

def Welcome(parent = None):
    vbox = gtk.VBox(False, 0)

    label = gtk.Label()
    label.set_markup(_("<span size=\"xx-large\">Welcome to <b>Ubuntu Tweak!</b></span>\n\n\nThis is a tool for Ubuntu which makes it easy to change hidden \nsystem and desktop settings.\n\nUbuntu Tweak can also be run in other distributions.\n\nIf you have any suggestions, please visit the website in \"About\" and \nshare ideas with me. \n\nEnjoy!"))
    label.set_justify(gtk.JUSTIFY_FILL)
    vbox.pack_start(label, False, False, 50)

    hbox = gtk.HBox(False, 0)
    vbox.pack_start(hbox, False, False, 0)
        
    return vbox

def Wait(parent = None):
    vbox = gtk.VBox(False, 0)

    label = gtk.Label()
    label.set_markup(_("<span size=\"xx-large\">Wait a moment...</span>"))
    label.set_justify(gtk.JUSTIFY_FILL)
    vbox.pack_start(label, False, False, 50)

    hbox = gtk.HBox(False, 0)
    vbox.pack_start(hbox, False, False, 0)
        
    return vbox

def Notice(parent = None):
    vbox = gtk.VBox(False, 0)

    label = gtk.Label()
    label.set_markup(_("<span size=\"x-large\">This feature is only enabled in Ubuntu 8.04</span>"))
    label.set_justify(gtk.JUSTIFY_FILL)
    vbox.pack_start(label, False, False, 50)

    hbox = gtk.HBox(False, 0)
    vbox.pack_start(hbox, False, False, 0)
        
    return vbox

from Computer import Computer
from Session import Session
from AutoStart import AutoStart
from Icon import Icon
from Compiz import DISABLE_APT, DISABLE_NOR, DISABLE_VER
if DISABLE_NOR and DISABLE_APT or DISABLE_VER:
    Compiz = None
    UNKOWN = 99
else:
    from Compiz import Compiz
    UNKOWN = 0
if GNOME >= 20:
    from UserDir import UserDir
    from Templates import Templates
else:
    UserDir = None
    Templates = None

if DISABLE_APT or DISABLE_HARDY:
    Installer = Notice
    ThirdSoft = Notice
else:
    from Installer import Installer
    from ThirdSoft import ThirdSoft
from Scripts import Scripts
from Shortcuts import Shortcuts
from PowerManager import PowerManager
from Gnome import Gnome
from Nautilus import Nautilus
from LockDown import LockDown
from Metacity import Metacity

(
    NUM_COLUMN,
    ICON_COLUMN,
    NAME_COLUMN,
    PAGE_COLUMN,
    VERSION_COLUMN,
    TOTAL_COLUMN,
) = range(6)

(
    WELCOME_PAGE,
    COMPUTER_PAGE,
    APPLICATIONS_PAGE,
    INSTALLER_PAGE,
    THIRDSOFT_PAGE,
    STARTUP_PAGE,
    SESSION_PAGE,
    AUTOSTART_PAGE,
    DESKTOP_PAGE,
    ICON_PAGE,
    METACITY_PAGE,
    COMPIZ_PAGE,
    PERSONAL_PAGE,
    USERDIR_PAGE,
    TEMPLATES_PAGE,
    SCRIPTS_PAGE,
    SHORTCUTS_PAGE,
    SYSTEM_PAGE,
    GNOME_PAGE,
    NAUTILUS_PAGE,
    POWER_PAGE,
    SECURITY_PAGE,
    SECU_OPTIONS_PAGE,
    TOTAL_PAGE
) = range(24)
icons = \
[
    "pixmaps/welcome.png",
    "pixmaps/computer.png",
    "pixmaps/applications.png",
    "pixmaps/installer.png",
    "pixmaps/third-soft.png",
    "pixmaps/startup.png",
    "pixmaps/session.png",
    "pixmaps/autostart.png",
    "pixmaps/desktop.png",
    "pixmaps/icon.png",
    "pixmaps/metacity.png",
    "pixmaps/compiz-fusion.png",
    "pixmaps/personal.png",
    "pixmaps/userdir.png",
    "pixmaps/template.png",
    "pixmaps/scripts.png",
    "pixmaps/shortcuts.png",
    "pixmaps/system.png",
    "pixmaps/gnome.png",
    "pixmaps/nautilus.png",
    "pixmaps/powermanager.png",
    "pixmaps/security.png",
    "pixmaps/lockdown.png",
]
def update_icons(icons):
    list = []
    for icon in icons:
        list.append(DATA_DIR + '/' + icon)

    return list

icons = update_icons(icons)

MODULE_LIST = \
[
    [WELCOME_PAGE, icons[WELCOME_PAGE], _("Welcome"), Welcome, None],
    [COMPUTER_PAGE, icons[COMPUTER_PAGE], _("Computer"), Computer, None],
    [APPLICATIONS_PAGE, icons[APPLICATIONS_PAGE], _("Applications"), None, True],
    [INSTALLER_PAGE, icons[INSTALLER_PAGE], _("Add/Remove"), Installer, None],
    [THIRDSOFT_PAGE, icons[THIRDSOFT_PAGE], _("Third Party Sources"), ThirdSoft, None],
    [STARTUP_PAGE, icons[STARTUP_PAGE], _("Startup"), None, True],
    [SESSION_PAGE, icons[SESSION_PAGE], _("Session Control"), Session, 0],
    [AUTOSTART_PAGE, icons[AUTOSTART_PAGE], _("Auto Start"), AutoStart, 0],
    [DESKTOP_PAGE, icons[DESKTOP_PAGE], _("Desktop"), None, True],
    [ICON_PAGE, icons[ICON_PAGE], _("Desktop Icon"), Icon, 0],
    [METACITY_PAGE, icons[METACITY_PAGE], _("Metacity"), Metacity, 0],
    [COMPIZ_PAGE, icons[COMPIZ_PAGE], _("Compiz Fusion"), Compiz, UNKOWN],
    [PERSONAL_PAGE, icons[PERSONAL_PAGE], _("Personal"), None, True],
    [USERDIR_PAGE, icons[USERDIR_PAGE], _("User Folder"), UserDir, 20],
    [TEMPLATES_PAGE, icons[TEMPLATES_PAGE], _("Templates"), Templates, 20],
    [SCRIPTS_PAGE, icons[SCRIPTS_PAGE], _("Scripts"), Scripts, 0],
    [SHORTCUTS_PAGE, icons[SHORTCUTS_PAGE], _("Shortcuts"), Shortcuts, 0],
    [SYSTEM_PAGE, icons[SYSTEM_PAGE], _("System"), None, True],
    [GNOME_PAGE, icons[GNOME_PAGE], _("GNOME"), Gnome, 0],
    [NAUTILUS_PAGE, icons[NAUTILUS_PAGE], _("Nautilus"), Nautilus, 0],
    [POWER_PAGE, icons[POWER_PAGE], _("Power Manager"), PowerManager, 0],
    [SECURITY_PAGE, icons[SECURITY_PAGE], _("Security"), None, True],
    [SECU_OPTIONS_PAGE, icons[SECU_OPTIONS_PAGE], _("Security Options"), LockDown, 0],
]

class MainWindow(gtk.Window):
    """the main Window of Ubuntu Tweak"""

    def __init__(self):
        gtk.Window.__init__(self)

        self.connect("destroy", self.destroy)
        self.set_title("Ubuntu Tweak")
        self.set_default_size(690, 680)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_border_width(10)
        gtk.window_set_default_icon_from_file(os.path.join(DATA_DIR, 'pixmaps/ubuntu-tweak.png'))

        vbox = gtk.VBox(False, 0)
        self.add(vbox)

        eventbox = gtk.EventBox()
        hbox = gtk.HBox(False, 0)
        eventbox.add(hbox)
        eventbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(8448, 8448, 8448))
        vbox.pack_start(eventbox, False, False, 0)

        banner_left = gtk.Image()
        banner_left.set_from_file("data/pixmaps/banner_left.png")
        hbox.pack_start(banner_left, False, False, 0)
        banner_right = gtk.Image()
        banner_right.set_from_file("data/pixmaps/banner_right.png")
        hbox.pack_end(banner_right, False, False, 0)

        hpaned = gtk.HPaned()
        vbox.pack_start(hpaned, True, True, 0)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.set_size_request(150, -1)
        hpaned.pack1(sw)

        model = self.__create_model()
        self.treeview = gtk.TreeView(model)
        self.__add_columns(self.treeview)
        selection = self.treeview.get_selection()
        selection.connect("changed", self.selection_cb)

        sw.add(self.treeview)

        self.notebook = self.create_notebook()
        self.moduletable = {0: 0}
        hpaned.pack2(self.notebook)

        hbox = gtk.HBox(False, 5)
        vbox.pack_start(hbox, False, False, 5)
        button = gtk.Button(stock = gtk.STOCK_ABOUT)
        button.connect("clicked", self.show_about)
        hbox.pack_start(button, False, False, 0)
        button = gtk.Button(stock = gtk.STOCK_QUIT)
        button.connect("clicked", self.destroy);
        hbox.pack_end(button, False, False, 0)
        
        self.show_all()
        gobject.timeout_add(5000, self.on_timeout)

    def __create_model(self):
        model = gtk.TreeStore(
                    gobject.TYPE_INT,
                    gtk.gdk.Pixbuf,
                    gobject.TYPE_STRING)

        have_child = False
        child_iter = None
        iter = None

        for module in MODULE_LIST:
            if have_child == False:
                icon = gtk.gdk.pixbuf_new_from_file(module[ICON_COLUMN])
                iter = model.append(None)
                model.set(iter,
                    NUM_COLUMN, module[NUM_COLUMN],
                    ICON_COLUMN, icon,
                    NAME_COLUMN, module[NAME_COLUMN]
                )
                if module[-1] == True:
                    have_child = True
                else:
                    have_child = False
            else:
                try:
                    if MODULE_LIST[module[NUM_COLUMN]+1][-1] == True:
                        have_child = False
                    else:
                        have_child = True
                except IndexError:
                    pass

                if GNOME >= module[VERSION_COLUMN]:
                    icon = gtk.gdk.pixbuf_new_from_file(module[ICON_COLUMN])
                    child_iter = model.append(iter)
                    model.set(child_iter,
                        NUM_COLUMN, module[NUM_COLUMN],
                        ICON_COLUMN, icon,
                        NAME_COLUMN, module[NAME_COLUMN]
                    )
                else:
                    continue

        return model

    def selection_cb(self, widget, data = None):
        if not widget.get_selected():
            return
        model, iter = widget.get_selected()

        if iter:
            path = model.get_path(iter)
            self.treeview.expand_row(path, True)

            if model.iter_has_child(iter):
                iter = model.iter_children(iter)

            page_num = model.get_value(iter, NUM_COLUMN)

            if page_num not in self.moduletable:
                self.notebook.set_current_page(1)
                widget.select_iter(iter)

                self.TEMP = {'page_num':page_num,'iter': iter}
                gobject.timeout_add(5, self.create_newpage, widget)
                return

            self.notebook.set_current_page(self.moduletable[page_num])
            widget.select_iter(iter)

    def create_newpage(self, widget):
        try:
            if self.TEMP:
                page_num = self.TEMP['page_num']
                iter = self.TEMP['iter']

                self.setup_notebook(page_num)
                self.moduletable[page_num] = self.notebook.get_n_pages() - 1
                self.notebook.set_current_page(self.moduletable[page_num])

                if iter:
                    widget.select_iter(iter)

                del self.TEMP
        except AttributeError:
            pass

    def __add_columns(self, treeview):
        renderer = gtk.CellRendererText()

        column = gtk.TreeViewColumn("Num",renderer,text = NUM_COLUMN)
        column.set_visible(False)
        treeview.append_column(column)

        column = gtk.TreeViewColumn("Title")
        column.set_spacing(5)

        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, pixbuf = ICON_COLUMN)

        renderer = gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.set_attributes(renderer, text = NAME_COLUMN)

        treeview.set_headers_visible(False)
        treeview.append_column(column)

    def create_notebook(self):
        """
        Create the notebook with welcome page.
        the remain page will be created when request.
        """
        notebook = gtk.Notebook()
        notebook.set_scrollable(True)
        notebook.set_show_tabs(False)

        page = MODULE_LIST[WELCOME_PAGE][PAGE_COLUMN]
        notebook.append_page(page())

        notebook.append_page(Wait())

        return notebook

    def setup_notebook(self, id):
        page = MODULE_LIST[id][PAGE_COLUMN]
        page = page()
        page.show_all()
        self.notebook.append_page(page)

    def click_website(self, dialog, link, data = None):
        url_show(link)
    
    def show_about(self, data = None):
        gtk.about_dialog_set_url_hook(self.click_website)

        about = gtk.AboutDialog()
        about.set_transient_for(self)
        about.set_name("Ubuntu Tweak")
        about.set_version(VERSION)
        about.set_website("http://ubuntu-tweak.com")
        about.set_website_label("ubuntu-tweak.com")
        about.set_logo(self.get_icon())
        about.set_comments(_("Ubuntu Tweak is a tool for Ubuntu that makes it easy to configure your system and desktop settings."))
        about.set_authors(["TualatriX <tualatrix@gmail.com>", "Lee Jarratt <lee.jarratt@live.co.uk> English consultants"])
        about.set_copyright("Copyright © 2007-2008 TualatriX")
        about.set_wrap_license(True)
        about.set_license("Ubuntu Tweak is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.\n\
Ubuntu Tweak is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.\n\
You should have received a copy of the GNU General Public License along with Ubuntu Tweak; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA")
        about.set_translator_credits(_("translator-credits"))
        about.set_artists(["m.Sharp <mac.sharp@gmail.com> Logo and Banner", "Medical-Wei <a790407@hotmail.com> ArtWork of 0.1 version"])
        about.run()
        about.destroy()

    def on_timeout(self):
        thread.start_new_thread(self.check_version, ())

    def check_version(self):
        gtk.gdk.threads_enter()

        client = gconf.client_get_default()
        version = client.get_string("/apps/ubuntu-tweak/update")
        if version > VERSION:
            dialog = MessageDialog(_("A newer version: %s is available online.\nWould you like to update?") % version)

            dialog.set_transient_for(self)
            if dialog.run() == gtk.RESPONSE_YES:
                url_show("http://ubuntu-tweak.com/downloads")
            dialog.destroy()

        gtk.gdk.threads_leave()

    def destroy(self, widget, data = None):
        if not DISABLE_APT and not DISABLE_HARDY:
            from PolicyKit import DbusProxy
            if DbusProxy.proxy:
                state = DbusProxy.get_liststate()
                if state == "expire":
                    from ThirdSoft import UpdateCacheDialog
                    dialog = UpdateCacheDialog(self)
                    res = dialog.run()

                DbusProxy.exit()
        gtk.main_quit()
