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

from ubuntutweak.modules  import TweakModule
from ubuntutweak.widgets import TablePack

#TODO
from ubuntutweak.common.factory import WidgetFactory

class PowerManager(TweakModule):
    __title__ = _('Advanced Powermanager Settings')
    __desc__ = _('Control your computer\'s power managerment')
    __icon__ = 'gnome-power-manager'
    __category__ = 'system'
    __desktop__ = 'gnome'

    def __init__(self):
        TweakModule.__init__(self)

        box = TablePack(_('Advanced Power Management Settings'), (
                WidgetFactory.create('GconfCheckButton',
                                      label=_('Enable "Lock screen" when "Blank Screen" activates'),
                                      key='blank_screen'),
                WidgetFactory.create('GconfCheckButton',
                                      label=_('Lock screen on hibernate'),
                                      key='/apps/gnome-power-manager/lock/hibernate'),
                WidgetFactory.create('GconfCheckButton',
                                      label=_('Lock screen on suspend'),
                                      key='/apps/gnome-power-manager/lock/suspend'),
                WidgetFactory.create('GconfScale',
                                      label=_('LCD brightness when on AC'),
                                      key='/apps/gnome-power-manager/backlight/brightness_ac',
                                      min=0, max=100, digits=0),
                WidgetFactory.create('GconfScale',
                                      label=_('LCD dimming amount when on battery'),
                                      key='/apps/gnome-power-manager/backlight/brightness_dim_battery',
                                      min=0, max=100, digits=0)
        ))
        self.add_start(box, False, False, 0)
