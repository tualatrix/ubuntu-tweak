import os
import sys
import glob
import logging
import inspect
import webbrowser
from new import classobj

import gobject
from gi.repository import Gtk, Pango

from ubuntutweak.utils import icon
from ubuntutweak.common.consts import DATA_DIR, CONFIG_ROOT
from ubuntutweak.common.debug import run_traceback

log = logging.getLogger('ModuleLoader')

def module_cmp(m1, m2):
    return cmp(m1.get_title(), m2.get_title())


class ModuleLoader:
    # the key will like this: 'Compiz': <class 'ubuntutweak.tweaks.compiz.Compiz'
    module_table = None
    category_table = None

    category_names = (
        ('broken', _('Broken Modules')),
        ('application', _('Applications')),
        ('startup', _('Startup')),
        ('desktop', _('Desktop')),
        ('personal', _('Personal')),
        ('system', _('System')),
        ('other', _('Other')),
        )

    default_features = ('tweaks', 'admins', 'janitors')

    search_loaded_table = {}

    def __init__(self, feature):
        '''feature choices: tweaks, admins and janitors'''
        self.module_table = {}
        self.category_table = {}
        self.feature = feature

        for k, v in self.category_names:
            self.category_table[k] = {}

        # First import system staff
        try:
            m = __import__('ubuntutweak.%s' % self.feature, fromlist='ubuntutweak')
            self.do_folder_import(m.__path__[0])
        except ImportError, e:
            log.error(e)

        # Second import user plugins
        user_folder = os.path.join(CONFIG_ROOT, self.feature)
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        package_identy_file = os.path.join(user_folder, '__init__.py')
        if not os.path.exists(package_identy_file):
            os.system("touch %s" % package_identy_file)

        log.info("Loading user plugins...")
        self.do_folder_import(user_folder)

    @classmethod
    def search_module_for_name(cls, name):
        for feature in cls.default_features:
            if name in cls.search_loaded_table:
                return feature, cls.search_loaded_table[name]
            #User's at first
            user_folder = os.path.join(CONFIG_ROOT, feature)

            if not os.path.exists(user_folder):
                os.makedirs(user_folder)

            package_identy_file = os.path.join(user_folder, '__init__.py')
            if not os.path.exists(package_identy_file):
                os.system("touch %s" % package_identy_file)

            log.info('Loading plugins "%s" for "%s"...' % (name, feature))
            module = cls._get_module_by_name_from_folder(name, user_folder)

            if module:
                if name not in cls.search_loaded_table:
                    cls.search_loaded_table[name] = module
                return feature, module

            try:
                m = __import__('ubuntutweak.%s' % feature, fromlist='ubuntutweak')
                module = cls._get_module_by_name_from_folder(name, m.__path__[0])
                if module:
                    if name not in cls.search_loaded_table:
                        cls.search_loaded_table[name] = module
                    return feature, module
            except ImportError, e:
                log.error(e)

        return 'overview', None

    @classmethod
    def _get_module_by_name_from_folder(cls, name, folder):
        for path in glob.glob(os.path.join(folder, '*')):
            module_name = os.path.splitext(os.path.basename(path))[0]
            dirname = os.path.dirname(path)
            if folder not in sys.path:
                sys.path.insert(0, folder)
            package = __import__(module_name)
            for k, v in inspect.getmembers(package):
                if k == name and k not in ('TweakModule', 'proxy') and \
                    hasattr(v, '__utmodule__') and v.__utactive__:
                    return v

    def do_single_import(self, path):
        module_name = os.path.splitext(os.path.basename(path))[0]
        try:
            package = __import__(module_name)
        except Exception, e:
            Broken = create_broken_module_class(module_name)
            self.module_table[Broken.get_name()] = Broken
            self.category_table['broken'][Broken.get_name()] = Broken
            log.error("Module import error: %s", str(e))
        else:
            for k, v in inspect.getmembers(package):
                self._insert_moduel(k, v)

    def do_folder_import(self, path):
        if path not in sys.path:
            sys.path.insert(0, path)

        for f in os.listdir(path):
            log.debug("Found %s in %s" % (f, path))
            full_path = os.path.join(path, f)

            if os.path.isdir(full_path) and \
                    os.path.exists(os.path.join(path, '__init__.py')):
                self.do_single_import(f)
            elif f.endswith('.py') and f != '__init__.py':
                module_name = os.path.splitext(f)[0]
                log.debug("Try to load module: %s" % module_name)
                self.do_single_import(f)

    def _insert_moduel(self, k, v):
        if k not in ('TweakModule', 'proxy') and hasattr(v, '__utmodule__'):
            if v.__utactive__:
                self.module_table[v.get_name()] = v
                if v.__category__ not in dict(self.category_names):
                    self.category_table['other'][v.get_name()] = v
                else:
                    self.category_table[v.__category__][v.get_name()] = v

    def get_categories(self):
        for k, v in self.category_names:
            yield k, v

    def get_modules_by_category(self, category):
        modules = self.category_table.get(category).values()
        modules.sort(module_cmp)
        return modules

    def get_module(self, name):
        return self.module_table[name]


