import gobject
from gi.repository import Gtk

from ubuntutweak.gui import GuiBuilder

class Clip(Gtk.VBox):
    def __init__(self):
        gobject.GObject.__init__(self, spacing=12)

        self.hbox = Gtk.HBox(spacing=12)
        self.pack_start(self.hbox, True, True, 0)

        self.image = Gtk.Image()
        self.image.set_alignment(0, 0)
        self.hbox.pack_start(self.image, False, False, 12)

        self.inner_vbox = Gtk.VBox()
        self.hbox.pack_start(self.inner_vbox, True, True, 0)

    def set_image_from_pixbuf(self, pixbuf):
        self.image.set_from_pixbuf(pixbuf)

    def set_title(self, title):
        label = Gtk.Label()
        label.set_alignment(0, 0.5)
        label.set_markup('<b>%s</b>' % title)

        self.inner_vbox.pack_start(label, False, False, 0)
        # Force reorder the title label, because sometime it will be called later
        self.inner_vbox.reorder_child(label, 0)

    def set_content(self, content):
        #TODO rename this API
        self.inner_vbox.pack_start(content, False, False, 3)

    def add_action_button(self, button):
        #TODO and #FIXME better API
        hbox = Gtk.HBox()
        self.inner_vbox.pack_start(hbox, False, False, 0)

        hbox.pack_end(button, False, False, 0)


class ClipPage(Gtk.VBox, GuiBuilder):
    def __init__(self):
        gobject.GObject.__init__(self)
        GuiBuilder.__init__(self, 'clippage.ui')

        #TODO
        from hardwareinfo import HardwareInfo
        from updateinfo import UpdateInfo
        from cleanerinfo import CleanerInfo

        self.clipvbox.pack_start(UpdateInfo(), False, False, 0)
        self.clipvbox.pack_start(HardwareInfo(), False, False, 0)
        self.clipvbox.pack_start(CleanerInfo(), True, True, 0)
