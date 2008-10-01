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
    def __init__(self):
        super(PackageView, self).__init__()

        model = self.__create_model()
        self.set_model(model)
        self.__packageworker = PackageWorker()

        self.__add_column()

        self.update_model()
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
#        renderer.connect('toggled', self.on_enable_toggled)
        column = gtk.TreeViewColumn(' ', renderer, active = COLUMN_CHECK)
        column.set_sort_column_id(COLUMN_CHECK)
        self.append_column(column)

        column = gtk.TreeViewColumn(_('Package'))
        column.set_sort_column_id(COLUMN_NAME)
        column.set_spacing(5)
        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, pixbuf = COLUMN_ICON)

        renderer = gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.set_attributes(renderer, markup = COLUMN_DISPLAY)

        self.append_column(column)

    def update_model(self):
        model = self.get_model()
        icon = get_icon_with_name('deb', 24)

        list = self.__packageworker.list_autoeemovable()

        for pkg in list:
            desc = self.__packageworker.get_pkgsummary(pkg)

            model.append((
                False,
                icon,
                pkg,
                desc,
                '<b>%s</b>\n%s' % (pkg, desc)
                ))

class PackageCleaner(TweakPage):
    def __init__(self):
        super(PackageCleaner, self).__init__(
                _('Package Cleaner'),
                _('Clean up non-useless packages and the package cache!'))

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
        treeview = PackageView()
        treeview.set_rules_hint(True)
        sw.add(treeview)

        # checkbutton
        checkbutton = gtk.CheckButton(_('Select All'))
        self.pack_start(checkbutton, False, False, 0)

        # button
        hbox = gtk.HBox(False, 0)
        self.pack_end(hbox, False ,False, 0)

        self.button = gtk.Button(stock = gtk.STOCK_CLEAR)
        self.button.set_sensitive(False)
        hbox.pack_end(self.button, False, False, 0)

        self.show_all()

    def on_button_toggled(self, widget):
        if widget == self.cache_button:
            self.pkg_button.set_active(not widget.get_active())
        elif widget == self.pkg_button:
            self.cache_button.set_active(not widget.get_active())

if __name__ == '__main__':
    from Utility import Test
    Test(PackageCleaner)