class TweakModule(Gtk.VBox):
    __title__ = ''
    __version__ = ''
    __icon__ = ''
    __author__ = ''
    __desc__ = ''
    __url__ = ''
    __url_title__ = _('More')
    #Identify whether it is a ubuntu tweak module
    __utmodule__ = ''
    __utactive__ = True
    __category__ = ''

    #update use internal, and call use between modules
    __gsignals__ = {
            'update': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
            'call': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
    }

    def __init__(self, path=None, domain='ubuntu-tweak'):
        gobject.GObject.__init__(self)
        self.set_border_width(6)

        self.scrolled_win = Gtk.ScrolledWindow()
        self.scrolled_win.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.pack_start(self.scrolled_win, True, True, 0)

        self.inner_vbox = Gtk.VBox(spacing=6)
        self.inner_vbox.set_border_width(6)
        self.scrolled_win.add_with_viewport(self.inner_vbox)
        viewport = self.scrolled_win.get_child()

        if path:
            path = os.path.join(DATA_DIR, 'ui', path)

            self.builder = Gtk.Builder()
            self.builder.set_translation_domain(domain)
            self.builder.add_from_file(path)
            self.builder.connect_signals(self)
            for o in self.builder.get_objects():
                if issubclass(type(o), Gtk.Buildable):
                    name = Gtk.Buildable.get_name(o)
                    setattr(self, name, o)
                else:
                    log.error("WARNING: can not get name for '%s'" % o)

    def add_start(self, child, expand=True, fill=True, padding=0):
        self.inner_vbox.pack_start(child, expand, fill, padding)

    def add_end(self, child, expand=True, fill=True, padding=0):
        self.inner_vbox.pack_end(child, expand, fill, padding)

    def remove_all_children(self):
        for child in self.inner_vbox.get_children():
            self.inner_vbox.remove(child) 

    def reparent(self, widget):
        '''
        If module use glade, it must call this method to reparent the main frame
        '''
        widget.reparent(self.inner_vbox)

    @classmethod
    def get_name(cls):
        '''Return the module name
        class Computer(TweakModule):
            pass
        the "Computer" is the module name
        '''
        return cls.__name__

    @classmethod
    def get_title(cls):
        '''Return the module title, it is for human read with i18n support
        '''
        return cls.__title__

    @classmethod
    def get_url(cls):
        return cls.__url__

    @classmethod
    def get_url_title(cls):
        return cls.__url_title__

    @classmethod
    def get_description(cls):
        '''Return the module description, it is for human read with i18n support
        '''
        return cls.__desc__

    @classmethod
    def get_category(cls):
        return cls.__category__

    def get_error(self):
        return self.error_view.get_buffer().get_property('text')

    @classmethod
    def get_pixbuf(cls, size=32):
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


def create_broken_module_class(name):
    module_name = 'Broken%s' % name.title()

    return classobj(module_name,
                    (BrokenModule,),
                    {'__name__': module_name,
                     '__title__': name,
                     '__category__': 'broken',
                     'error_view': run_traceback('error', textview_only=True)})


class BrokenModule(TweakModule):
    __icon__ = 'gtk-dialog-error'

    def __init__(self):
        TweakModule.__init__(self, 'brokenmodule.ui')

        if '/etc/apt/apt.conf.d' in self.get_error():
            p = re.compile('(/etc/apt/apt.conf.d/[\w-]+)')
            broken_file = p.findall(self.get_error())[0]
            self.message_label.set_text(_("Ubuntu Tweak has detected that your"
             " apt configuration is broken.\nTry to fix by following steps:\n"
             "\n\t1. Open your terminal\n\t2. Run the commands to fix:\n\n\t"
             "\tsudo chmod 644 %(broken_file)s\n\t\tsudo chown root:root "
             "%(broken_file)s\n\nOr you can submit the Error Message to the "
             "developer for help:" % {'broken_file': broken_file}))
        elif '/etc/apt/sources.list.d/' in self.get_error():
            p = re.compile('(/etc/apt/sources.list.d/[\w-]+)')
            broken_file = p.findall(self.get_error())[0]

            self.message_label.set_text(_("Ubuntu Tweak has detected that your"
             "apt list file is broken.\nTry to fix by following steps:\n\n\t1."
             "Open your terminal\n\t2. Run the command to open apt list file:"
             "\n\n\t\tsudo gedit %s\n\n\t3. Edit the list to make it correctly"
             "\n\nOr you can submit the Error Message to the developer for"
             "help:" % broken_file))

        self.error_view.reparent(self.scrolled_window)
        self.reparent(self.alignment1)

    def on_report_button_clicked(self, widget):
        webbrowser.open('https://bugs.launchpad.net/ubuntu-tweak/+filebug')
