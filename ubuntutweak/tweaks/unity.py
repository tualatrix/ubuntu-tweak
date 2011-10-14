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

from gi.repository import Gtk, Gio

from ubuntutweak.gui.containers import ListPack, TablePack
from ubuntutweak.modules  import TweakModule
from ubuntutweak.factory import WidgetFactory

class UnitySettings(TweakModule):
    __title__ = _('Unity Settings')
    __desc__ = _('Tweak the powerful Unity desktop')
    __icon__ = 'plugin-unityshell'
    __category__ = 'desktop'
    __desktop__ = 'ubuntu'

    def __init__(self):
        TweakModule.__init__(self)

        box = TablePack(_("Launcher"), (
                    WidgetFactory.create("Scale",
                                         label=_('Icon Size'),
                                         key="unityshell.icon_size",
                                         min=32,
                                         max=64,
                                         backend="compiz",
                                         enable_reset=True),
                    WidgetFactory.create("Scale",
                                         label=_('Launcher Opacity'),
                                         key="unityshell.launcher_opacity",
                                         min=0,
                                         max=1,
                                         digits=2,
                                         backend="compiz",
                                         enable_reset=True),
                    WidgetFactory.create("Scale",
                                         label=_('Launcher Reveal Edge Timeout'),
                                         key="unityshell.launcher_reveal_edge_timeout",
                                         min=1,
                                         max=1000,
                                         backend="compiz",
                                         enable_reset=True),
            ))

        self.add_start(box, False, False, 0)
