__all__ = (
    'ModuleLoader',
    'TweakModule',
)
import os
import gtk
import sys
import pango
import inspect
import gobject

from ubuntutweak.common.consts import DATA_DIR
from ubuntutweak.common.systeminfo import SystemInfo
from ubuntutweak.utils import icon

def module_cmp(m1, m2):
    return cmp(m1.__title__, m2.__title__)

class ModuleLoader:
    module_table = {}
    id_table = {}

    def __init__(self, path):
        if os.path.isdir(path):
            for f in os.listdir(path):
                if f.endswith('.py') and f != '__init__.py':
                    module = os.path.splitext(f)[0]
                    package = __import__('.'.join([__name__, module]), fromlist=['modules'])
                    self.do_package_import(package)
        else:
            module = os.path.splitext(os.path.basename(path))[0]
            folder = os.path.dirname(path)
            package = __import__('.'.join([folder, module]))
            self.do_module_import(package, module)

        for k in self.module_table.keys():
            self.module_table[k].sort(module_cmp)

    def do_module_import(self, package, module):
        for k, v in inspect.getmembers(getattr(package, module)):
            self._insert_moduel(k, v)

    def do_package_import(self, package):
        for k, v in inspect.getmembers(package):
            self._insert_moduel(k, v)

    def _insert_moduel(self, k, v):
        if k not in ('TweakModule', 'proxy') and hasattr(v, '__utmodule__'):
            if self.is_supported_desktop(v.__desktop__) and v.__utactive__:
                key = v.__category__
                if self.module_table.has_key(key):
                    self.module_table[key].append(v)
                else:
                    self.module_table[key] = [v]

                self.id_table[v.__name__] = v

    def get_category(self, category):
        return self.module_table.get(category, [])

    def get_module(self, id):
        return self.id_table[id]

    def get_all_module(self):
        return self.id_table.values()

    def get_pixbuf(self, id):
        module = self.get_module(id)

        if module.__icon__:
            if type(module.__icon__) != list:
                if module.__icon__.endswith('.png'):
                    icon_path = os.path.join(DATA_DIR, 'pixmaps', module.__icon__)
                    pixbuf = gtk.gd.pixbuf_new_from_file(icon_path)
                else:
                    pixbuf = icon.get_from_name(module.__icon__, size=24)
            else:
                pixbuf = icon.get_from_list(module.__icon__, size=24)

            return pixbuf

    def is_supported_desktop(self, desktop_name):
        if desktop_name:
            return SystemInfo.desktop in desktop_name
        else:
            return True

class TweakModule(gtk.VBox):
    __title__ = ''
    __version__ = ''
    __icon__ = ''
    __author__ = ''
    __desc__ = ''
    __url__ = ''
    __urltitle__ = _('More')
    #Identify whether it is a ubuntu tweak module
    __utmodule__ = ''
    __utactive__ = True
    __desktop__ = ''

    #update use internal, and call use between modules
    __gsignals__ = {
            'update': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
            'call': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
    }

    def __init__(self, path=None, domain='ubuntu-tweak'):
        assert(self.__title__ and self.__desc__)

        gtk.VBox.__init__(self)

        self.draw_title()

        self.scrolled_win = gtk.ScrolledWindow()
        self.scrolled_win.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.pack_start(self.scrolled_win)

        self.inner_vbox = gtk.VBox(False, 6)
        self.inner_vbox.set_border_width(5)
        self.scrolled_win.add_with_viewport(self.inner_vbox)
        viewport = self.scrolled_win.get_child()
        viewport.set_shadow_type(gtk.SHADOW_NONE)

        if path:
            path = os.path.join(DATA_DIR, 'ui', path)

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

    def add_start(self, child, expand=True, fill=True, padding=0):
        self.inner_vbox.pack_start(child, expand, fill, padding)

    def add_end(self, child, expand=True, fill=True, padding=0):
        self.inner_vbox.pack_end(child, expand, fill, padding)

    def draw_title(self):
        eventbox = gtk.EventBox()
        eventbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
        self.pack_start(eventbox, False, False, 0)

        vbox = gtk.VBox()
        eventbox.add(vbox)

        align = gtk.Alignment(0.5, 0.5, 1.0, 1.0)
        align.set_padding(5, 5, 5, 5)
        vbox.pack_start(align)

        hbox = gtk.HBox(False, 6)
        align.add(hbox)

        inner_vbox = gtk.VBox(False, 6)
        hbox.pack_start(inner_vbox)

        align = gtk.Alignment(0.5, 0.5, 1.0, 1.0)
        inner_vbox.pack_start(align, False, False, 0)

        inner_hbox = gtk.HBox(False, 0)
        align.add(inner_hbox)

        name = gtk.Label()
        name.set_markup('<b><big>%s</big></b>' % self.__title__)
        name.set_alignment(0, 0.5)
        inner_hbox.pack_start(name, False, False, 0)

        if self.__url__:
            more = gtk.Label()
            more.set_markup('<a href="%s">%s</a>' % (self.__url__, self.__urltitle__))
            inner_hbox.pack_end(more, False, False, 0)

        desc = gtk.Label(self.__desc__)
        desc.set_ellipsize(pango.ELLIPSIZE_END)
        desc.set_alignment(0, 0.5)
        inner_vbox.pack_start(desc, False, False, 0)

        if self.__icon__:
            if type(self.__icon__) != list:
                if self.__icon__.endswith('.png'):
                    icon_path = os.path.join(DATA_DIR, 'pixmaps', self.__icon__)
                    image = gtk.image_new_from_file(icon_path)
                else:
                    pixbuf = icon.get_from_name(self.__icon__, size=48)
                    image = gtk.image_new_from_pixbuf(pixbuf)
            else:
                pixbuf = icon.get_from_list(self.__icon__, size=48)
                image = gtk.image_new_from_pixbuf(pixbuf)

            image.set_alignment(0, 0)
            image.set_padding(5, 5)
            hbox.pack_end(image, False, False, 0)

        vbox.pack_start(gtk.HSeparator(), False, False, 0)

    def remove_all_children(self):
        for child in self.inner_vbox.get_children():
            self.inner_vbox.remove(child) 

    def reparent(self, widget):
        '''
        If module use glade, it must call this method to reparent the main frame
        '''
        widget.reparent(self.inner_vbox)
