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
import gobject
from common.LookupIcon import *
from common.PolicyKit import DbusProxy, PolkitButton
from common.PackageWorker import PackageWorker, update_apt_cache
from common.Widgets import TweakPage, InfoDialog, QuestionDialog, ErrorDialog

(
    COLUMN_CHECK,
    COLUMN_ICON,
    COLUMN_NAME,
    COLUMN_DESC,
    COLUMN_DISPLAY,
) = range(5)

class PackageView(gtk.TreeView):
    __gsignals__ = {
        'checked': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, 
                    (gobject.TYPE_BOOLEAN,)),
        'cleaned': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())
    }

    def __init__(self):
        super(PackageView, self).__init__()

        model = self.__create_model()
        self.set_model(model)

        self.__check_list = []
        self.__proxy = DbusProxy()
        self.__packageworker = PackageWorker()

        self.__add_column()

        self.mode = 'package'
        self.update_package_model()
        self.selection = self.get_selection()
        self.set_sensitive(False)

    def __create_model(self):
        model = gtk.ListStore(
                gobject.TYPE_BOOLEAN,
                gtk.gdk.Pixbuf,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING)

        return model

    def __add_column(self):
        renderer = gtk.CellRendererToggle()
        renderer.connect('toggled', self.on_package_toggled)
        column = gtk.TreeViewColumn(' ', renderer, active = COLUMN_CHECK)
        column.set_sort_column_id(COLUMN_CHECK)
        self.append_column(column)

        self.__column = gtk.TreeViewColumn(_('Package'))
        self.__column.set_sort_column_id(COLUMN_NAME)
        self.__column.set_spacing(5)
        renderer = gtk.CellRendererPixbuf()
        self.__column.pack_start(renderer, False)
        self.__column.set_attributes(renderer, pixbuf = COLUMN_ICON)

        renderer = gtk.CellRendererText()
        self.__column.pack_start(renderer, True)
        self.__column.set_attributes(renderer, markup = COLUMN_DISPLAY)

        self.append_column(self.__column)

    def get_list(self):
        return self.__check_list

    def update_package_model(self):
        model = self.get_model()
        model.clear()
        self.mode = 'package'

        icon = get_icon_with_name('deb', 24)
        list = self.__packageworker.list_autoremovable()
        self.total_num = len(list)
        self.__column.set_title('Packages need to be removed')

        for pkg in list:
            desc = self.__packageworker.get_pkgsummary(pkg)

            model.append((
                False,
                icon,
                pkg,
                desc,
                '<b>%s</b>\n%s' % (pkg, desc)
                ))

    def update_cache_model(self):
        model = self.get_model()
        model.clear()
        self.mode = 'cache'

        cache_dir = '/var/cache/apt/archives' 
        icon = get_icon_with_name('deb', 24)
        list = map(lambda file: "%s/%s" % (cache_dir, file),
                    filter(lambda x:x.endswith('deb'), os.listdir(cache_dir))) 
        self.total_num = len(list)
        self.__column.set_title('Cache need to be removed')

        for pkg in list:
            size = str(os.path.getsize(pkg)/1024)

            model.append((
                False,
                icon,
                pkg,
                size,
                '<b>%s</b>\nTake space %s KB' % (os.path.basename(pkg), size)
                ))

    def on_package_toggled(self, cell, path):
        model = self.get_model()
        iter = model.get_iter(path)

        check = model.get_value(iter, COLUMN_CHECK)
        model.set(iter, COLUMN_CHECK, not check)
        if not check:
            self.__check_list.append(model.get_value(iter, COLUMN_NAME))
        else:
            self.__check_list.remove(model.get_value(iter, COLUMN_NAME))

        if len(self.__check_list) == self.total_num:
            self.emit('checked', True)
        else:
            self.emit('checked', False)

        self.set_column_title()

    def set_column_title(self):
        if self.mode == 'package':
            self.__column.set_title(_('Package (%d Packages selected to remove)') % 
                             len(self.__check_list))
        else:
            self.computer_cache_size()
            self.__column.set_title(_('Cache (%d KB Space will be free)') % 
                             self.size)

    def computer_cache_size(self):
        self.size = 0

        model = self.get_model()
        model.foreach(self.__cache_foreach)

    def __cache_foreach(self, model, path, iter):
        cache = model.get_value(iter, COLUMN_NAME)

        if cache in self.__check_list:
            size = model.get_value(iter, COLUMN_DESC)
            self.size = self.size + int(size)

    def select_all(self, check = True):
        self.__check_list = []

        model = self.get_model()
        model.foreach(self.__select_foreach, check)
        self.emit('checked', check)

        self.set_column_title()

    def __select_foreach(self, model, path, iter, check):
        model.set(iter, COLUMN_CHECK, check)
        if check:
            self.__check_list.append(model.get_value(iter, COLUMN_NAME))

    def clean_selected_package(self):
        state = self.__packageworker.perform_action(self.get_toplevel(), [],self.__check_list)

        if state == 0:
            InfoDialog(_('Clean Successfully!')).launch()
        else:
            InfoDialog(_('Clean Failed!')).launch()

        update_apt_cache()
        self.update_package_model()
        self.__check_list = []
        self.emit('cleaned')

    def clean_selected_cache(self):
        model = self.get_model()
        for file in self.__check_list:
            result = self.__proxy.delete_file(file)
            if result == 'error': break

        if result == 'done':
            InfoDialog(_('Clean Successfully!')).launch()
        else:
            InfoDialog(_('Clean Failed!')).launch()

        self.update_cache_model()
        self.emit('cleaned')

