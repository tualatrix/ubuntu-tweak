#! /usr/bin/env python
#-*- encoding:utf-8 -*-
#文件名:cellrenderbutton.py
"""Test code

Description:________
"""
__version__  = "0.1"
__date__     = "2009-02-20 15:38:24"
__author__   = "Mingxi Wu <fengshenx@gmail.com> "
__license__  = "Licensed under the GPL v2, see the file LICENSE in this tarball."
__copyright__= "Copyright (C) 2009 by Mingxi Wu <fengshenx@gmail.com>."
#=================================================================================#
# ChangeLog
# 2009-11-18
# TualatriX, make it can accept text data

import cairo
from gi.repository import GObject, Gtk, Pango

class CellRendererButton(Gtk.CellRenderer):
    __gsignals__ = {
        'clicked': (GObject.SignalFlags.RUN_FIRST,
                    None,
                    (GObject.TYPE_STRING,))
    }

    __gproperties__ = {
        'text': (GObject.TYPE_STRING, 'Text',
                 'Text for button', '', GObject.PARAM_READWRITE)
    }

    def __init__(self, text=None):
        GObject.GObject.__init__(self)

        self.text = text
        self._xpad = 6
        self._ypad = 2
        self.set_property('mode', Gtk.CellRendererMode.ACTIVATABLE)

    def do_set_property(self, pspec, value):
        setattr(self, pspec.name, value)

    def do_get_property(self, pspec):
        return getattr(self, pspec.name)

    def do_get_size (self, widget, x, y, width, height, data):
        context = widget.get_pango_context()
        metrics = context.get_metrics(widget.style.font_desc, 
                                      context.get_language())
        row_height = metrics.get_ascent() + metrics.get_descent()
        height = (row_height + 512 >> 10) + self._ypad * 2

        layout = widget.create_pango_layout(self.text)
        (row_width, layout_height) = layout.get_pixel_size()
        width = row_width + self._xpad * 2
        print width, height
        
        return (0, 0, width, height)

    def do_render(self, window, widget,
                  background_area, cell_area, expose_area, flags):
        layout = widget.create_pango_layout(self.text)
        (layout_width, layout_height) = layout.get_pixel_size()
        layout_xoffset = (cell_area.width - layout_width) / 2 + cell_area.x
        layout_yoffset = (cell_area.height - layout_height) / 2 + cell_area.y

        Gtk.paint_box(widget.style, window, widget.state, Gtk.ShadowType.OUT, 
                               expose_area, widget, 'button',
                               cell_area.x, cell_area.y,
                               cell_area.width, cell_area.height)
        Gtk.paint_layout(widget.style, window, widget.state, True, expose_area,
                                  widget, "cellrenderertext", layout_xoffset,
                                  layout_yoffset, layout)

    def do_activate(self, event, widget, path,
                    background_area, cell_area, flags):
        self.emit('clicked', path)

GObject.type_register(CellRendererButton)
