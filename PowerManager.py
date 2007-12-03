import pygtk
pygtk.require("2.0")
import gtk
import os
import gconf
import gettext

from Widgets import GConfCheckButton, ItemBox

gettext.install("ubuntu-tweak", unicode = True)

powermanager_keys = \
[
	"/apps/gnome-power-manager/general/can_hibernate",
	"/apps/gnome-power-manager/general/can_suspend",
	"/apps/gnome-power-manager/ui/cpufreq_show",
	"/apps/gnome-power-manager/cpufreq/policy_ac",
	"/apps/gnome-power-manager/cpufreq/policy_battery",
	"/apps/gnome-power-manager/ui/icon_policy"
]

powermanager_names = \
[
	_("Enable Hibernation"),
	_("Enable Suspend"),
	_("Show CPU frequency option in \"Power Management\""),
	_("\"GNOME Panel\" Power Management icon"),
	_("When using AC power, CPU frequency policy"),
	_("When using Battery power, CPU frequency policy")
]

class PowerManager(gtk.VBox):
        """Advanced Powermanager Settings"""

	def value_changed_cb(self, widget, data = None):
		client = gconf.client_get_default()
		text = widget.get_active_text()
		client.set_string(data, widget.values[widget.texts.index(text)]) 

	def combobox_item(self, label, texts, values, key):
		hbox = gtk.HBox(False, 10)
		hbox.pack_start(gtk.Label(label), False, False, 0)	

		combobox = gtk.combo_box_new_text()
		combobox.texts = texts
		combobox.values = values
		combobox.connect("changed", self.value_changed_cb, key)
		hbox.pack_end(combobox, False, False, 0)

		for element in texts:
			combobox.append_text(element)

		client = gconf.client_get_default()
		combobox.set_active(values.index(client.get_string(key)))

		return hbox 

	def hscale_item(self, label, key):
		hbox = gtk.HBox(False, 10)
		hbox.pack_start(gtk.Label(label), False, False, 0)
		
		hscale = gtk.HScale()
		hscale.set_size_request(150, -1)
		hscale.set_range(25, 100)
		hscale.set_digits(0)
		hscale.set_value_pos(gtk.POS_RIGHT)
		hbox.pack_end(hscale, False, False, 0)
		hscale.connect("value-changed", self.hscale_value_changed_cb, key)

		client = gconf.client_get_default()
		hscale.set_value(client.get_int(key))
		return hbox

	def hscale_value_changed_cb(self, widget, data = None):
		client = gconf.client_get_default()
		client.set_int(data, int(widget.get_value()))

        def __init__(self):
                gtk.VBox.__init__(self)

                button1 = GConfCheckButton(powermanager_names[0], powermanager_keys[0])
                button2 = GConfCheckButton(powermanager_names[1], powermanager_keys[1])
                button3 = GConfCheckButton(powermanager_names[2], powermanager_keys[2])
		button4 = GConfCheckButton(_("Disconnected NetworkManager on sleep"), "/apps/gnome-power-manager/general/network_sleep")
		button5 = GConfCheckButton(_("Lock screen when blanked"), "/apps/gnome-power-manager/lock/blank_screen")

		comboboxitem1 = self.combobox_item(_("\"GNOME Panel\" Power Management icon"), [_("Never display"), _("When charging"), _("Always display")], ["never", "charge", "always"], powermanager_keys[5])
		comboboxitem2 = self.combobox_item(_("When using AC power, CPU frequency policy"), [_("On Demand"), _("Power Save"), _("Performance")], ["ondemand", "powersave", "performance"], powermanager_keys[3])
		comboboxitem3 = self.combobox_item(_("When using Battery power, CPU frequency policy"), [_("On Demand"), _("Power Save"), _("Performance")], ["ondemand", "powersave", "performance"], powermanager_keys[4])
		
		hscaleitem1 = self.hscale_item("performance_ac", "/apps/gnome-power-manager/cpufreq/performance_ac")
		hscaleitem2 = self.hscale_item("performance_battery", "/apps/gnome-power-manager/cpufreq/performance_battery")
                box = ItemBox(_("<b>Advanced Power Management Settings</b>"), (button1, button2, button3, button4, button5, comboboxitem1)) 
                self.pack_start(box, False, False, 0)

		box = ItemBox(_("<b>CPU Policy</b>"), (comboboxitem2, comboboxitem3, hscaleitem1, hscaleitem2))
                self.pack_start(box, False, False, 0)
