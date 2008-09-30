#!/usr/bin/env python

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

import gconf
import gobject

__all__ = (
    'Setting',
    'BoolSetting',
    'StringSetting',
    'NumSetting',
    'ConstStringSetting',
)

class Setting(gobject.GObject):
    """
    The base class of an option, client is shared by all subclass
    Every Setting hold a key and a value
    """

    __client = gconf.client_get_default()

    def __init__(self, key):
        super(Setting, self).__init__()
        self.__key = key
        self.__dir = self.get_dir()

        self.__client.add_dir(self.__dir, gconf.CLIENT_PRELOAD_NONE)
#       self.__client.notify_add(key, self.value_changed, key)

    def value_changed(self, client, id, entry, data = None):
        pass

    def set_value(self, value):
        pass

    def set_string(self, string):
        self.__client.set_string(self.__key, string)

    def get_dir(self):
        return "/".join(self.__key.split("/")[0: -1])

    def get_key(self):
        return self.__key

    def get_value(self):
        return self.__client.get(self.__key)

    def get_client(self):
        return self.__client

    def unset(self):
        self.__client.unset(self.__key)

gobject.type_register(Setting)

class BoolSetting(Setting):
    def __init__(self, key):
        super(BoolSetting, self).__init__(key)

    def set_bool(self, bool):
        self.get_client().set_bool(self.get_key(), bool)

    def get_bool(self):
        value = self.get_value()
        if value:
            if value.type == gconf.VALUE_BOOL:
                return value.get_bool()
            elif value.type == gconf.VALUE_STRING:
                return bool(value.get_string())
            elif value.type == gconf.VALUE_INT:
                return bool(value.get_int())
        else:
            return False

class StringSetting(Setting):
    def __init__(self, key):
        super(StringSetting, self).__init__(key)

    def get_string(self):
        value = self.get_value()
        if value:
            return value.get_string()
        else:
            return ''

class IntString(Setting):
    def __init__(self, key):
        super(IntString, self).__init__(key)

        self.__int = self.__get_int()

    def __get_int(self):
        self.__value = self.__client.get(self.__key)
        if self.__value:
            return self.__value.get_int()
        else:
            return 0

    def get_int(self):
        return self.__int

class FloatString(Setting):
    def __init__(self, key):
        super(IntString, self).__init__(key)

        self.__float = self.__get_float()

    def __get_float(self):
        self.__value = self.__client.get(self.__key)
        if self.__value:
            return self.__value.get_float()
        else:
            return 0

    def get_float(self):
        return self.__float

class NumSetting(Setting):
    def __init__(self, key):
        super(NumSetting, self).__init__(key)

    def get_num(self):
        value = self.get_value()
        if value:
            if value.type == gconf.VALUE_INT:
                return value.get_int()
            elif value.type == gconf.VALUE_FLOAT:
                return value.get_float()
        else:
            return 0

    def set_num(self, num):
        value = self.get_value()
        key = self.get_key()
        client = self.get_client()
        if value:
            if value.type == gconf.VALUE_INT:
                client.set_int(key, int(num))
            elif value.type == gconf.VALUE_FLOAT:
                client.set_float(key, num)
        else:
            client.set_float(key, num)

class ConstStringSetting(StringSetting):
    def __init__(self, key, values):
        StringSetting.__init__(self, key)

        self.values = values
