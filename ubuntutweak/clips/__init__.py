import gobject
from gi.repository import Gtk

from ubuntutweak.gui import GuiBuilder

class Clip(Gtk.VBox):
    def __init__(self):
        gobject.GObject.__init__(self, spacing=12)

        self.hbox = Gtk.HBox(spacing=12)
        self.pack_start(self.hbox, False, False, 0)

        self.image = Gtk.Image()
        self.image.set_alignment(0, 0)
        self.hbox.pack_start(self.image, False, False, 12)

        self.inner_vbox = Gtk.VBox()
        self.hbox.pack_start(self.inner_vbox, False, False, 0)

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
        self.inner_vbox.pack_start(content, False, False, 6)


class ClipPage(Gtk.VBox, GuiBuilder):
    def __init__(self):
        gobject.GObject.__init__(self)
        GuiBuilder.__init__(self, 'clips/clippage.ui')

        #TODO
        from hardwareinfo import HardwareInfo
        from updateinfo import UpdateInfo
        from systeminfo import SystemInfo
        from cleanerinfo import CleanerInfo

        self.clipvbox.pack_start(UpdateInfo(), False, False, 0)
        self.clipvbox.pack_start(SystemInfo(), False, False, 0)
        self.clipvbox.pack_start(HardwareInfo(), False, False, 0)
        self.clipvbox.pack_start(CleanerInfo(), False, False, 0)
