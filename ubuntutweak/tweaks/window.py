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

from gi.repository import GObject, Gtk

from ubuntutweak.modules  import TweakModule
from ubuntutweak.gui.containers import GridPack
from ubuntutweak.factory import WidgetFactory
from ubuntutweak.settings.gconfsettings import GconfSetting
from ubuntutweak import system


class Window(TweakModule):
    __title__ = _('Window')
    __desc__ = _('Manage Window Manager settings')
    __icon__ = 'preferences-system-windows'
    __category__ = 'desktop'

    left_default = 'close,minimize,maximize:'
    right_default = ':minimize,maximize,close'

    if system.DESKTOP == 'gnome-shell':
        config = GconfSetting(key='/desktop/gnome/shell/windows/button_layout')
    else:
        config = GconfSetting(key='/apps/metacity/general/button_layout')

    def __init__(self):
        TweakModule.__init__(self, 'window.ui')

        box = GridPack(
                    (Gtk.Label(_('Window control button position')),
                     self.place_hbox),
                    Gtk.Separator(),
                    WidgetFactory.create('ComboBox',
                        label=_('Titlebar mouse wheel action:'),
                        key='/apps/gwd/mouse_wheel_action',
                        enable_reset=True,
                        backend='gconf',
                        texts=[_('None'), _('Roll up')],
                        values=['none', 'shade']),
                    WidgetFactory.create('ComboBox',
                        label=_('Titlebar double-click action:'),
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
                        label=_('Titlebar middle-click action:'),
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
                        label=_('Titlebar right-click action:'),
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

    def on_right_radio_toggled(self, widget):
        if widget.get_active():
            self.config.set_value(self.right_default)

    def on_left_radio_toggled(self, widget):
        if widget.get_active():
            self.config.set_value(self.left_default)