class PackageCleaner(TweakPage):
    def __init__(self):
        super(PackageCleaner, self).__init__(
                _('Package Cleaner'),
                _('Clean up the no more needed packages and the package cache.'))

        update_apt_cache(True)

        self.to_add = []
        self.to_rm = []

        hbox = gtk.HBox(False, 0)
        self.pack_start(hbox, True, True, 0)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        hbox.pack_start(sw)

        vbox = gtk.VBox(False, 8)
        hbox.pack_start(vbox, False, False, 5)

        self.pkg_button = gtk.ToggleButton(_('Clean Package'))
        self.pkg_button.set_image(gtk.image_new_from_pixbuf(get_icon_with_name('deb', 24)))
        self.pkg_button.set_active(True)
        self.pkg_button.connect('toggled', self.on_button_toggled)
        vbox.pack_start(self.pkg_button, False, False, 0)

        self.cache_button = gtk.ToggleButton(_('Clean Cache'))
        self.cache_button.set_image(gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_BUTTON))
        self.cache_button.connect('toggled', self.on_button_toggled)
        vbox.pack_start(self.cache_button, False, False, 0)

        # create tree view
        self.treeview = PackageView()
        self.treeview.set_rules_hint(True)
        self.treeview.connect('checked', self.on_item_checked)
        self.treeview.connect('cleaned', self.on_item_cleaned)
        sw.add(self.treeview)

        # checkbutton
        self.select_button = gtk.CheckButton(_('Select All'))
        self.select_button.set_sensitive(False)
        self.__handler_id = self.select_button.connect('toggled', self.on_select_all)
        self.pack_start(self.select_button, False, False, 0)

        # button
        hbox = gtk.HBox(False, 0)
        self.pack_end(hbox, False ,False, 5)

        un_lock = PolkitButton()
        un_lock.connect('authenticated', self.on_polkit_action)
        un_lock.connect('failed', self.on_auth_failed)
        hbox.pack_end(un_lock, False, False, 5)

        self.clean_button = gtk.Button(stock = gtk.STOCK_CLEAR)
        self.clean_button.connect('clicked', self.on_clean_button_clicked)
        self.clean_button.set_sensitive(False)
        hbox.pack_end(self.clean_button, False, False, 5)

        self.show_all()

    def on_select_all(self, widget):
        check = widget.get_active()

        self.treeview.select_all(check)

    def on_item_checked(self, widget, all):
        list = widget.get_list()
        if list:
            self.clean_button.set_sensitive(True)
        else:
            self.clean_button.set_sensitive(False)

        self.select_button.handler_block(self.__handler_id)
        if all:
            self.select_button.set_active(True)
        else:
            self.select_button.set_active(False)
        self.select_button.handler_unblock(self.__handler_id)

    def on_item_cleaned(self, widget):
        self.select_button.set_active(False)
        self.clean_button.set_sensitive(False)

    def on_button_toggled(self, widget):
        self.select_button.set_active(False)

        if widget == self.cache_button:
            self.pkg_button.set_active(not widget.get_active())
        elif widget == self.pkg_button:
            self.cache_button.set_active(not widget.get_active())

        if self.pkg_button.get_active():
            self.treeview.update_package_model()
        else:
            self.treeview.update_cache_model()

    def on_clean_button_clicked(self, widget):
        mode = self.treeview.mode
        if mode == 'package':
            self.treeview.clean_selected_package()
        elif mode == 'cache':
            self.treeview.clean_selected_cache()

    def on_auth_failed(self, widget):
        gtk.gdk.threads_enter()
        ErrorDialog(_('<b><big>Could not authenticate</big></b>\n\nAn unexpected error has occurred.')).launch()
        gtk.gdk.threads_leave()

    def on_polkit_action(self, widget):
        gtk.gdk.threads_enter()
        proxy = DbusProxy.get_proxy()

        if proxy:
            self.treeview.set_sensitive(True)
            self.select_button.set_sensitive(True)
        else:
            ErrorDialog(_("<b><big>Service hasn't initialized yet</big></b>\n\nYou need to restart your Ubuntu.")).launch()

        gtk.gdk.threads_leave()

if __name__ == '__main__':
    from Utility import Test
    Test(PackageCleaner)
