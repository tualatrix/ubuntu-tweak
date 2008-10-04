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
import pygtk
pygtk.require('2.0')
import os
import gtk
import sys
import gconf
import thread
import gobject

from gnome import url_show
from common.Consts import *
from common.Canvas import RenderCell
from common.Widgets import QuestionDialog, TweakPage
from common.SystemInfo import GnomeVersion, SystemInfo, SystemModule
from UpdateManager import UpdateManager
from Config import Config, TweakSettings

class Tip(gtk.HBox):
    def __init__(self, tip):
        gtk.HBox.__init__(self)

        image = gtk.image_new_from_stock(gtk.STOCK_GO_FORWARD, gtk.ICON_SIZE_BUTTON)
        self.pack_start(image, False, False, 15)

        label = gtk.Label(tip)
        self.pack_start(label, False, False, 0)

class TipsFactory(gtk.VBox):
    def __init__(self, *tips):
        gtk.VBox.__init__(self)

        for tip in tips:
            self.pack_start(Tip(tip), False, False, 10)

def Welcome(parent = None):
    vbox = gtk.VBox(False, 0)
    vbox.set_border_width(20)

    title = gtk.MenuItem('')
    label = title.get_child()
    label.set_markup('\n<span size="xx-large">%s <b>Ubuntu Tweak!</b></span>\n' % _('Welcome to'))
    label.set_alignment(0.5, 0.5)
    title.select()
    vbox.pack_start(title, False, False, 10)

    tips = TipsFactory(
            'Tweak your desktop to make it what you like.',
            'Use templates and scripts to enhance your desktop.',
            'Easily install various kinds of applications in your option.',
            'More useful features wait you to use!',
            )
    vbox.pack_start(tips, False, False, 10)

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
    label.set_markup(_("<span size=\"x-large\">This feature isn't available in current distrobution</span>"))
    label.set_justify(gtk.JUSTIFY_FILL)
    vbox.pack_start(label, False, False, 50)

    hbox = gtk.HBox(False, 0)
    vbox.pack_start(hbox, False, False, 0)
        
    return vbox

from Computer import Computer
from Session import Session
from AutoStart import AutoStart
from Icon import Icon
#if SystemModule.has_ccm() and SystemModule.has_apt() or SystemModule.has_right_compiz():
if SystemModule.has_apt() or SystemModule.has_right_compiz():
    from Compiz import Compiz
else:
    Compiz = Notice

if SystemModule.gnome_version() >= 20:
    from UserDir import UserDir
    from Templates import Templates
else:
    UserDir = Notice
    Templates = Notice

if SystemModule.is_hardy() or SystemModule.is_intrepid():
    from Installer import Installer
    from ThirdSoft import ThirdSoft
else:
    Installer = Notice
    ThirdSoft = Notice
if SystemModule.is_intrepid():
    from PackageCleaner import PackageCleaner
else:
    PackageCleaner = Notice
from Scripts import Scripts
from Shortcuts import Shortcuts
from PowerManager import PowerManager
from Gnome import Gnome
from Nautilus import Nautilus
from LockDown import LockDown
from Metacity import Metacity

(
    ID_COLUMN,
    DATA_COLUMN,
    MODULE_COLUMN,
    CHILD_COLUMN,
) = range(4)

(
    MODULE_ID,
    MODULE_LOGO,
    MODULE_TITLE,
    MODULE_FUNC,
    MODULE_TYPE,
) = range(5)

(
    SHOW_ALWAYS,
    SHOW_CHILD,
    SHOW_NONE,
) = range(3)

(
    WELCOME,
    COMPUTER,
    APPLICATIONS,
    INSTALLER,
    THIRDSOFT,
    PACKAGE,
    STARTUP,
    SESSION,
    AUTOSTART,
    DESKTOP,
    ICON,
    METACITY,
    COMPIZ,
    PERSONAL,
    USERDIR,
    TEMPLATES,
    SCRIPTS,
    SHORTCUTS,
    SYSTEM,
    GNOME,
    NAUTILUS,
    POWER,
    SECURITY,
    SECU_OPTIONS,
    TOTAL
) = range(25)

MODULES_TABLE = {
    APPLICATIONS: [INSTALLER, THIRDSOFT, PACKAGE],
    STARTUP: [SESSION, AUTOSTART],
    DESKTOP: [ICON, METACITY, COMPIZ],
    PERSONAL: [USERDIR, TEMPLATES, SCRIPTS, SHORTCUTS],
    SYSTEM: [GNOME, NAUTILUS, POWER],
    SECURITY: [SECU_OPTIONS],
}

