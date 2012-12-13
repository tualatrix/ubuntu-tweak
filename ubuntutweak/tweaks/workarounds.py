# coding: utf-8
# Ubuntu Tweak - Ubuntu Configuration Tool
#
# Copyright (C) 2007-2012 Tualatrix Chou <tualatrix@gmail.com>
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

import os
import logging

from gi.repository import Gtk

from ubuntutweak.modules  import TweakModule
from ubuntutweak.policykit.dbusproxy import proxy
from ubuntutweak.gui.containers import GridPack
from ubuntutweak.factory import WidgetFactory

log = logging.getLogger('Workarounds')

class Workarounds(TweakModule):
    __title__ = _('Workarounds')
    __desc__ = _('The workarounds to fix some problems')
    __icon__ = 'application-octet-stream'
    __category__ = 'system'

    utext_fix_theme = _('Fix the appearance of themes when granted root privileges:')
    utext_chinese_gedit = _("Auto detect text encoding for Simplified Chinese in Gedit:")

    ROOT_THEMES = '/root/.themes'
    ROOT_ICONS = '/root/.icons'

    def __init__(self):
        TweakModule.__init__(self)

        self.fix_theme_button = Gtk.Switch()
        self.fix_theme_label = Gtk.Label(self.utext_fix_theme)
        self.set_fix_theme_button_status()

        self.fix_theme_button.connect('notify::active', self.on_fix_theme_button_toggled)

        box = GridPack(
                (self.fix_theme_label, self.fix_theme_button),
                WidgetFactory.create("Switch",
                                     label=self.utext_chinese_gedit,
                                     key="org.gnome.gedit.preferences.encodings.auto-detected",
                                     on=['GB18030', 'UTF-8', 'CURRENT', 'ISO-8859-15', 'UTF-16'],
                                     off=['UTF-8', 'CURRENT', 'ISO-8859-15', 'UTF-16'],
                                     backend="gsettings",
                                     enable_reset=True)
            )
        self.add_start(box)

    def on_fix_theme_button_toggled(self, widget, *args):
        try:
            if widget.get_active():
                proxy.link_file(os.path.expanduser('~/.themes'), self.ROOT_THEMES)
                proxy.link_file(os.path.expanduser('~/.icons'), self.ROOT_ICONS)
            else:
                proxy.unlink_file(self.ROOT_THEMES)
                proxy.unlink_file(self.ROOT_ICONS)
                self.set_fix_theme_button_status()
        except Exception, e:
            log.error(e)
            self.set_fix_theme_button_status()

    def set_fix_theme_button_status(self):
        if proxy.is_exists(self.ROOT_THEMES) and proxy.is_exists(self.ROOT_ICONS):
            self.fix_theme_button.set_active(True)
        else:
            self.fix_theme_button.set_active(False)
