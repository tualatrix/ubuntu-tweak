#!/usr/bin/python
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
import gobject
import webbrowser

from common.consts import *
from common.debug import run_traceback
from common.widgets import TweakPage
from common.widgets.dialogs import QuestionDialog
from common.systeminfo import module_check
from common.config import TweakSettings
try:
    from common.package import package_worker
except:
    package_worker = None
from updatemanager import UpdateManager
from preferences import PreferencesDialog
from common.utils import set_label_for_stock_button

class Tip(gtk.HBox):
    def __init__(self, tip):
        gtk.HBox.__init__(self)

        image = gtk.image_new_from_stock(gtk.STOCK_GO_FORWARD, gtk.ICON_SIZE_BUTTON)
        self.pack_start(image, False, False, 15)

        label = gtk.Label()
        label.set_markup(tip)
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
    label.set_markup('\n<span size="xx-large">%s <b>%s!</b></span>\n' % (_('Welcome to'), APP))
    label.set_alignment(0.5, 0.5)
    title.select()
    vbox.pack_start(title, False, False, 10)

    tips = TipsFactory(
            _('Tweak otherwise hidden settings.'),
            _('Clean up unneeded packages to free diskspace.'),
            _('Easily install up-to-date versions of many applications.'),
            _('Configure file templates and shortcut scripts for easy access to common tasks.'),
            _('And many more useful features!'),
            )
    align = gtk.Alignment(0.5)
    align.add(tips)
    vbox.pack_start(align, False, False, 10)

    return vbox

def Wait(parent = None):
    vbox = gtk.VBox(False, 0)

    label = gtk.Label()
    label.set_markup("<span size=\"xx-large\">%s</span>" % _('Please wait a moment...'))
    label.set_justify(gtk.JUSTIFY_FILL)
    vbox.pack_start(label, False, False, 50)

    hbox = gtk.HBox(False, 0)
    vbox.pack_start(hbox, False, False, 0)
        
    return vbox

def Distro_Notice(parent=None):
    vbox = gtk.VBox(False, 0)

    label = gtk.Label()
    label.set_markup('<span size="x-large">%s</span>' % _("This feature isn't currently available in your distribution"))
    label.set_justify(gtk.JUSTIFY_FILL)
    vbox.pack_start(label, False, False, 50)

    hbox = gtk.HBox(False, 0)
    vbox.pack_start(hbox, False, False, 0)
        
    return vbox

def Desktop_Notice(parent=None):
    vbox = gtk.VBox(False, 0)

    label = gtk.Label()
    label.set_markup('<span size="x-large">%s</span>' % _("This feature is currently only available in GNOME Desktop Environment"))
    label.set_justify(gtk.JUSTIFY_FILL)
    vbox.pack_start(label, False, False, 50)

    hbox = gtk.HBox(False, 0)
    vbox.pack_start(hbox, False, False, 0)

    return vbox

def ErrorPage(parent=None):
    vbox = gtk.VBox(False, 0)

    label = gtk.Label()
    label.set_markup("<span size=\"x-large\">%s</span>" % _("This module is error while loading."))
    label.set_justify(gtk.JUSTIFY_FILL)
    vbox.pack_start(label, False, False, 50)

    hbox = gtk.HBox(False, 0)
    vbox.pack_start(hbox, False, False, 0)
        
    return vbox

def AptErrorPage(parent = None):
    vbox = gtk.VBox(False, 0)

    label = gtk.Label()
    label.set_line_wrap(True)
    label.set_markup('<span size="x-large">%s</span>' %
            _("This is a major failure of your software management system. Please check for broken packages with synaptic, check the file permissions and correctness of the file '/etc/apt/sources.list' and reload the software information with: 'sudo apt-get update' and 'sudo apt-get install -f'."))
    label.set_justify(gtk.JUSTIFY_FILL)
    vbox.pack_start(label, False, False, 50)

    hbox = gtk.HBox(False, 0)
    vbox.pack_start(hbox, False, False, 0)

    return vbox

from computer import Computer
if module_check.has_right_compiz():
    from compiz import Compiz
else:
    Compiz = Distro_Notice

if module_check.is_ubuntu():
    if package_worker.get_cache():
        from installer import Installer
        from cleaner import PackageCleaner
    else:
        Installer = AptErrorPage
        PackageCleaner = AptErrorPage
else:
    Installer = Distro_Notice
    PackageCleaner = Distro_Notice

if module_check.is_supported_ubuntu():
    from sourceeditor import SourceEditor
    if package_worker.get_cache():
        from thirdsoft import ThirdSoft
    else:
        ThirdSoft = AptErrorPage