MODULES = \
[
    [WELCOME, 'welcome.png', _("Welcome"), Welcome, SHOW_ALWAYS],
    [COMPUTER, 'computer.png', _("Computer"), Computer, SHOW_ALWAYS],
    [APPLICATIONS, 'applications.png', _("Applications"), None, SHOW_CHILD],
    [INSTALLER, 'installer.png', _("Add/Remove"), Installer, SHOW_NONE],
    [THIRDSOFT, 'third-soft.png', _("Third Party Sources"), ThirdSoft, SHOW_NONE],
    [PACKAGE, 'package.png', _("Package Cleaner"), PackageCleaner, SHOW_NONE],
    [STARTUP, 'startup.png', _("Startup"), None, SHOW_CHILD],
    [SESSION, 'session.png', _("Session Control"), Session, SHOW_NONE],
    [AUTOSTART, 'autostart.png', _("Auto Start"), AutoStart, SHOW_NONE],
    [DESKTOP, 'desktop.png', _("Desktop"), None, SHOW_CHILD],
    [ICON, 'icon.png', _("Desktop Icon"), Icon, SHOW_NONE],
    [METACITY, 'metacity.png', _("Window Settings"), Metacity, SHOW_NONE],
    [COMPIZ, 'compiz-fusion.png', _("Compiz Fusion"), Compiz, SHOW_NONE],
    [PERSONAL, 'personal.png', _("Personal"), None, SHOW_CHILD],
    [USERDIR, 'userdir.png', _("User Folder"), UserDir, SHOW_NONE],
    [TEMPLATES, 'templates.png', _("Templates"), Templates, SHOW_NONE],
    [SCRIPTS, 'scripts.png', _("Scripts"), Scripts, SHOW_NONE],
    [SHORTCUTS, 'shortcuts.png', _("Shortcuts"), Shortcuts, SHOW_NONE],
    [SYSTEM, 'system.png', _("System"), None, SHOW_CHILD],
    [GNOME, 'gnome.png', _("GNOME"), Gnome, SHOW_NONE],
    [NAUTILUS, 'nautilus.png', _("Nautilus"), Nautilus, SHOW_NONE],
    [POWER, 'powermanager.png', _("Power Manager"), PowerManager, SHOW_NONE],
    [SECURITY, 'security.png', _("Security"), None, SHOW_CHILD],
    [SECU_OPTIONS, 'lockdown.png', _("Security Options"), LockDown, SHOW_NONE],
]

class ItemCellRenderer(gtk.GenericCellRenderer):
    __gproperties__ = {
        "data": (gobject.TYPE_PYOBJECT, "Data", "Data", gobject.PARAM_READWRITE ), 
    }
   
    def __init__(self):
        self.__gobject_init__()
        self.height = 36
        self.width = 100
        self.set_fixed_size(self.width, self.height)
        self.data = None
        
    def do_set_property(self, pspec, value):
        setattr(self, pspec.name, value)
        
    def do_get_property(self, pspec):
        return getattr(self, pspec.name)
		
    def on_render(self, window, widget, background_area, cell_area, expose_area, flags):
        if not self.data: return
        cairo = window.cairo_create()
        icon, title, type = self.data
        
        x, y, width, height = expose_area
        cell_area = gtk.gdk.Rectangle(x, y, width, height)

        RenderCell(cairo, 
                 title, 
                 icon,
                 type,
                 cell_area)

    def on_get_size(self, widget, cell_area = None ):
        return (0, 0, self.width, self.height )
        
