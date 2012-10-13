import os
import sys
import glob
import logging
import inspect
import traceback
from new import classobj

from gi.repository import GObject, Gtk, Gdk, GdkPixbuf

from ubuntutweak import system
from ubuntutweak.utils import icon
from ubuntutweak.common.consts import DATA_DIR, CONFIG_ROOT, IS_INSTALLED 
from ubuntutweak.common.debug import run_traceback, log_traceback, open_bug_report

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
        ('appearance', _('Appearance')),
        ('startup', _('Startup')),
        ('desktop', _('Desktop')),
        ('personal', _('Personal')),
        ('system', _('System')),
        ('other', _('Other')),
        )

    default_features = ('tweaks', 'admins', 'janitor')

    search_loaded_table = {}
    fuzz_search_table = {}

    def __init__(self, feature, user_only=False):
        '''feature choices: tweaks, admins and janitor'''
        self.module_table = {}
        self.category_table = {}
        self.feature = feature

        for k, v in self.category_names:
            self.category_table[k] = {}

        # First import system staff
        if not user_only:
            log.info("Loading system modules for %s..." % feature)
            try:
                m = __import__('ubuntutweak.%s' % self.feature, fromlist='ubuntutweak')
                self.do_folder_import(m.__path__[0])
            except ImportError, e:
                log.error(e)

        # Second import user plugins
        user_folder = self.get_user_extension_dir(self.feature)

        log.info("Loading user extensions for %s..." % feature)
        self.do_folder_import(user_folder, mark_user=True)

    @classmethod
    def fuzz_search(cls, text):
        modules = []
        text = text.lower()
        for k, v in cls.fuzz_search_table.items():
            if text in k and v not in modules:
                modules.append(v)

        return modules

    @classmethod
    def get_user_extension_dir(cls, feature):
        user_folder = os.path.join(CONFIG_ROOT, feature)
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        package_identy_file = os.path.join(user_folder, '__init__.py')
        if not os.path.exists(package_identy_file):
            os.system("touch %s" % package_identy_file)

        return user_folder

    @classmethod
    def search_module_for_name(cls, name):
        if name in cls.search_loaded_table:
            log.info('Module "%s" has already loaded.' % name)
            return cls.search_loaded_table[name]

        for feature in cls.default_features:
            #User's at first
            user_folder = os.path.join(CONFIG_ROOT, feature)

            if not os.path.exists(user_folder):
                os.makedirs(user_folder)

            package_identy_file = os.path.join(user_folder, '__init__.py')
            if not os.path.exists(package_identy_file):
                os.system("touch %s" % package_identy_file)

            module = cls._get_module_by_name_from_folder(name, user_folder)

            if module:
                log.info('Loading module "%s" for "%s"...' % (name, feature))
                if name not in cls.search_loaded_table:
                    cls.search_loaded_table[name] = feature, module
                return feature, module

            try:
                m = __import__('ubuntutweak.%s' % feature, fromlist='ubuntutweak')
                module = cls._get_module_by_name_from_folder(name, m.__path__[0])
                if module:
                    log.info('Loading module "%s" for "%s"...' % (name, feature))
                    if name not in cls.search_loaded_table:
                        cls.search_loaded_table[name] = feature, module
                    return feature, module
            except ImportError, e:
                log.error(traceback.print_exc())

        return 'overview', None

    @classmethod
    def _get_module_by_name_from_folder(cls, name, folder):
        for path in glob.glob(os.path.join(folder, '*.py')):
            module_name = os.path.splitext(os.path.basename(path))[0]
            dirname = os.path.dirname(path)
            if folder not in sys.path:
                sys.path.insert(0, folder)
            package = __import__(module_name)
            for k, v in inspect.getmembers(package):
                if k == name and cls.is_module_active(k, v):
                    return v

    @classmethod
    def is_target_class(cls, path, klass):
        if os.path.dirname(path) not in sys.path:
            sys.path.insert(0, os.path.dirname(path))

        module_name = os.path.splitext(os.path.basename(path))[0]
        if module_name in sys.modules:
            del sys.modules[module_name]
        package = __import__(module_name)

        for k, v in inspect.getmembers(package):
            if k in ('TweakModule', 'Clip', 'proxy', 'JanitorPlugin'):
                continue
            if hasattr(v, '__utmodule__'):
                return issubclass(v, klass)

        return False

    def do_single_import(self, path, mark_user=False):
        module_name = os.path.splitext(os.path.basename(path))[0]
        log.debug("Try to load module: %s" % module_name)
        if module_name in sys.modules:
            del sys.modules[module_name]

        try:
            package = __import__(module_name)
        except Exception, e:
            Broken = create_broken_module_class(module_name)
            self.module_table[Broken.get_name()] = Broken
            self.category_table['broken'][Broken.get_name()] = Broken
            log.error("Module import error: %s", str(e))
        else:
            for k, v in inspect.getmembers(package):
                self._insert_moduel(k, v, mark_user)

    def do_folder_import(self, path, mark_user=False):
        if path not in sys.path:
            sys.path.insert(0, path)

        for f in os.listdir(path):
            full_path = os.path.join(path, f)

            if os.path.isdir(full_path) and \
                    os.path.exists(os.path.join(path, '__init__.py')):
                self.do_single_import(f, mark_user)
            elif f.endswith('.py') and f != '__init__.py':
                self.do_single_import(f, mark_user)

    def _insert_moduel(self, k, v, mark_user=False):
        if self.is_module_active(k, v):
            self.module_table[v.get_name()] = v

            if mark_user:
                v.__user_extension__ = True

            if v.get_category() not in dict(self.category_names):
                self.category_table['other'][v.get_name()] = v
            else:
                self.category_table[v.get_category()][v.get_name()] = v
            if hasattr(v, '__keywords__'):
                for attr in ('name', 'title', 'description', 'keywords'):
                    value = getattr(v, 'get_%s' % attr)()
                    self.fuzz_search_table[value.lower()] = v

    @classmethod
    def is_module_active(cls, k, v):
        try:
            if k not in ('TweakModule', 'Clip', 'JanitorPlugin', 'proxy') and \
                    hasattr(v, '__utmodule__'):
                if cls.is_supported_desktop(v.__desktop__) and \
                   cls.is_supported_distro(v.__distro__) and \
                   v.is_active():
                       return True
            return False
        except Exception, e:
            log_traceback(log)
            return False

    def get_categories(self):
        for k, v in self.category_names:
            yield k, v

    def get_modules_by_category(self, category):
        modules = self.category_table.get(category).values()
        modules.sort(module_cmp)
        return modules

    def get_module(self, name):
        return self.module_table[name]

    @classmethod
    def is_supported_desktop(cls, desktop_name):
        if desktop_name:
            return system.DESKTOP in desktop_name
        else:
            return True

    @classmethod
    def is_supported_distro(cls, distro):
        log.debug('is_supported_distro')
        if distro:
            return system.CODENAME in distro
        else:
            return True


