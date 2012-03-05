import os
import logging
import traceback

from gi.repository import Gtk, Pango, GObject

from ubuntutweak import system
from ubuntutweak.gui import GuiBuilder
from ubuntutweak.settings.gsettings import GSetting
from ubuntutweak.modules import ModuleLoader
from ubuntutweak.utils import icon


log = logging.getLogger("ClipPage")


class Clip(Gtk.VBox):
    '''
    __icon__: the default icon name of Clip, and you can set the icon by call
              set_icon
    __title__: the default title, and you can set the title by call: set_title
    '''
    __icon__  = 'info'
    __title__ = ''
    __desktop__ = ''
    __distro__ = ''

    __utmodule__ = ''
    __utactive__ = True

    __gsignals__ = {
        'load_module': (GObject.SignalFlags.RUN_FIRST,
                        None,
                        (GObject.TYPE_STRING,)),
        'load_feature': (GObject.SignalFlags.RUN_FIRST,
                         None,
                         (GObject.TYPE_STRING,))
    }

    def __init__(self):
        GObject.GObject.__init__(self)

        self._hbox = Gtk.HBox(spacing=12)
        self.add(self._hbox)

        self._image = Gtk.Image()
        self._image.set_alignment(0, 0)
        self._hbox.pack_start(self._image, False, False, 12)

        self._inner_vbox = Gtk.VBox()
        self._hbox.pack_start(self._inner_vbox, True, True, 0)

        self._label = Gtk.Label()
        self._label.set_alignment(0, 0.5)
        self._inner_vbox.pack_start(self._label, False, False, 0)

        self.set_icon(self.get_pixbuf())
        self.set_title(self.__title__)

    def __str__(self):
        return '%s' % self.__class__

    @classmethod
    def get_name(cls):
        return cls.__name__

    @classmethod
    def get_category(cls):
        return 'clips'

    @classmethod
    def get_pixbuf(cls, size=48):
        '''Return gtk Pixbuf'''
        if cls.__icon__:
            if type(cls.__icon__) != list:
                if cls.__icon__.endswith('.png'):
                    icon_path = os.path.join(DATA_DIR, 'pixmaps', cls.__icon__)
                    pixbuf = Gtk.gd.pixbuf_new_from_file(icon_path)
                else:
                    pixbuf = icon.get_from_name(cls.__icon__, size=size)
            else:
                pixbuf = icon.get_from_list(cls.__icon__, size=size)

            return pixbuf

    def set_title(self, title):
        self._label.set_markup('<b>%s</b>' % title)

    def set_icon(self, pixbuf):
        self._image.set_from_pixbuf(pixbuf)

    def add_content(self, widget):
        '''Add the widget to inner vbox with proper space'''
        self._inner_vbox.pack_start(widget, False, False, 6)

    def add_action_button(self, button):
        '''Add an action button if you want to call the other modules or show
        website'''
        hbox = Gtk.HBox()
        self._inner_vbox.pack_start(hbox, False, False, 0)

        hbox.pack_end(button, False, False, 6)


class ClipPage(Gtk.VBox, GuiBuilder):
    __gsignals__ = {
        'load_module': (GObject.SignalFlags.RUN_FIRST,
                            None,
                            (GObject.TYPE_STRING,)),
        'load_feature': (GObject.SignalFlags.RUN_FIRST,
                            None,
                            (GObject.TYPE_STRING,))
    }

    def __init__(self):
        GObject.GObject.__init__(self)
        GuiBuilder.__init__(self, 'clippage.ui')

        self.recently_used_settings = GSetting('com.ubuntu-tweak.tweak.recently-used')
        self.clips_settings = GSetting('com.ubuntu-tweak.tweak.clips')

        self.load_cips()
        self.setup_recently_used()

        self.pack_start(self.get_object('hbox1'), True, True, 0)
        self.recently_used_settings.connect_notify(self.setup_recently_used)
        self.clips_settings.connect_notify(self.load_cips, True)

        self.show()

    def load_cips(self, a=None, b=None, do_remove=False):
        log.debug("Load clips, do_remove: %s" % do_remove)

        if do_remove:
            for child in self.clipvbox.get_children():
                log.debug("Remove clip: %s" % child)
                self.clipvbox.remove(child)

        clips = self.clips_settings.get_value()
        log.debug("All clips to load: %s" % clips)

        if clips and clips != ['']:
            loader = ModuleLoader('clips')

            for name in clips:
                try:
                    ClipClass = loader.get_module(name)
                    log.debug("Load clip: %s" % name)
                    clip = ClipClass()
                    clip.connect('load_module', self._on_module_button_clicked)
                    clip.connect('load_feature', self.on_clip_load_feature)
                    clip.show_all()
                    self.clipvbox.pack_start(clip, False, False, 0)
                except Exception, e:
                    log.error(traceback.print_exc())
                    if name in self.clips_settings.get_value():
                        new_list = self.clips_settings.get_value().remove(name)
                        self.clips_settings.set_value(new_list)

    def setup_recently_used(self, *args):
        log.debug("Overview page: setup_recently_used")

        used_list = self.recently_used_settings.get_value()
        for child in self.recently_used_box.get_children():
            self.recently_used_box.remove(child)

        for name in used_list:
            feature, module = ModuleLoader.search_module_for_name(name)
            if module:
                button = Gtk.Button()
                button.set_relief(Gtk.ReliefStyle.NONE)
                hbox = Gtk.HBox(spacing=6)
                button.add(hbox)

                image = Gtk.Image.new_from_pixbuf(module.get_pixbuf(size=16))
                hbox.pack_start(image, False, False, 0)

                label = Gtk.Label(label=module.get_title())
                label.set_ellipsize(Pango.EllipsizeMode.END)
                label.set_alignment(0, 0.5)

                hbox.pack_start(label, True, True, 0)

                button.connect('clicked', self._on_module_button_clicked, name)
                button.show_all()

                self.recently_used_vbox.pack_start(button, False, False, 0)

    def _on_module_button_clicked(self, widget, name):
        self.emit('load_module', name)

    def on_clip_load_feature(self, widget, name):
        self.emit('load_feature', name)
