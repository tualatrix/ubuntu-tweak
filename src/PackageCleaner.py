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
from common.Widgets import TweakPage
from common.PackageWorker import PackageWorker, update_apt_cache

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
                    (gobject.TYPE_BOOLEAN,))
    }
    def __init__(self):
        super(PackageView, self).__init__()

        model = self.__create_model()
        self.set_model(model)

        self.__check_list = []
        self.__packageworker = PackageWorker()

        self.__add_column()

        self.update_package_model()
        self.selection = self.get_selection()

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

        icon = get_icon_with_name('deb', 24)
        list = self.__packageworker.list_autoeemovable()
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

        cache_dir = '/var/cache/apt/archives' 
        icon = get_icon_with_name('deb', 24)
        list = map(lambda file: "%s/%s" % (cache_dir, file),
                    filter(lambda x:x.endswith('deb'), os.listdir(cache_dir))) 
        self.total_num = len(list)
        self.__column.set_title('Cache need to be removed')

        for pkg in list:
            size = os.path.getsize(pkg)/1024

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

        self.__column.set_title(_('Package (%d Packages selected to remove)') % 
                             len(self.__check_list))

    def select_all(self, check = True):
        self.__check_list = []

        model = self.get_model()
        model.foreach(self.__select_foreach, check)
        self.emit('checked', check)

        self.__column.set_title(_('Package (%d Packages selected to remove)') % 
                             len(self.__check_list))

    def __select_foreach(self, model, path, iter, check):
        model.set(iter, COLUMN_CHECK, check)
        if check:
            self.__check_list.append(model.get_value(iter, COLUMN_NAME))

class PackageCleaner(TweakPage):
    def __init__(self):
        super(PackageCleaner, self).__init__(
                _('Package Cleaner'),
                _('Clean up the no more needed packages and the package cache.'))

        update_apt_cache(True)

        self.to_add = []
        self.to_rm = []

        hbox = gtk.HBox(False, 0)
        self.pack_start(hbox, True, True, 5)

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
        sw.add(self.treeview)

        # checkbutton
        self.select_button = gtk.CheckButton(_('Select All'))
        self.__handler_id = self.select_button.connect('toggled', self.on_select_all)
        self.pack_start(self.select_button, False, False, 0)

        # button
        hbox = gtk.HBox(False, 0)
        self.pack_end(hbox, False ,False, 0)

        self.clean_button = gtk.Button(stock = gtk.STOCK_CLEAR)
        self.clean_button.set_sensitive(False)
        hbox.pack_end(self.clean_button, False, False, 0)

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

if __name__ == '__main__':
    from Utility import Test
    Test(PackageCleaner)
