# coding: utf-8

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import gettext

from gnome import url_show
from Session import Session
from Icon import Icon
from Compiz import Compiz
from Gnome import Gnome
from Nautilus import Nautilus
from PowerManager import PowerManager
from LockDown import LockDown
from Root import Root

gettext.install("ubuntu-tweak", unicode = True)

VERSION = "0.2.4"

(
        NUM_COLUMN,
        ICON_COLUMN,
        NAME_COLUMN,
	PAGE_COLUMN,
        TOTAL_COLUMN
) = range(5)

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
		ROOT_PAGE,
	SECURITY_PAGE,
		SECU_OPTIONS_PAGE,
	APPLICATION_PAGE,
		FCITX_PAGE,
	TOTAL_PAGE
) = range(16)

icons = \
[
	"pixmaps/welcome.png",
	"pixmaps/startup.png",
	"pixmaps/session.png",
	"pixmaps/desktop.png",
	"pixmaps/icon.png",
	"pixmaps/compiz-fusion.png",
	"pixmaps/gnome.png",
	"pixmaps/nautilus.png",
	"pixmaps/system.png",
	"pixmaps/powermanager.png",
	"pixmaps/root.png",
	"pixmaps/security.png",
	"pixmaps/lockdown.png",
	"pixmaps/applications.png",
	"pixmaps/lockdown.png",
]

def Welcome():
	vbox = gtk.VBox(False, 0)

	label = gtk.Label()
	label.set_markup(_("<span size=\"xx-large\">Welcome to <b>Ubuntu Tweak!</b></span>\n\n\nThis is a tool for Ubuntu which makes it easy to change hidden \nsystem and desktop settings.\n\nUbuntu Tweak is currently only for the GNOME Desktop Environment.\n\nAlthough this application is only in early stages, I'll keep developing it.\n\nIf you have any suggestions, Please E-mail me. \n\nThank You!"))
	label.set_justify(gtk.JUSTIFY_FILL)
	vbox.pack_start(label, False, False, 50)

	return vbox

def Blank():
	vbox = gtk.VBox(True, 0)

	label = gtk.Label()
	label.set_markup(_("<span size=\"xx-large\">Please select the child item</span>"))
	vbox.pack_start(label, False, False, 0)

	return vbox


startup = \
[
	[SESSION_PAGE, icons[SESSION_PAGE], _("Session Control"), Session()]
]

desktop = \
[
	[ICON_PAGE, icons[ICON_PAGE], _("Desktop Icon"), Icon()],
	[COMPIZ_PAGE, icons[COMPIZ_PAGE], _("Compiz Fusion"), Compiz()],
	[GNOME_PAGE, icons[GNOME_PAGE], _("GNOME"), Gnome()],
	[NAUTILUS_PAGE, icons[NAUTILUS_PAGE], _("Nautilus"), Nautilus()]
]

system = \
[
	[POWER_PAGE, icons[POWER_PAGE], _("Power Manager"), PowerManager()],
	[ROOT_PAGE, icons[ROOT_PAGE], _("Root Options"), Root()]
]

security = \
[
	[SECU_OPTIONS_PAGE, icons[SECU_OPTIONS_PAGE], _("Security Options"), LockDown()]
]

#application = \
#[
#	[FCITX_PAGE, icons[FCITX_PAGE], _("Fcitx")]
#]

itemlist = \
[
	[WELCOME_PAGE, icons[WELCOME_PAGE], _("Welcome"), Welcome(), None],
	[STARTUP_PAGE, icons[SESSION_PAGE], _("Startup"), Blank(), startup],
	[DESKTOP_PAGE, icons[DESKTOP_PAGE], _("Desktop"), Blank(), desktop],
	[SYSTEM_PAGE, icons[SYSTEM_PAGE], _("System"), Blank(), system],
	[SECURITY_PAGE, icons[SECURITY_PAGE], _("Security"), Blank(), security],
	[APPLICATION_PAGE, icons[APPLICATION_PAGE], _("Application"),Blank(), None]
]

class MainWindow(gtk.Window):
	"""the main Window of Ubuntu Tweak"""

	def create_model(self):
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
		self.notebook.set_current_page(data.get_value(iter, NUM_COLUMN))

	def add_columns(self, treeview):
		model = treeview.get_model()
		selection = treeview.get_selection()
		selection.connect("changed", self.selection_cb, model)

		renderer = gtk.CellRendererText()

		column = gtk.TreeViewColumn("Num",renderer,text = NUM_COLUMN)
		column.set_visible(False)
		treeview.append_column(column)

		column = gtk.TreeViewColumn("Title")

		renderer = gtk.CellRendererPixbuf()
		column.pack_start(renderer, True)
		column.set_attributes(renderer, pixbuf = ICON_COLUMN)

		renderer = gtk.CellRendererText()
		column.pack_start(renderer, True)
		column.set_attributes(renderer, text = NAME_COLUMN)

		treeview.set_headers_visible(False)
		treeview.append_column(column)

	def create_notebook(self):
		notebook = gtk.Notebook()
		notebook.set_scrollable(True)
		notebook.set_show_tabs(False)

		for item in itemlist:
			page = item[PAGE_COLUMN]
			notebook.append_page(page, None)

			if item[-1]:
				for child_item in item[-1]:
					page = child_item[PAGE_COLUMN]
					notebook.append_page(page, None)

		return notebook

	def click_website(self, dialog, link, data = None):
		url_show(link)
	
	def show_about(self, data = None):
		gtk.about_dialog_set_url_hook(self.click_website)
		about = gtk.AboutDialog()
		about.set_name("Ubuntu Tweak")
		about.set_version(VERSION)
		about.set_website("http://ubuntu-tweak.com")
		about.set_website_label("ubuntu-tweak.com")
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
		gtk.Window.__init__(self)
		self.connect("destroy", lambda *w: gtk.main_quit())
		self.set_title("Ubuntu Tweak")
		self.set_default_size(650,680)
		self.set_position(gtk.WIN_POS_CENTER)
		self.set_border_width(10)
		self.set_icon_from_file("pixmaps/ubuntu-tweak.png")

		vbox = gtk.VBox(False, 0)
		self.add(vbox)

		banner = gtk.Image()
		banner.set_from_file("pixmaps/banner.png")
		vbox.pack_start(banner, False, False, 0)

		hpaned = gtk.HPaned()
		vbox.pack_start(hpaned, True, True, 0)

		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		sw.set_size_request(150, -1)
		hpaned.pack1(sw)

		model = self.create_model()
		self.treeview = gtk.TreeView(model)
		self.add_columns(self.treeview)
		sw.add(self.treeview)

		self.notebook = self.create_notebook()
		hpaned.pack2(self.notebook)

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
