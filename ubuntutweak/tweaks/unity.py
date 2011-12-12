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
from ubuntutweak import system

class UnitySettings(TweakModule):
    __title__ = _('Unity Settings')
    __desc__ = _('Tweak the powerful Unity desktop')
    __icon__ = 'plugin-unityshell'
    __category__ = 'desktop'
    __desktop__ = ['ubuntu', 'ubuntu-2d']

    def __init__(self):
        TweakModule.__init__(self)

        if system.DESKTOP == 'ubuntu':
            box = TablePack(_("Launcher"), (
                        WidgetFactory.create("Scale",
                                             label=_('Icon size'),
                                             key="unityshell.icon_size",
                                             min=32,
                                             max=64,
                                             backend="compiz",
                                             enable_reset=True),
                        WidgetFactory.create("Scale",
                                             label=_('Launcher opacity'),
                                             key="unityshell.launcher_opacity",
                                             min=0,
                                             max=1,
                                             digits=2,
                                             backend="compiz",
                                             enable_reset=True),
                        WidgetFactory.create("Scale",
                                             label=_('Launcher reveal edge timeout'),
                                             key="unityshell.launcher_reveal_edge_timeout",
                                             min=1,
                                             max=1000,
                                             backend="compiz",
                                             enable_reset=True),
                        WidgetFactory.create("ComboBox",
                                             label=_('Launcher hide mode'),
                                             key="unityshell.launcher_hide_mode",
                                             texts=(_('Never'), _('Auto Hide'),
                                                    _('Dodge Window'), _('Dodge Active Window')),
                                             values=(0, 1, 2, 3),
                                             type=int,
                                             backend="compiz",
                                             enable_reset=True),
                        WidgetFactory.create("ComboBox",
                                             label=_('Icon backlight'),
                                             key="unityshell.backlight_mode",
                                             texts=(_('Backlight Always On'),
                                                    _('Backlight Toggles'),
                                                    _('Backlight Always Off'),
                                                    _('Edge Illumination Toggles'),
                                                    _('Backlight and Edge Illumination Toggles')),
                                             values=(0, 1, 2, 3, 4),
                                             type=int,
                                             backend="compiz",
                                             enable_reset=True),
                ))
            self.add_start(box, False, False, 0)

            box = TablePack(_("Dash and Panel"), (
                        WidgetFactory.create("ComboBox",
                                             label=_('Dash size'),
                                             key="com.canonical.Unity.form-factor",
                                             texts=(_('Automatic'),
                                                    _('Desktop'),
                                                    _('Netbook')),
                                             values=('Automatic',
                                                     'Desktop',
                                                     'Netbook'),
                                             backend="gsettings",
                                             enable_reset=True),
                        WidgetFactory.create("ComboBox",
                                             label=_('Blur'),
                                             key="unityshell.dash_blur_experimental",
                                             texts=(_('No blur'),
                                                    _('Static blur'),
                                                    _('Active blur')),
                                             values=(0, 1, 2),
                                             type=int,
                                             backend="compiz",
                                             enable_reset=True),
                        WidgetFactory.create("Scale",
                                             label=_('Panel opacity'),
                                             key="unityshell.panel_opacity",
                                             min=0,
                                             max=1,
                                             digits=2,
                                             backend="compiz",
                                             enable_reset=True),
                ))

            self.add_start(box, False, False, 0)
        else:
            box = ListPack(_('Compositing Manager'), (
                                    WidgetFactory.create('CheckButton',
                                                         label=_("Enable Metacity's compositing feature"),
                                                         enable_reset=True,
                                                         backend='gconf',
                                                         key='/apps/metacity/general/compositing_manager'),
                            ))
            self.add_start(box, False, False, 0)

            box = TablePack(_("Launcher"), (
                        WidgetFactory.create("CheckButton",
                                             label=_('Enable the Super key'),
                                             key="com.canonical.Unity2d.Launcher.super-key-enable",
                                             backend="gsettings",
                                             enable_reset=True),
                        WidgetFactory.create("CheckButton",
                                             label=_('Reserve launcher area'),
                                             key="com.canonical.Unity2d.Launcher.use-strut",
                                             backend="gsettings",
                                             enable_reset=True),
                        WidgetFactory.create("ComboBox",
                                             label=_('Launcher hide mode'),
                                             key="com.canonical.Unity2d.Launcher.hide-mode",
                                             texts=(_('Never'), _('Auto Hide'),
                                                    _('Intellihide')),
                                             values=(0, 1, 2),
                                             type=int,
                                             backend="gsettings",
                                             enable_reset=True),
                ))

            self.add_start(box, False, False, 0)
