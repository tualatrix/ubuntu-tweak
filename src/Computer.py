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
import gtop
import time

from aptsources import distro
from Widgets import GConfCheckButton, ItemBox, EntryBox

UBUNTU = distro.get_distro()
DISTRIB = UBUNTU.codename

gettext.install("ubuntu-tweak", unicode = True)

def system_time():
	uptime = gtop.uptime().dict()['uptime']
	boot_time = gtop.uptime().dict()['boot_time']

	day = time.gmtime(int(uptime))[2] - 1
	new_uptime = str(day) + " day " + time.strftime("%H h %M m", time.gmtime(int(uptime)))
	new_boot_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(boot_time)))

	return (new_uptime, new_boot_time)

class Computer(gtk.VBox):
	"""Some options about current user"""
	def __init__(self):
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

		box = ItemBox(_("<b>System information</b>"),(
			EntryBox(_("Hostname"),		os.uname()[1]),
			EntryBox(_("Distribution"), 	UBUNTU.description),
			EntryBox(_("Kernel"), 		os.uname()[0]+" "+os.uname()[2]),
			EntryBox(_("Platform"), 	os.uname()[-1]),
			EntryBox(_("CPU"), 		cpumodel[0:-1]),
			EntryBox(_("Memory"), 		str(int(raminfo)/1024)+" MB"),
				))
		self.pack_start(box, False, False, 0)

		uptime, boot_time = system_time()
		box = ItemBox(_("<b>User information</b>"),(
			EntryBox(_("Current User"), 	os.getenv("USER")),
			EntryBox(_("Home Directory"), 	os.getenv("HOME")),
			EntryBox(_("Shell"), 		os.getenv("SHELL")),
			EntryBox(_("Language"), 	os.getenv("LANG")),
			EntryBox(_("Boot time"), 	boot_time),
			EntryBox(_("Uptime"), 		uptime),
				))
			
		self.pack_start(box, False, False, 0)

if __name__ == "__main__":
        win = gtk.Window()
        win.connect('destroy', lambda *w: gtk.main_quit())
        win.set_title("Computer")
        win.set_default_size(450, 400)
        win.set_border_width(8)

        computer = Computer()
        win.add(computer)

        win.show_all()
        gtk.main()
