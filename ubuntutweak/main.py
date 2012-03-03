# Ubuntu Tweak - Ubuntu Configuration Tool
#
# Copyright (C) 2007-2011 Tualatrix Chou <tualatrix@gmail.com>
#
# Ubuntu Tweak is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Ubuntu Tweak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ubuntu Tweak; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

import os
import logging

from gi.repository import GObject, Gtk, Unique, Pango, GdkPixbuf

from ubuntutweak import modules
from ubuntutweak import admins
from ubuntutweak import system
from ubuntutweak.gui import GuiBuilder
from ubuntutweak.gui.gtk import post_ui
from ubuntutweak.policykit.widgets import PolkitButton
from ubuntutweak.utils import icon
from ubuntutweak.common.consts import VERSION, DATA_DIR
from ubuntutweak.modules import ModuleLoader, create_broken_module_class
from ubuntutweak.gui.dialogs import ErrorDialog
from ubuntutweak.clips import ClipPage
from ubuntutweak.apps import AppsPage
from ubuntutweak.janitor import JanitorPage
from ubuntutweak.policykit.dbusproxy import proxy
from ubuntutweak.settings import GSetting
from ubuntutweak.preferences import PreferencesDialog

log = logging.getLogger('app')

def show_splash():
    win = Gtk.Window(type=Gtk.WindowType.POPUP)
    win.set_position(Gtk.WindowPosition.CENTER)

    vbox = Gtk.VBox()
    image = Gtk.Image()
    image.set_from_file(os.path.join(DATA_DIR, 'pixmaps/splash.png'))

    vbox.pack_start(image, True, True, 0)
    win.add(vbox)

    win.show_all()

    while Gtk.events_pending():
        Gtk.main_iteration()

    win.destroy()


class ModuleButton(Gtk.Button):

    _module = None

    def __init__(self, module):
        GObject.GObject.__init__(self)

        log.info('Creating ModuleButton: %s' % module)

        self.set_relief(Gtk.ReliefStyle.NONE)

        self._module = module

        hbox = Gtk.HBox(spacing=6)
        self.add(hbox)

        image = Gtk.Image.new_from_pixbuf(module.get_pixbuf())
        hbox.pack_start(image, False, False, 0)

        label = Gtk.Label(label=module.get_title())
        label.set_alignment(0.0, 0.5)
        label.set_line_wrap(True)
        label.set_line_wrap_mode(Pango.WrapMode.WORD)
        label.set_size_request(120, -1)
        hbox.pack_start(label, False, False, 0)

        self.show_all()

    def get_module(self):
        return self._module


class CategoryBox(Gtk.VBox):
    _modules = None
    _buttons = None
    _current_cols = 0
    _current_modules = 0

    def __init__(self, modules=None, category='', category_name=''):
        GObject.GObject.__init__(self)

        self._modules = modules

        self.set_spacing(6)

        header = Gtk.HBox()
        header.set_spacing(12)
        label = Gtk.Label()
        label.set_markup("<span color='#aaa' size='x-large' weight='640'>%s</span>" % category_name)
        header.pack_start(label, False, False, 0)

        self._table = Gtk.Table()

        self._buttons = []
        for module in self._modules:
            self._buttons.append(ModuleButton(module))

        self.pack_start(header, False, False, 0)
        self.pack_start(self._table, False, False, 0)

        self.show_all()

    def get_modules(self):
        return self._modules

    def get_buttons(self):
        return self._buttons

    def rebuild_table(self, ncols):
        self._current_cols = ncols
        self._current_modules = len(self._modules)

        children = self._table.get_children()
        if children:
            for child in children:
                self._table.remove(child)

        row = 0
        col = 0
        for button in self._buttons:
            if button.get_module() in self._modules:
                self._table.attach(button, col, col + 1, row, row + 1, 0,
                                   xpadding=4, ypadding=2)
                col += 1
                if col == ncols:
                    col = 0
                    row += 1
        self.show_all()


