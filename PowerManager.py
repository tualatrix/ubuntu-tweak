import pygtk
pygtk.require("2.0")
import gtk
import os
import gconf
import gettext

from Widgets import GConfCheckButton, ItemBox, HScaleBox, ComboboxItem

gettext.install("ubuntu-tweak", unicode = True)

class PowerManager(gtk.VBox):
        """Advanced Powermanager Settings"""

        def __init__(self):
                gtk.VBox.__init__(self)

                box = ItemBox(_("<b>Advanced Power Management Settings</b>"), (
			GConfCheckButton(_("Enable Hibernation"), "/apps/gnome-power-manager/general/can_hibernate"),
			GConfCheckButton(_("Enable Suspend"), "/apps/gnome-power-manager/general/can_suspend"),
			GConfCheckButton(_("Show CPU frequency option in \"Power Management\""), "/apps/gnome-power-manager/ui/cpufreq_show"),
			GConfCheckButton(_("Disconnected NetworkManager on sleep"), "/apps/gnome-power-manager/general/network_sleep"),
			GConfCheckButton(_("Lock screen when blanked"), "/apps/gnome-power-manager/lock/blank_screen"),
			ComboboxItem(_("\"GNOME Panel\" Power Management icon"), [_("Never display"), _("When charging"), _("Always display")], ["never", "charge", "always"], "/apps/gnome-power-manager/ui/icon_policy"),
			)) 
                self.pack_start(box, False, False, 0)

		box = ItemBox(_("<b>CPU Policy</b>"), (
			HScaleBox("performance_ac", 0, 100, "/apps/gnome-power-manager/cpufreq/performance_ac"),
			HScaleBox("performance_battery", 0, 100, "/apps/gnome-power-manager/cpufreq/performance_battery"),
			ComboboxItem(_("When using AC power, CPU frequency policy"), [_("On Demand"), _("Power Save"), _("Performance")], ["ondemand", "powersave", "performance"], "/apps/gnome-power-manager/cpufreq/policy_ac"),
			ComboboxItem(_("When using Battery power, CPU frequency policy"), [_("On Demand"), _("Power Save"), _("Performance")], ["ondemand", "powersave", "performance"], "/apps/gnome-power-manager/cpufreq/policy_battery")
		))
			
                self.pack_start(box, False, False, 0)
