import os
import gobject
from gi.repository import Gtk, Pango

from ubuntutweak.gui import GuiBuilder
from ubuntutweak.settings.gsettings import GSetting
from ubuntutweak.modules import ModuleLoader

class Clip(Gtk.VBox):
    __gsignals__ = {
        'load_module': (gobject.SIGNAL_RUN_FIRST,
                            gobject.TYPE_NONE,
                            (gobject.TYPE_STRING,)),
        'load_feature': (gobject.SIGNAL_RUN_FIRST,
                            gobject.TYPE_NONE,
                            (gobject.TYPE_STRING,))
    }

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
    __gsignals__ = {
        'load_module': (gobject.SIGNAL_RUN_FIRST,
                            gobject.TYPE_NONE,
                            (gobject.TYPE_STRING,)),
        'load_feature': (gobject.SIGNAL_RUN_FIRST,
                            gobject.TYPE_NONE,
                            (gobject.TYPE_STRING,))
    }

    max_recently_used_size = 200

    def __init__(self):
        gobject.GObject.__init__(self)
        GuiBuilder.__init__(self, 'clippage.ui')

        #TODO
        from hardwareinfo import HardwareInfo
        from updateinfo import UpdateInfo
        from cleanerinfo import CleanerInfo
        self.rencently_used_settings = GSetting('com.ubuntu-tweak.tweak.rencently-used')

        for ClipClass in (HardwareInfo, UpdateInfo, CleanerInfo):
            clip = ClipClass()
            clip.connect('load_module', self._on_module_button_clicked)
            clip.connect('load_feature', self.on_clip_load_feature)
            self.clipvbox.pack_start(clip, False, False, 0)

        self.setup_rencently_used()

        self.pack_start(self.get_object('hbox1'), True, True, 0)
        self.connect('size-allocate', self.on_size_allocation)
        self.rencently_used_settings.connect_notify(self.setup_rencently_used)

        self.show_all()

    def on_size_allocation(self, widget, allocation):
        frame_width = int(allocation.width / 4.5)

        if frame_width > self.max_recently_used_size:
            frame_width = self.max_recently_used_size
        self.rencently_frame.set_size_request(frame_width, -1)

    def setup_rencently_used(self, *args):
        used_list = self.rencently_used_settings.get_value()
        for child in self.rencently_used_vbox.get_children():
            self.rencently_used_vbox.remove(child)

        size_list = []
        for name in used_list:
            feature, module = ModuleLoader.search_module_for_name(name)
            if module:
                size_list.append(Gtk.Label(module.get_title()).get_layout().get_pixel_size()[0])

                button = Gtk.Button()
                button.set_relief(Gtk.ReliefStyle.NONE)
                hbox = Gtk.HBox(spacing=6)
                button.add(hbox)

                image = Gtk.Image.new_from_pixbuf(module.get_pixbuf(size=16))
                hbox.pack_start(image, False, False, 0)

                label = Gtk.Label(module.get_title())
                label.set_ellipsize(Pango.EllipsizeMode.END)
                label.set_alignment(0, 0.5)

                hbox.pack_start(label, True, True, 0)

                button.connect('clicked', self._on_module_button_clicked, name)
                button.show_all()

                self.rencently_used_vbox.pack_start(button, False, False, 0)

        if size_list:
            self.max_recently_used_size = max(size_list) + 58

    def _on_module_button_clicked(self, widget, name):
        self.emit('load_module', name)

    def on_clip_load_feature(self, widget, name):
        self.emit('load_feature', name)
