#!/usr/bin/env python
# coding: utf-8

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import gettext

from sessionpage import SessionPage
from iconpage import IconPage
from compizpage import CompizPage
from gnomepage import GnomePage
from nautiluspage import NautilusPage

gettext.install("ubuntu-tweak", unicode = True)

VERSION = "0.3.0"

(
        NUM_COLUMN,
        ICON_COLUMN,
        NAME_COLUMN,
        TOTAL_COLUMN
) = range(4)

(
        WELCOME_PAGE,
	STARTUP_PAGE,
		SESSION_PAGE,
	DESKTOP_PAGE,
		ICON_PAGE,
		COMPIZ_PAGE,
		GNOME_PAGE,
		NAUTILUS_PAGE,
	SYSTEM_PAGE,
		POWER_PAGE,
	SECURITY_PAGE,
		SECU_OPTIONS_PAGE,
	APPLICATION_PAGE,
		FCITX_PAGE,
	TOTAL_PAGE
) = range(15)

icons = \
[
	"/usr/share/ubuntu-tweak/pixmaps/welcome.png",
	"/usr/share/ubuntu-tweak/pixmaps/startup.png",
	"/usr/share/ubuntu-tweak/pixmaps/session-properties.png",
	"/usr/share/ubuntu-tweak/pixmaps/desktop.png",
	"/usr/share/ubuntu-tweak/pixmaps/icon.png",
	"/usr/share/ubuntu-tweak/pixmaps/compiz-fusion.png",
	"/usr/share/ubuntu-tweak/pixmaps/gnome.png",
	"/usr/share/ubuntu-tweak/pixmaps/nautilus.png",
	"/usr/share/ubuntu-tweak/pixmaps/system.png",
	"/usr/share/ubuntu-tweak/pixmaps/power-manager.png",
	"/usr/share/ubuntu-tweak/pixmaps/security.png",
	"/usr/share/ubuntu-tweak/pixmaps/security-options.png",
	"/usr/share/ubuntu-tweak/pixmaps/applications.png",
	"/usr/share/ubuntu-tweak/pixmaps/security-options.png",
]

startup = \
[
	[SESSION_PAGE, icons[SESSION_PAGE], _("Session Control")]
]

desktop = \
[
	[ICON_PAGE, icons[ICON_PAGE], _("Desktop Icon")],
	[COMPIZ_PAGE, icons[COMPIZ_PAGE], _("Compiz Fusion")],
	[GNOME_PAGE, icons[GNOME_PAGE], _("GNOME")],
	[NAUTILUS_PAGE, icons[NAUTILUS_PAGE], _("Nautilus")]
]

system = \
[
	[POWER_PAGE, icons[POWER_PAGE], _("Power Manager")]
]

security = \
[
	[SECU_OPTIONS_PAGE, icons[SECU_OPTIONS_PAGE], _("Security Options")]
]

application = \
[
	[FCITX_PAGE, icons[FCITX_PAGE], _("Fcitx")]
]

itemlist = \
[
	[WELCOME_PAGE, icons[WELCOME_PAGE], _("Welcome"), None],
	[STARTUP_PAGE, icons[SESSION_PAGE], _("Startup"), startup],
	[DESKTOP_PAGE, icons[DESKTOP_PAGE], _("Desktop"), desktop],
	[SYSTEM_PAGE, icons[SYSTEM_PAGE], _("System"), system],
	[SECURITY_PAGE, icons[SECURITY_PAGE], _("Security"), security],
	[APPLICATION_PAGE, icons[APPLICATION_PAGE], _("Application"), application]
]

