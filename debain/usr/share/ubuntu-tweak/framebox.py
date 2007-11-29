import pygtk
pygtk.require("2.0")
import gtk

class VFrameWithButton(gtk.Frame):
	"""create a frame to pack buttons"""

	def __init__(self, label, buttons):
		gtk.Frame.__init__(self)
		self.set_label(label)
		hbox =gtk.HBox(False, 5)
		self.add(hbox)

		label = gtk.Label(" ")
		hbox.pack_start(label, False, False, 0)

		vbox = gtk.VBox(False, 0)
		hbox.pack_start(vbox, False, False, 0)

		for button in buttons:
			vbox.pack_start(button, False, False, 0)
