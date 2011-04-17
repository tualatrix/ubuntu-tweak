import gobject
from gi.repository import Gtk, Pango

from ubuntutweak.gui import GuiBuilder

class AppsPage(Gtk.VBox, GuiBuilder):
    def __init__(self):
        gobject.GObject.__init__(self)
        GuiBuilder.__init__(self, 'appspage.ui')

        self.hpaned1.reparent(self)

        self.update_model()
        self.show_all()

    def update_model(self):
        self.category_model.append(None, (0, 'Featured'))
        self.category_model.append(None, (1, 'New Added'))
        iter = self.category_model.append(None, (2, 'All Apps'))
        self.category_model.append(iter, (3, 'Desktop'))
        self.category_model.append(iter, (4, 'Email'))
        self.category_model.append(None, (1, 'All Installed'))
