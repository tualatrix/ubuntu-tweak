import pygtk
pygtk.require("2.0")
import gtk
import os
import gconf
import gettext

from gconfcheckbutton import GConfCheckButton
from itembox import ItemBox

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

class PowermanagerPage(gtk.VBox):
        """Advanced Powermanager Settings"""

        __key_powermanager_dir = "/apps/nautilus/preferences"
	__key_powermanager_ui_dir = "/apps/gnome-power-manager/ui"

	def __value_changed_cb(self, widget, data = None):
		client = gconf.client_get_default()
		text = widget.get_active_text()
		client.set_string(data, widget.values[widget.texts.index(text)]) 

	def __combobox_item(self, label, texts, values, key):
		hbox = gtk.HBox(False, 10)
		hbox.pack_start(gtk.Label(label), False, False, 0)	

		combobox = gtk.combo_box_new_text()
		combobox.texts = texts
		combobox.values = values
		combobox.connect("changed", self.__value_changed_cb, key)
		hbox.pack_end(combobox, False, False, 0)

		for element in texts:
			combobox.append_text(element)

		client = gconf.client_get_default()
		combobox.set_active(values.index(client.get_string(key)))

		return hbox 

        def __init__(self):
                gtk.VBox.__init__(self)

                button1 = GConfCheckButton(powermanager_names[0], powermanager_keys[0], self.__key_powermanager_dir)
                button2 = GConfCheckButton(powermanager_names[1], powermanager_keys[1], self.__key_powermanager_dir)
                button3 = GConfCheckButton(powermanager_names[2], powermanager_keys[2], self.__key_powermanager_ui_dir)

		comboboxitem1 = self.__combobox_item(_("\"GNOME Panel\" Power Management icon"), [_("Never display"), _("When charging"), _("Always display")], ["never", "charge", "always"], powermanager_keys[5])
		comboboxitem2 = self.__combobox_item(_("When using AC power, CPU frequency policy"), [_("On Demand"), _("Power Save"), _("Performance")], ["ondemand", "powersave", "performance"], powermanager_keys[3])
		comboboxitem3 = self.__combobox_item(_("When using Battery power, CPU frequency policy"), [_("On Demand"), _("Power Save"), _("Performance")], ["ondemand", "powersave", "performance"], powermanager_keys[4])
		
                box = ItemBox(_("<b>Advanced Power Management Settings</b>"), (button1, button2, button3, comboboxitem1, comboboxitem2, comboboxitem3)) 

                self.pack_start(box, False, False, 0)
