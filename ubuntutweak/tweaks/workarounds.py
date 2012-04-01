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
from gi.repository import Gtk

from ubuntutweak.modules  import TweakModule
from ubuntutweak.policykit import PK_ACTION_TWEAK
from ubuntutweak.policykit.dbusproxy import proxy
from ubuntutweak.gui.containers import GridPack
from ubuntutweak.factory import WidgetFactory

class Workarounds(TweakModule):
    __title__ = _('Workarounds')
    __desc__ = _('The workarounds to fix some problems')
    __icon__ = 'application-octet-stream'
    __category__ = 'system'
    __policykit__ = PK_ACTION_TWEAK

    ROOT_THEMES = '/root/.themes'
    ROOT_ICONS = '/root/.icons'

    def __init__(self):
        TweakModule.__init__(self)

        self.fix_theme_button = Gtk.Switch()
        self.fix_theme_label = Gtk.Label(_('Fix the appearance of themes when granted root privileges'))
        if proxy.is_exists(self.ROOT_THEMES) and proxy.is_exists(self.ROOT_ICONS):
            self.fix_theme_button.set_active(True)

        self.fix_theme_button.connect('notify::active', self.on_fix_theme_btn_taggled)
        self.fix_theme_button.set_sensitive(False)

        encoding_label, encoding_switch, reset_encoding = WidgetFactory.create("Switch",
                                                label=_("Auto detect text encoding for Chinese in Gedit"),
                                                key="org.gnome.gedit.preferences.encodings.auto-detected",
                                                on=['GB18030', 'UTF-8', 'CURRENT', 'ISO-8859-15', 'UTF-16'],
                                                off=['UTF-8', 'CURRENT', 'ISO-8859-15', 'UTF-16'],
                                                backend="gsettings",
                                                enable_reset=True)
        box = GridPack(
                (self.fix_theme_label, self.fix_theme_button),
                (encoding_label, encoding_switch, reset_encoding),
            )
        self.add_start(box)

    def on_fix_theme_btn_taggled(self, widget, *args):
        if widget.get_active():
            proxy.link_file(os.path.expanduser('~/.themes'), self.ROOT_THEMES)
            proxy.link_file(os.path.expanduser('~/.icons'), self.ROOT_ICONS)
        else:
            proxy.unlink_file(self.ROOT_THEMES)
            proxy.unlink_file(self.ROOT_ICONS)
            if proxy.is_exists(self.ROOT_THEMES) and proxy.is_exists(self.ROOT_ICONS):
                widget.set_active(True)

    def on_polkit_action(self, widget):
        self.fix_theme_button.set_sensitive(True)
