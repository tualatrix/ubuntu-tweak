import logging

from gi.repository import GObject, Gtk, WebKit
from aptsources.sourceslist import SourcesList

from ubuntutweak import system
from ubuntutweak.common.debug import log_func
from ubuntutweak.gui.gtk import set_busy, unset_busy
from ubuntutweak.utils.package import AptWorker
from ubuntutweak.utils.parser import Parser
from ubuntutweak.policykit.dbusproxy import proxy

log = logging.getLogger('apps')


class AppsPage(Gtk.ScrolledWindow):
    def __init__(self, go_back_button, forward_button):
        GObject.GObject.__init__(self)

        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)

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

    @log_func(log)
    def on_load_status_changed(self, widget, *args):
        self._go_back_button.set_sensitive(widget.can_go_back())
        self._forward_button.set_sensitive(widget.can_go_forward())

    @log_func(log)
    def on_go_back_clicked(self, widget):
        self._webview.go_back()

    @log_func(log)
    def on_go_forward_clicked(self, widget):
        self._webview.go_forward()

    def on_size_allocate(self, widget, allocation):
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

        self.load_uri('http://127.0.0.1:8000/utapp/')

        self.connect('notify::title', self.on_title_changed)

    def on_title_changed(self, *args):
        if self.get_title() and '::' in self.get_title() and self.get_property('load-status') == WebKit.LoadStatus.FINISHED:
            parameters = self.get_title().strip().split('::')
            getattr(self, parameters[0])(*parameters[1:])

    @log_func(log)
    def update_app(self, pkgname, *args):
        if pkgname != self.current_app:
            self.current_app = pkgname

        if proxy.is_package_avaiable(pkgname):
            if proxy.is_package_installed(pkgname):
                self.update_action_button(self.UNINSTALL_ACTION)
            else:
                self.update_action_button(self.INSTALL_ACTION)
        else:
            self.update_action_button(self.NOT_AVAILABLE_ACTION)

        self.update_sources();

    @log_func(log)
    def do_source_operation(self, enable_str, url, *args):
        enable = str(enable_str)

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
                $(".source-view").each(function(index) {
                    var distro_value = '';
                    console.log($(this).attr('urldata') + " is filtering codename for: ");
                    $(this).attr('distributions').split(' ').forEach(function(codename) {
                        console.log('\t' + codename);
                        if (ubuntu_codenames.contains(codename)){
                            if (system_codename == codename) {
                                distro_value = codename;
                                return false;
                            }
                        } else {
                            distro_value = codename;
                            return false;
                        };
                    });
                    if (distro_value == '') {
                        $(this).parent().hide();
                    }
                    $(this).attr('distro', distro_value);
                    console.log("Done: " + index);
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
