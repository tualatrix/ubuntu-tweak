# Ubuntu Tweak - Ubuntu Configuration Tool
#
# Copyright (C) 2007-2011 Tualatrix Chou <tualatrix@gmail.com>
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
from ubuntutweak.policykit import PolkitButton, proxy
from ubuntutweak.gui.containers import ListPack
from ubuntutweak.gui.dialogs import AuthenticateFailDialog
from ubuntutweak.factory import WidgetFactory

class Workarounds(TweakModule):
    __title__ = _('Workarounds')
    __desc__ = _('The workarounds to fix some problems')
    __icon__ = 'application-octet-stream'
    __category__ = 'system'

    ROOT_THEMES = '/root/.themes'
    ROOT_ICONS = '/root/.icons'

    def __init__(self):
        TweakModule.__init__(self)

        self.fix_theme_button = Gtk.CheckButton(_('Fix the appearance of themes when granted root privileges'))
        if proxy.is_exists(self.ROOT_THEMES) and proxy.is_exists(self.ROOT_ICONS):
            self.fix_theme_button.set_active(True)

        self.fix_theme_button.connect('toggled', self.on_fix_theme_btn_taggled)
        self.fix_theme_button.set_sensitive(False)
        box = ListPack(_('Miscellaneous Options'), (self.fix_theme_button,))
        self.add_start(box, False, False, 0)

        hbox = Gtk.HBox(spacing=12)
        self.add_end(hbox, False ,False, 0)

        un_lock = PolkitButton()
        un_lock.connect('changed', self.on_polkit_action)
        hbox.pack_end(un_lock, False, False, 0)

    def on_fix_theme_btn_taggled(self, widget):
        if widget.get_active():
            proxy.link_file(os.path.expanduser('~/.themes'), self.ROOT_THEMES)
            proxy.link_file(os.path.expanduser('~/.icons'), self.ROOT_ICONS)
        else:
            proxy.unlink_file(self.ROOT_THEMES)
            proxy.unlink_file(self.ROOT_ICONS)
            if proxy.is_exists(ROOT_THEMES) and proxy.is_exists(self.ROOT_ICONS):
                widget.set_active(True)

    def on_polkit_action(self, widget, action):
        if action:
            self.fix_theme_button.set_sensitive(True)
        else:
            AuthenticateFailDialog().launch()
