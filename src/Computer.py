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
pygtk.require('2.0')
import gtk
import os
import gobject
import gettext

from Widgets import EntryBox, ListPack
from SystemInfo import SystemInfo

gettext.install("ubuntu-tweak", unicode = True)

class Computer(gtk.VBox):
	"""Some options about current user"""
	def __init__(self, parent = None):
		gtk.VBox.__init__(self)

		if os.uname()[4][0:3] == "ppc":
			for element in file("/proc/cpuinfo"):
				if element.split(":")[0][0:3] == "cpu":
					cpumodel = element.split(":")[1]
		else:
			for element in file("/proc/cpuinfo"):
				if element.split(":")[0] == "model name\t":
					cpumodel = element.split(":")[1]

		for element in file("/proc/meminfo"):
			if element.split(" ")[0] == "MemTotal:":
				raminfo = element.split(" ")[-2]

		box = ListPack(_("<b>System information</b>"),(
			EntryBox(_("Hostname"),		os.uname()[1]),
			EntryBox(_("Distribution"), 	SystemInfo.distro),
			EntryBox(_("Desktop Environment"), 	SystemInfo.gnome),
			EntryBox(_("Kernel"), 		os.uname()[0]+" "+os.uname()[2]),
			EntryBox(_("Platform"), 	os.uname()[-1]),
			EntryBox(_("CPU"), 		cpumodel[0:-1]),
			EntryBox(_("Memory"), 		str(int(raminfo)/1024)+" MB"),
				))
		self.pack_start(box, False, False, 0)

		box = ListPack(_("<b>User information</b>"),(
			EntryBox(_("Current User"), 	os.getenv("USER")),
			EntryBox(_("Home Directory"), 	os.getenv("HOME")),
			EntryBox(_("Shell"), 		os.getenv("SHELL")),
			EntryBox(_("Language"), 	os.getenv("LANG")),
				))
			
		self.pack_start(box, False, False, 0)

if __name__ == "__main__":
	from Utility import Test
	Test(Computer)
