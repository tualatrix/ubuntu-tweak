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

import os
import gtk
import gconf

from ubuntutweak0.conf import GconfSetting
from ubuntutweak0.common.factory import GconfKeys

class Config(GconfSetting):
    def set_value_from_key(self, key, value):
        self.set_key(key)
        self.set_value(value)

    def get_value_from_key(self, key, default=None):
        self.set_key(key)
        self.set_default(default)
        return self.get_value()

class TweakSettings:
    '''Manage the settings of ubuntu tweak'''
    config = Config()

    url = 'tweak_url'
    version = 'tweak_version'
    toolbar_size = 'toolbar_size'
    window_size= 'window_size'
    window_height = 'window_height'
    window_width = 'window_width'
    show_donate_notify = 'show_donate_notify'
    default_launch = 'default_launch'
    check_update = 'check_update'
    sync_notify = 'sync_notify'
    separated_sources = 'separated_sources'
    use_mirror_ppa = 'use_mirror_ppa'
    enable_new_item = 'enable_new_item'
    need_save = True

    @classmethod
    def get_enable_new_item(cls):
        return cls.config.get_value_from_key(cls.enable_new_item, default=True)

    @classmethod
    def set_enable_new_item(cls, bool):
        cls.config.set_value_from_key(cls.enable_new_item, bool)

    @classmethod
    def get_check_update(cls):
        return cls.config.get_value_from_key(cls.check_update, default=True)

    @classmethod
    def set_check_update(cls, bool):
        cls.config.set_value_from_key(cls.check_update, bool)

    @classmethod
    def set_default_launch(cls, id):
        cls.config.set_value_from_key(cls.default_launch, id)

    @classmethod
    def get_default_launch(cls):
        return cls.config.get_value_from_key(cls.default_launch)

    @classmethod
    def set_show_donate_notify(cls, bool):
        return cls.config.set_value_from_key(cls.show_donate_notify, bool)

    @classmethod
    def get_show_donate_notify(cls):
        return cls.config.get_value_from_key(cls.show_donate_notify, default=True)

    @classmethod
    def set_sync_notify(cls, bool):
        return cls.config.set_value_from_key(cls.sync_notify, bool)

    @classmethod
    def get_sync_notify(cls):
        return cls.config.get_value_from_key(cls.sync_notify, default=True)

    def set_use_mirror_ppa(cls, bool):
        return cls.config.set_value_from_key(cls.use_mirror_ppa, bool)

    @classmethod
    def get_use_mirror_ppa(cls):
        return cls.config.get_value_from_key(cls.use_mirror_ppa, default=False)

    @classmethod
    def set_separated_sources(cls, bool):
        return cls.config.set_value_from_key(cls.separated_sources, bool)

    @classmethod
    def get_separated_sources(cls):
        return cls.config.get_value_from_key(cls.separated_sources, default=True)

    @classmethod
    def set_url(cls, url):
        return cls.config.set_value_from_key(cls.url, url)

    @classmethod
    def get_url(cls):
        return cls.config.get_value_from_key(cls.url)

    @classmethod
    def set_version(cls, version):
        return cls.config.set_value_from_key(cls.version, version)

    @classmethod
    def get_version(cls):
        return cls.config.get_value_from_key(cls.version)

    @classmethod
    def set_paned_size(cls, size):
        cls.config.set_value_from_key(cls.toolbar_size, size)

    @classmethod
    def get_paned_size(cls):
        position = cls.config.get_value_from_key(cls.toolbar_size)

        if position:
            return position
        else:
            return 150

    @classmethod
    def set_window_size(cls, width, height):
        cls.config.set_value_from_key(cls.window_width, width)
        cls.config.set_value_from_key(cls.window_height, height)

    @classmethod
    def get_window_size(cls):
        width = cls.config.get_value_from_key(cls.window_width, default=900)
        height = cls.config.get_value_from_key(cls.window_height, default=500)

        return (width, height)

    @classmethod
    def get_icon_theme(cls):
        return cls.config.get_value_from_key('/desktop/gnome/interface/icon_theme')

if __name__ == '__main__':
    print Config().get_value_from_key('show_donate_notify')
