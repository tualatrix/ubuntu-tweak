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

import os
import gtk
import gconf
from common.settings import *
from common.factory import GconfKeys

class Config:
    #FIXME The class should be generic config getter and setter
    __client = gconf.Client()

    def set_value(self, key, value):
        if not key.startswith("/"):
            key = GconfKeys.keys[key]

        if type(value) == int:
            self.__client.set_int(key, value)
        elif type(value) == float:
            self.__client.set_float(key, value)
        elif type(value) == str:
            self.__client.set_string(key, value)
        elif type(value) == bool:
            self.__client.set_bool(key, value)

    def get_value(self, key, default = None):
        if not key.startswith("/"):
            key = GconfKeys.keys[key]
		
        try:
            value = self.__client.get_value(key)
        except:
            if default is not None:
                self.set_value(key, default)
                return default
            else:
                return None
        else:
            return value

    def set_pair(self, key, type1, type2, value1, value2):
        if not key.startswith("/"):
            key = GconfKeys.keys[key]
		
        self.__client.set_pair(key, type1, type2, value1, value2)

    def get_pair(self, key):
        if not key.startswith("/"):
            key = GconfKeys.keys[key]

        value = self.__client.get(key)
        if value:
            return value.to_string().strip('()').split(',')
        else:
            return (0, 0)

    def get_string(self, key):
        if not key.startswith("/"):
            key = GconfKeys.keys[key]

        string = self.get_value(key)
        if string: 
            return string
        else: 
            return '0'

    def get_client(self):
        return self.__client

class TweakSettings:
    '''Manage the settings of ubuntu tweak'''
    config = Config()

    url = 'tweak_url'
    version = 'tweak_version'
    toolbar_size = 'toolbar_size'
    toolbar_color = 'toolbar_color'
    toolbar_font_color = 'toolbar_font_color'
    window_size= 'window_size'
    window_height = 'window_height'
    window_width = 'window_width'
    show_donate_notify = 'show_donate_notify'
    default_launch = 'default_launch'
    check_update = 'check_update'
    power_user = 'power_user'
    need_save = True

    @classmethod
    def get_power_user(cls):
        return cls.config.get_value(cls.power_user, default=False)

    @classmethod
    def set_power_user(cls, bool):
        cls.config.set_value(cls.power_user, bool)

    @classmethod
    def get_check_update(cls):
        return cls.config.get_value(cls.check_update, default = True)

    @classmethod
    def set_check_update(cls, bool):
        cls.config.set_value(cls.check_update, bool)

    @classmethod
    def get_toolbar_color(cls, instance = False):
        color = cls.config.get_value(cls.toolbar_color)
        if color == None:
            if instance:
                return gtk.gdk.Color(32767, 32767, 32767)
            return (0.5, 0.5, 0.5)
        else:
            try:
                color = gtk.gdk.color_parse(color)
                if instance:
                    return color
                red, green, blue = color.red/65535.0, color.green/65535.0, color.blue/65535.0
                return (red, green, blue)
            except:
                return (0.5, 0.5, 0.5)

    @classmethod
    def set_toolbar_color(cls, color):
        cls.config.set_value(cls.toolbar_color, color)

    @classmethod
    def get_toolbar_font_color(cls, instance = False):
        color = cls.config.get_value(cls.toolbar_font_color)
        if color == None:
            if instance:
                return gtk.gdk.Color(65535, 65535, 65535)
            return (1, 1, 1)
        else:
            try:
                color = gtk.gdk.color_parse(color)
                if instance:
                    return color
                red, green, blue = color.red/65535.0, color.green/65535.0, color.blue/65535.0
                return (red, green, blue)
            except:
                return (1, 1, 1)

    @classmethod
    def set_toolbar_font_color(cls, color):
        cls.config.set_value(cls.toolbar_font_color, color)

    @classmethod
    def set_default_launch(cls, id):
        cls.config.set_value(cls.default_launch, id)

    @classmethod
    def get_default_launch(cls):
        return cls.config.get_value(cls.default_launch)

    @classmethod
    def set_show_donate_notify(cls, bool):
        return cls.config.set_value(cls.show_donate_notify, bool)

    @classmethod
    def get_show_donate_notify(cls):
        value = cls.config.get_value(cls.show_donate_notify, default = True)

        return value

    @classmethod
    def set_url(cls, url):
        return cls.config.set_value(cls.url, url)

    @classmethod
    def get_url(cls):
        return cls.config.get_string(cls.url)

    @classmethod
    def set_version(cls, version):
        return cls.config.set_value(cls.version, version)

    @classmethod
    def get_version(cls):
        return cls.config.get_string(cls.version)

    @classmethod
    def set_paned_size(cls, size):
        cls.config.set_value(cls.toolbar_size, size)

    @classmethod
    def get_paned_size(cls):
        position = cls.config.get_value(cls.toolbar_size)

        if position:
            return position
        else:
            return 150

    @classmethod
    def set_window_size(cls, width, height):
        cls.config.set_value(cls.window_width, width)
        cls.config.set_value(cls.window_height, height)

    @classmethod
    def get_window_size(cls):
        width = cls.config.get_value(cls.window_width)
        height = cls.config.get_value(cls.window_height)

        if width and height:
            height, width = int(height), int(width)
            return (width, height)
        else:
            return (740, 480)

    @classmethod
    def get_icon_theme(cls):
        return cls.config.get_value('/desktop/gnome/interface/icon_theme')

if __name__ == '__main__':
    print Config().get_value('show_donate_notify')
