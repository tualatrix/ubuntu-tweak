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

from Widgets import GConfCheckButton, ItemBox
from Computer import DISTRIB

gettext.install("ubuntu-tweak", unicode = True)

nautilus_keys = \
[
	"/apps/nautilus/preferences/show_advanced_permissions",
	"/apps/nautilus-cd-burner/burnproof",
	"/apps/nautilus-cd-burner/overburn",
	"/apps/nautilus/preferences",
	"/apps/nautilus-cd-burner",
]

nautilus_names = \
[
	_("Show advanced Permissions on File and Folder Property pages"),
	_("Enable BurnProof technology"),
	_("Enable OverBurn"),
]

class Nautilus(gtk.VBox):
        """Nautilus Settings"""

        def __init__(self):
                gtk.VBox.__init__(self)

                button = GConfCheckButton(nautilus_names[0], nautilus_keys[0])

                box = ItemBox(_("<b>Settings for Nautilus behavior</b>"), (button, )) 
                self.pack_start(box, False, False, 0)

		if DISTRIB != "feisty":
			hbox = gtk.HBox(False, 5)
			label = gtk.Label(_("Default Thumbnail Icon Size"))
			hbox.pack_start(label, False, False, 0)

			client = gconf.client_get_default()
			spinbutton = gtk.SpinButton(gtk.Adjustment(client.get_int("/apps/nautilus/icon_view/thumbnail_size"), 16, 512, 16, 16, 16))
			spinbutton.connect("value-changed", self.spinbutton_value_changed_cb)
			hbox.pack_end(spinbutton, False, False, 0)
			box.vbox.pack_start(hbox, False, False, 0)

                button1 = GConfCheckButton(nautilus_names[1], nautilus_keys[1])
                button2 = GConfCheckButton(nautilus_names[2], nautilus_keys[2])
                box = ItemBox(_("<b>CD Burner</b>"), (button1, button2)) 
                self.pack_start(box, False, False, 0)

	def spinbutton_value_changed_cb(self, widget, data = None):
		widget.set_increments(widget.get_value(), widget.get_value())
		client = gconf.client_get_default()
		client.set_int("/apps/nautilus/icon_view/thumbnail_size", int(widget.get_value()))
