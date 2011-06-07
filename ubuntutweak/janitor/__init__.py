import logging

import apt
import gobject
from gi.repository import Gtk, Pango

from ubuntutweak.gui import GuiBuilder
from ubuntutweak.utils import icon
from ubuntutweak.modules import ModuleLoader
from ubuntutweak.settings import GSetting

log = logging.getLogger('Janitor')


class JanitorPlugin(object):
    __title__ = ''
    __category__ = ''
    __utmodule__ = ''
    __utactive__ = True

    @classmethod
    def get_name(cls):
        return cls.__name__

    @classmethod
    def get_title(cls):
        return cls.__title__

    @classmethod
    def get_category(cls):
        return cls.__category__


class JanitorPage(Gtk.VBox, GuiBuilder):
    (COLUMN_CHECK,
     COLUMN_PIXBUF,
     COLUMN_NAME) = range(3)

    def __init__(self):
        gobject.GObject.__init__(self)
        self.set_border_width(6)
        GuiBuilder.__init__(self, 'janitorpage.ui')

        self.loader = ModuleLoader('janitor')
        self.autoscan_setting = GSetting('com.ubuntu-tweak.tweak.auto-scan')

        self.pack_start(self.vbox1, True, True, 0)

        self.connect('realize', self.setup_ui_tasks)
        self.show()

    def is_auto_scan(self):
        return self.autoscan_button.get_active()

    def setup_ui_tasks(self, widget):
        icon_renderer = self.get_object('icon_renderer')
        self.janitor_column.set_cell_data_func(icon_renderer, self.logo_column_view_func)

        auto_scan = self.autoscan_setting.get_value()
        log.info("Auto scan status: %s", auto_scan)

        self.scan_button.set_visible(not auto_scan)
        self.autoscan_button.set_active(auto_scan)

        self.update_model()
        self.janitor_treeview.expand_all()

    def on_check_renderer_toggled(self, cell, path):
        iter = self.janitor_model.get_iter(path)
        checked = self.janitor_model.get_value(iter, self.COLUMN_CHECK)

        if self.janitor_model.iter_has_child(iter):
            child_iter = self.janitor_model.iter_children(iter)
            while child_iter:
                self.janitor_model.set_value(child_iter, self.COLUMN_CHECK, not checked)

                child_iter = self.janitor_model.iter_next(child_iter)

        self.janitor_model.set_value(iter, self.COLUMN_CHECK, not checked)

        if self.is_auto_scan():
            self.scan_cruft()

        self.check_child_is_all_the_same(iter, not checked)

    def check_child_is_all_the_same(self, iter, status):
        iter = self.janitor_model.iter_parent(iter)

        if iter:
            child_iter = self.janitor_model.iter_children(iter)

            while child_iter:
                if status != self.janitor_model.get_value(child_iter, self.COLUMN_CHECK):
                    self.janitor_model.set_value(iter, self.COLUMN_CHECK, False)
                    break
                child_iter = self.janitor_model.iter_next(child_iter)
            else:
                self.janitor_model.set_value(iter, self.COLUMN_CHECK, status)

    def scan_cruft(self):
        log.info('Scan cruft')

    def on_autoscan_button_toggled(self, widget):
        if widget.get_active():
            self.autoscan_setting.set_value(True)
            self.scan_button.hide()
        else:
            self.autoscan_setting.set_value(False)
            self.scan_button.show()

    def logo_column_view_func(self, cell_layout, renderer, model, iter, func):
        pixbuf = model.get_value(iter, 1)
        if pixbuf == None:
            renderer.set_property("visible", False)
        else:
            renderer.set_property("visible", True)

    def update_model(self):
        iter = self.janitor_model.append(None, (None,
                                                icon.get_from_name('ubuntu-logo', size=32),
                                                _('System')))

        for plugin in self.loader.get_modules_by_category('system'):
            self.janitor_model.append(iter, (False, None, plugin.get_title()))

        iter = self.janitor_model.append(None, (None,
                                                icon.get_from_name('system-users', size=32),
                                                _('Personal')))

        for plugin in self.loader.get_modules_by_category('personal'):
            self.janitor_model.append(iter, (False, None, plugin.get_title()))
