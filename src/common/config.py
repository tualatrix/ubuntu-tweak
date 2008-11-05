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
import gconf

class Config:
    dir = '/apps/ubuntu-tweak'
    __client = gconf.Client()

    def set_value(self, key, value):
        if not key.startswith("/"):
            key = self.build_key(key)

        if type(value) == int:
            self.__client.set_int(key, value)
        elif type(value) == float:
            self.__client.set_float(key, value)
        elif type(value) == str:
            self.__client.set_string(key, value)
        elif type(value) == bool:
            self.__client.set_bool(key, value)

    def get_value(self, key):
        if not key.startswith("/"):
            key = self.build_key(key)
		
        try:
            value = self.__client.get_value(key)
        except:
            return None
        else:
            return value

    def set_pair(self, key, type1, type2, value1, value2):
        if not key.startswith("/"):
            key = self.build_key(key)
		
        self.__client.set_pair(key, type1, type2, value1, value2)

    def get_pair(self, key):
        if not key.startswith("/"):
            key = self.build_key(key)

        value = self.__client.get(key)
        if value:
            return value.to_string().strip('()').split(',')
        else:
            return (0, 0)

    def get_string(self, key):
        if not key.startswith("/"):
            key = self.build_key(key)
        string = self.get_value(key)
        if string: 
            return string
        else: 
            return '0'

    def build_key(self, key):
        return os.path.join(self.dir, key)

    def get_client(self):
        return self.__client

class TweakSettings:
    '''Manage the settings of ubuntu tweak'''
    client = gconf.client_get_default()

    url = 'url'
    version = 'version'
    paned_size = 'paned_size'
    window_size= 'window_size'

    def __init__(self):
        self.__config = Config()

    def set_url(self, url):
        '''The new version's download url'''
        return self.__config.set_value(self.url, url)

    def get_url(self):
        return self.__config.get_string(self.url)

    def set_version(self, version):
        return self.__config.set_value(self.version, version)

    def get_version(self):
        return self.__config.get_string(self.version)

    def set_paned_size(self, size):
        self.__config.set_value(self.paned_size, size)

    def get_paned_size(self):
        position = self.__config.get_value(self.paned_size)

        if position:
            return position
        else:
            return 150

    def set_window_size(self, height, width):
        self.__config.set_pair(self.window_size, gconf.VALUE_INT, gconf.VALUE_INT, height, width)

    def get_window_size(self):
        height, width = self.__config.get_pair(self.window_size)
        height, width = int(height), int(width)

        if height and width:
            return (height, width)
        else:
            return (740, 480)

    def get_icon_theme(self):
        return self.__config.get_value('/desktop/gnome/interface/icon_theme')

if __name__ == '__main__':
    print Config().build_key('hello')
