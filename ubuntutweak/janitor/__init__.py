import logging


import gobject
from gi.repository import Gtk, Pango

from ubuntutweak.gui import GuiBuilder

log = logging.getLogger('Janitor')


class JanitorPage(Gtk.VBox, GuiBuilder):
    i = 0

    def __init__(self):
        gobject.GObject.__init__(self)
        GuiBuilder.__init__(self, 'janitorpage.ui')

        self.hpaned1.reparent(self)

        self.update_model()
        self.show_all()

    def update_model(self):
        #TODO
        self.janitor_model.append((False, 'Cache', False, 0))
        self.janitor_model.append((False, 'Pakcages', False, 0))
        self.janitor_model.append((False, 'Configs', False, 0))
        self.janitor_model.append((False, 'Kernel', False, 0))
