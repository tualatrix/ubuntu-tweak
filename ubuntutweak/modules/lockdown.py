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

import os
import gtk

from ubuntutweak.modules  import TweakModule
from ubuntutweak.policykit import PolkitButton, proxy
from ubuntutweak.widgets import ListPack
from ubuntutweak.common.factory import WidgetFactory

ROOT_THEMES = '/root/.themes'
ROOT_ICONS = '/root/.icons'

class LockDown(TweakModule):
    __title__ = _('Security Related')
    __desc__ = _('Setup some security options')
    __icon__ = ['gtk-dialog-authentication', 'stock_keyring']
    __category__ = 'system'

    """Lock down some function"""
    def __init__(self):
        TweakModule.__init__(self)

        box = ListPack(_("System Security options"), (
                    WidgetFactory.create("GconfCheckButton",
                                         label=_("Disable \"Run Application\" dialog (Alt+F2)"),
                                         key="disable_command_line"),
                    WidgetFactory.create("GconfCheckButton",
                                         label=_('Disable "Lock Screen"'),
                                         key="disable_lock_screen"),
                    WidgetFactory.create("GconfCheckButton",
                                         label=_("Disable printing"),
                                         key="disable_printing"),
                    WidgetFactory.create("GconfCheckButton",
                                         label=_("Disable print setup"),
                                         key="disable_print_setup"),
                    WidgetFactory.create("GconfCheckButton",
                                         label=_("Disable save to disk"),
                                         key="disable_save_to_disk"),
                    WidgetFactory.create("GconfCheckButton",
                                         label=_('Disable "Fast User Switching"'),
                                         key="disable_user_switching"),
            ))

        self.add_start(box, False, False, 0)

        self.fix_theme_button = gtk.CheckButton(_('Fix the theme appearance when grant the root privileges'))
        if proxy.is_exists(ROOT_THEMES) and proxy.is_exists(ROOT_ICONS):
            self.fix_theme_button.set_active(True)

        self.fix_theme_button.connect('toggled', self.on_fix_theme_btn_taggled)
        self.fix_theme_button.set_sensitive(False)
        box = ListPack(_('Miscellaneous Options'), (self.fix_theme_button,))
        self.add_start(box, False, False, 0)

        # button
        hbox = gtk.HBox(False, 0)
        self.pack_end(hbox, False ,False, 5)

        un_lock = PolkitButton()
        un_lock.connect('changed', self.on_polkit_action)
        hbox.pack_end(un_lock, False, False, 5)

    def on_fix_theme_btn_taggled(self, widget):
        if widget.get_active():
            proxy.link_file(os.path.expanduser('~/.themes'), ROOT_THEMES)
            proxy.link_file(os.path.expanduser('~/.icons'), ROOT_ICONS)
        else:
            proxy.unlink_file(ROOT_THEMES)
            proxy.unlink_file(ROOT_ICONS)
            if proxy.is_exists(ROOT_THEMES) and proxy.is_exists(ROOT_ICONS):
                widget.set_active(True)

    def on_polkit_action(self, widget, action):
        if action:
            self.fix_theme_button.set_sensitive(True)
        else:
            AuthenticateFailDialog().launch()
