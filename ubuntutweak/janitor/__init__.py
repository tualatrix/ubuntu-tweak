import threading
import logging
import traceback

from collections import OrderedDict

from gi.repository import GObject, Gtk, Gdk, Pango

from ubuntutweak.gui import GuiBuilder
from ubuntutweak.gui.gtk import post_ui
from ubuntutweak.utils import icon, filesizeformat
from ubuntutweak.modules import ModuleLoader
from ubuntutweak.settings import GSetting
from ubuntutweak.common.debug import run_traceback
from ubuntutweak.gui.dialogs import ErrorDialog

log = logging.getLogger('Janitor')

class CruftObject(object):
    def __init__(self, name, path=None, size=0):
        self.name = name
        self.path = path
        self.size = size

    def __str__(self):
        return self.get_name()

    def get_name(self):
        return self.name

    def get_size(self):
        return int(self.size)

    def get_size_display(self):
        return ''

    def get_icon(self):
        return None


class PackageObject(CruftObject):
    def __init__(self, name, package_name, size):
        self.name = name
        self.package_name = package_name
        self.size = size

    def get_size_display(self):
        return filesizeformat(self.size)

    def get_icon(self):
        return icon.get_from_name('deb')

    def get_package_name(self):
        return self.package_name


class JanitorPlugin(GObject.GObject):
    __title__ = ''
    __category__ = ''
    __utmodule__ = ''
    __desktop__ = ''
    __distro__ = ''
    __utactive__ = True
    __user_extension__ = False

    __gsignals__ = {
        'find_object': (GObject.SignalFlags.RUN_FIRST, None, (GObject.TYPE_PYOBJECT,)),
        'scan_finished': (GObject.SignalFlags.RUN_FIRST, None,
                          (GObject.TYPE_BOOLEAN,
                           GObject.TYPE_INT,
                           GObject.TYPE_INT)),
        'cleaned': (GObject.SignalFlags.RUN_FIRST, None, (GObject.TYPE_BOOLEAN,)),
        'error': (GObject.SignalFlags.RUN_FIRST, None, (GObject.TYPE_STRING,)),
    }

    @classmethod
    def get_name(cls):
        return cls.__name__

    @classmethod
    def get_title(cls):
        return cls.__title__

    @classmethod
    def get_category(cls):
        return cls.__category__

    @classmethod
    def is_user_extension(cls):
        return cls.__user_extension__

    @classmethod
    def get_pixbuf(cls):
        #TODO
        return None

    def get_cruft(self):
        return ()

    def get_summary(self, count, size):
        return self.get_title()

    def clean_cruft(self, parent, cruft_list):
        '''Clean all the cruft, you must emit the "cleaned" signal to tell the
        main thread your task is finished

        :param parent: the toplevel window, use for transient
        :param cruft_list: a list contains all the cruft objects to be clean
        :param rescan_handler: the handler to rescan the result, must be called
            after the clean task is done
        '''
        pass


