import pygtk
pygtk.require("2.0")
import gtk
import os
import gconf
import gettext

from Widgets import GConfCheckButton, ItemBox

gettext.install("ubuntu-tweak", unicode = True)

lockdown_keys = \
[
	"/desktop/gnome/lockdown/disable_command_line",
	"/desktop/gnome/lockdown/disable_lock_screen",
	"/desktop/gnome/lockdown/disable_printing",
	"/desktop/gnome/lockdown/disable_print_setup",
	"/desktop/gnome/lockdown/disable_save_to_disk",
	"/desktop/gnome/lockdown/disable_user_switching",
]

lockdown_names = \
[
	_("Disable \"Run Application\" dialog (Alt+F2)"),
	_("Disable Lock Screen (Ctrl+Alt+L)"),
	_("Disable Printing"),
	_("Disable Print Setup"),
	_("Disable Save To Disk"),
	_("Disable User Switching"),
]

class LockDown(gtk.VBox):
        """Lock down some function"""

        def __init__(self):
                gtk.VBox.__init__(self)

		box = ItemBox(_("<b>System Security options</b>"), ())
		for key in lockdown_keys:
			button = GConfCheckButton(lockdown_names[lockdown_keys.index(key)], key)
			box.vbox.pack_start(button, False, False, 0)

		self.pack_start(box, False, False, 0)
