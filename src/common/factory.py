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

import UserDict
from consts import *
from widgets import *
from systeminfo import GnomeVersion
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class XmlHandler(ContentHandler):
    def __init__(self, dict):
        self.dict = dict

    def startElement(self, name, attrs):
        if name == 'item':
            try:
                minor = attrs['version']
            except KeyError:
                self.dict[attrs['title']] = attrs['key']
            else:
                if GnomeVersion.minor >= minor:
                    if attrs['key']:
                        self.dict[attrs['title']] = attrs['key']
                    else:
                        self.dict.pop(attrs['title'])

class GconfKeys:
    '''This class used to store the keys, it will create for only once'''
    keys = {}
    parser = make_parser()
    handler = XmlHandler(keys)
    parser.setContentHandler(handler)
    parser.parse('%s/tweaks.xml' % DATA_DIR)

class WidgetFactory:
    keys = GconfKeys.keys

    @classmethod
    def create(self, widget, *argv):
        return getattr(WidgetFactory, 'create_%s' % widget)(*argv)
    
    @classmethod
    def create_gconfcheckbutton(self, *argv):
        if len(argv) > 2:
            (label, key, tooltip) = argv[:3]
        else:
            tooltip = None
            (label, key) = argv[:2]

        if key in self.keys:
            button = GconfCheckButton(label, self.keys[key])
            if tooltip:
                button.set_tooltip_text(tooltip)
            return button
        else:
            return None

    @classmethod
    def create_cgconfcheckbutton(self, label, key, mediator, tooltip = None):
        if key in self.keys:
            button = CGconfCheckButton(label, self.keys[key], mediator)
            if tooltip:
                button.set_tooltip_text(tooltip)
            return button
        else:
            return None

    @classmethod
    def create_strgconfcheckbutton(self, label, key, mediator, tooltip = None):
        if key in self.keys:
            button = StrGconfCheckButton(label, self.keys[key], mediator)
            if tooltip:
                button.set_tooltip_text(tooltip)
            return button
        else:
            return None

    @classmethod
    def create_gconfentry(self, key, mediator = None, tooltip = None):
        if key in self.keys:
            entry = GconfEntry(self.keys[key])
            if tooltip:
                entry.set_tooltip_text(tooltip)
            return entry
        else:
            return None

    @classmethod
    def create_gconfcombobox(self, key, texts, values):
        if key in self.keys:
            combobox = GconfCombobox(self.keys[key], texts, values)
            return combobox.combobox
        else:
            return None

    @classmethod
    def create_gconfscale(self, min, max, key, digits = None):
        if key in self.keys:
            scale = GconfScale(min, max, self.keys[key], digits)
            return scale
        else:
            return None

class Factory:
    keys = GconfKeys.keys

    @staticmethod
    def create(widget = None, *argv):
        if len(argv) == 1:
            return getattr(Factory(), 'create_%s' % widget)(argv[0])
        elif len(argv) == 2:
            return getattr(Factory(), 'create_%s' % widget)(argv[0], argv[1])
        elif len(argv) == 3:
            return getattr(Factory(), 'create_%s' % widget)(argv[0], argv[1], argv[2])
        elif len(argv) == 4:
            return getattr(Factory(), 'create_%s' % widget)(argv[0], argv[1], argv[2], argv[3])
        elif len(argv) == 5:
            return getattr(Factory(), 'create_%s' % widget)(argv[0], argv[1], argv[2], argv[3], argv[4])
        elif len(argv) == 6:
            return getattr(Factory(), 'create_%s' % widget)(argv[0], argv[1], argv[2], argv[3], argv[4], argv[5])
    
    def create_gconfcheckbutton(self, label, key, tooltip = None):
        if key in self.keys:
            button = GconfCheckButton(label, self.keys[key])
            if tooltip:
                button.set_tooltip_text(tooltip)
            return button
        else:
            return None

    def create_cgconfcheckbutton(self, label, key, mediator, tooltip = None):
        if key in self.keys:
            button = CGconfCheckButton(label, self.keys[key], mediator)
            if tooltip:
                button.set_tooltip_text(tooltip)
            return button
        else:
            return None

    def create_strgconfcheckbutton(self, label, key, tooltip = None):
        if key in self.keys:
            button = StrGconfCheckButton(label, self.keys[key])
            if tooltip:
                button.set_tooltip_text(tooltip)
            return button
        else:
            return None

    def create_gconfentry(self, key, mediator = None, tooltip = None):
        if key in self.keys:
            entry = GconfEntry(self.keys[key])
            if tooltip:
                entry.set_tooltip_text(tooltip)
            return entry
        else:
            return None

    def create_gconfcombobox(self, key, texts, values):
        if key in self.keys:
            combobox = GconfCombobox(self.keys[key], texts, values)
            return combobox.combobox
        else:
            return None

    def create_gconfscale(self, min, max, key, digits = None):
        if key in self.keys:
            scale = GconfScale(min, max, self.keys[key], digits)
            return scale
        else:
            return None

    def create_gconfspinbutton(self, key, min = 0, max = 0, step = 0):
        if key in self.keys:
            button = GconfSpinButton(self.keys[key], min, max, step)
            return button
        else:
            return None


if __name__ == '__main__':
    for k,v in Factory.keys.items():
        print '%s\t%s\n' % (k, v)

    print WidgetFactory.create('gconfcheckbutton', _('Disable \'Run Application\' dialog (Alt+F2)'), 'disable_command_line')
