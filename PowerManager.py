#!/usr/bin/env python

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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import pygtk
pygtk.require("2.0")
import gtk
import os
import gconf
import gettext

from Widgets import GConfCheckButton, ItemBox, HScaleBox, ComboboxItem
from Computer import DISTRIB

gettext.install("ubuntu-tweak", unicode = True)

class PowerManager(gtk.VBox):
        """Advanced Powermanager Settings"""

        def __init__(self):
                gtk.VBox.__init__(self)

		if DISTRIB == "feisty":
			box = ItemBox(_("<b>Advanced Power Management Settings</b>"), (
				GConfCheckButton(_("Enable Hibernation"), "/apps/gnome-power-manager/can_hibernate"),
				GConfCheckButton(_("Enable Suspend"), "/apps/gnome-power-manager/can_suspend"),
				GConfCheckButton(_("Show CPU frequency option in \"Power Management\""), "/apps/gnome-power-manager/show_cpufreq_ui"),
				GConfCheckButton(_("Lock screen when blanked"), "/apps/gnome-power-manager/lock_on_blank_screen"),
				ComboboxItem(_("\"GNOME Panel\" Power Management icon"), [_("Never display"), _("When charging"), _("Always display")], ["never", "charge", "always"], "/apps/gnome-power-manager/display_icon_policy"),
				)) 
			
		else:
			box = ItemBox(_("<b>Advanced Power Management Settings</b>"), (
				GConfCheckButton(_("Enable Hibernation"), "/apps/gnome-power-manager/general/can_hibernate"),
				GConfCheckButton(_("Enable Suspend"), "/apps/gnome-power-manager/general/can_suspend"),
				GConfCheckButton(_("Show CPU frequency option in \"Power Management\""), "/apps/gnome-power-manager/ui/cpufreq_show"),
				GConfCheckButton(_("Disconnected NetworkManager on sleep"), "/apps/gnome-power-manager/general/network_sleep"),
				GConfCheckButton(_("Lock screen when blanked"), "/apps/gnome-power-manager/lock/blank_screen"),
				ComboboxItem(_("\"GNOME Panel\" Power Management icon"), [_("Never display"), _("When charging"), _("Always display")], ["never", "charge", "always"], "/apps/gnome-power-manager/ui/icon_policy"),
				)) 
                self.pack_start(box, False, False, 0)

		if DISTRIB == "feisty":
			box = ItemBox(_("<b>CPU Policy</b>"), (
				HScaleBox(_("The Performance value when on AC power"), 0, 100, "/apps/gnome-power-manager/cpufreq_ac_performance"),
				HScaleBox(_("The Performance value when on battery power"), 0, 100, "/apps/gnome-power-manager/cpufreq_battery_performance"),
				ComboboxItem(_("The CPU frequency policy when on AC power"), [_("On Demand"), _("Power Save"), _("Performance")], ["ondemand", "powersave", "performance"], "/apps/gnome-power-manager/cpufreq_ac_policy"),
				ComboboxItem(_("The CPU frequency policy when on battery power"), [_("On Demand"), _("Power Save"), _("Performance")], ["ondemand", "powersave", "performance"], "/apps/gnome-power-manager/cpufreq_battery_policy")
			))
		else:
			box = ItemBox(_("<b>CPU Policy</b>"), (
				HScaleBox(_("The Performance value when on AC power"), 0, 100, "/apps/gnome-power-manager/cpufreq/performance_ac"),
				HScaleBox(_("The Performance value when on battery power"), 0, 100, "/apps/gnome-power-manager/cpufreq/performance_battery"),
				ComboboxItem(_("The CPU frequency policy when on AC power"), [_("On Demand"), _("Power Save"), _("Performance")], ["ondemand", "powersave", "performance"], "/apps/gnome-power-manager/cpufreq/policy_ac"),
				ComboboxItem(_("The CPU frequency policy when on battery power"), [_("On Demand"), _("Power Save"), _("Performance")], ["ondemand", "powersave", "performance"], "/apps/gnome-power-manager/cpufreq/policy_battery")
			))
			
                self.pack_start(box, False, False, 0)