else:
    SourceEditor = Distro_Notice
    ThirdSoft = Distro_Notice

if module_check.is_gnome():
    from session import Session
    from autostart import AutoStart
    from icons import Icon
    from scripts import Scripts
    from shortcuts import Shortcuts
    from powermanager import PowerManager
    from gnomesettings import Gnome
    from nautilus import Nautilus
    from lockdown import LockDown
    from metacity import Metacity
    from userdir import UserDir
    from templates import Templates
else:
    Session = Desktop_Notice
    AutoStart = Desktop_Notice
    Icon = Desktop_Notice
    UserDir = Desktop_Notice
    Templates = Desktop_Notice
    Scripts = Desktop_Notice
    Shortcuts = Desktop_Notice
    PowerManager = Desktop_Notice
    Gnome = Desktop_Notice
    Nautilus = Desktop_Notice
    LockDown = Desktop_Notice
    Metacity = Desktop_Notice

if module_check.has_gio():
    from filetype import FileType
else:
    FileType = Distro_Notice

(
    ID_COLUMN,
    LOGO_COLUMN,
    TITLE_COLUMN,
    MODULE_NAME_COLUMN,
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
    SOURCEEDITOR,
    THIRDSOFT,
    PACKAGE,
    STARTUP,
    SESSION,
    AUTOSTART,
    DESKTOP,
    ICON,
    METACITY,
    COMPIZ,
    GNOME,
    PERSONAL,
    USERDIR,
    TEMPLATES,
    SCRIPTS,
    SHORTCUTS,
    SYSTEM,
    FILETYPE,
    NAUTILUS,
    POWER,
    SECU_OPTIONS,
    TOTAL
) = range(26)

MODULES_TABLE = {
    APPLICATIONS: [INSTALLER, SOURCEEDITOR, THIRDSOFT, PACKAGE],
    STARTUP: [SESSION, AUTOSTART],
    DESKTOP: [ICON, METACITY, COMPIZ, GNOME],
    PERSONAL: [USERDIR, TEMPLATES, SCRIPTS, SHORTCUTS],
    SYSTEM: [FILETYPE, NAUTILUS, POWER, SECU_OPTIONS],
}

MODULES = \
[
    [WELCOME, 'welcome.png', _("Welcome"), Welcome, SHOW_ALWAYS],
    [COMPUTER, 'computer.png', _("Computer"), Computer, SHOW_ALWAYS],
    [APPLICATIONS, 'applications.png', _("Applications"), None, SHOW_CHILD],
    [INSTALLER, 'installer.png', _("Add/Remove"), Installer, SHOW_NONE],
    [SOURCEEDITOR, 'sourceeditor.png', _('Source Editor'), SourceEditor, SHOW_NONE],
    [THIRDSOFT, 'third-soft.png', _("Third-Party Sources"), ThirdSoft, SHOW_NONE],
    [PACKAGE, 'package.png', _("Package Cleaner"), PackageCleaner, SHOW_NONE],
    [STARTUP, 'startup.png', _("Startup"), None, SHOW_CHILD],
    [SESSION, 'session.png', _("Session Control"), Session, SHOW_NONE],
    [AUTOSTART, 'autostart.png', _("Autostart"), AutoStart, SHOW_NONE],
    [DESKTOP, 'desktop.png', _("Desktop"), None, SHOW_CHILD],
    [ICON, 'icon.png', _("Icons"), Icon, SHOW_NONE],
    [METACITY, 'metacity.png', _("Windows"), Metacity, SHOW_NONE],
    [COMPIZ, 'compiz-fusion.png', _("Compiz Fusion"), Compiz, SHOW_NONE],
    [GNOME, 'gnome.png', _("GNOME"), Gnome, SHOW_NONE],
    [PERSONAL, 'personal.png', _("Personal"), None, SHOW_CHILD],
    [USERDIR, 'userdir.png', _("Folders"), UserDir, SHOW_NONE],
    [TEMPLATES, 'templates.png', _("Templates"), Templates, SHOW_NONE],
    [SCRIPTS, 'scripts.png', _("Scripts"), Scripts, SHOW_NONE],
    [SHORTCUTS, 'shortcuts.png', _("Shortcuts"), Shortcuts, SHOW_NONE],
    [SYSTEM, 'system.png', _("System"), None, SHOW_CHILD],
    [FILETYPE, 'filetype.png', _('File Type Manager'), FileType, SHOW_NONE],
    [NAUTILUS, 'nautilus.png', _("Nautilus"), Nautilus, SHOW_NONE],
    [POWER, 'powermanager.png', _("Power Management"), PowerManager, SHOW_NONE],
    [SECU_OPTIONS, 'lockdown.png', _("Security"), LockDown, SHOW_NONE],
]

