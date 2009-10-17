import os
import gtk
import sys
import pango
import gobject

from common.consts import DATA_DIR

class TweakModule(gtk.ScrolledWindow):
    __name__ = ''
    __version__ = ''
    __icon__ = ''
    __author__ = ''
    __desc__ = ''
    __url__ = ''

    __gsignals__ = {
            'update': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_STRING)),
            'call': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
    }

    def __init__(self, path=None, domain='ubuntu-tweak'):
        assert(self.__name__ and self.__desc__)

        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.vbox = gtk.VBox(False, 0)
        self.add_with_viewport(self.vbox)
        viewport = self.get_child()
        viewport.set_shadow_type(gtk.SHADOW_NONE)

        self.draw_title()

        self.inner_vbox = gtk.VBox(False, 6)
        self.inner_vbox.set_border_width(6)
        self.vbox.pack_start(self.inner_vbox, False, False, 0)

        if path:
            path = os.path.join(DATA_DIR, 'gui', path)

            self.builder = gtk.Builder()
            self.builder.set_translation_domain(domain)
            self.builder.add_from_file(path)
            self.builder.connect_signals(self)
            for o in self.builder.get_objects():
                if issubclass(type(o), gtk.Buildable):
                    name = gtk.Buildable.get_name(o)
                    setattr(self, name, o)
                else:
                    print >>sys.stderr, "WARNING: can not get name for '%s'" % o
            self.reparent()

    def pack_start(self, child, expand = True, fill = True, padding = 0):
        self.inner_vbox.pack_start(child, expand, fill, padding)

    def pack_end(self, child, expand = True, fill = True, padding = 0):
        self.inner_vbox.pack_end(child, expand, fill, padding)

    def draw_title(self):
        eventbox = gtk.EventBox()
        eventbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
        self.vbox.pack_start(eventbox, False, False, 0)

        hbox = gtk.HBox(False, 12)
        eventbox.add(hbox)

        vbox = gtk.VBox(False, 6)
        hbox.pack_start(vbox)

        vbox.pack_start(gtk.Label(self.__name__), False, False, 0)
        vbox.pack_start(gtk.Label(self.__desc__), False, False, 0)

        vbox.pack_start(gtk.HSeparator(), False, False, 0)

    def reparent(self):
        raise NotImplementedError
