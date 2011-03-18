import gobject
from gi.repository import Gtk

class BasePack(Gtk.VBox):
    def __init__(self, label):
        gobject.GObject.__init__(self)
        self.set_border_width(5)

        title = Gtk.MenuItem(label=label)
        title.select()
        self.pack_start(title, False, False, 0)


class BaseListPack(BasePack):
    def __init__(self, title):
        BasePack.__init__(self, title)

        hbox = Gtk.HBox()
        hbox.set_border_width(5)
        self.pack_start(hbox, True, False, 0)

        label = Gtk.Label(label=" ")
        hbox.pack_start(label, False, False, 0)

        self.vbox = Gtk.VBox()
        hbox.pack_start(self.vbox, True, True, 0)


class SinglePack(BasePack):
    def __init__(self, title, widget):
        BasePack.__init__(self, title)

        self.pack_start(widget, True, True, 10)


class ListPack(BaseListPack):
    def __init__(self, title, widgets, padding=6):
        BaseListPack.__init__(self, title)
        self.items = []

        if widgets:
            for widget in widgets:
                if widget: 
                    if widget.get_parent():
                        widget.unparent()
                    self.vbox.pack_start(widget, False, False, padding)
                    self.items.append(widget)
        else:
            self = None
