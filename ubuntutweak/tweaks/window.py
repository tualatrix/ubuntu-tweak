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

import re

from gi.repository import GObject, Gtk

from ubuntutweak.modules  import TweakModule
from ubuntutweak.gui.containers import GridPack
from ubuntutweak.factory import WidgetFactory
from ubuntutweak.settings.gconfsettings import GconfSetting
from ubuntutweak.settings.gsettings import GSetting
from ubuntutweak import system


class Window(TweakModule):
    __title__ = _('Window')
    __desc__ = _('Manage Window Manager settings')
    __icon__ = 'preferences-system-windows'
    __category__ = 'desktop'
    __desktop__ = ['ubuntu', 'ubuntu-2d', 'gnome', 'gnome-classic', 'gnome-shell', 'gnome-fallback', 'gnome-fallback-compiz']
    __distro__ = ['precise', 'quantal', 'raring', 'saucy']

    left_default = 'close,minimize,maximize:'
    right_default = ':minimize,maximize,close'

    if system.DESKTOP in ('gnome', 'gnome-shell'):
        config = GSetting(key='org.gnome.shell.overrides.button-layout')
    else:
        if system.CODENAME == 'precise':
            config = GconfSetting(key='/apps/metacity/general/button_layout')
        else:
            config = GSetting(key='org.gnome.desktop.wm.preferences.button-layout')

    utext_window_button = _('Window control button position:')
    utext_only_close_button = _('"Close" button only')
    utext_titlebar_wheel = _('Titlebar mouse wheel action:')
    utext_titlebar_double = _('Titlebar double-click action:')
    utext_titlebar_middle = _('Titlebar middle-click action:')
    utext_titlebar_right = _('Titlebar right-click action:')

    def __init__(self):
        TweakModule.__init__(self, 'window.ui')

        close_pattern = re.compile('\w+')

        only_close_switch = Gtk.Switch()
        only_close_switch.connect('notify::active', self.on_switch_activate)
        button_value = self.config.get_value()
        if len(close_pattern.findall(button_value)) == 1 and 'close' in button_value:
            only_close_switch.set_active(True)
        only_close_label = Gtk.Label(self.utext_only_close_button)

        if system.CODENAME == 'precise' and system.DESKTOP == 'ubuntu':
            box = GridPack(
                        (Gtk.Label(self.utext_window_button),
                         self.place_hbox),
                        (only_close_label, only_close_switch),
                        Gtk.Separator(),
                        WidgetFactory.create('ComboBox',
                            label=self.utext_titlebar_wheel,
                            key='/apps/gwd/mouse_wheel_action',
                            enable_reset=True,
                            backend='gconf',
                            texts=[_('None'), _('Roll up')],
                            values=['none', 'shade']),
                        WidgetFactory.create('ComboBox',
                            label=self.utext_titlebar_double,
                            key='/apps/metacity/general/action_double_click_titlebar',
                            enable_reset=True,
                            backend='gconf',
                            texts=[_('None'), _('Maximize'), \
                                    _('Minimize'), _('Roll up'), \
                                    _('Lower'), _('Menu')],
                            values=['none', 'toggle_maximize', \
                                    'minimize', 'toggle_shade', \
                                    'lower', 'menu']),
                        WidgetFactory.create('ComboBox',
                            label=self.utext_titlebar_middle,
                            key='/apps/metacity/general/action_middle_click_titlebar',
                            enable_reset=True,
                            backend="gconf",
                            texts=[_('None'), _('Maximize'), \
                                   _('Maximize Horizontally'), \
                                   _('Maximize Vertically'), \
                                   _('Minimize'), _('Roll up'), \
                                   _('Lower'), _('Menu')],
                                   values=['none', 'toggle_maximize', \
                                           'toggle_maximize_horizontally', \
                                           'toggle_maximize_vertically', \
                                           'minimize', 'toggle_shade', \
                                           'lower', 'menu']),
                        WidgetFactory.create('ComboBox',
                            label=self.utext_titlebar_right,
                            key='/apps/metacity/general/action_right_click_titlebar',
                            enable_reset=True,
                            backend="gconf",
                            texts=[_('None'), _('Maximize'), \
                                    _('Maximize Horizontally'), \
                                    _('Maximize Vertically'), \
                                    _('Minimize'), _('Roll up'), \
                                    _('Lower'), _('Menu')],
                            values=['none', 'toggle_maximize', \
                                    'toggle_maximize_horizontally', \
                                    'toggle_maximize_vertically', \
                                    'minimize', 'toggle_shade', \
                                    'lower', 'menu']),
                    )

            self.add_start(box)
        else:
            box = GridPack(
                        (Gtk.Label(self.utext_window_button),
                         self.place_hbox),
                        (only_close_label, only_close_switch),
                        Gtk.Separator(),
                        WidgetFactory.create('ComboBox',
                            label=self.utext_titlebar_wheel,
                            key='org.compiz.gwd.mouse-wheel-action',
                            enable_reset=True,
                            backend='gsettings',
                            texts=[_('None'), _('Roll up')],
                            values=['none', 'shade']),
                        WidgetFactory.create('ComboBox',
                            label=self.utext_titlebar_double,
                            key='org.gnome.desktop.wm.preferences.action-double-click-titlebar',
                            enable_reset=True,
                            backend='gsettings',
                            texts=[_('None'), _('Maximize'), \
                                   _('Minimize'), _('Roll up'), \
                                   _('Lower'), _('Menu')],
                            values=['none', 'toggle-maximize', \
                                    'minimize', 'toggle-shade', \
                                    'lower', 'menu']),
                        WidgetFactory.create('ComboBox',
                            label=self.utext_titlebar_middle,
                            key='org.gnome.desktop.wm.preferences.action-middle-click-titlebar',
                            enable_reset=True,
                            backend="gsettings",
                            texts=[_('None'), _('Maximize'), \
                                   _('Minimize'), _('Roll up'), \
                                   _('Lower'), _('Menu')],
                            values=['none', 'toggle-maximize', \
                                    'minimize', 'toggle-shade', \
                                    'lower', 'menu']),
                        WidgetFactory.create('ComboBox',
                            label=self.utext_titlebar_right,
                            key='org.gnome.desktop.wm.preferences.action-right-click-titlebar',
                            enable_reset=True,
                            backend="gsettings",
                            texts=[_('None'), _('Maximize'), \
                                   _('Minimize'), _('Roll up'), \
                                   _('Lower'), _('Menu')],
                            values=['none', 'toggle-maximize', \
                                    'minimize', 'toggle-shade', \
                                    'lower', 'menu']),
                        )

            self.add_start(box)

    def on_switch_activate(self, widget, value):
        if widget.get_active():
            self.left_default = 'close:'
            self.right_default = ':close'
        else:
            self.left_default = 'close,minimize,maximize:'
            self.right_default = ':minimize,maximize,close'

        self.on_right_radio_toggled(self.right_radio)
        self.on_left_radio_toggled(self.left_radio)

    def on_right_radio_toggled(self, widget):
        if widget.get_active():
            self.config.set_value(self.right_default)

    def on_left_radio_toggled(self, widget):
        if widget.get_active():
            self.config.set_value(self.left_default)
