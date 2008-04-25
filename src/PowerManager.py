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

from Constants import *
from Widgets import HScaleBox
from Widgets import TablePack
from Factory import Factory

gettext.install(App, unicode = True)

class PowerManager(gtk.VBox):
        """Advanced Powermanager Settings"""

        def __init__(self, parent = None):
                gtk.VBox.__init__(self)

		box = TablePack(_("<b>Advanced Power Management Settings</b>"), [
			[Factory.create("gconfcheckbutton", _("Enable Hibernation"), "can_hibernate", _("If you disable this option, hibernation option will disappear in the exit dialog"))],
			[Factory.create("gconfcheckbutton", _("Enable Suspend"), "can_suspend", _("If you disable this option, suspend option will disappear in the exit dialog"))],
			[Factory.create("gconfcheckbutton", _("Show CPU frequency control option"), "cpufreq_show", _("If you enable this option, the Power Management will display the CPU frequency option"))],
			[Factory.create("gconfcheckbutton", _("Disconnected NetworkManager on sleep"), "network_sleep", _("Whether NetworkManager should disconnect before suspending or hibernating and connect on resume."))],
			[Factory.create("gconfcheckbutton", _("Lock screen when blanked"), "blank_screen")],
			[gtk.Label(_("\"GNOME Panel\" Power Management icon")), Factory.create("gconfcombobox", "icon_policy", [_("Never display"), _("When charging"), _("Always display")], ["never", "charge", "always"])],
				]) 
                self.pack_start(box, False, False, 0)

		box = TablePack(_("<b>CPU Policy</b>"), [
			[gtk.Label(_("The Performance value when on AC power")), Factory.create("gconfscale", 0, 100, "performance_ac", 0)],
			[gtk.Label(_("The Performance value when on battery power")), Factory.create("gconfscale", 0, 100, "performance_battery", 0)],
			[gtk.Label(_("The CPU frequency policy when on AC power")), Factory.create("gconfcombobox", "policy_ac", [_("On Demand"), _("Power Save"), _("Performance")], ["ondemand", "powersave", "performance"])],
			[gtk.Label(_("The CPU frequency policy when on battery power")), Factory.create("gconfcombobox", "policy_battery", [_("On Demand"), _("Power Save"), _("Performance")], ["ondemand", "powersave", "performance"])],
		])
			
                self.pack_start(box, False, False, 0)

if __name__ == "__main__":
	from Utility import Test
	Test(PowerManager)
