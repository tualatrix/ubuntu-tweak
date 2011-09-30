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

from gi.repository import Gtk, GConf

from ubuntutweak.gui.containers import ListPack
from ubuntutweak.modules  import TweakModule
from ubuntutweak.factory import WidgetFactory

class LockDown(TweakModule):
    __title__ = _('Security Related')
    __desc__ = _('Tweak some security settings')
    __icon__ = ['gtk-dialog-authentication', 'stock_keyring']
    __category__ = 'system'
    __distro__ = 'natty'

    """Lock down some function"""
    def __init__(self):
        TweakModule.__init__(self)

        box = ListPack(_("System Security options"), (
                    WidgetFactory.create("CheckButton",
                                         label=_('Disable "Lock Screen"'),
                                         key="/desktop/gnome/lockdown/disable_lock_screen",
                                         backend=GConf,
                                         enable_reset=True),
                    WidgetFactory.create("CheckButton",
                                         label=_("Disable printing"),
                                         key="/desktop/gnome/lockdown/disable_printing",
                                         backend=GConf,
                                         enable_reset=True),
                    WidgetFactory.create("CheckButton",
                                         label=_("Disable printer settings"),
                                         key="/desktop/gnome/lockdown/disable_print_setup",
                                         backend=GConf,
                                         enable_reset=True),
                    WidgetFactory.create("CheckButton",
                                         label=_("Disable save to disk"),
                                         key="/desktop/gnome/lockdown/disable_save_to_disk",
                                         backend=GConf,
                                         enable_reset=True),
                    WidgetFactory.create("CheckButton",
                                         label=_('Disable "Fast User Switching"'),
                                         key="/desktop/gnome/lockdown/disable_user_switching",
                                         backend=GConf,
                                         enable_reset=True),
            ), padding=2)

        self.add_start(box, False, False, 0)
