#!/usr/bin/env python
# coding: utf-8

import gtk
import gettext
from Computer import DISTRIB

gettext.install("ubuntu-tweak", unicode = True)

if __name__ == "__main__":
	if DISTRIB != "feisty" and DISTRIB != "gutsy":
		dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK)
		dialog.set_title("Error")
		dialog.set_markup(_("Sorry!\n\nUbuntu Tweak can only run on <b>Ubuntu 7.04 or 7.10.</b>\n"))
		dialog.run()
		dialog.destroy()
	else:
		from MainWindow import MainWindow
		MainWindow().main()
