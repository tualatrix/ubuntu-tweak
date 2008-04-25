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
from Factory import Factory
from Widgets import ListPack

gettext.install(App, unicode = True)

class LockDown(gtk.VBox):
        """Lock down some function"""
        def __init__(self, parent = None):
                gtk.VBox.__init__(self)

		box = ListPack(_("<b>System Security options</b>"), (
			Factory.create("gconfcheckbutton", _("Disable \"Run Application\" dialog (Alt+F2)"), "disable_command_line"),
			Factory.create("gconfcheckbutton", _("Disable Lock Screen"), "disable_lock_screen"),
			Factory.create("gconfcheckbutton", _("Disable Printing"), "disable_printing"),
			Factory.create("gconfcheckbutton", _("Disable Print Setup"), "disable_print_setup"),
			Factory.create("gconfcheckbutton", _("Disable Save To Disk"), "disable_save_to_disk"),
			Factory.create("gconfcheckbutton", _("Disable User Switching"), "disable_user_switching"),
			Factory.create("gconfcheckbutton", _("Disable User Switchingg"), "disable_user_switchingg"),
			))

		self.pack_start(box, False, False, 0)

if __name__ == "__main__":
	from Utility import Test
        Test(LockDown)
