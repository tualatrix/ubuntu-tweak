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

import gconf
import gobject

from ubuntutweak.policykit import proxy

__all__ = (
    'Setting',
    'BoolSetting',
    'SystemBoolSetting',
    'StringSetting',
    'IntSetting',
    'FloatSetting',
    'NumSetting',
    'ConstStringSetting',
)

class Setting(object):
    """
    The base class of an option, client is shared by all subclass
    Every Setting hold a key and a value
    """

    __client = gconf.client_get_default()

    def __init__(self, key = None, default = None):
        assert key is not None
        self.__key = key

        if default is not None:
            value = self.get_value()
            if value is None:
                self.set_value(default)

        self.__client.add_dir(self.dir, gconf.CLIENT_PRELOAD_NONE)

    def set_key(self, key):
        self.__key == key

    def get_key(self):
        return self.__key
    key = property(get_key, set_key)

    def get_dir(self):
        return '/'.join(self.__key.split('/')[0: -1])
    dir = property(get_dir)

    def set_value(self, value):
        self.__client.set_value(self.__key, value)
    def get_value(self):
        try:
            return self.__client.get_value(self.__key)
        except ValueError:
            return None
    value = property(get_value, set_value)

    def get_client(self):
        return self.__client
    client = property(get_client)

    def unset(self):
        self.client.unset(self.key)

    def connect_notify(self, func):
        self.__client.notify_add(self.key, func)

class BoolSetting(Setting):
    def __init__(self, key, default = None):
        super(BoolSetting, self).__init__(key, default)

    def set_bool(self, value):
        self.value = bool(value)

    def get_bool(self):
        return bool(self.value)

class SystemBoolSetting(object):
    def __init__(self, key, default=None):
        self.__key = key

    def set_bool(self, value):
        if value:
            proxy.set_system_gconf(self.__key, 'true', 'bool', '')
        else:
            proxy.set_system_gconf(self.__key, 'false', 'bool', '')

    def get_bool(self):
        data = proxy.get_system_gconf(self.__key)
        if str(data).startswith('true'):
            return True
        else:
            return False

class StringSetting(Setting):
    def __init__(self, key, default = None):
        super(StringSetting, self).__init__(key, default)

    def set_string(self, value):
        self.value = value

    def get_string(self):
        if self.value:
            return str(self.value)
        else:
            return ''

class IntSetting(Setting):
    def __init__(self, key, default = None):
        super(IntSetting, self).__init__(key, default)

    def set_int(self, value):
        self.value = int(value)

    def get_int(self):
        if self.value:
            return int(self.value)
        else:
            return 0

class FloatSetting(Setting):
    def __init__(self, key, default = None):
        super(FloatSetting, self).__init__(key, default)

    def set_float(self, value):
        self.value = float(value)

    def get_float(self):
        if self.value:
            return float(self.value)
        else:
            return 0.0

class NumSetting(Setting):
    def __init__(self, key, default = None):
        super(NumSetting, self).__init__(key, default)

    def get_num(self):
        if self.value:
            value = self.client.get(self.key)
            if value:
                if value.type == gconf.VALUE_INT:
                    return value.get_int()
                elif value.type == gconf.VALUE_FLOAT:
                    return value.get_float()
            else:
                return 0
        else:
            return 0

    def set_num(self, num):
        value = self.client.get(self.key)
        if value:
            if value.type == gconf.VALUE_INT:
                self.client.set_int(self.key, int(num))
            elif value.type == gconf.VALUE_FLOAT:
                self.client.set_float(self.key, num)
        else:
            self.client.set_int(self.key, int(num))

class ConstStringSetting(StringSetting):
    def __init__(self, key, values):
        StringSetting.__init__(self, key)

        self.values = values
