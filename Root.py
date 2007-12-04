import pygtk
pygtk.require('2.0')
import gtk
import gobject
import gettext

class Root(gtk.VBox):
	def __init__(self):
		gtk.VBox.__init__(self)
#os.symlink(os.getenv("HOME")+"/.icons","/root/.icons")
#os.symlink(os.getenv("HOME")+"/.themes","/root/.themes")