class FeaturePage(Gtk.ScrolledWindow):

    __gsignals__ = {
        'module_selected': (GObject.SignalFlags.RUN_FIRST,
                            None,
                            (GObject.TYPE_STRING,))
    }

    _categories = None
    _boxes = []

    def __init__(self, feature_name):
        GObject.GObject.__init__(self,
                                 shadow_type=Gtk.ShadowType.NONE,
                                 hscrollbar_policy=Gtk.PolicyType.NEVER,
                                 vscrollbar_policy=Gtk.PolicyType.AUTOMATIC)
        self.set_border_width(12)

        self._feature = feature_name
        self._setting = GSetting('com.ubuntu-tweak.tweak.%s' % feature_name)
        self._categories = {}
        self._boxes = []

        self._box = Gtk.VBox(spacing=6)
        viewport = Gtk.Viewport(shadow_type=Gtk.ShadowType.NONE)
        viewport.add(self._box)
        self.add(viewport)

        self.load_modules()

        self.connect('draw', self.rebuild_boxes)

        self._setting.connect_notify(self.load_modules)

        self.show_all()

    def load_modules(self, *args, **kwargs):
        log.debug("Loading modules...")

        loader = ModuleLoader(self._feature)

        self._boxes = []
        for child in self._box.get_children():
            self._box.remove(child)

        for category, category_name in loader.get_categories():
            modules = loader.get_modules_by_category(category)
            if modules:
                module_to_loads = self._setting.get_value()

                for module in modules:
                    if module.is_user_extension() and module.get_name() not in module_to_loads:
                        modules.remove(module)

                category_box = CategoryBox(modules=modules, category_name=category_name)

                self._connect_signals(category_box)
                self._boxes.append(category_box)
                self._box.pack_start(category_box, False, False, 0)

        self.rebuild_boxes()

    def _connect_signals(self, category_box):
        for button in category_box.get_buttons():
            button.connect('clicked', self.on_button_clicked)

    def on_button_clicked(self, widget):
        log.info('Button clicked')
        module = widget.get_module()
        self.emit('module_selected', module.get_name())

    def rebuild_boxes(self, widget=None, event=None):
        request = self.get_allocation()
        ncols = request.width / 164 # 32 + 120 + 6 + 4
        width = ncols * (164 + 2 * 4) + 40
        if width > request.width:
            ncols -= 1

        pos = 0
        last_box = None
        children = self._box.get_children()
        for box in self._boxes:
            modules = box.get_modules()
            if len (modules) == 0:
                if box in children:
                    self._box.remove(box)
            else:
                if box not in children:
                    self._box.pack_start(box, False, False, 0)
                    self._box.reorder_child(box, pos)
                box.rebuild_table(ncols)
                pos += 1

                last_box = box


class UbuntuTweakApp(Unique.App):
    _window = None

    def __init__(self, name='com.ubuntu-tweak.Tweak', startup_id=''):
        Unique.App.__init__(self, name=name, startup_id=startup_id)
        log.debug("Distribution: %s\nApplication: %s\nDesktop:%s" % (system.DISTRO,
                                           system.APP,
                                           system.DESKTOP))
        self.connect('message-received', self.on_message_received)

    def set_window(self, window):
        self._window = window
        self.watch_window(self._window.mainwindow)

    def on_message_received(self, app, command, message, time):
        log.debug("on_message_received: command: %s, message: %s, time: %s" % (
            command, message, time))
        if command == Unique.Command.ACTIVATE:
            self._window.present()
            if message.get_text():
                self._window.select_target_feature(message.get_text())
        elif command == Unique.Command.OPEN:
            self._window.do_load_module(message.get_text())

        return False

    def run(self):
        Gtk.main()


class UbuntuTweakWindow(GuiBuilder):
    current_feature = 'overview'
    feature_dict = {}
    navigation_dict = {'tweaks': [None, None]}
    # the module name and page index: 'Compiz': 2
    loaded_modules = {}
    # reversed dict: 2: 'CompizClass'
    modules_index = {}

    def __init__(self, feature='', module=''):
        GuiBuilder.__init__(self, file_name='mainwindow.ui')

        tweaks_page = FeaturePage('tweaks')
        admins_page = FeaturePage('admins')
        clip_page = ClipPage()
#        apps_page = AppsPage()
        janitor_page = JanitorPage()
        self.preferences_dialog = PreferencesDialog(self.mainwindow)

        self.rencently_used_settings = GSetting('com.ubuntu-tweak.tweak.rencently-used')

        self.feature_dict['overview'] = self.notebook.append_page(clip_page, Gtk.Label())