class MainWindow(gtk.Window):
    """the main Window of Ubuntu Tweak"""

    def __init__(self):
        gtk.Window.__init__(self)

        self.__settings = TweakSettings()

        self.connect("destroy", self.destroy)
        self.set_title("Ubuntu Tweak")
        self.set_default_size(720, 480)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_border_width(10)
        gtk.window_set_default_icon_from_file(os.path.join(DATA_DIR, 'pixmaps/ubuntu-tweak.png'))

        vbox = gtk.VBox(False, 0)
        self.add(vbox)

        self.hpaned = gtk.HPaned()
        vbox.pack_start(self.hpaned, True, True, 0)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.set_size_request(150, -1)
        self.hpaned.pack1(sw)

        self.model = self.__create_model()
        self.update_model()
        self.treeview = gtk.TreeView(self.model)
        self.__add_columns(self.treeview)
        selection = self.treeview.get_selection()
        selection.connect("changed", self.selection_cb)

        sw.add(self.treeview)

        self.notebook = self.create_notebook()
        self.moduletable = {0: 0}
        self.modules = {}
        self.hpaned.pack2(self.notebook)

        hbox = gtk.HBox(False, 5)
        vbox.pack_start(hbox, False, False, 5)
        button = gtk.Button(stock = gtk.STOCK_ABOUT)
        button.connect("clicked", self.show_about)
        hbox.pack_start(button, False, False, 0)
        button = gtk.Button(stock = gtk.STOCK_QUIT)
        button.connect("clicked", self.destroy);
        hbox.pack_end(button, False, False, 0)

        self.get_gui_state()
        self.show_all()
        gobject.timeout_add(8000, self.on_timeout)

    def save_gui_state(self):
        self.__settings.set_window_size(*(self.get_size()))
        self.__settings.set_paned_size(self.hpaned.get_position())

    def get_gui_state(self):
        self.set_size_request(*(self.__settings.get_window_size()))
        self.hpaned.set_position(self.__settings.get_paned_size())

    def __create_model(self):
        model = gtk.ListStore(
                    gobject.TYPE_INT,
                    gobject.TYPE_PYOBJECT)

        return model

    def update_model(self, id = None):
        '''如果指定了ID，则将此ID下的所有子模块显示'''
        model = self.model
        model.clear()

        have_child = False
        child_iter = None
        iter = None

        for i, module in enumerate(MODULES):
            assert module[MODULE_ID] == i

            if module[MODULE_TYPE] in (SHOW_ALWAYS, SHOW_CHILD):
                icon = os.path.join(DATA_DIR, 'pixmaps', module[MODULE_LOGO])
                title = module[MODULE_TITLE]
                iter = model.append(None)
                model.set(iter,
                    ID_COLUMN, module[MODULE_ID],
                    DATA_COLUMN, (icon, title, module[MODULE_TYPE]),
                )

            if i == id:
                for child_id in MODULES_TABLE[id]:
                    module = MODULES[child_id]
                    icon = os.path.join(DATA_DIR, 'pixmaps', module[MODULE_LOGO])
                    title = module[MODULE_TITLE]
                    iter = model.append(None)
                    model.set(iter,
                        ID_COLUMN, module[MODULE_ID],
                        DATA_COLUMN, (icon, title, module[MODULE_TYPE]),
                    )

        return model

    def selection_cb(self, widget, data = None):
        if not widget.get_selected():
            return
        model, iter = widget.get_selected()

        if iter:
            id = model.get_value(iter, ID_COLUMN)
            data = model.get_value(iter, DATA_COLUMN)

            if data[-1] == SHOW_CHILD:
                self.shrink = False
                self.need_shrink(id)
                if self.shrink:
                    self.update_model()
                    return

                self.update_model(id)
                child_id =  id + 1

                if child_id not in self.moduletable:
                    self.notebook.set_current_page(1)

                    gobject.timeout_add(5, self.__create_newpage, child_id)
                else:
                    self.__select_child_item(id + 1)
            else:
                if id not in self.moduletable:
                    self.notebook.set_current_page(1)
                    gobject.timeout_add(5, self.__create_newpage, id)
                else:
                    self.notebook.set_current_page(self.moduletable[id])
                    widget.select_iter(iter)

    def __shrink_for_each(self, model, path, iter, id):
        m_id = model.get_value(iter, ID_COLUMN)
        if id + 1 == m_id:
            self.shrink = True

    def need_shrink(self, id):
        self.model.foreach(self.__shrink_for_each, id)

    def __select_for_each(self, model, path, iter, id):
        m_id = model.get_value(iter, ID_COLUMN)
        if id == m_id:
            selection = self.treeview.get_selection()
            selection.select_iter(iter)

    def __select_child_item(self, id):
        self.model.foreach(self.__select_for_each, id)

    def __create_newpage(self, id):
        self.setup_notebook(id)
        self.moduletable[id] = self.notebook.get_n_pages() - 1
        self.notebook.set_current_page(self.moduletable[id])

        self.__select_child_item(id)

    def __add_columns(self, treeview):
        column = gtk.TreeViewColumn('ID', gtk.CellRendererText(),text = ID_COLUMN)
        column.set_visible(False)
        treeview.append_column(column)

        column = gtk.TreeViewColumn('DATA', ItemCellRenderer(), data = DATA_COLUMN)
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

        page = MODULES[WELCOME][MODULE_FUNC]
        notebook.append_page(page())
        notebook.append_page(Wait())

        return notebook

    def setup_notebook(self, id):
        page = MODULES[id][MODULE_FUNC]
        page = page()
        page.show_all()
        if isinstance(page, TweakPage):
            page.connect('update', self.on_child_page_update)
        self.modules[page.__module__] = page
        self.notebook.append_page(page)

    def on_child_page_update(self, widget, module, action):
        getattr(self.modules[module], action)()

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
        about.set_copyright("Copyright 漏 2007-2008 TualatriX")
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

        version = self.__settings.get_version()
        if version > VERSION:
            dialog = QuestionDialog(_("A newer version: %s is available online.\nWould you like to update?") % version)

            update = False

            if dialog.run() == gtk.RESPONSE_YES:
                update = True
            dialog.destroy()

            if update: 
                UpdateManager(self.get_toplevel())

        gtk.gdk.threads_leave()

    def destroy(self, widget, data = None):
        if SystemModule.has_apt() and SystemModule.is_hardy() or SystemModule.is_intrepid():
            from common.PolicyKit import DbusProxy
            if DbusProxy.get_proxy():
                state = DbusProxy.get_liststate()
                if state == "expire":
                    from ThirdSoft import UpdateCacheDialog
                    dialog = UpdateCacheDialog(self)
                    res = dialog.run()

                DbusProxy.exit()

        self.save_gui_state()
        gtk.main_quit()
