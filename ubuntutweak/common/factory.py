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

from xml.sax import make_parser
from xml.sax.handler import ContentHandler

from ubuntutweak.widgets import *
from ubuntutweak.common.settings import *
from ubuntutweak.common.consts import *
from ubuntutweak.common.systeminfo import GnomeVersion

class KeysHandler(ContentHandler):
    def __init__(self, dict):
        self.dict = dict

    def startElement(self, name, attrs):
        if name == 'key':
            if attrs.has_key('version'):
                version = attrs['version']

                if len(version.split(':')) == 2:
                        start, end = version.split(':')
                        if int(start) <= int(GnomeVersion.minor) <= int(end):
                            self.dict[attrs['name']] = attrs['value']
                else:
                    if GnomeVersion.minor == version:
                        self.dict[attrs['name']] = attrs['value']
            else:
                self.dict[attrs['name']] = attrs['value']

class GconfKeys:
    '''This class used to store the keys, it will create for only once'''
    keys = {}
    parser = make_parser()
    handler = KeysHandler(keys)
    parser.setContentHandler(handler)
    parser.parse('%s/keys.xml' % DATA_DIR)

class SettingFactory:
    keys = GconfKeys.keys

    @classmethod
    def create(cls, setting, **kwargs):
        if 'key' in kwargs:
            if not kwargs['key'].startswith('/'):
                kwargs['key'] = cls.keys[kwargs['key']]
            return getattr(cls, 'do_create')(setting, **kwargs)
        else:
            return None

    @classmethod
    def do_create(cls, **kwargs):
        return globals().get(setting)(**kwargs)

class WidgetFactory:
    keys = GconfKeys.keys

    @classmethod
    def create(cls, widget, **kwargs):
        if 'key' in kwargs:
            key = kwargs['key']

            if not key.startswith('/'):
                if key not in cls.keys:
                    return None
                else:
                    key = cls.keys[key]

            kwargs['key'] = key
            return getattr(cls, 'do_create')(widget, **kwargs)
        else:
            return None

    @classmethod
    def do_create(cls, widget, **kwargs):
        return globals().get(widget)(**kwargs)

if __name__ == '__main__':
    for k,v in GconfKeys.keys.items():
        print '%s\t%s\n' % (k, v)
