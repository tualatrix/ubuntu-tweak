import pygtk
pygtk.require('2.0')
import gtk
import gobject
import gettext

from Widgets import GConfCheckButton, ItemBox

class Root(gtk.VBox):
	"""Some options about root user"""
	def __init__(self):
		gtk.VBox.__init__(self)

		button = GConfCheckButton(_("Display information message when no password is needed"), "/apps/gksu/display-no-pass-info")

		box = ItemBox(_("<b>root user options</b>"),(button,))
		self.pack_start(box, False, False, 0)
#os.symlink(os.getenv("HOME")+"/.icons","/root/.icons")
#os.symlink(os.getenv("HOME")+"/.themes","/root/.themes")