class MainWindow(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)

        self.connect("destroy", self.destroy)
        self.set_title(APP)
        self.set_default_size(740, 480)
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

        d_button = gtk.Button(stock = gtk.STOCK_YES)
        set_label_for_stock_button(d_button, _('_Donate'))
        d_button.connect("clicked", self.on_d_clicked)
        hbox.pack_start(d_button, False, False, 0)

        button = gtk.Button(stock = gtk.STOCK_QUIT)
        button.connect("clicked", self.destroy);
        hbox.pack_end(button, False, False, 0)

        button = gtk.Button(stock = gtk.STOCK_PREFERENCES)
        button.connect('clicked', self.on_preferences_clicked)
        hbox.pack_end(button, False, False, 0)

        self.get_gui_state()
        self.set_icon_name('ubuntu-tweak')
        self.show_all()

#        if TweakSettings.get_show_donate_notify():
#            gobject.timeout_add(3000, self.on_d_timeout, d_button)
        if TweakSettings.get_check_update():
            gobject.timeout_add(8000, self.on_timeout)

        launch = TweakSettings.get_default_launch()
        if launch:
            self.__create_newpage(launch)
		
    def on_d_timeout(self, widget):
        from common.notify import notify
        notify.update(_('Help the development of Ubuntu Tweak'), _('Ubuntu Tweak is a free-software, you can use it for free. If you like it, Please consider to donate for Ubuntu Tweak.'))
        notify.add_action("never_show", _('Never Show This Again'), self.on_never_show)
        notify.attach_to_widget(widget)
        notify.show()
		
    def on_d_clicked(self, widget):
        webbrowser.open('http://ubuntu-tweak.com/donate')

    def on_preferences_clicked(self, widget):
        dialog = PreferencesDialog()
        dialog.dialog.set_transient_for(widget.get_toplevel())
        dialog.run()
        dialog.destroy()

    def on_never_show(self, widget, action):
        TweakSettings.set_show_donate_notify(False)

    def save_gui_state(self):
        if TweakSettings.need_save:
            TweakSettings.set_window_size(*self.get_size())
            TweakSettings.set_paned_size(self.hpaned.get_position())

    def get_gui_state(self):
        self.set_default_size(*TweakSettings.get_window_size())
        self.hpaned.set_position(TweakSettings.get_paned_size())

    def __create_model(self):
        model = gtk.TreeStore(
                    gobject.TYPE_INT,
                    gtk.gdk.Pixbuf,
                    gobject.TYPE_STRING,
                    gobject.TYPE_STRING)

        return model

    def update_model(self):
        model = self.model
        model.clear()

        have_child = False
        child_iter = None
        iter = None

        for i, module in enumerate(MODULES):
            assert module[MODULE_ID] == i
            if have_child == False:
                pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(DATA_DIR, 'pixmaps', module[MODULE_LOGO]))
                title = module[MODULE_TITLE]
                iter = model.append(None)
                model.set(iter,
                    ID_COLUMN, module[MODULE_ID],
                    LOGO_COLUMN, pixbuf,
                    TITLE_COLUMN, title,
                    MODULE_NAME_COLUMN, getattr(module[MODULE_FUNC], '__module__', None),
                )
                if module[MODULE_TYPE] == SHOW_CHILD:
                    have_child = True
                else:
                    have_child = False
            else:
                try:
                    if MODULES[module[MODULE_ID] + 1][MODULE_TYPE] == SHOW_CHILD:
                        have_child = False
                    else:
                        have_child = True
                except:
                    pass

                pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(DATA_DIR, 'pixmaps', module[MODULE_LOGO]))
                title = module[MODULE_TITLE]
                child_iter = model.append(iter)
                model.set(child_iter,
                    ID_COLUMN, module[MODULE_ID],
                    LOGO_COLUMN, pixbuf,
                    TITLE_COLUMN, title,
                    MODULE_NAME_COLUMN, getattr(module[MODULE_FUNC], '__module__', None),
                )

        return model

    def selection_cb(self, widget):
        model, iter = widget.get_selected()

        if iter:
            id = model.get_value(iter, ID_COLUMN)

            if model.iter_has_child(iter):
                path = model.get_path(iter)
                self.treeview.expand_row(path, True)
                iter = model.iter_children(iter)

                if id not in self.moduletable:
                    self.notebook.set_current_page(1)

                    gobject.timeout_add(5, self.__create_newpage, id + 1)
                else:
                    self.__select_child_item(id + 1)
            else:
                if id not in self.moduletable:
                    self.notebook.set_current_page(1)
                    gobject.timeout_add(5, self.__create_newpage, id)
                else:
                    self.notebook.set_current_page(self.moduletable[id])
                    widget.select_iter(iter)
        self.do_notify()

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

    def __select_for_each_name(self, model, path, iter, name):
        m_name = model.get_value(iter, MODULE_NAME_COLUMN)
        if name == m_name:
            selection = self.treeview.get_selection()
            selection.select_iter(iter)

    def select_module(self, name):
        self.model.foreach(self.__select_for_each_name, name)

    def __select_child_item(self, id):
        self.model.foreach(self.__select_for_each, id)

    def __create_newpage(self, id):
        self.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        self.setup_notebook(id)
        self.moduletable[id] = self.notebook.get_n_pages() - 1
        self.notebook.set_current_page(self.moduletable[id])

        self.__select_child_item(id)
        self.window.set_cursor(None)

    def __add_columns(self, treeview):
        column = gtk.TreeViewColumn('ID', gtk.CellRendererText(), text=ID_COLUMN)
        column.set_visible(False)
        treeview.append_column(column)

        column = gtk.TreeViewColumn("Title") 
        column.set_spacing(5) 
        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, pixbuf=LOGO_COLUMN)
        renderer = gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.set_attributes(renderer, text=TITLE_COLUMN)

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
        try:
            page = MODULES[id][MODULE_FUNC]
            page = page()
        except:
            run_traceback('error')
            page = ErrorPage()

        page.show_all()
        if isinstance(page, TweakPage):
            page.connect('update', self.on_child_page_update)
            page.connect('call', self.on_child_page_call)
        self.modules[page.__module__] = page
        self.notebook.append_page(page)

    def on_child_page_call(self, widget, target, action, params):
        # FIXME: Need to combin with page update
        if target == 'mainwindow':
            getattr(self, action)(**params)

    def on_child_page_update(self, widget, module, action):
        # FIXME: If the module hasn't load yet! 
        if module in self.modules:
            getattr(self.modules[module], action)()

    def click_website(self, dialog, link, data = None):
        webbrowser.open(link)
    
    def show_about(self, data = None):
        gtk.about_dialog_set_url_hook(self.click_website)

        about = gtk.AboutDialog()
        about.set_transient_for(self)
        about.set_name(APP)
        about.set_version(VERSION)
        about.set_website("http://ubuntu-tweak.com")
        about.set_website_label(_('Ubuntu Tweak Website'))
        about.set_logo(self.get_icon())
        about.set_comments(_("Ubuntu Tweak is a tool for Ubuntu that makes it easy to configure your system and desktop settings."))
        about.set_authors(["TualatriX <tualatrix@gmail.com>", "",
            _("Contributors of 2007"),
            "Super Jamie <jamie@superjamie.net>", "",
            _("Contributors of 2008"),
            "Lee Jarratt <lee.jarratt@googlemail.com>", "",
            _("Contributors of 2009"),
            "Iven <ivenvd@gmail.com>",
            "Dig Ge <Dig.Ge.CN@Gmail.com>",
            ])
        about.set_copyright("Copyright © 2007-2009 TualatriX")
        about.set_wrap_license(True)
        about.set_license("Ubuntu Tweak is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.\n\
Ubuntu Tweak is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.\n\
You should have received a copy of the GNU General Public License along with Ubuntu Tweak; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA")
        about.set_translator_credits(_("translator-credits"))
        about.set_artists(["m.Sharp <mac.sharp@gmail.com> Logo and Banner", "Medical-Wei <a790407@hotmail.com> Artwork of 0.1 version"])
        about.run()
        about.destroy()

    def on_timeout(self):
        gobject.idle_add(self.check_version)

    def check_version(self):
        gtk.gdk.threads_enter()

        version = TweakSettings.get_version()
        if version > VERSION:
            dialog = QuestionDialog(_('A newer version: %s is available online.\nWould you like to update?' % version), 
                    title = _('Software Update'))

            update = False

            if dialog.run() == gtk.RESPONSE_YES:
                update = True
            dialog.destroy()

            if update: 
                UpdateManager(self.get_toplevel())

        gtk.gdk.threads_leave()

    def destroy(self, widget, data = None):
        self.do_notify()
        self.save_gui_state()
        gtk.main_quit()

    def prepare_notify(self, data):
        self.notify_func = data

    def get_notify(self):
        if hasattr(self, 'notify_func') and self.notify_func:
            notify_func = self.notify_func
            self.notify_func = None
            return notify_func

    def do_notify(self):
        notify_func = self.get_notify()
        if notify_func:
            notify_func()
