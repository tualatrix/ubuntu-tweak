import os
import glob
import shutil
import logging
import threading
import traceback

from defer import inline_callbacks
from collections import OrderedDict

from gi.repository import GObject, Gtk, Gdk, Pango

from ubuntutweak.gui import GuiBuilder
from ubuntutweak.gui.gtk import post_ui
from ubuntutweak.utils import icon, filesizeformat
from ubuntutweak.modules import ModuleLoader
from ubuntutweak.settings import GSetting
from ubuntutweak.common.debug import run_traceback, log_func
from ubuntutweak.common.consts import DATA_DIR
from ubuntutweak.gui.dialogs import ErrorDialog
from ubuntutweak.policykit import PK_ACTION_CLEAN
from ubuntutweak.policykit.widgets import PolkitAction

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


class CacheObject(CruftObject):
    def __init__(self, name, path, size):
        self.name = name
        self.path = path
        self.size = size

    def get_path(self):
        return self.path

    def get_size_display(self):
        return filesizeformat(self.size)

    def get_icon(self):
        return icon.guess_from_path(self.get_path())

    def is_dir(self):
        return os.path.isdir(self.path)


class JanitorPlugin(GObject.GObject):
    __title__ = ''
    __category__ = ''
    __utmodule__ = ''
    __desktop__ = ''
    __distro__ = ''
    __utactive__ = True
    __user_extension__ = False

    __gsignals__ = {
        'find_object': (GObject.SignalFlags.RUN_FIRST, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_INT)),
        'scan_finished': (GObject.SignalFlags.RUN_FIRST, None,
                          (GObject.TYPE_BOOLEAN,
                           GObject.TYPE_INT,
                           GObject.TYPE_INT)),
        'object_cleaned': (GObject.SignalFlags.RUN_FIRST, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_INT)),
        'all_cleaned': (GObject.SignalFlags.RUN_FIRST, None, (GObject.TYPE_BOOLEAN,)),
        'scan_error': (GObject.SignalFlags.RUN_FIRST, None, (GObject.TYPE_STRING,)),
        'clean_error': (GObject.SignalFlags.RUN_FIRST, None, (GObject.TYPE_STRING,)),
    }

    @classmethod
    def is_active(cls):
        return cls.__utactive__

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

    def clean_cruft(self, parent=None, cruft_list=[]):
        '''Clean all the cruft, you must emit the "cleaned" signal to tell the
        main thread your task is finished

        :param parent: the toplevel window, use for transient
        :param cruft_list: a list contains all the cruft objects to be clean
        :param rescan_handler: the handler to rescan the result, must be called
            after the clean task is done
        '''
        pass