class UbuntuTweak(gtk.Window):
	"""the main class of Ubuntu Tweak"""

	def __create_model(self):
		model = gtk.TreeStore(
				gobject.TYPE_INT,
				gtk.gdk.Pixbuf,
				gobject.TYPE_STRING)

		for item in itemlist:
			icon = gtk.gdk.pixbuf_new_from_file(item[ICON_COLUMN])
			iter = model.append(None)
			model.set(iter,
				NUM_COLUMN, item[NUM_COLUMN],
				ICON_COLUMN, icon,
				NAME_COLUMN, item[NAME_COLUMN]
			)
			if item[-1]:
				for child_item in item[-1]:
					icon = gtk.gdk.pixbuf_new_from_file(child_item[ICON_COLUMN])
					child_iter = model.append(iter)
					model.set(child_iter,
						NUM_COLUMN, child_item[NUM_COLUMN],
						ICON_COLUMN, icon,
						NAME_COLUMN, child_item[NAME_COLUMN]
					)

		return model

	def selection_cb(self, widget, data=None):
		if not widget.get_selected():
			return
		iter = widget.get_selected()[1]
		path = data.get_path(iter)
		self.treeview.expand_row(path, True)

	def __add_columns(self, treeview):
		model = treeview.get_model()
		selection = treeview.get_selection()
		selection.connect("changed", self.selection_cb, model)

		renderer = gtk.CellRendererText()

		column = gtk.TreeViewColumn("Num",renderer,text = NUM_COLUMN)
		column.set_fixed_width(50)
		treeview.append_column(column)

		column = gtk.TreeViewColumn("Title")
		column.set_fixed_width(100)

		renderer = gtk.CellRendererPixbuf()
		column.pack_start(renderer, True)
		column.set_attributes(renderer, pixbuf = ICON_COLUMN)

		renderer = gtk.CellRendererText()
		column.pack_start(renderer, True)
		column.set_attributes(renderer, text = NAME_COLUMN)

		treeview.append_column(column)

	def __create_notebook(self):
		notebook = gtk.Notebook()
		notebook.set_scrollable(True)

		vbox = gtk.VBox(False, 0)

		label = gtk.Label()
		label.set_markup(_("<span size=\"xx-large\">Welcome to <b>Ubuntu Tweak!</b></span>\n\n\nThis is a tool for Ubuntu which makes it easy to change hidden \nsystem and desktop settings.\n\nUbuntu Tweak is currently only for the GNOME Desktop Environment.\n\nAlthough this application is only in early stages, I'll keep developing it.\n\nIf you have any suggestions, Please E-mail me. \n\nThank You!"))
		vbox.pack_start(label, False, False, 0)

		page_label = gtk.Label(_("Welcome"));
		notebook.append_page(vbox, page_label)

		page_label = gtk.Label(_("Session Control"));
		notebook.append_page(SessionPage(), page_label)

		page_label = gtk.Label(_("Desktop Icon"));
		notebook.append_page(IconPage(), page_label)

		page_label = gtk.Label(_("Virsual Efforts"));
		notebook.append_page(CompizPage(), page_label)

		page_label = gtk.Label(_("GNOME Settings"));
		notebook.append_page(GnomePage(), page_label)

		page_label = gtk.Label(_("Nautilus Settings"));
		notebook.append_page(NautilusPage(), page_label)

		return notebook
	
	def show_about(self, data = None):
		about = gtk.AboutDialog()
		about.set_name("Ubuntu Tweak")
		about.set_version(VERSION)
		about.set_website("http://ubuntu-tweak.com")
		about.set_logo(self.get_icon())
		about.set_comments(_("Ubuntu Tweak is a tool for Ubuntu that makes it easy to configure your system and desktop settings."))
		about.set_authors(["TualatriX <tualatrix@gmail.com>"])
		about.set_copyright("Copyright © 2007 TualatriX")
		about.set_license('GNU General Public License')
		about.set_translator_credits("Super Jamie <jamie@superjamie.net>\nThree-leg-cat <threelegcat@gmail.com>\nWilliams <ff9will@gmail.com>")
		about.set_artists(["Medical-Wei <a790407@hotmail.com>", "m.Sharp <mac.sharp@gmail.com>", "taiwan ock ting <a2d8a4v@gmail.com>"])
		about.run()
		about.destroy()

	def __init__(self):
		#create the main window
		gtk.Window.__init__(self)
		self.connect("destroy", lambda *w: gtk.main_quit())
		self.set_title("Ubuntu Tweak")
		self.set_default_size(650,680)
		self.set_position(gtk.WIN_POS_CENTER)
		self.set_border_width(10)
		self.set_icon_from_file("/usr/share/ubuntu-tweak/pixmaps/ubuntu-tweak.png")

		#create the vbox and pack it to window
		vbox = gtk.VBox(False, 0)
		self.add(vbox)

		#add the banner to vbox
		banner = gtk.Image()
		banner.set_from_file("/usr/share/ubuntu-tweak/pixmaps/banner.png")
		vbox.pack_start(banner, False, False, 0)

		#create the hpaned and pack it to vbox
		hpaned = gtk.HPaned()
		vbox.pack_start(hpaned, True, True, 0)

		#create a ScrolledWindow to pack treeview
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		sw.set_size_request(150, -1)
		hpaned.pack1(sw)

		#create the treeview
		model = self.__create_model()
		self.treeview = gtk.TreeView(model)
		self.__add_columns(self.treeview)
		sw.add(self.treeview)

		#create the notebook
		notebook = self.__create_notebook()
		hpaned.pack2(notebook)

		#create the buttons
		hbox = gtk.HBox(False,5)
		vbox.pack_start(hbox, False, False,0)
		button = gtk.Button(stock = gtk.STOCK_ABOUT)
		button.connect("clicked", self.show_about)
		hbox.pack_start(button, False, False, 0)
		button = gtk.Button(stock = gtk.STOCK_QUIT)
		button.connect("clicked", lambda *w: gtk.main_quit())
		hbox.pack_end(button, False, False, 0)
		
		self.show_all()

	def main(self):
		gtk.main()
