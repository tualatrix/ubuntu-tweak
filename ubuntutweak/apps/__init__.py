import logging

from xdg.DesktopEntry import DesktopEntry
from gi.repository import GObject, Gtk, WebKit

from ubuntutweak.common.debug import log_func
from ubuntutweak.gui.gtk import post_ui, set_busy, unset_busy
from ubuntutweak.utils.package import AptWorker
from ubuntutweak.utils.parser import Parser

log = logging.getLogger('apps')

class PackageInfo:
    DESKTOP_DIR = '/usr/share/app-install/desktop/'

    def __init__(self, name):
        self.name = name
        self.pkg = AptWorker.get_cache()[name]
        self.desktopentry = DesktopEntry(self.DESKTOP_DIR + name + '.desktop')

    def check_installed(self):
        return self.pkg.isInstalled

    def get_comment(self):
        return self.desktopentry.getComment()

    def get_name(self):
        appname = self.desktopentry.getName()
        if appname == '':
            return self.name.title()

        return appname

    def get_version(self):
        try:
            return self.pkg.versions[0].version
        except:
            return ''


class AppsPage(Gtk.ScrolledWindow):
    def __init__(self):
        GObject.GObject.__init__(self)

        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)

        self._webview = AppsWebView()
        self.add(self._webview)

        self._webview.connect('size-allocate', self.on_size_allocate)

        self.show_all()

    def on_size_allocate(self, widget, allocation):
        log.debug("The page size: %dx%d", widget.get_allocation().width, widget.get_allocation().height)
        height = widget.get_allocation().height

        self._webview.execute_script('$(".container").css("height", "%dpx");' % (height - 16))
        self._webview.execute_script('$(".sidebar").css("height", "%dpx");' % height)

#        self._webview.execute_script('''
#                                    var width = %d - $(".sidebar").width() - 17;
#                                    console.log("the width is: " + width);
#                                    $(".content").width(width);
#                                    ''' % width)


class AppsWebView(WebKit.WebView):
    current_app = None

    def __init__(self):
        GObject.GObject.__init__(self)

        self.load_uri('http://127.0.0.1:8000/utapp/')

        self.connect('notify::title', self.on_title_changed)

    def on_title_changed(self, *args):
        if ':' in self.get_title():
            parameters = self.get_title().strip().split(':')
            getattr(self, parameters[0])(parameters[1])

    @log_func(log)
    def update_app(self, pkgname):
        if pkgname != self.current_app:
            self.current_app = pkgname
        try:
            package = PackageInfo(pkgname)
            is_installed = package.check_installed()

            if is_installed:
                self._update_install_button(_('Installed'))
            else:
                self._update_install_button(_('Install'))
        except Exception, e:
            log.error(e)
            self._update_install_button(_('Not avaiable'), disabled=True)

    @log_func(log)
    def install_app(self, pkgname):
        set_busy(self)
        worker = AptWorker(self.get_toplevel(),
                           finish_handler=self.on_package_work_finished,
                           data={'parent': self})
        worker.install_packages([pkgname])

        self._update_install_button(_('Installing'))

    @log_func(log)
    def _update_install_button(self, text, disabled=False):
        self.execute_script('$(".install-button")[0].innerHTML = "%s";' % text);
        if disabled:
            self.execute_script('$(".install-button").attr("disabled", "disabled")');
        else:
            self.execute_script('$(".install-button").removeAttr("disabled")');

    def reset_install_button(self):
        self.update_app(self.current_app)

    @log_func(log)
    def on_package_work_finished(self, transaction, status, kwargs):
        parent = kwargs['parent']
        AptWorker.update_apt_cache(init=True)
        unset_busy(parent)
        self.reset_install_button()

class CateParser(Parser):
    def __init__(self, path):
        Parser.__init__(self, path, 'slug')

    def get_name(self, key):
        return self.get_by_lang(key, 'name')

    def get_id(self, key):
        return self[key]['id']


class CategoryView(Gtk.TreeView):
    (CATE_ID,
     CATE_NAME,
     CATE_DISPLAY) = range(3)

    def __init__(self, path):
        GObject.GObject.__init__(self)

        self.path = path
        self._status = None
        self.parser = None

        self.set_headers_visible(False)
        self.set_rules_hint(True)
        self.model = self._create_model()
        self.set_model(self.model)
        self._add_columns()

    def _create_model(self):
        '''The model is icon, title and the list reference'''
        model = Gtk.TreeStore(GObject.TYPE_INT,
                              GObject.TYPE_STRING,
                              GObject.TYPE_STRING)

        return model

    def _add_columns(self):
        column = Gtk.TreeViewColumn(_('Category'))

        renderer = Gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.set_sort_column_id(self.CATE_NAME)
        column.add_attribute(renderer, 'markup', self.CATE_DISPLAY)
        self.append_column(column)

    def set_status_from_view(self, view):
        self._status = view.get_status()

    def update_cate_model(self):
        self.model.clear()
        self.parser = CateParser(self.path)

        self.pre_update_cate_model()

        iter = self.model.append(None, (0,
                                        'all',
                                        _('All')))

        for slug in self.get_cate_items():
            child_iter = self.model.append(iter)
            id = self.parser.get_id(slug)
            name = self.parser.get_name(slug)
            display = name

            if self._status:
                self._status.load_category_from_parser(self.parser)
                count = self._status.get_cate_unread_count(id)
                if count:
                    display = '<b>%s (%d)</b>' % (name, count)

            log.debug("Insert category model: id: %s"
                    "\tname: %s"
                    "\tdisplay: %s" % (id, name, display))
            self.model.set(child_iter, 
                           self.CATE_ID, id,
                           self.CATE_NAME, name,
                           self.CATE_DISPLAY, display)

    def get_cate_items(self):
        OTHER = u'other'
        keys = self.parser.keys()
        keys.sort()
        if OTHER in keys:
            keys.remove(OTHER)
            keys.append(OTHER)
        return keys

    def update_selected_item(self):
        model, iter = self.get_selection().get_selected()

        if iter:
            id = model[iter][self.CATE_ID]
            if id <= 0:
                return True

            name = model[iter][self.CATE_NAME]

            count = self._status.get_cate_unread_count(id)
            if count:
                model[iter][self.CATE_DISPLAY] = '<b>%s (%d)</b>' % (name, count)
            else:
                model[iter][self.CATE_DISPLAY] = name