#        self.feature_dict['apps'] = self.notebook.append_page(apps_page, Gtk.Label())
        self.feature_dict['tweaks'] = self.notebook.append_page(tweaks_page, Gtk.Label())
        self.feature_dict['admins'] = self.notebook.append_page(admins_page, Gtk.Label())
        self.feature_dict['janitor'] = self.notebook.append_page(janitor_page, Gtk.Label())
        self.feature_dict['wait'] = self.notebook.append_page(self._crete_wait_page(),
                                                           Gtk.Label())

        # Always show welcome page at first
        self.mainwindow.connect('realize', self._initialize_ui_states)
        tweaks_page.connect('module_selected', self.on_module_selected)
        admins_page.connect('module_selected', self.on_module_selected)
        clip_page.connect('load_module', lambda widget, name: self.do_load_module(name))
        clip_page.connect('load_feature', lambda widget, name: self.select_target_feature(name))
        self.mainwindow.show()

        if module:
            self.do_load_module(module)
        elif feature:
            self.select_target_feature(feature)

    def get_module_and_index(self, name):
        index = self.loaded_modules[name]

        return self.modules_index[index], index

    def select_target_feature(self, text):
        toggle_button = getattr(self, '%s_button' % text, None)
        log.info("select_target_feature: %s" % text)
        if toggle_button:
            self.current_feature = text
            toggle_button.set_active(True)

    def _initialize_ui_states(self, widget):
        self.window_size_setting = GSetting('com.ubuntu-tweak.tweak.window-size')
        width, height = self.window_size_setting.get_value()
        if width >= 800 and height >= 480:
            self.mainwindow.set_default_size(width, height)

    def _crete_wait_page(self):
        vbox = Gtk.VBox()

        label = Gtk.Label()
        label.set_markup("<span size=\"xx-large\">%s</span>" % \
                        _('Please wait a moment...'))
        label.set_justify(Gtk.Justification.FILL)
        vbox.pack_start(label, False, False, 50)
        hbox = Gtk.HBox()
        vbox.pack_start(hbox, False, False, 0)

        vbox.show_all()

        return vbox

    def on_mainwindow_destroy(self, widget):
        allocation = widget.get_allocation()
        self.window_size_setting.set_value((allocation.width, allocation.height))

        Gtk.main_quit()
        try:
            proxy.exit()
        except Exception, e:
            log.error(e)

    def on_about_button_clicked(self, widget):
        self.aboutdialog.set_version(VERSION)
        self.aboutdialog.set_transient_for(self.mainwindow)
        self.aboutdialog.run()
        self.aboutdialog.hide()

    def on_preference_button_clicked(self, widget):
        self.preferences_dialog.run(self.current_feature)
        self.preferences_dialog.hide()

    def on_module_selected(self, widget, name):
        log.debug('Select module: %s' % name)

        if name in self.loaded_modules:
            module, index = self.get_module_and_index(name)
            self._save_loaded_info(name, module, index)
            self.set_current_module(module, index)
        else:
            self.do_load_module(name)

    def do_load_module(self, name):
        self.notebook.set_current_page(self.feature_dict['wait'])
        GObject.timeout_add(5, self._load_module, name)

    def set_current_module(self, module=None, index=None):
        if index:
            self.notebook.set_current_page(index)

        if module and index:
            self.module_image.set_from_pixbuf(module.get_pixbuf(size=48))
            self.title_label.set_markup('<b><big>%s</big></b>' % module.get_title())
            self.description_label.set_text(module.get_description())
            page = self.notebook.get_nth_page(index)

            if page.__policykit__:
                if hasattr(page, 'un_lock'):
                    page.un_lock.show()
                    self._last_unlock = page.un_lock
                else:
                    page.un_lock = PolkitButton(page.__policykit__)
                    page.un_lock.connect('authenticated', page.on_polkit_action)
                    page.un_lock.show()
                    self._last_unlock = page.un_lock
                    self.right_top_box.pack_end(page.un_lock, False, False, 6)

            if not module.__name__.startswith('Broken'):
                self.log_used_module(module.__name__)
            self.update_jump_buttons()
        else:
            # no module, so back to logo
            self.module_image.set_from_pixbuf(icon.get_from_name('ubuntu-tweak', size=48))
            self.title_label.set_markup('')
            self.description_label.set_text('')

            if hasattr(self, '_last_unlock'):
                self._last_unlock.hide()

    def _save_loaded_info(self, name, module, index):
        log.info('_save_loaded_info: %s, %s, %s' % (name, module, index))
        self.loaded_modules[name] = index
        self.modules_index[index] = module
        self.navigation_dict[self.current_feature] = name, None

    @post_ui
    def _load_module(self, name):
        feature, module = ModuleLoader.search_module_for_name(name)

        if module:
            self.select_target_feature(feature)

            if name in self.loaded_modules:
                module, index = self.get_module_and_index(name)
            else:
                try:
                    page = module()
                except Exception, e:
                    log.error(e)
                    module = create_broken_module_class(name)
                    page = module()

                page.show_all()
                index = self.notebook.append_page(page, Gtk.Label(label=name))

            self._save_loaded_info(name, module, index)
            self.navigation_dict[feature] = name, None
            self.set_current_module(module, index)
            self.update_jump_buttons()
        else:
            dialog = ErrorDialog(title=_('No module named "%s"') % name,
                                 message=_('Please ensure you have entered the correct module name.'))
            dialog.launch()
            self.notebook.set_current_page(self.feature_dict[self.current_feature])

    def update_jump_buttons(self, disable=False):
        if not disable:
            back, forward = self.navigation_dict[self.current_feature]
            self.back_button.set_sensitive(bool(back))
            self.next_button.set_sensitive(bool(forward))
        else:
            self.back_button.set_sensitive(False)
            self.next_button.set_sensitive(False)

    def on_back_button_clicked(self, widget):
        self.navigation_dict[self.current_feature] = tuple(reversed(self.navigation_dict[self.current_feature]))
        self.notebook.set_current_page(self.feature_dict[self.current_feature])
        self.set_current_module(None)

        self.update_jump_buttons()

    def on_next_button_clicked(self, widget):
        back, forward = self.navigation_dict[self.current_feature]
        self.navigation_dict[self.current_feature] = forward, back

        module, index = self.get_module_and_index(forward)
        log.debug("Try to forward to: %d" % index)
        self.notebook.set_current_page(index)
        self.set_current_module(module, index)

        self.update_jump_buttons()

    def on_apps_button_toggled(self, widget):
        self.on_feature_button_clicked(widget, 'apps')

    def on_apps_button_clicked(self, widget):
        self.navigation_dict['apps'] = tuple(reversed(self.navigation_dict['apps']))
        self.on_apps_button_toggled(widget)

    def on_tweaks_button_clicked(self, widget):
        self.navigation_dict['tweaks'] = tuple(reversed(self.navigation_dict['tweaks']))
        self.on_tweaks_button_toggled(widget)

    def on_tweaks_button_toggled(self, widget):
        self.on_feature_button_clicked(widget, 'tweaks')

    def on_admins_button_clicked(self, widget):
        self.navigation_dict['admins'] = tuple(reversed(self.navigation_dict['admins']))
        self.on_admins_button_toggled(widget)

    def on_admins_button_toggled(self, widget):
        self.on_feature_button_clicked(widget, 'admins')

    def on_overview_button_toggled(self, widget):
        self.on_feature_button_clicked(widget, 'overview')

    def on_janitor_button_toggled(self, widget):
        self.on_feature_button_clicked(widget, 'janitor')
        self.module_image.set_from_pixbuf(icon.get_from_name('computerjanitor', size=48))
        self.title_label.set_markup('<b><big>%s</big></b>' % _('Computer Janitor'))
        self.description_label.set_text(_("Clean up a system so it's more like a freshly installed one"))

    def on_feature_button_clicked(self, widget, feature):
        log.debug("on_%s_button_toggled and widget.active is: %s" % (feature, widget.get_active()))
        self.current_feature = feature

        if widget.get_active():
            if feature not in self.navigation_dict:
                log.debug("Feature %s is not in self.navigation_dict" % feature)
                self.navigation_dict[feature] = None, None
                self.notebook.set_current_page(self.feature_dict[feature])
                self.set_current_module(None)
            else:
                back, backwards = self.navigation_dict[feature]
                if back:
                    module, index = self.get_module_and_index(back)
                    self.set_current_module(module, index)
                    self.notebook.set_current_page(index)
                else:
                    self.notebook.set_current_page(self.feature_dict[feature])
                    self.set_current_module(None)

            self.update_jump_buttons()

    def log_used_module(self, name):
        log.debug("Log the %s to Recently Used" % name)
        used_list = self.rencently_used_settings.get_value()

        if name in used_list:
            used_list.remove(name)

        used_list.insert(0, name)
        self.rencently_used_settings.set_value(used_list[:15])

    def present(self):
        self.mainwindow.present()
