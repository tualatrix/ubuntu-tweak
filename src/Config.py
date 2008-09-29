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
from common.Settings import *

class Config:
    dir = '/apps/ubuntu-tweak'

    @classmethod
    def set_value(self, key, value):
        if type(value) == int:
            pass
        elif type(value) == str:
            pass
        elif type(value) == bool:
            pass

    @classmethod
    def get_value(self, key):
        pass

    @classmethod
    def build_key(self, key):
        return os.path.join(self.dir, key)

if __name__ == '__main__':
    print Config.build_key('hello')
