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
import re
import logging

from gi.repository import GObject, Gtk, Gio, GdkPixbuf

from ubuntutweak import system
from ubuntutweak.utils import icon
from ubuntutweak.gui.containers import ListPack, GridPack, SinglePack
from ubuntutweak.gui.treeviews import get_local_path
from ubuntutweak.modules  import TweakModule
from ubuntutweak.factory import WidgetFactory
from ubuntutweak.settings.gsettings import GSetting
from ubuntutweak.settings.compizsettings import CompizPlugin, CompizSetting

log = logging.getLogger('Unity')


class Unity(TweakModule):
    __title__ = 'Unity'
    __desc__ = _('Tweak the powerful Unity desktop')
    __icon__ = 'plugin-unityshell'
    __category__ = 'desktop'
    __desktop__ = ['ubuntu', 'ubuntu-2d']

    utext_hud = 'HUD:'
    utext_overlay = _('Shortcut hits overlay:')
    utext_launcher_size = _('Launcher icon size:')
    utext_launcher_opacity = _('Launcher opacity:')
    utext_launcher_hide = _('Launcher hide mode:')
    utext_launcher_backlight = _('Launcher icon backlight:')
    utext_device = _('Launcher show devices:')
    utext_dash_size = _('Dash size:')
    utext_dash_color = _('Dash color:')
    utext_blur_type = _('Blur type:')
    utext_panel_opacity = _('Panel opacity:')
    utext_panel_toggle_max = _('Panel opacity for maximized windows:')
    utext_super_key = _('Enable the Super key')
    utext_fullscreen = _('Full screen dash')
    utext_one_launcher = _('Only one launcher when multi-monitor')

    def __init__(self):
        TweakModule.__init__(self)

        version_pattern = re.compile('\d.\d+.\d')

        if system.DESKTOP == 'ubuntu':
            grid_pack = GridPack(
                        WidgetFactory.create("Switch",
                            label=self.utext_hud,
                            key="unityshell.show_hud",
                            on='<Alt>',
                            off='Disabled',
                            backend="compiz",
                            enable_reset=True),
                        WidgetFactory.create("Switch",
                            label=self.utext_overlay,
                            key="unityshell.shortcut_overlay",
                            backend="compiz",
                            enable_reset=True),
                        Gtk.Separator(),
                        WidgetFactory.create("Scale",
                            label=self.utext_launcher_size,
                            key="unityshell.icon_size",
                            min=32,
                            max=64,
                            step=16,
                            backend="compiz",
                            enable_reset=True),
                        WidgetFactory.create("Scale",
                            label=self.utext_launcher_opacity,
                            key="unityshell.launcher_opacity",
                            min=0,
                            max=1,
                            step=0.1,
                            digits=2,
                            backend="compiz",
                            enable_reset=True),
                        WidgetFactory.create("ComboBox",
                            label=self.utext_launcher_hide,
                            key="unityshell.launcher_hide_mode",
                            texts=(_('Never'), _('Auto Hide')),
                            values=(0, 1),
                            type=int,
                            backend="compiz",
                            enable_reset=True),
                        WidgetFactory.create("ComboBox",
                            label=self.utext_launcher_backlight,
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
                        WidgetFactory.create("ComboBox",
                            label=self.utext_device,
                            key="unityshell.devices_option",
                            texts=(_('Never'),
                                   _('Only Mounted'),
                                   _('Always')),
                             values=(0, 1, 2),
                             type=int,
                             backend="compiz",
                             enable_reset=True),
                        Gtk.Separator(),
                        WidgetFactory.create("ComboBox",
                             label=self.utext_dash_size,
                             key="com.canonical.Unity.form-factor",
                             texts=(_('Automatic'), _('Desktop'), _('Netbook')),
                             values=('Automatic', 'Desktop', 'Netbook'),
                             backend="gsettings",
                             enable_reset=True),
                        WidgetFactory.create("ColorButton",
                             label=self.utext_dash_color,
                             key="unityshell.background_color",
                             backend="compiz",
                             enable_reset=True),
                        WidgetFactory.create("ComboBox",
                             label=self.utext_blur_type,
                             key="unityshell.dash_blur_experimental",
                             texts=(_('No blur'),
                                    _('Static blur'),
                                    _('Active blur')),
                             values=(0, 1, 2),
                             type=int,
                             backend="compiz",
                             enable_reset=True),
                        WidgetFactory.create("Scale",
                             label=self.utext_panel_opacity,
                             key="unityshell.panel_opacity",
                             min=0, max=1, step=0.1, digits=2,
                             backend="compiz",
                             enable_reset=True),
                        WidgetFactory.create("Switch",
                             label=self.utext_panel_toggle_max,
                             key="unityshell.panel_opacity_maximized_toggle",
                             backend="compiz",
                             reverse=True,
                             enable_reset=True),
                )

            self.add_start(grid_pack, False, False, 0)
        else:
            super_key_button, super_key_reset = WidgetFactory.create("CheckButton",
                                             label=self.utext_super_key,
                                             key="com.canonical.Unity2d.Launcher.super-key-enable",
                                             backend="gsettings",
                                             enable_reset=True)
            box = GridPack(
                        WidgetFactory.create("Switch",
                            label=self.utext_hud,
                            key="unityshell.show_hud",
                            on='<Alt>',
                            off='Disabled',
                            backend="compiz",
                            enable_reset=True),
                        WidgetFactory.create("Switch",
                                             label=self.utext_fullscreen,
                                             key="com.canonical.Unity2d.Dash.full-screen",
                                             backend="gsettings",
                                             enable_reset=True),
                        (Gtk.Label(_("Launcher")), super_key_button, super_key_reset),
                        WidgetFactory.create("CheckButton",
                                             label=self.utext_one_launcher,
                                             key="com.canonical.Unity2d.Launcher.use-strut",
                                             backend="gsettings",
                                             enable_reset=True),
                        WidgetFactory.create("ComboBox",
                                             label=self.utext_launcher_hide,
                                             key="com.canonical.Unity2d.Launcher.hide-mode",
                                             texts=(_('Never'), _('Auto Hide'),
                                                    _('Intellihide')),
                                             values=(0, 1, 2),
                                             type=int,
                                             backend="gsettings",
                                             enable_reset=True),
                )

            self.add_start(box, False, False, 0)
