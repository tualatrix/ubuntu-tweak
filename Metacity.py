import pygtk
pygtk.require('2.0')
import gtk
import os
import gobject
import gettext

from Widgets import GConfCheckButton, ItemBox, EntryBox, HScaleBox

class Metacity(gtk.VBox):
	"""Some options about Metacity Window Manager"""
	def __init__(self):
		gtk.VBox.__init__(self)

		box = ItemBox(_("<b>Metacity Window Decorate Options</b>"), (
			GConfCheckButton(_("Use metacity theme"), "/apps/gwd/use_metacity_theme"),
			GConfCheckButton(_("ope"), "/apps/gwd/metacity_theme_shade_opacity"),
			HScaleBox(_("Metacity theme opacity"), 0, 1, "/apps/gwd/metacity_theme_opacity"),
			))

		self.pack_start(box, False, False, 0)
