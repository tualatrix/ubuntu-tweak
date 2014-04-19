import os
import json
import random
import logging
import webbrowser

from gi.repository import GObject, Gtk, WebKit, Soup
from gi.repository import Notify
from aptsources.sourceslist import SourcesList

from ubuntutweak import system
from ubuntutweak import __version__
from ubuntutweak.common.consts import IS_TESTING, LANG
from ubuntutweak.common.debug import log_func
from ubuntutweak.common.consts import CONFIG_ROOT
from ubuntutweak.gui.gtk import set_busy, unset_busy
from ubuntutweak.utils.package import AptWorker
from ubuntutweak.utils.parser import Parser
from ubuntutweak.utils import ppa
from ubuntutweak.policykit.dbusproxy import proxy

log = logging.getLogger('apps')


class AppsPage(Gtk.ScrolledWindow):
    is_loaded = False

    __gsignals__ = {
        'loaded': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, go_back_button, forward_button):
        GObject.GObject.__init__(self)

        self._go_back_button = go_back_button
        self._forward_button = forward_button
        self._webview = AppsWebView()
        self.add(self._webview)

        self._webview.connect('size-allocate', self.on_size_allocate)
        self._webview.connect('notify::load-status', self.on_load_status_changed)

        self.show_all()

    @log_func(log)
    def set_web_buttons_active(self, active):
        if active:
            self._go_back_handle_id = self._go_back_button.connect('clicked', self.on_go_back_clicked)
            self._forward_handle_id = self._forward_button.connect('clicked', self.on_go_forward_clicked)
        else:
            self._go_back_button.disconnect(self._go_back_handle_id)
            self._forward_button.disconnect(self._forward_handle_id)
        self.on_load_status_changed(self._webview)

    @log_func(log)
    def on_load_status_changed(self, widget, *args):
        if widget.get_property('load-status') == WebKit.LoadStatus.FINISHED:
            self._go_back_button.set_sensitive(widget.can_go_back())
            self._forward_button.set_sensitive(widget.can_go_forward())
            self.on_size_allocate(widget)
            # TODO enable when it will not crash
            # self._webview.save_cache()
            if self.is_loaded == False:
                self.is_loaded = True
                self.emit('loaded')

    def load(self):
        self._webview.load_uri('http://ubuntu-tweak.com/utapp/')

    @log_func(log)
    def on_go_back_clicked(self, widget):
        self._webview.go_back()

    @log_func(log)
    def on_go_forward_clicked(self, widget):
        self._webview.go_forward()

    def on_size_allocate(self, widget, allocation=None):
        if widget.get_property('load-status') == WebKit.LoadStatus.FINISHED:
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

    (INSTALL_ACTION,
     UNINSTALL_ACTION,
     UPDATE_ACTION,
     INSTALLING_ACTION,
     UNINSTALLING_ACTION,
     UPDATING_ACTION,
     NOT_AVAILABLE_ACTION) = range(7)

    action_text_dict = {
        INSTALL_ACTION: _('Install'),
        UNINSTALL_ACTION: _('Uninstall'),
        UPDATE_ACTION: _('Update'),
        INSTALLING_ACTION: _('Installing'),
        UNINSTALLING_ACTION: _('Uninstalling'),
        UPDATING_ACTION: _('Updating'),
        NOT_AVAILABLE_ACTION: _('Not Available')
    }

    def __init__(self):
        GObject.GObject.__init__(self)

        self.get_settings().set_property('enable-default-context-menu', False)
        self.get_settings().set_property('enable-plugins', False)

        # TODO enable when it will not crash
        # self.setup_features()
        self.setup_user_agent()

        self.connect('notify::title', self.on_title_changed)
        self.connect('new-window-policy-decision-requested', self.on_window)

    def setup_features(self):
        try:
            session = WebKit.get_default_session()
            session.connect('request-queued', self.on_session_request_queued)

            cookie = Soup.CookieJarText(filename=os.path.join(CONFIG_ROOT, 'cookies'))
            session.add_feature(cookie)

            self._cache = Soup.Cache(cache_dir=os.path.join(CONFIG_ROOT, 'cache'),
                                     cache_type=Soup.CacheType.SHARED)
            session.add_feature(self._cache)
            self._cache.set_max_size(10 * 1024 * 1024)
            self._cache.load()
        except Exception, e:
            log.error("setup_features failed with %s" % e)

    def on_session_request_queued(self, session, message):
        message.request_headers.replace('Accept-language', LANG)

    @log_func(log)
    def save_cache(self):
        if hasattr(self, '_cache'):
            self._cache.flush()
            self._cache.dump()

    def setup_user_agent(self):
        user_agent = 'Mozilla/5.0 (X11; Linux %(arch)s) Chrome/%(version)s-%(codename)s' % {'arch': os.uname()[-1],
                          'version': __version__,
                          'codename': system.CODENAME}
        if IS_TESTING:
            user_agent = user_agent + '-beta'
        self.get_settings().set_property('user-agent', user_agent)

    @log_func(log)
    def on_window(self, webview, frame, request, *args):
        webbrowser.open_new_tab(request.get_uri())

    def on_title_changed(self, *args):
        if self.get_title() and '::' in self.get_title() and self.get_property('load-status') == WebKit.LoadStatus.FINISHED:
            parameters = self.get_title().strip().split('::')
            if hasattr(self, parameters[0]):
                getattr(self, parameters[0])(*parameters[1:])

    @log_func(log)
    def initialize_apps(self, apps_json, *args):
        apps = json.loads(apps_json)
        for package in apps.keys():
            apps[package] = proxy.is_package_installed(package)

        self.execute_script('''
                            var apps_dict = %s;
                            Utapp.get("router.appsController").content.forEach(function(app) {
                            app.set('isInstalled', apps_dict[app.package]);
                            });''' % json.dumps(apps))

    @log_func(log)
    def update_app(self, pkgname, *args):
        if pkgname != self.current_app:
            self.current_app = pkgname

        if proxy.is_package_avaiable(pkgname):
            if proxy.is_package_installed(pkgname):
                self.execute_script('Utapp.get("router.appController").currentApp.set("isInstalled", true);');
                self.update_action_button(self.UNINSTALL_ACTION)
            else:
                self.execute_script('Utapp.get("router.appController").currentApp.set("isInstalled", false);');
                self.update_action_button(self.INSTALL_ACTION)
        else:
            self.update_action_button(self.NOT_AVAILABLE_ACTION)

        self.update_sources();

    @log_func(log)
    def do_source_operation(self, enable_str, source_json, *args):
        enable = int(enable_str)
        source = json.loads(source_json)
        distro = source['distro_value']
        log.debug("Enable? %s for source: %s for distro: %s" % (enable, source['name'], distro))

        if ppa.is_ppa(source['url']):
            file_name = '%s-%s' % (ppa.get_source_file_name(source['url']), distro)
        else:
            file_name = source['slug']

        # TODO these kinds of source should never be featured
        if not source['component'] and distro:
            distro = distro + '/'
        elif not source['component'] and not distro:
            distro = './'

        try:
            result = proxy.set_separated_entry(source['url'], distro, source['component'],
                                               source['summary'], enable, file_name)
            log.debug("Enable source: %s result: %s" % (source['name'], result))
            if source['key']:
                proxy.add_apt_key_from_content(source['key'])

            if result == 'enabled':
                notify = Notify.Notification(summary=_('New source has been enabled'),
                                             body=_('"%s" is enabled now, Please click the update button to update %s') % (source['name'], self.current_app))
                notify.set_property('icon-name', 'ubuntu-tweak')
                notify.set_hint_string("x-canonical-append", "true")
                notify.show()

                self.update_action_button(self.UPDATE_ACTION)
        except Exception, e:
            log.error(e)
            self.update_sources()

    @log_func(log)
    def do_action_for_app(self, pkgname, action_id, *args):
        action_id = int(action_id)

        if action_id == self.INSTALL_ACTION:
            set_busy(self)
            worker = AptWorker(self.get_toplevel(),
                               finish_handler=self.on_package_work_finished,
                               data={'parent': self})
            worker.install_packages([pkgname])

            self.update_action_button(self.INSTALLING_ACTION)
        elif action_id == self.UNINSTALL_ACTION:
            set_busy(self)
            worker = AptWorker(self.get_toplevel(),
                               finish_handler=self.on_package_work_finished,
                               data={'parent': self})
            worker.remove_packages([pkgname])

            self.update_action_button(self.UNINSTALLING_ACTION)
        elif action_id == self.UPDATE_ACTION:
            set_busy(self)
            worker = AptWorker(self.get_toplevel(),
                               finish_handler=self.on_update_work_finished,
                               data={'parent': self})
            worker.update_cache()
            self.update_action_button(self.UPDATING_ACTION)

    @log_func(log)
    def update_action_button(self, action_id, disabled=False):
        text = self.action_text_dict[action_id]

        self.execute_script('$(".install-button")[0].innerHTML = "%s";' % text);
        self.execute_script('$(".install-button").attr("action-id", "%d")' % action_id);

        if action_id == self.NOT_AVAILABLE_ACTION:
            self.execute_script('$(".install-button").attr("disabled", "disabled")');
        else:
            self.execute_script('$(".install-button").removeAttr("disabled")');

    @log_func(log)
    def update_sources(self):
        #First hide the item not supported by current distribution
        self.execute_script('''
                var system_codename = "%s";
                var ubuntu_codenames = %s;
                console.log("Updating source for system: " + system_codename + ', codenames: ' + ubuntu_codenames);
                var appController = Utapp.get('router.appController');
                appController.currentApp.sources.forEach(function(source) {
                    var distro_value = '';
                    console.log(source.name + " is filtering codename for: ");
                    source.distros.forEach(function(distro) {
                        var codename = distro.codename;
                        console.log('\t' + codename);
                        if (ubuntu_codenames.contains(codename)){
                            console.log('\t\tThis is ubuntu codename');
                            if (system_codename == codename) {
                                console.log('\t\tCodename match!');
                                distro_value = codename;
                                return false;
                            }
                        } else {
                            console.log("\t\tThis isn't Ubuntu codename!");
                            distro_value = codename;
                            return false;
                        };
                    });
                    if (distro_value == '') {
                        console.log('Set source: ' + source.name + ' to hide');
                        source.set('is_available', false);
                    } else {
                        source.set('distro_value', distro_value);
                    }
                });
                ''' % (system.CODENAME, list(system.UBUNTU_CODENAMES)));

        enabled_list = []

        for source in SourcesList().list:
            if source.type == 'deb' and not source.disabled:
                enabled_list.append(source.uri)

        self.execute_script('''
                var enabled_list = %s;
                $(".source-view").each(function(index) {
                    if (enabled_list.contains($(this).attr('urldata')))
                    {
                        this.checked = true;
                    }
                    console.log(index + ': ' + $(this).attr('urldata'));
                });
                ''' % enabled_list);

    def reset_install_button(self):
        self.update_app(self.current_app)

    @log_func(log)
    def on_update_work_finished(self, transaction, status, kwargs):
        parent = kwargs['parent']
        proxy.update_apt_cache(True)
        if proxy.is_package_upgradable(self.current_app) or \
           (not proxy.is_package_installed(self.current_app) and \
            proxy.is_package_avaiable(self.current_app)):
            worker = AptWorker(self.get_toplevel(),
                               finish_handler=self.on_package_work_finished,
                               data={'parent': self})
            worker.install_packages([self.current_app])
        else:
            unset_busy(parent)
            self.reset_install_button()

    @log_func(log)
    def on_package_work_finished(self, transaction, status, kwargs):
        parent = kwargs['parent']
        proxy.update_apt_cache(True)
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
