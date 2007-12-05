import pygtk
pygtk.require('2.0')
import gtk
import os
import gobject
import gettext

from Widgets import GConfCheckButton, ItemBox, EntryBox

class Computer(gtk.VBox):
	"""Some options about root user"""
	def __init__(self):
		gtk.VBox.__init__(self)

		entry = EntryBox(_("Hostname"),os.uname()[1])
		entry1 = EntryBox(_("Kernel"), os.uname()[0]+" "+os.uname()[2])

		distrib = open("/etc/lsb-release")
		distriblines = distrib.readlines()
		for element in distriblines:
			if element.split("=")[0] == "DISTRIB_ID":
				distribinfo = element.split("=")[1][0:-1]
			if element.split("=")[0] == "DISTRIB_RELEASE":
				distribinfo = distribinfo + " " + element.split("=")[1][0:-1]
			if element.split("=")[0] == "DISTRIB_CODENAME":
				distribinfo = distribinfo + "(" + element.split("=")[1][0:-1] + ")"

		cpu = open("/proc/cpuinfo")
		cpuinfo = cpu.readlines()
		for element in cpuinfo:
			if element.split(":")[0] == "model name\t":
				cpumodel = element.split(":")[1]

		ram = open("/proc/meminfo")
		ramlines = ram.readlines()
		for element in ramlines:
			if element.split(" ")[0] == "MemTotal:":
				raminfo = element.split(" ")[6]

		box = ItemBox(_("<b>System information</b>"),(entry, entry1,
			EntryBox(_("Distubute"), distribinfo),
			EntryBox(_("User"), os.getenv("USER")),
			EntryBox(_("Shell"), os.getenv("SHELL")),
			EntryBox(_("Home"), os.getenv("HOME")),
			EntryBox(_("LANG"), os.getenv("LANG")),
				))
		self.pack_start(box, False, False, 0)

		box = ItemBox(_("<b>Hardware infomation</b>"),(
			EntryBox(_("CPU"), cpumodel[0:-1]),
			EntryBox(_("Memery"), raminfo+" KB"),
				))
			
		self.pack_start(box, False, False, 0)
