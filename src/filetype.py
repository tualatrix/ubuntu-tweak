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
import gobject

from common.factory import Factory
from common.widgets import TweakPage
from common.mimetype import MIMETYPE, MIMETYPE_LIST
from common.utils import get_icon_with_name, mime_type_get_icon

(
    COLUMN_ICON,
    COLUMN_TITLE,
    COLUMN_LIST,
) = range(3)

class CateView(gtk.TreeView):
    def __init__(self):
        gtk.TreeView.__init__(self)

        self.set_headers_visible(False)
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
        column = gtk.TreeViewColumn()

        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, pixbuf = COLUMN_ICON)

        renderer = gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.set_attributes(renderer, text = COLUMN_TITLE)

        self.append_column(column)

    def update_model(self):
        for title, (list, icon) in MIMETYPE.items():
            pixbuf = get_icon_with_name(icon, 24)
            iter = self.model.append(None)
            self.model.set(iter, COLUMN_ICON, pixbuf, COLUMN_TITLE, title)

class TypeView(gtk.TreeView):
    def __init__(self):
        gtk.TreeView.__init__(self)

        self.set_headers_visible(False)
        self.model = self.__create_model()
        self.set_model(self.model)
        self.update_model()
        self.__add_columns()

    def __create_model(self):
        '''The model is icon, title and the list reference'''
        model = gtk.ListStore(
                    gtk.gdk.Pixbuf,
                    gobject.TYPE_STRING)
        
        return model

    def __add_columns(self):
        column = gtk.TreeViewColumn()

        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, pixbuf = COLUMN_ICON)

        renderer = gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.set_attributes(renderer, text = COLUMN_TITLE)

        self.append_column(column)

    def update_model(self):
        for type in MIMETYPE_LIST:
            pixbuf = mime_type_get_icon(type, 24)
            iter = self.model.append(None)
            self.model.set(iter, COLUMN_ICON, pixbuf, COLUMN_TITLE, type)

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

        self.show_all()

if __name__ == "__main__":
    from utility import Test
    Test(FileType)
