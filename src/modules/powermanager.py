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

import pygtk
pygtk.require("2.0")
import gtk
import os
import gconf
import gettext

from tweak import TweakModule
from common.systeminfo import module_check
from common.factory import WidgetFactory
from common.widgets import HScaleBox, TablePack

class PowerManager(TweakModule):
    __title__ = _('Advanced Powermanager Settings')
    __desc__ = _('Control your computer\'s power managerment')
    __icon__ = 'gnome-power-manager'
    __category__ = 'system'

    def __init__(self):
        TweakModule.__init__(self)

        box = TablePack(_("Advanced Power Management Settings"), [
                [WidgetFactory.create("GconfCheckButton", 
                                      label = _('Enable "Hibernation"'), 
                                      key = "can_hibernate")],
                [WidgetFactory.create("GconfCheckButton", 
                                      label = _('Enable "Suspend"'), 
                                      key = "can_suspend")],
                [WidgetFactory.create("GconfCheckButton", 
                                      label = _('Show "CPU frequency control option" in Power Management Preferences'), 
                                      key = "cpufreq_show")],
                [WidgetFactory.create("GconfCheckButton", 
                                      label = _("Disable Network Manager when asleep"), 
                                      key = "network_sleep")],
                [WidgetFactory.create("GconfCheckButton", 
                                      label = _('Enable "Lock screen" when "Blank Screen" activates'), 
                                      key = "blank_screen")],
                [gtk.Label(_('Display "Power Manager" panel item')), 
                    WidgetFactory.create("GconfComboBox", 
                                         key = "icon_policy", 
                                         texts = [_("Never display"), _("When charging"), _("Always display")], 
                                         values = ["never", "charge", "always"])],
        ]) 
        self.add_start(box, False, False, 0)

        if module_check.get_gnome_version() < 24:
            cpu_policy_text = [_("Normal"), _("On Demand"), _("Power Save"), _("Performance")]
            cpu_policy_value = ["nothing", "ondemand", "powersave", "performance"]
            box = TablePack(_("CPU Policy"), [
                    [gtk.Label(_("The Performance value when on AC power")), 
                        WidgetFactory.create("GconfScale", 
                                             key = "performance_ac", 
                                             min = 0, 
                                             max = 100, 
                                             digits = 0)],
                    [gtk.Label(_("The Performance value when on battery power")), 
                        WidgetFactory.create("GconfScale", 
                                             key = "performance_battery", 
                                             min = 0, 
                                             max = 100, 
                                             digits = 0)],
                    [gtk.Label(_("The CPU frequency policy when on AC power")), 
                        WidgetFactory.create("GconfComboBox", 
                                             key = "policy_ac", 
                                             texts = cpu_policy_text, 
                                             values = cpu_policy_value)],
                    [gtk.Label(_("The CPU frequency policy when on battery power")), 
                        WidgetFactory.create("GconfComboBox", 
                                             key = "policy_battery", 
                                             texts = cpu_policy_text, 
                                             values = cpu_policy_value)],
            ])
                
            self.add_start(box, False, False, 0)
