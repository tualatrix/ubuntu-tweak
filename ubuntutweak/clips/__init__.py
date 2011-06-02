import os
import gobject
from gi.repository import Gtk, Pango

from ubuntutweak.gui import GuiBuilder
from ubuntutweak.settings.gsettings import GSetting
from ubuntutweak.modules import ModuleLoader

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
    rencently_used_settings = GSetting('com.ubuntu-tweak.tweak.rencently-used')

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

        self.setup_rencently_used()
        self.rencently_used_settings.connect_notify(self.setup_rencently_used)

    def setup_rencently_used(self, *args):
        used_list = self.rencently_used_settings.get_value()
        for child in self.rencently_used_vbox.get_children():
            self.rencently_used_vbox.remove(child)

        for name in used_list:
            feature, module = ModuleLoader.search_module_for_name(name)
            if module:
                button = Gtk.Button()
                button.set_relief(Gtk.ReliefStyle.NONE)
                hbox = Gtk.HBox(spacing=6)
                button.add(hbox)

                image = Gtk.Image.new_from_pixbuf(module.get_pixbuf(size=16))
                hbox.pack_start(image, False, False, 0)

                label = Gtk.Label(module.get_title())
                label.set_max_width_chars(12)
                label.set_ellipsize(Pango.EllipsizeMode.END)
                hbox.pack_start(label, False, False, 0)

                button.connect('clicked', self._on_module_button_clicked, name)
                button.show_all()

                self.rencently_used_vbox.pack_start(button, False, False, 0)

    def _on_module_button_clicked(self, widget, name):
        os.system('ubuntu-tweak -m %s name &' % name)
