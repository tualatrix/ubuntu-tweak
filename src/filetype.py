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

import pygtk
pygtk.require("2.0")
import gtk
import gio
import gobject

from common.factory import Factory
from common.widgets import TweakPage
from common.mimetype import MIMETYPE, MIMETYPE_LIST
from common.utils import get_icon_with_name, mime_type_get_icon, get_icon_with_app

(
    COLUMN_ICON,
    COLUMN_TITLE,
    COLUMN_LIST,
) = range(3)

class CateView(gtk.TreeView):
    def __init__(self):
        gtk.TreeView.__init__(self)

        self.set_rules_hint(True)
        self.model = self.__create_model()
        self.set_model(self.model)
        self.update_model()
        self.__add_columns()

#        self.set_size_request(80, -1)

    def __create_model(self):
        '''The model is icon, title and the list reference'''
        model = gtk.ListStore(
                    gtk.gdk.Pixbuf,
                    gobject.TYPE_STRING)
        
        return model

    def __add_columns(self):
        column = gtk.TreeViewColumn(_('Type Categories'))

        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, pixbuf = COLUMN_ICON)

        renderer = gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.set_sort_column_id(COLUMN_TITLE)
        column.set_attributes(renderer, text = COLUMN_TITLE)

        self.append_column(column)

    def update_model(self):
        for title, (list, icon) in MIMETYPE.items():
            pixbuf = get_icon_with_name(icon, 24)
            iter = self.model.append(None)
            self.model.set(iter, COLUMN_ICON, pixbuf, COLUMN_TITLE, title)


(
    TYPE_ICON,
    TYPE_DESCRIPTION,
    TYPE_APPICON,
    TYPE_APP,
) = range(4)

class TypeView(gtk.TreeView):
    def __init__(self):
        gtk.TreeView.__init__(self)

        self.model = self.__create_model()
        self.set_search_column(TYPE_DESCRIPTION)
        self.set_model(self.model)
        self.set_rules_hint(True)
        self.__add_columns()
        self.update_model()

    def __create_model(self):
        '''The model is icon, title and the list reference'''
        model = gtk.ListStore(
                    gtk.gdk.Pixbuf,
                    gobject.TYPE_STRING,
                    gtk.gdk.Pixbuf,
                    gobject.TYPE_STRING,
                    )
        
        return model

    def __add_columns(self):
        column = gtk.TreeViewColumn(_('File Type'))

        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, pixbuf = TYPE_ICON)

        renderer = gtk.CellRendererText()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, text = TYPE_DESCRIPTION)
        column.set_sort_column_id(TYPE_DESCRIPTION)
        self.append_column(column)

        column = gtk.TreeViewColumn(_('Associated Application'))

        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, pixbuf = TYPE_APPICON)

        renderer = gtk.CellRendererText()
        column.pack_start(renderer, False)
        column.set_sort_column_id(TYPE_APP)
        column.set_attributes(renderer, text = TYPE_APP)

        self.append_column(column)

    def update_model(self, all = False):
        for type in gio.content_types_get_registered()[:100]:
            pixbuf = mime_type_get_icon(type, 24)
            description = gio.content_type_get_description(type)
            app = gio.app_info_get_default_for_type(type, False)

            if app:
                appname = app.get_name()
                applogo = get_icon_with_app(app, 24)
            elif all and not app:
                appname = ''
                applogo = get_icon_with_name('gtk-execute', 24)
            else:
                continue
            
#            self.model.set(iter, TYPE_ICON, pixbuf, TYPE_DESCRIPTION, description, TYPE_APP, appname)
            iter = self.model.append()
            self.model.set(iter, 
                    TYPE_ICON, pixbuf, 
                    TYPE_DESCRIPTION, description,
                    TYPE_APPICON, applogo,
                    TYPE_APP, appname)

class FileType(TweakPage):
    def __init__(self):
        TweakPage.__init__(self,
                _('File Type'),
                _('Modify your file type.'))

        hbox = gtk.HBox(False, 5)
        self.pack_start(hbox)

        cateview = CateView()
        hbox.pack_start(cateview, False, False, 0)

        typeview = TypeView()
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(typeview)
        hbox.pack_start(sw)

        vbox = gtk.VBox(False, 5)
        hbox.pack_start(vbox, False, False, 0)

        button = gtk.Button(stock = gtk.STOCK_ADD)
        vbox.pack_start(button, False, False, 0)

        button = gtk.Button(stock = gtk.STOCK_REMOVE)
        button.set_sensitive(False)
        vbox.pack_start(button, False, False, 0)

        button = gtk.Button(stock = gtk.STOCK_EDIT)
        button.set_sensitive(False)
        vbox.pack_start(button, False, False, 0)

        show_have_app = gtk.CheckButton(_('Only show associated type'))
        self.pack_start(show_have_app, False, False, 5)

        self.show_all()

if __name__ == "__main__":
    from utility import Test
    Test(FileType)
