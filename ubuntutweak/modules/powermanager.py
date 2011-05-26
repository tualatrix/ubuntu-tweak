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

from gi.repository import GConf

from ubuntutweak.modules  import TweakModule
from ubuntutweak.gui.containers import TablePack
from ubuntutweak.factory import WidgetFactory


class PowerManager(TweakModule):
    __title__ = _('Power Manager Settings')
    __desc__ = _('Control your computer\'s power management')
    __icon__ = 'gnome-power-manager'
    __category__ = 'system'

    def __init__(self):
        TweakModule.__init__(self)

        hibernate_box = WidgetFactory.create('CheckButton',
                                      label=_('Lock screen on hibernate'),
                                      enable_reset=True,
                                      backend=GConf,
                                      key='/apps/gnome-power-manager/lock/hibernate')
        suspend_box = WidgetFactory.create('CheckButton',
                                      label=_('Lock screen on suspend'),
                                      enable_reset=True,
                                      backend=GConf,
                                      key='/apps/gnome-power-manager/lock/suspend')
        screensaver_box = WidgetFactory.create('CheckButton',
                                      label=_('Use Screensaver lock settings'),
                                      enable_reset=True,
                                      backend=GConf,
                                      key='/apps/gnome-power-manager/lock/use_screensaver_settings')
        hibernate_button = hibernate_box.get_data('widget')
        suspend_button = suspend_box.get_data('widget')
        screensaver_button = screensaver_box.get_data('widget')
        screensaver_button.connect('toggled', self.on_screensaver_button_toggled,
                                   (hibernate_button, suspend_button))
        self.on_screensaver_button_toggled(screensaver_button, (hibernate_button, suspend_button))

        box = TablePack(_('Advanced Power Management Settings'), (
                WidgetFactory.create('CheckButton',
                                      label=_('Enable "Lock screen" when "Blank Screen" activates'),
                                      enable_reset=True,
                                      backend=GConf,
                                      key='/apps/gnome-power-manager/lock/blank_screen'),
                screensaver_box, hibernate_box, suspend_box
        ))
        self.add_start(box, False, False, 0)

    def on_screensaver_button_toggled(self, widget, buttons):
        if widget.get_active():
            [button.set_sensitive(False) for button in buttons]
        else:
            [button.set_sensitive(True) for button in buttons]
