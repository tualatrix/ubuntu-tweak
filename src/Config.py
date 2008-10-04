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

    def build_key(self, key):
        return os.path.join(self.dir, key)

    def get_client(self):
        return self.__client

if __name__ == '__main__':
    print Config().build_key('hello')
