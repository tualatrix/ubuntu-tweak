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
import pango
import gobject
import webbrowser

from ubuntutweak.utils import icon
from ubuntutweak import modules
from ubuntutweak.modules import TweakModule, ModuleLoader
from ubuntutweak.common.consts import *
from ubuntutweak.common.debug import run_traceback
from ubuntutweak.common.systeminfo import module_check
from ubuntutweak.common.config import TweakSettings
from ubuntutweak.widgets.dialogs import QuestionDialog
try:
    from ubuntutweak.common.package import package_worker
except:
    package_worker = None
from ubuntutweak.network.downloadmanager import DownloadDialog
from ubuntutweak.preferences import PreferencesDialog
from ubuntutweak.common.utils import set_label_for_stock_button

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
            _('Configure file templates and shortcut scripts for easy access to ubuntutweak.common tasks.'),
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
    align = gtk.Alignment(0.5, 0.3)

    hbox = gtk.HBox(False, 12)
    align.add(hbox)

    image = gtk.image_new_from_pixbuf(icon.get_with_name('emblem-ohno', size=64))
    hbox.pack_start(image, False, False, 0)

    label = gtk.Label()
    label.set_markup("<span size=\"x-large\">%s</span>" % _("This module is error while loading."))
    label.set_justify(gtk.JUSTIFY_FILL)
    hbox.pack_start(label)
        
    return align

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

(
    ID_COLUMN,
    LOGO_COLUMN,
    TITLE_COLUMN,
    MODULE_CLASS,
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
    APPLICATIONS,
    STARTUP,
    DESKTOP,
    PERSONAL,
    SYSTEM,
    TOTAL
) = range(7)

MODULES_TABLE = [
    [WELCOME, 'ubuntu-tweak', _("Welcome"), Welcome, None],
    [APPLICATIONS, '', _("Applications"), None, 'application'],
    [STARTUP, '', _("Startup"), None, 'startup'],
    [DESKTOP, '', _("Desktop"), None, 'desktop'],
    [PERSONAL, '', _("Personal"), None, 'personal'],
    [SYSTEM, '', _("System"), None, 'system'],
]

module_loader = ModuleLoader(modules.__path__[0])

class UpdateDialog(DownloadDialog):
    def __init__(self, parent=None):
        DownloadDialog.__init__(self, url=TweakSettings.get_url(),
                            title=_('Download the Ubuntu Tweak %s') % TweakSettings.get_version(),
                            parent=parent)

    def on_downloaded(self, downloader):
        super(UpdateDialog, self).on_downloaded(downloader)
        os.system('xdg-open %s' % self.downloader.get_downloaded_file())

