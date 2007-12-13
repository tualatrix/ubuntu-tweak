#!/usr/bin/env python
# coding: utf-8

import gtk
import gettext
import os

from Computer import DISTRIB

gettext.install("ubuntu-tweak", unicode = True)

def show_error(message, title = _("Error"), parent = None):
	dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK)
	dialog.set_title(title)
	dialog.set_markup(message)
	dialog.run()
	dialog.destroy()

if __name__ == "__main__":
	if DISTRIB != "feisty" and DISTRIB != "gutsy":
		show_error(_("Sorry!\n\nUbuntu Tweak can only run on <b>Ubuntu 7.04 or 7.10.</b>\n"))
	else:
		#determine whether the gnome is the default desktop
		if os.getenv("GNOME_DESKTOP_SESSION_ID"):
			from MainWindow import MainWindow
			MainWindow().main()
		else:
			show_error(_("Sorry!\n\nUbuntu Tweak can only run in <b>GNOME Desktop.</b>\n"))
