#!/usr/bin/python

# Ubuntu Tweak - PyGTK based desktop configuration tool
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
import pango
import gobject
import logging

log = logging.getLogger('containers')

class BasePack(gtk.VBox):
    def __init__(self, title):
        gtk.VBox.__init__(self)
        self.set_border_width(5)

        title = gtk.MenuItem(title)
        title.select()
        self.pack_start(title, False, False, 0)

class SinglePack(BasePack):
    def __init__(self, title, widget):
        BasePack.__init__(self, title)

        self.pack_start(widget, True, True, 10)

class BaseListPack(BasePack):
    def __init__(self, title):
        BasePack.__init__(self, title)

        hbox = gtk.HBox(False, 0)
        hbox.set_border_width(5)
        self.pack_start(hbox, True, False, 0)

        label = gtk.Label(" ")
        hbox.pack_start(label, False, False, 0)

        self.vbox = gtk.VBox(False, 0)
        hbox.pack_start(self.vbox, True, True, 0)

class ListPack(BaseListPack):
    def __init__(self, title, widgets, padding=6):
        BaseListPack.__init__(self, title)
        self.items = []

        if widgets:
            for widget in widgets:
                if widget: 
                    if widget.get_parent():
                        widget.unparent()
                    self.vbox.pack_start(widget, False, False, padding)
                    self.items.append(widget)
        else:
            self = None

class TablePack(BaseListPack):
    def __init__(self, title, items):
        BaseListPack.__init__(self, title)

        columns = 1
        for i, item in enumerate(items):
            rows = i + 1
            if len(item) > columns:
                columns = len(item)

        table = gtk.Table(rows, columns)

        for item in items:
            if item is not None:
                top_attach = items.index(item)

                if issubclass(item.__class__, gtk.Widget):
                    table.attach(item, 0, columns, top_attach, top_attach + 1, ypadding=6)
                else:
                    for widget in item:
                        if widget:
                            left_attch = item.index(widget)

                            if type(widget) == gtk.Label:
                                widget.set_alignment(0, 0.5)

                            if left_attch == 1:
                                table.attach(widget, left_attch, left_attch + 1, top_attach, top_attach + 1, xpadding=12, ypadding=6)
                            else:
                                table.attach(widget, left_attch, left_attch + 1, top_attach, top_attach + 1, gtk.FILL, ypadding=6)

        self.vbox.pack_start(table)
        
class TweakPage(gtk.ScrolledWindow):
    """The standard page of tweak"""
    __gsignals__ = {
            'update': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_STRING)),
            'call': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
    }

    def __init__(self, title = None, des = None):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.vbox = gtk.VBox(False, 0)
        self.add_with_viewport(self.vbox)
        viewport = self.get_child()
        viewport.set_shadow_type(gtk.SHADOW_NONE)

        if title:
            self.set_title(title)

        if des:
            self.set_description(des)

    def pack_start(self, child, expand = True, fill = True, padding = 0):
        self.vbox.pack_start(child, expand, fill, padding)

    def pack_end(self, child, expand = True, fill = True, padding = 0):
        self.vbox.pack_end(child, expand, fill, padding)

    def set_title(self, title):
        if not getattr(self, 'title', None):
            self.set_border_width(5)

            self.title = gtk.MenuItem(title)
            self.title.select()
            self.pack_start(self.title, False, False, 0)

    def set_description(self, des):
        if not getattr(self, 'description', None):
            self.description = gtk.Label()
            self.description.set_ellipsize(pango.ELLIPSIZE_END)
            self.description.set_alignment(0, 0)
            self.pack_start(self.description, False, False, 5)
            self.description.set_markup(des)        

    def remove_all_children(self):
        for child in self.vbox.get_children():
            self.vbox.remove(child)