class MainWindow(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)

        self.connect("destroy", self.destroy)
        self.set_title(APP)
        self.set_default_size(740, 480)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_border_width(10)

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
        self.treeview.set_enable_tree_lines(True)

        self.__add_columns(self.treeview)
        selection = self.treeview.get_selection()
        selection.connect("changed", self.selection_cb)
        self.treeview.expand_all()

        sw.add(self.treeview)

        self.notebook = self.create_notebook()
        self.moduletable = {'0': 0}
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
        self.set_icon(icon.get_with_name('ubuntu-tweak', size=48))
        self.show_all()

        if TweakSettings.get_check_update():
            gobject.timeout_add(5000, self.on_timeout)

        launch = TweakSettings.get_default_launch()
        if launch and launch != '0':
            self.__create_newpage(launch)
		
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
                    gobject.TYPE_STRING,
                    gtk.gdk.Pixbuf,
                    gobject.TYPE_STRING)

        return model

    def update_model(self):
        model = self.model
        model.clear()

        have_child = False
        child_iter = None
        iter = None

        for i, module in enumerate(MODULES_TABLE):
            if module[MODULE_LOGO]:
                pixbuf = icon.get_with_name(module[MODULE_LOGO], size=32)
            else:
                pixbuf = None
            title = module[MODULE_TITLE]
            iter = model.append(None)
            model.set(iter,
                ID_COLUMN, module[MODULE_ID],
                LOGO_COLUMN, pixbuf,
                TITLE_COLUMN, "<b><big>%s</big></b>" % title,
            )

            if module[MODULE_TYPE]:
                module_list = module_loader.get_category(module[MODULE_TYPE])
                if module_list:
                    for module in module_list:
                        child_iter = model.append(iter)

                        model.set(child_iter,
                            ID_COLUMN, module.__name__,
                            LOGO_COLUMN, module_loader.get_pixbuf(module.__name__),
                            TITLE_COLUMN, module.__title__,
                        )

        return model

    def selection_cb(self, widget):
        model, iter = widget.get_selected()

        if iter:
            if model.iter_has_child(iter):
                path = model.get_path(iter)
                self.treeview.expand_row(path, True)
                iter = model.iter_children(iter)
                id = model.get_value(iter, ID_COLUMN)

                widget.select_iter(iter)
                if id not in self.moduletable:
                    self.notebook.set_current_page(1)

                    gobject.timeout_add(5, self.__create_newpage, id)
                else:
                    self.__select_child_item(id)
            else:
                id = model.get_value(iter, ID_COLUMN)

                if id not in self.moduletable:
                    self.notebook.set_current_page(1)
                    gobject.timeout_add(5, self.__create_newpage, id)
                else:
                    self.notebook.set_current_page(self.moduletable[id])
                    widget.select_iter(iter)
        self.do_notify()

    def __select_for_each(self, model, path, iter, name):
        m_name = model.get_value(iter, TITLE_COLUMN)
        if name == m_name:
            selection = self.treeview.get_selection()
            selection.select_iter(iter)

    def __select_for_each_name(self, model, path, iter, name):
        m_name = model.get_value(iter, MODULE_CLASS)
        if name == m_name:
            selection = self.treeview.get_selection()
            selection.select_iter(iter)

    def select_module(self, name):
        self.model.foreach(self.__select_for_each_name, name)

    def __select_child_item(self, name):
        self.model.foreach(self.__select_for_each, name)

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
        column.set_spacing(3)
        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, pixbuf=LOGO_COLUMN)
        column.set_cell_data_func(renderer, self.logo_column_view_func)
        renderer = gtk.CellRendererText()
        renderer.set_property('ellipsize',  pango.ELLIPSIZE_END)
        column.pack_start(renderer, True)
        column.set_attributes(renderer, markup=TITLE_COLUMN)

        treeview.set_headers_visible(False)
        treeview.append_column(column)

        column = gtk.TreeViewColumn()
        column.set_visible(False)
        treeview.append_column(column)
        treeview.set_expander_column(column)

    def logo_column_view_func(self, cell_layout, renderer, model, iter):
        icon = model.get_value(iter, LOGO_COLUMN)
        if icon == None:
            renderer.set_property("visible", False)
        else:
            renderer.set_property("visible", True)

    def create_notebook(self):
        """
        Create the notebook with welcome page.
        the remain page will be created when request.
        """
        notebook = gtk.Notebook()
        notebook.set_scrollable(True)
        notebook.set_show_tabs(False)

        page = MODULES_TABLE[WELCOME][MODULE_FUNC]
        notebook.append_page(page())
        notebook.append_page(Wait())

        return notebook

    def setup_notebook(self, id):
        try:
            module = module_loader.get_module(id)
            page = module()
        except:
            run_traceback('error')
            page = ErrorPage()

        page.show_all()
        if isinstance(page, TweakModule):
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
        about.set_logo(icon.get_with_name('ubuntu-tweak', size=128))
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
        if version < VERSION:
            dialog = QuestionDialog(_('A newer version: %s is available online.\nWould you like to update?\n\nNote: if you prefer update from the source, you can disable this feature in Preference.') % version, 
                    title = _('Software Update'))

            update = False

            if dialog.run() == gtk.RESPONSE_YES:
                update = True
            dialog.destroy()

            if update: 
                dialog = UpdateDialog(parent=self.get_toplevel())
                dialog.run()
                dialog.destroy()

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
