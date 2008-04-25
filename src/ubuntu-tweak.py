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
# along with Ubuntu Tweak; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

import gtk
import gettext
import os

from Constants import *
from SystemInfo import GnomeVersion

gettext.install(App, unicode = True)

def show_error(message, title = _("Error"), parent = None):
	dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK)
	dialog.set_title(title)
	dialog.set_markup(message)
	dialog.run()
	dialog.destroy()

if __name__ == "__main__":
	if GnomeVersion.minor < 18:
		show_error(_("Sorry!\n\nUbuntu Tweak can only run under <b>GNOME 2.18 or above.</b>\n"))
	else:
		#determine whether the gnome is the default desktop
		if os.getenv("GNOME_DESKTOP_SESSION_ID"):
			from MainWindow import MainWindow
			MainWindow().main()
		else:
			show_error(_("Sorry!\n\nUbuntu Tweak can only run in <b>GNOME Desktop.</b>\n"))
