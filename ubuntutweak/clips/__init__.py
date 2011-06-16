import os
import logging
import gobject
from gi.repository import Gtk, Pango

from ubuntutweak.gui import GuiBuilder
from ubuntutweak.settings.gsettings import GSetting
from ubuntutweak.modules import ModuleLoader


log = logging.getLogger("ClipPage")


class Clip(Gtk.VBox):
    __utmodule__ = ''
    __utactive__ = True

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
        self.image.set_from_pixbuf(self.get_image_pixbuf())
        self.image.set_alignment(0, 0)
        self.hbox.pack_start(self.image, False, False, 12)

        self.inner_vbox = Gtk.VBox()
        self.hbox.pack_start(self.inner_vbox, True, True, 0)

    @classmethod
    def get_name(cls):
        return cls.__name__

    @classmethod
    def get_category(cls):
        return 'clips'

    def get_image_pixbuf(self):
        return NotImplemented

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
        self.inner_vbox.pack_start(content, False, False, 6)

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

    (DIRECTION_UP, DIRECTION_DOWN) = range(2)
    direction = None

    def __init__(self):
        gobject.GObject.__init__(self)
        GuiBuilder.__init__(self, 'clippage.ui')

        self.rencently_used_settings = GSetting('com.ubuntu-tweak.tweak.rencently-used')

        loader = ModuleLoader('clips')

        for name, ClipClass in loader.module_table.items():
            log.debug("Load clip: %s" % name)
            clip = ClipClass()
            clip.connect('load_module', self._on_module_button_clicked)
            clip.connect('load_feature', self.on_clip_load_feature)
            clip.show()
            self.clipvbox.pack_start(clip, False, False, 0)

        self.setup_rencently_used()

        self.pack_start(self.get_object('hbox1'), True, True, 0)
        self.connect('expose-event', self.on_expose_event)
        self.rencently_used_settings.connect_notify(self.setup_rencently_used)

        self.show()

    def on_expose_event(self, widget, event):
        log.debug('on_expose_event')
        frame_width = int(self.get_allocation().width / 4.5)

        if frame_width > self.max_recently_used_size:
            frame_width = self.max_recently_used_size
        self.rencently_frame.set_size_request(frame_width, -1)

        self.slide_clips()

    def slide_clips(self, direction=None):
        max_height = self.get_allocation().height
        height_sum = 0

        if direction == self.DIRECTION_DOWN:
            self.clipvbox.set_data('direction', self.DIRECTION_DOWN)

            for clip in self.clipvbox.get_children()[1:-1]:
                if clip.get_visible():
                    log.debug("%s is visible, hide it" % clip)
                    clip.hide()
                else:
                    height_sum += clip.get_allocation().height
                    height_sum += 32

                    if height_sum < max_height:
                        log.debug("%s is not visible, show it" % clip)
                        clip.show()

            self.clipvbox.get_children()[0].set_visible(True)
            self.clipvbox.get_children()[-1].set_visible(height_sum > max_height)
        elif direction == self.DIRECTION_UP:
            self.clipvbox.set_data('direction', self.DIRECTION_UP)

            for clip in self.clipvbox.get_children()[1:-1]:
                if clip.get_visible():
                    log.debug("%s is visible, hide it" % clip)
                    clip.hide()
                else:
                    height_sum += clip.get_allocation().height
                    height_sum += 32

                    if height_sum < max_height:
                        log.debug("%s is not visible, show it" % clip)
                        clip.show()

            self.clipvbox.get_children()[0].set_visible(height_sum > max_height)
            self.clipvbox.get_children()[-1].set_visible(True)
        else:
            direction = self.clipvbox.get_data('direction')
            if direction == self.DIRECTION_DOWN:
                index = 0
                for i, clip in enumerate(self.clipvbox.get_children()[1:-1]):
                    if clip.get_visible():
                        index = i
                        break
                index += 1
            else:
                index = 1

            for clip in self.clipvbox.get_children()[index:-1]:
                height_sum += clip.get_allocation().height
                height_sum += 32

                if height_sum > max_height:
                    clip.hide()
                else:
                    clip.show()

            self.clipvbox.get_children()[-1].set_visible(height_sum > max_height)

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

    def on_up_button_clicked(self, widget):
        log.debug("on_up_button_clicked")
        self.slide_clips(self.DIRECTION_UP)

    def on_down_button_clicked(self, widget):
        log.debug("on_down_button_clicked")
        self.slide_clips(self.DIRECTION_DOWN)
