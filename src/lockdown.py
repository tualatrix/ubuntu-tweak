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

from common.policykit import proxy
from common.factory import WidgetFactory
from common.widgets import ListPack, TweakPage

ROOT_THEMES = '/root/.themes'
ROOT_ICONS = '/root/.icons'

class LockDown(TweakPage):
    """Lock down some function"""
    def __init__(self):
        TweakPage.__init__(self)

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

        self.pack_start(box, False, False, 0)

        button = gtk.CheckButton(_('Fix the theme appearance when grant the root privileges'))
        if proxy.is_exists(ROOT_THEMES) and proxy.is_exists(ROOT_ICONS):
            button.set_active(True)

        button.connect('toggled', self.on_fix_theme_btn_taggled)
        box = ListPack(_('Miscellaneous Options'), (button,))
        self.pack_start(box, False, False, 0)

    def on_fix_theme_btn_taggled(self, widget):
        if widget.get_active():
            proxy.link_file(os.path.expanduser('~/.themes'), ROOT_THEMES)
            proxy.link_file(os.path.expanduser('~/.icons'), ROOT_ICONS)
        else:
            proxy.unlink_file(ROOT_THEMES)
            proxy.unlink_file(ROOT_ICONS)
            if proxy.is_exists(ROOT_THEMES) and proxy.is_exists(ROOT_ICONS):
                widget.set_active(True)

if __name__ == "__main__":
    from utility import Test
    Test(LockDown)
