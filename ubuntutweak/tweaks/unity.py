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

from gi.repository import Gtk

from ubuntutweak import system
from ubuntutweak.utils import icon
from ubuntutweak.gui.containers import GridPack
from ubuntutweak.modules  import TweakModule
from ubuntutweak.factory import WidgetFactory
from ubuntutweak.settings.gconfsettings import GconfSetting

log = logging.getLogger('Unity')


class Unity(TweakModule):
    __title__ = 'Unity'
    __desc__ = _('Tweak the powerful Unity desktop')
    __icon__ = 'plugin-unityshell'
    __category__ = 'desktop'
    __desktop__ = ['ubuntu', 'ubuntu-2d']

    utext_hud = _('HUD:')
    utext_overlay = _('Shortcut hints overlay:')
    utext_launcher_size = _('Launcher icon size:')
    utext_launcher_opacity = _('Launcher opacity:')
    utext_web_apps_integration = _('Web Apps integration:')
    utext_launcher_hide = _('Launcher hide mode:')
    utext_launcher_backlight = _('Launcher icon backlight:')
    utext_device = _('Launcher show devices:')
    utext_show_desktop_icon = _('"Show desktop" icon:')
    utext_launcher_minimize_window = _('Launcher click to minimize app:')
    utext_disable_show_desktop_switcher = _('Disable "Show Desktop" in the switcher:')
    utext_dash_size = _('Dash size:')
    utext_blur_type = _('Blur type:')
    utext_panel_opacity = _('Panel opacity:')
    utext_panel_toggle_max = _('Panel opacity for maximized windows:')
    utext_super_key = _('Super key:')
    utext_fullscreen = _('Full screen dash:')
    utext_compositing_manager = _('Compositing manager:')
    utext_num_workspaces = _('Number of workspaces:')

    def __init__(self):
        TweakModule.__init__(self)

        version_pattern = re.compile('\d.\d+.\d')

        if system.DESKTOP == 'ubuntu':
            hide_texts = (_('Never'), _('Auto Hide'))
            hide_values = (0, 1)

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
                        WidgetFactory.create("Switch",
                            label=self.utext_web_apps_integration,
                            key="com.canonical.unity.webapps.integration-allowed",
                            backend="gsettings",
                            enable_reset=True),
                        Gtk.Separator(),
                        WidgetFactory.create("Switch",
                            label=self.utext_show_desktop_icon,
                            key="unityshell.show_desktop_icon",
                            backend="compiz",
                            enable_reset=True),
                        WidgetFactory.create("Switch",
                            label=self.utext_disable_show_desktop_switcher,
                            key="unityshell.disable_show_desktop",
                            backend="compiz",
                            enable_reset=True),
                        WidgetFactory.create("Switch",
                            label=self.utext_launcher_minimize_window,
                            key="unityshell.launcher_minimize_window",
                            backend="compiz",
                            enable_reset=True),
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
                            texts=hide_texts,
                            values=hide_values,
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
            notes_label = Gtk.Label()
            notes_label.set_property('halign', Gtk.Align.START)
            notes_label.set_markup('<span size="smaller">%s</span>' % \
                    _('Note: you may need to log out to take effect'))
            notes_label._ut_left = 1

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
                        WidgetFactory.create("Switch",
                                             label=self.utext_super_key,
                                             key="com.canonical.Unity2d.Launcher.super-key-enable",
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
                        Gtk.Separator(),
                        WidgetFactory.create("Switch",
                                             label=self.utext_compositing_manager,
                                             key="/apps/metacity/general/compositing_manager",
                                             backend="gconf",
                                             signal_dict={'notify::active': self.on_compositing_enabled},
                                             enable_reset=True),
                        notes_label,
                        WidgetFactory.create("Scale",
                                             label=self.utext_num_workspaces,
                                             key="/apps/metacity/general/num_workspaces",
                                             backend="gconf",
                                             min=1,
                                             max=36,
                                             step=1,
                                             type=int,
                                             enable_reset=True),
                )

            self.add_start(box, False, False, 0)

    def on_compositing_enabled(self, widget, prop):
         setting = GconfSetting("/apps/metacity/general/compositor_effects")
         setting.set_value(widget.get_active())