class JanitorCachePlugin(JanitorPlugin):
    root_path = ''
    pattern = '*'
    targets = []

    def __str__(self):
        try:
            return self.__module__.split('.')[-1]
        except Exception, e:
            return "%s Plugin" % self.__title__

    @classmethod
    def is_active(cls):
        return cls.__utactive__ and os.path.exists(cls.get_path())

    def get_cruft(self):
        if self.pattern == '*':
            if self.targets:
                total_size = 0
                count = 0

                for target in self.targets:
                    new_root_path = os.path.join(self.get_path(), target)

                    if os.path.exists(new_root_path):
                        if os.path.isdir(new_root_path):
                            try:
                                size = os.popen('du -bs "%s"' % new_root_path).read().split()[0]
                            except:
                                size = 0
                        else:
                            size = os.path.getsize(new_root_path)

                        total_size += int(size)
                        count += 1

                        self.emit('find_object',
                                  CacheObject(os.path.basename(new_root_path), new_root_path, size),
                                  count)

                self.emit('scan_finished', True, count, total_size)
            else:
                self.get_cruft_by_path()
        else:
            self.get_cruft_by_glob()

    def clean_cruft(self, cruft_list=[], parent=None):
        for index, cruft in enumerate(cruft_list):
            try:
                log.debug('Cleaning...%s' % cruft.get_name())
                if cruft.is_dir():
                    shutil.rmtree(cruft.get_path())
                else:
                    os.remove(cruft.get_path())
                self.emit('object_cleaned', cruft, index + 1)
            except Exception, e:
                log.error(run_traceback(e))
                self.emit('clean_error', cruft.get_name())
                break

        self.emit('all_cleaned', True)

    def on_done(self, widget):
        widget.destroy()

    def get_cruft_by_glob(self):
        cruft_list = glob.glob('%s/%s' % (self.get_path(), self.pattern))
        cruft_list.sort()
        size = 0
        count = 0

        for full_path in cruft_list:
            current_size = os.path.getsize(full_path)
            size += current_size
            count += 1

            self.emit('find_object',
                      CacheObject(os.path.basename(full_path), full_path, current_size),
                      count)

        self.emit('scan_finished', True, len(cruft_list), size)

    @classmethod
    def get_path(cls):
        if cls.root_path.startswith('~'):
            return os.path.expanduser(cls.root_path)
        else:
            return cls.root_path

    def get_cruft_by_path(self, root_path=None):
        if root_path is None:
            root_path = self.get_path()

        try:
            count = 0
            total_size = 0
            for root, dirs, files in os.walk(root_path):
                if root == root_path and dirs:
                    dirs.sort()
                    files.sort()

                    to_deleted = dirs + files

                    for path in to_deleted:
                        full_path = os.path.join(root_path, path)

                        try:
                            size = os.popen('du -bs "%s"' % full_path).read().split()[0]
                        except:
                            size = 0
                        count += 1
                        total_size += int(size)

                        self.emit('find_object',
                                  CacheObject(path, full_path, size),
                                  count)
                else:
                    continue

            self.emit('scan_finished', True, count, total_size)
        except Exception, e:
            log.error(e)
            self.emit('scan_error', e)

    def get_summary(self, count):
        if count:
            return _('[%d] %s') % (count, self.__title__)
        else:
            return _('%s (No cache to be cleaned)') % self.__title__


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
        self._total_count = 0

        self.set_border_width(6)
        GuiBuilder.__init__(self, 'janitorpage.ui')

        self.autoscan_setting = GSetting('com.ubuntu-tweak.janitor.auto-scan')
        self.autoscan_setting.connect_notify(self.on_autoscan_button_toggled)
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

        # cancel the size request, or it will fail to resize
        # TODO why the first scan will make it fail? 
        self.janitor_view.set_size_request(self.max_janitor_view_width, -1)

    def is_auto_scan(self):
        return self.autoscan_setting.get_value()

    @log_func(log)
    def on_result_view_row_activated(self, treeview, path, column):
        iter = self.result_model.get_iter(path)
        cruft = self.result_model[iter][self.RESULT_CRUFT]

        if hasattr(cruft, 'get_path'):
            path = cruft.get_path()
            if not os.path.isdir(path):
                path = os.path.dirname(path)
            os.system("xdg-open '%s' &" % path)

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
        renderer.set_property('ellipsize', Pango.EllipsizeMode.END)
        janitor_column.pack_start(renderer, True)
        janitor_column.add_attribute(renderer, 'markup', self.JANITOR_DISPLAY)

        renderer = Gtk.CellRendererSpinner()
        janitor_column.pack_start(renderer, False)
        janitor_column.add_attribute(renderer, 'active', self.JANITOR_SPINNER_ACTIVE)
        janitor_column.add_attribute(renderer, 'pulse', self.JANITOR_SPINNER_PULSE)

        self.janitor_view.append_column(janitor_column)
        #end janitor columns

        #new result columns
        result_display_renderer = self.builder.get_object('result_display_renderer')
        result_display_renderer.set_property('ellipsize', Pango.EllipsizeMode.END)
        result_icon_renderer= self.builder.get_object('result_icon_renderer')
        self.result_column.set_cell_data_func(result_icon_renderer,
                                              self.icon_column_view_func,
                                              self.RESULT_ICON)
        #end new result columns

        auto_scan = self.autoscan_setting.get_value()
        log.info("Auto scan status: %s", auto_scan)

        self.scan_button.set_visible(not auto_scan)

        self.update_model()

        self._expand_janitor_view()

        self.hpaned1.connect('notify::position', self.on_move_handle)

    def _expand_janitor_view(self):
        self.janitor_view.expand_all()

        left_view_width = self.view_width_setting.get_value()
        log.debug("left_view_width is: %d, max_janitor_view_width is: %d" %
                  (left_view_width, self.max_janitor_view_width))

        if left_view_width:
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

    def _is_scanning_or_cleaning(self):
        for row in self.janitor_model:
            for child_row in row.iterchildren():
                if child_row[self.JANITOR_SPINNER_ACTIVE]:
                    return True
        else:
            return False

    def on_janitor_check_button_toggled(self, cell, path):
        self.result_view.show()
        self.happy_box.hide()

        iter = self.janitor_model.get_iter(path)

        if self._is_scanning_or_cleaning():
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

        if self._is_scanning_or_cleaning():
            return

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

        self.scan_tasks = list(scan_dict.items())
        self._total_count = 0
        self.result_view.show()
        self.happy_box.hide()

        self.set_busy()
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
                                                   '<b>%s</b>' % _('Scanning cruft for "%s"...') % plugin.get_title(),
                                                   None,
                                                   plugin,
                                                   None))

            self.janitor_model[plugin_iter][self.JANITOR_SPINNER_ACTIVE] = True
            self.janitor_model[plugin_iter][self.JANITOR_SPINNER_PULSE] = 0

            self._find_handler = plugin.connect('find_object', self.on_find_object, (plugin_iter, iter))
            self._scan_handler = plugin.connect('scan_finished', self.on_scan_finished, (plugin_iter, iter))
            self._error_handler = plugin.connect('scan_error', self.on_scan_error, plugin_iter)

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
                if self._total_count == 0:
                    self.result_view.hide()
                    self.happy_box.show()
                else:
                    self.result_view.show()
                    self.happy_box.hide()

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

            thread.join()

            if len(self.scan_tasks) != 0:
                log.debug("Pending scan tasks: %d" % len(self.scan_tasks))
                self.do_scan_task()
            else:
                log.debug("total_count is: %d" % self._total_count)
                if self._total_count == 0:
                    self.result_view.hide()
                    self.happy_box.show()
                else:
                    self.result_view.show()
                    self.happy_box.hide()

                self.unset_busy()

        return not finished

    @post_ui
    def on_find_object(self, plugin, cruft, count, iters):
        while Gtk.events_pending():
            Gtk.main_iteration()

        plugin_iter, result_iter = iters

        self.result_model.append(result_iter, (False,
                                               cruft.get_icon(),
                                               cruft.get_name(),
                                               cruft.get_name(),
                                               cruft.get_size_display(),
                                               plugin,
                                               cruft))

        self.result_view.expand_row(self.result_model.get_path(result_iter), True)

        # Update the janitor title
        if count:
            self.janitor_model[plugin_iter][self.JANITOR_DISPLAY] = "<b>[%d] %s</b>" % (count, plugin.get_title())
        else:
            self.janitor_model[plugin_iter][self.JANITOR_DISPLAY] = "[0] %s" % plugin.get_title()

    @post_ui
    def on_scan_finished(self, plugin, result, count, size, iters):
        plugin.disconnect(self._find_handler)
        plugin.disconnect(self._scan_handler)
        plugin.set_data('scan_finished', True)

        plugin_iter, result_iter = iters

        if count == 0:
            self.result_model.remove(result_iter)
        else:
            self.result_model[result_iter][self.RESULT_DISPLAY] = "<b>%s</b>" % plugin.get_summary(count)
            if size != 0:
                self.result_model[result_iter][self.RESULT_DESC] = "<b>%s</b>" % filesizeformat(size)

        # Update the janitor title
        self._total_count += count

        if count:
            self.janitor_model[plugin_iter][self.JANITOR_DISPLAY] = "<b>[%d] %s</b>" % (count, plugin.get_title())
            self.result_view.collapse_row(self.result_model.get_path(result_iter))
        else:
            self.janitor_model[plugin_iter][self.JANITOR_DISPLAY] = "[0] %s" % plugin.get_title()

    @post_ui
    def on_scan_error(self, plugin, error, plugin_iter):
        #TODO deal with the error
        self.janitor_model[plugin_iter][self.JANITOR_ICON] = icon.get_from_name('error', size=16)
        plugin.set_data('scan_finished', True)
        self.scan_tasks = []

    @inline_callbacks
    def on_clean_button_clicked(self, widget):
        '''plugin_dict: {plugin: {cruft: iter}}'''
        try:
            yield PolkitAction(PK_ACTION_CLEAN).do_authenticate()
        except Exception, e:
            log.debug(e)
            return

        self.plugin_to_run = 0

        self.set_busy()
        self.clean_button.set_sensitive(False)

        plugin_dict = OrderedDict()

        for row in self.result_model:
            plugin = row[self.RESULT_PLUGIN]
            cruft_dict = OrderedDict()

            for child_row in row.iterchildren():
                checked = child_row[self.RESULT_CHECK]

                if checked:
                    cruft_dict[child_row[self.RESULT_CRUFT]] =  child_row.iter

            if cruft_dict:
                plugin_dict[plugin] = cruft_dict

        self.clean_tasks = list(plugin_dict.items())

        self.do_real_clean_task()
        log.debug("All finished!")

    def do_real_clean_task(self):
        if len(self.clean_tasks) != 0:
            plugin, cruft_dict = self.clean_tasks.pop(0)
            plugin.set_data('clean_finished', False)

            for row in self.janitor_model:
                for child_row in row.iterchildren():
                    if child_row[self.JANITOR_PLUGIN] == plugin:
                        plugin_iter = child_row.iter

            log.debug("Call %s to clean cruft" % plugin)
            self._object_clean_handler = plugin.connect('object_cleaned',
                                                        self.on_plugin_object_cleaned,
                                                        (plugin_iter, cruft_dict))
            self._all_clean_handler = plugin.connect('all_cleaned', self.on_plugin_cleaned, plugin_iter)
            self._error_handler = plugin.connect('clean_error', self.on_clean_error, plugin_iter)

            t = threading.Thread(target=plugin.clean_cruft,
                                 kwargs={'cruft_list': cruft_dict.keys(),
                                         'parent': self.get_toplevel()})

            for row in self.result_model:
                if row[self.RESULT_PLUGIN] == plugin:
                    self.result_view.get_selection().select_path(row.path)
                    self.result_view.scroll_to_cell(row.path)
                    row[self.RESULT_DISPLAY] = '<b>%s</b>' % _('Cleaning cruft for "%s"...') % plugin.get_title()
                    self.result_view.expand_row(self.result_model.get_path(row.iter), True)

            self.janitor_model[plugin_iter][self.JANITOR_SPINNER_ACTIVE] = True
            self.janitor_model[plugin_iter][self.JANITOR_SPINNER_PULSE] = 0

            GObject.timeout_add(50, self._on_clean_spinner_timeout, plugin_iter, t)

            t.start()
        else:
            self.on_scan_button_clicked()
            self.unset_busy()

    def _on_clean_spinner_timeout(self, plugin_iter, thread):
        plugin = self.janitor_model[plugin_iter][self.JANITOR_PLUGIN]
        finished = plugin.get_data('clean_finished')

        self.janitor_model[plugin_iter][self.JANITOR_SPINNER_PULSE] += 1
        if finished:
            log.debug("Disconnect the cleaned signal for %s, or it will clean many times" % plugin)
            for handler in (self._object_clean_handler,
                            self._all_clean_handler,
                            self._error_handler):
                if plugin.handler_is_connected(handler):
                    plugin.disconnect(handler)

            self.janitor_model[plugin_iter][self.JANITOR_SPINNER_ACTIVE] = False

            thread.join()

            self.do_real_clean_task()

        return not finished

    @post_ui
    def on_plugin_object_cleaned(self, plugin, cruft, count, user_data):
        while Gtk.events_pending():
            Gtk.main_iteration()

        plugin_iter, cruft_dict = user_data
        self.result_model.remove(cruft_dict[cruft])

        self.janitor_model[plugin_iter][self.JANITOR_DISPLAY]
        remain = len(cruft_dict) - count

        if remain:
            self.janitor_model[plugin_iter][self.JANITOR_DISPLAY] = "<b>[%d] %s</b>" % (remain, plugin.get_title())
        else:
            self.janitor_model[plugin_iter][self.JANITOR_DISPLAY] = "[0] %s" % plugin.get_title()

    def on_plugin_cleaned(self, plugin, cleaned, plugin_iter):
        #TODO should accept the cruft_list
        plugin.set_data('clean_finished', True)
        self.janitor_model[plugin_iter][self.JANITOR_DISPLAY] = "[0] %s" % plugin.get_title()

    def on_clean_error(self, plugin, error, plugin_iter):
        #TODO response to user?
        self.janitor_model[plugin_iter][self.JANITOR_ICON] = icon.get_from_name('error', size=16)
        self.clean_tasks = []
        plugin.set_data('clean_finished', True)

    def on_autoscan_button_toggled(self, *args):
        if self.autoscan_setting.get_value():
            self.scan_button.hide()
        else:
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

        app_text = _('Apps')

        iter = self.janitor_model.append(None, (None,
                                                icon.get_from_name('gnome-app-install'),
                                                app_text,
                                                "<b><big>%s</big></b>" % app_text,
                                                None,
                                                None,
                                                None))

        for plugin in loader.get_modules_by_category('application'):
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