class TweakModule(Gtk.VBox):
    __title__ = ''
    __version__ = ''
    __icon__ = ''
    __author__ = ''
    __desc__ = ''
    __desktop__ = ''
    __distro__ = ''
    __url__ = ''
    __url_title__ = _('More')
    #Identify whether it is a ubuntu tweak module
    __utmodule__ = ''
    __utactive__ = True
    __category__ = ''
    __policykit__ = ''
    __user_extension__ = False
    __keywords__ = ''

    #update use internal, and call use between modules
    __gsignals__ = {
            'update': (GObject.SignalFlags.RUN_FIRST, None, (GObject.TYPE_STRING,)),
            'call': (GObject.SignalFlags.RUN_FIRST, None, (GObject.TYPE_STRING, GObject.TYPE_STRING, GObject.TYPE_PYOBJECT)),
    }

    def __init__(self, path=None, domain='ubuntu-tweak'):
        GObject.GObject.__init__(self)

        self.scrolled_win = Gtk.ScrolledWindow()
        self.scrolled_win.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.pack_start(self.scrolled_win, True, True, 0)

        self.inner_vbox = Gtk.VBox(spacing=6)
        self.inner_vbox.set_border_width(6)
        self.scrolled_win.add_with_viewport(self.inner_vbox)
        viewport = self.scrolled_win.get_child()

#        self.alignment = Gtk.Alignment(xalign=1)
#        self.alignment.add(self.inner_vbox)
#        self.pack_start(self.alignment, False, False, 0)

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

    @classmethod
    def is_active(cls):
        return not IS_INSTALLED or cls.__utactive__

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
    def get_keywords(cls):
        keywords = [cls.__keywords__]
        for k, v in inspect.getmembers(cls):
            if k.startswith('utext'):
                keywords.append(v)
        return ' '.join(keywords)

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
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon_path)
                    pixbuf = pixbuf.scale_simple(size, size, GdkPixbuf.InterpType.BILINEAR)
                else:
                    pixbuf = icon.get_from_name(cls.__icon__, size=size)
            else:
                pixbuf = icon.get_from_list(cls.__icon__, size=size)

            return pixbuf

    @classmethod
    def get_icon(cls, size=32):
        '''Return icon path'''
        if cls.__icon__:
            if type(cls.__icon__) != list:
                if cls.__icon__.endswith('.png'):
                    icon_path = os.path.join(DATA_DIR, 'pixmaps', cls.__icon__)
                    pixbuf = Gtk.gd.pixbuf_new_from_file(icon_path)
                else:
                    pixbuf = icon.get_from_name(cls.__icon__, size=size, only_path=True)
            else:
                pixbuf = icon.get_from_list(cls.__icon__, size=size, only_path=True)

            return pixbuf

    @classmethod
    def is_user_extension(cls):
        return cls.__user_extension__

    def set_busy(self):
        if self.get_parent_window():
            self.get_parent_window().set_cursor(Gdk.Cursor.new(Gdk.CursorType.WATCH))
            self.get_toplevel().set_sensitive(False)

    def unset_busy(self):
        if self.get_parent_window():
            self.get_parent_window().set_cursor(None)
            self.get_toplevel().set_sensitive(True)


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
             " apt list file is broken.\nTry to fix by following steps:\n\n\t1."
             "Open your terminal\n\t2. Run the command to open apt list file:"
             "\n\n\t\tsudo gedit %s\n\n\t3. Edit the list to make it correctly"
             "\n\nOr you can submit the Error Message to the developer for"
             "help:" % broken_file))

        self.error_view.reparent(self.scrolled_window)
        self.ohno_image.set_from_file(os.path.join(DATA_DIR, 'pixmaps/emblem-ohno.png'))

        self.add_start(self.alignment1)

    def on_report_button_clicked(self, widget):
        open_bug_report()