class JanitorPage(Gtk.VBox, GuiBuilder):
    (JANITOR_CHECK,
     JANITOR_ICON,
     JANITOR_NAME,
     JANITOR_DISPLAY,
     JANITOR_PLUGIN,
     JANITOR_SPINNER_ACTIVE,
     JANITOR_SPINNER_PULSE) = range(7)

    (RESULT_CHECK,
     RESULT_ICON,
     RESULT_NAME,
     RESULT_DISPLAY,
     RESULT_DESC,
     RESULT_PLUGIN,
     RESULT_CRUFT) = range(7)

    max_janitor_view_width = 0

    def __init__(self):
        GObject.GObject.__init__(self)

        self.scan_tasks = []
        self.clean_tasks = []

        self.set_border_width(6)
        GuiBuilder.__init__(self, 'janitorpage.ui')

        self.autoscan_setting = GSetting('com.ubuntu-tweak.janitor.auto-scan')
        self.plugins_setting = GSetting('com.ubuntu-tweak.janitor.plugins')
        self.view_width_setting = GSetting('com.ubuntu-tweak.janitor.janitor-view-width')

        self.pack_start(self.vbox1, True, True, 0)

        self.connect('realize', self.setup_ui_tasks)
        self.janitor_view.get_selection().connect('changed', self.on_janitor_selection_changed)
        self.plugins_setting.connect_notify(self.update_model, True)
        self.show()

    def on_move_handle(self, widget, gproperty):
        log.debug("on_move_handle: %d", widget.get_property('position'))
        self.view_width_setting.set_value(widget.get_property('position'))

    def is_auto_scan(self):
        return self.autoscan_button.get_active()

    def setup_ui_tasks(self, widget):
        self.janitor_model.set_sort_column_id(self.JANITOR_NAME, Gtk.SortType.ASCENDING)

        #add janitor columns
        janitor_column = Gtk.TreeViewColumn()

        renderer = Gtk.CellRendererToggle()
        renderer.connect('toggled', self.on_janitor_check_button_toggled)
        janitor_column.pack_start(renderer, False)
        janitor_column.add_attribute(renderer, 'active', self.JANITOR_CHECK)

        self.janitor_view.append_column(janitor_column)

        janitor_column = Gtk.TreeViewColumn()

        renderer = Gtk.CellRendererPixbuf()
        janitor_column.pack_start(renderer, False)
        janitor_column.add_attribute(renderer, 'pixbuf', self.JANITOR_ICON)
        janitor_column.set_cell_data_func(renderer,
                                          self.icon_column_view_func,
                                          self.JANITOR_ICON)

        renderer = Gtk.CellRendererText()
        renderer.set_property('ellipsize', Pango.EllipsizeMode.MIDDLE)
        janitor_column.pack_start(renderer, True)
        janitor_column.add_attribute(renderer, 'markup', self.JANITOR_DISPLAY)

        renderer = Gtk.CellRendererSpinner()
        janitor_column.pack_start(renderer, False)
        janitor_column.add_attribute(renderer, 'active', self.JANITOR_SPINNER_ACTIVE)
        janitor_column.add_attribute(renderer, 'pulse', self.JANITOR_SPINNER_PULSE)

        self.janitor_view.append_column(janitor_column)
        #end janitor columns

        #add result columns
        result_column = Gtk.TreeViewColumn()

        renderer = Gtk.CellRendererToggle()
        renderer.connect('toggled', self.on_result_check_renderer_toggled)
        result_column.pack_start(renderer, False)
        result_column.add_attribute(renderer, 'active', self.RESULT_CHECK)

        renderer = Gtk.CellRendererPixbuf()
        result_column.pack_start(renderer, False)
        result_column.add_attribute(renderer, 'pixbuf', self.RESULT_ICON)
        result_column.set_cell_data_func(renderer,
                                         self.icon_column_view_func,
                                         self.RESULT_ICON)

        renderer = Gtk.CellRendererText()
        renderer.set_property('ellipsize', Pango.EllipsizeMode.END)
        result_column.pack_start(renderer, True)
        result_column.add_attribute(renderer, 'markup', self.RESULT_DISPLAY)

        renderer = Gtk.CellRendererText()
        result_column.pack_start(renderer, False)
        result_column.add_attribute(renderer, 'text', self.RESULT_DESC)

        self.result_view.append_column(result_column)
        #end result columns

        auto_scan = self.autoscan_setting.get_value()
        log.info("Auto scan status: %s", auto_scan)

        self.scan_button.set_visible(not auto_scan)
        self.autoscan_button.set_active(auto_scan)

        self.update_model()

        self._expand_janitor_view()

        self.hpaned1.connect('notify::position', self.on_move_handle)

    def _expand_janitor_view(self):
        self.janitor_view.expand_all()

        left_view_width = self.view_width_setting.get_value()

        if left_view_width:
            log.debug("left_view_width is: %d", left_view_width)
            self.janitor_view.set_size_request(left_view_width, -1)
        elif self.max_janitor_view_width:
            self.janitor_view.set_size_request(self.max_janitor_view_width, -1)

    def set_busy(self):
        self.get_parent_window().set_cursor(Gdk.Cursor.new(Gdk.CursorType.WATCH))

    def unset_busy(self):
        self.get_parent_window().set_cursor(None)

    def on_janitor_selection_changed(self, selection):
        model, iter = selection.get_selected()
        if iter:
            if self.janitor_model.iter_has_child(iter):
                iter = self.janitor_model.iter_children(iter)

            plugin = model[iter][self.JANITOR_PLUGIN]

            for row in self.result_model:
                if row[self.RESULT_PLUGIN] == plugin:
                    self.result_view.get_selection().select_path(row.path)
                    self.result_view.scroll_to_cell(row.path)

    def on_janitor_check_button_toggled(self, cell, path):
        iter = self.janitor_model.get_iter(path)

        for row in self.janitor_model:
            for child_row in row.iterchildren():
                if child_row[self.JANITOR_SPINNER_ACTIVE]:
                    return

        checked = not self.janitor_model[iter][self.JANITOR_CHECK]

        if self.janitor_model.iter_has_child(iter):
            child_iter = self.janitor_model.iter_children(iter)
            while child_iter:
                self.janitor_model[child_iter][self.JANITOR_CHECK] = checked

                child_iter = self.janitor_model.iter_next(child_iter)

        self.janitor_model[iter][self.JANITOR_CHECK] = checked

        self._check_child_is_all_the_same(self.janitor_model, iter,
                                         self.JANITOR_CHECK, checked)

        if self.is_auto_scan():
            self._auto_scan_cruft(iter, checked)

    def _update_clean_button_sensitive(self):
        self.clean_button.set_sensitive(False)

        for row in self.result_model:
            for child_row in row.iterchildren():
                if child_row[self.RESULT_CHECK]:
                    self.clean_button.set_sensitive(True)
                    break

    def on_result_check_renderer_toggled(self, cell, path):
        iter = self.result_model.get_iter(path)
        checked = self.result_model[iter][self.RESULT_CHECK]

        if self.result_model.iter_has_child(iter):
            child_iter = self.result_model.iter_children(iter)
            while child_iter:
                self.result_model[child_iter][self.RESULT_CHECK] = not checked

                child_iter = self.result_model.iter_next(child_iter)

        self.result_model[iter][self.RESULT_CHECK] = not checked

        self._check_child_is_all_the_same(self.result_model, iter,
                                         self.RESULT_CHECK, not checked)

        self._update_clean_button_sensitive()

    def _check_child_is_all_the_same(self, model, iter, column_id, status):
        iter = model.iter_parent(iter)

        if iter:
            child_iter = model.iter_children(iter)

            while child_iter:
                if status != model[child_iter][column_id]:
                    model[iter][column_id] = False
                    break
                child_iter = model.iter_next(child_iter)
            else:
                model[iter][column_id] = status

    def on_scan_button_clicked(self, widget=None):
        self.result_model.clear()
        self.clean_button.set_sensitive(False)

        scan_dict = OrderedDict()

        for row in self.janitor_model:
            for child_row in row.iterchildren():
                checked = child_row[self.JANITOR_CHECK]

                scan_dict[child_row.iter] = checked

        self.set_busy()
        self.scan_tasks = list(scan_dict.items())
        self.do_scan_task()

    def _auto_scan_cruft(self, iter, checked):
        self.set_busy()

        scan_dict = OrderedDict()

        if self.janitor_model.iter_has_child(iter):
            log.info('Scan cruft for all plugins')
            #Scan cruft for children
            child_iter = self.janitor_model.iter_children(iter)

            while child_iter:
                scan_dict[child_iter] = checked
                child_iter = self.janitor_model.iter_next(child_iter)
        else:
            scan_dict[iter] = checked

        self.scan_tasks = list(scan_dict.items())

        for plugin_iter, checked in self.scan_tasks:
            plugin = self.janitor_model[plugin_iter][self.JANITOR_PLUGIN]

            for row in self.result_model:
                if row[self.RESULT_PLUGIN] == plugin:
                    self.result_model.remove(row.iter)

        self.do_scan_task()

    def do_scan_task(self):
        plugin_iter, checked = self.scan_tasks.pop(0)

        plugin = self.janitor_model[plugin_iter][self.JANITOR_PLUGIN]
        plugin.set_data('scan_finished', False)

        log.debug("do_scan_task for %s for status: %s" % (plugin, checked))

        if checked:
            log.info('Scan cruft for plugin: %s' % plugin.get_name())

            iter = self.result_model.append(None, (None,
                                                   None,
                                                   plugin.get_title(),
                                                   "<b>%s</b>" % plugin.get_title(),
                                                   None,
                                                   plugin,
                                                   None))

            self.janitor_model[plugin_iter][self.JANITOR_SPINNER_ACTIVE] = True
            self.janitor_model[plugin_iter][self.JANITOR_SPINNER_PULSE] = 0

            self._find_handler = plugin.connect('find_object', self.on_find_object, iter)
            self._scan_handler = plugin.connect('scan_finished', self.on_scan_finished, iter)
            self._error_handler = plugin.connect('error', self.on_scan_error, plugin_iter)

            t = threading.Thread(target=plugin.get_cruft)
            GObject.timeout_add(50, self._on_spinner_timeout, plugin_iter, t)

            t.start()
        else:
            # Update the janitor title
            for row in self.janitor_model:
                for child_row in row.iterchildren():
                    if child_row[self.JANITOR_PLUGIN] == plugin:
                        child_row[self.JANITOR_DISPLAY] = plugin.get_title()

            if self.scan_tasks:
                self.do_scan_task()
            else:
                self.unset_busy()

    def _on_spinner_timeout(self, plugin_iter, thread):
        plugin = self.janitor_model[plugin_iter][self.JANITOR_PLUGIN]
        finished = plugin.get_data('scan_finished')

        self.janitor_model[plugin_iter][self.JANITOR_SPINNER_PULSE] += 1

        if finished:
            for handler in (self._find_handler, self._scan_handler):
                if plugin.handler_is_connected(handler):
                    log.debug("Disconnect the cleaned signal, or it will clean many times")
                    plugin.disconnect(handler)

            self.janitor_model[plugin_iter][self.JANITOR_SPINNER_ACTIVE] = False

            for view in (self.janitor_view, self.result_view):
                view.hide()
                view.show()
            thread.join()

            if len(self.scan_tasks) != 0:
                self.do_scan_task()
            else:
                self.unset_busy()

        return not finished

    @post_ui
    def on_find_object(self, plugin, cruft, result_iter):
        while Gtk.events_pending():
            Gtk.main_iteration()

        self.result_model.append(result_iter, (False,
                                               cruft.get_icon(),
                                               cruft.get_name(),
                                               cruft.get_name(),
                                               cruft.get_size_display(),
                                               plugin,
                                               cruft))

        self.result_view.expand_row(self.result_model.get_path(result_iter), True)

    @post_ui
    def on_scan_finished(self, plugin, result, count, size, result_iter):
        plugin.disconnect(self._find_handler)
        plugin.disconnect(self._scan_handler)
        plugin.set_data('scan_finished', True)

        if count == 0:
            self.result_model.remove(result_iter)
        else:
            self.result_model[result_iter][self.RESULT_DISPLAY] = "<b>%s</b>" % plugin.get_summary(count, size)

        # Update the janitor title
        for row in self.janitor_model:
            for child_row in row.iterchildren():
                if child_row[self.JANITOR_PLUGIN] == plugin:
                    if count:
                        child_row[self.JANITOR_DISPLAY] = "<b>%s (%d) </b>" % (plugin.get_title(), count)
                    else:
                        child_row[self.JANITOR_DISPLAY] = "%s (%d)" % (plugin.get_title(), count)

    @post_ui
    def on_scan_error(self, plugin, error, plugin_iter):
        #TODO deal with the error
        self.janitor_model[plugin_iter][self.JANITOR_ICON] = icon.get_from_name('error', size=16)
        plugin.set_data('scan_finished', True)
        self.scan_tasks = []

    def on_clean_button_clicked(self, widget):
        self.plugin_to_run = 0

        plugin_dict = OrderedDict()

        for row in self.result_model:
            plugin = row[self.RESULT_PLUGIN]
            cruft_list = []

            for child_row in row.iterchildren():
                checked = child_row[self.RESULT_CHECK]

                if checked:
                    cruft = child_row[self.RESULT_CRUFT]
                    cruft_list.append(cruft)

            if cruft_list:
                plugin_dict[plugin] = cruft_list

        self.clean_tasks = list(plugin_dict.items())

        self.do_real_clean_task()
        log.debug("All finished!")

    def do_real_clean_task(self):
        plugin, cruft_list = self.clean_tasks.pop(0)

        log.debug("Call %s to clean cruft" % plugin)
        self._plugin_handler = plugin.connect('cleaned', self.on_plugin_cleaned)
        self._error_handler = plugin.connect('error', self.on_clean_error)
        plugin.clean_cruft(self.get_toplevel(), cruft_list)

    def on_plugin_cleaned(self, plugin, cleaned):
        for handler in (self._plugin_handler, self._error_handler):
            if plugin.handler_is_connected(handler):
                log.debug("Disconnect the cleaned signal, or it will clean many times")
                plugin.disconnect(handler)

        if len(self.clean_tasks) == 0:
            self.on_scan_button_clicked()
        else:
            GObject.timeout_add(300, self.do_real_clean_task)

    def on_clean_error(self, plugin, error):
        self.clean_tasks = []

    def on_autoscan_button_toggled(self, widget):
        if widget.get_active():
            self.autoscan_setting.set_value(True)
            self.scan_button.hide()
        else:
            self.autoscan_setting.set_value(False)
            self.scan_button.show()

    def icon_column_view_func(self, cell_layout, renderer, model, iter, id):
        if model[iter][id] == None:
            renderer.set_property("visible", False)
        else:
            renderer.set_property("visible", True)

    def update_model(self, a=None, b=None, expand=False):
        self.janitor_model.clear()
        self.result_model.clear()
        size_list = []

        loader = ModuleLoader('janitor')
        plugin_to_load = self.plugins_setting.get_value()

        system_text = _('System')
        iter = self.janitor_model.append(None, (None,
                                                icon.get_from_name('distributor-logo'),
                                                system_text,
                                                "<b><big>%s</big></b>" % system_text,
                                                None,
                                                None,
                                                None))

        for plugin in loader.get_modules_by_category('system'):
            if plugin.is_user_extension() and plugin.get_name() not in plugin_to_load:
                log.debug("User extension: %s not in setting to load" % plugin.get_name())
                continue
            size_list.append(Gtk.Label(label=plugin.get_title()).get_layout().get_pixel_size()[0])
            self.janitor_model.append(iter, (False,
                                             None,
                                             plugin.get_title(),
                                             plugin.get_title(),
                                             plugin(),
                                             None,
                                             None))

        personal_text = _('Personal')

        iter = self.janitor_model.append(None, (None,
                                                icon.get_from_name('system-users'),
                                                personal_text,
                                                "<b><big>%s</big></b>" % personal_text,
                                                None,
                                                None,
                                                None))

        for plugin in loader.get_modules_by_category('personal'):
            if plugin.is_user_extension() and plugin.get_name() not in plugin_to_load:
                log.debug("User extension: %s not in setting to load" % plugin.get_name())
                continue
            size_list.append(Gtk.Label(label=plugin.get_title()).get_layout().get_pixel_size()[0])
            self.janitor_model.append(iter, (False,
                                             None,
                                             plugin.get_title(),
                                             plugin.get_title(),
                                             plugin(),
                                             None,
                                             None))
        if size_list:
            self.max_janitor_view_width = max(size_list) + 80

        if expand:
            self._expand_janitor_view()
