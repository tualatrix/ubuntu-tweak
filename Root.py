import pygtk
pygtk.require('2.0')
import gtk
import gobject
import gettext

from Widgets import GConfCheckButton

class Root(gtk.VBox):
	"""Some options about root user"""
	def __init__(self):
		gtk.VBox.__init__(self)

		button = GConfCheckButton(_("Display information message when no password is needed"), "/apps/gksu/display-no-pass-info")

		
#os.symlink(os.getenv("HOME")+"/.icons","/root/.icons")
#os.symlink(os.getenv("HOME")+"/.themes","/root/.themes")
