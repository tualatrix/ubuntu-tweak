import pygtk
pygtk.require("2.0")
import gtk

class ItemBox(gtk.VBox):
	"""create a vbox to show a title and pack some widgets"""

	def __init__(self, title, widgets = None):
		gtk.VBox.__init__(self)
		self.set_border_width(5)
		
		label = gtk.Label()
		label.set_markup(title)
		label.set_alignment(0, 0)
		self.pack_start(label, False, False, 0)

		hbox = gtk.HBox(False, 5)
		hbox.set_border_width(5)
		self.pack_start(hbox, False, False, 0)

		label = gtk.Label(" ")
		hbox.pack_start(label, False, False, 0)

		vbox = gtk.VBox(False, 0)
		hbox.pack_start(vbox, False, False, 0)

		if widgets:
			if widgets.__len__() < 2:
				self.add(widgets[0])
			else:
				for widget in widgets:
					vbox.pack_start(widget, False, False, 0)
