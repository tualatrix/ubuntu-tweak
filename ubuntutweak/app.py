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

import gobject
from gi.repository import Gtk, Unique, Pango, GdkPixbuf

from ubuntutweak import modules
from ubuntutweak.gui import GuiBuilder
from ubuntutweak.utils import icon
from ubuntutweak.common.consts import VERSION, DATA_DIR
from ubuntutweak.modules import ModuleLoader, create_broken_module_class
from ubuntutweak.gui.dialogs import ErrorDialog
from ubuntutweak.clips import ClipPage

log = logging.getLogger('app')

MODULE_LOADER = ModuleLoader(modules.__path__[0])


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
        gobject.GObject.__init__(self)

        log.info('Creating ModuleButton: %s' % module)

        self.set_relief(Gtk.ReliefStyle.NONE)

        self._module = module

        vbox = Gtk.VBox(spacing=6)
        self.add(vbox)

        image = Gtk.Image.new_from_pixbuf(module.get_pixbuf())
        vbox.pack_start(image, False, False, 0)

        label = Gtk.Label(label=module.get_title())
        vbox.pack_start(label, False, False, 0)

    def get_module(self):
        return self._module


class CategoryBox(Gtk.VBox):
    _modules = None
    _buttons = None
    _current_cols = 0
    _current_modules = 0

    def __init__(self, modules=None, category='', category_name=''):
        gobject.GObject.__init__(self)

        self._modules = modules

        self.set_spacing(6)

        header = Gtk.HBox()
        header.set_spacing(12)
        label = Gtk.Label()
        label.set_markup("<span color='#aaa' size='x-large' weight='800'>%s</span>" % category_name)
        header.pack_start(label, False, False, 0)

        self._table = Gtk.Table()

        self._buttons = []
        for module in self._modules:
            self._buttons.append(ModuleButton(module))

        self.pack_start(header, False, False, 0)
        self.pack_start(self._table, False, False, 0)

    def get_modules(self):
        return self._modules

    def get_buttons(self):
        return self._buttons

    def rebuild_table (self, ncols, force=False):
        if (not force and ncols == self._current_cols and
                len(self._modules) == self._current_modules):
            return
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


class ModuleWindow(Gtk.ScrolledWindow):

    __gsignals__ = {
        'module_selected': (gobject.SIGNAL_RUN_FIRST,
                            gobject.TYPE_NONE,
                            (gobject.TYPE_STRING,))
        }

    _categories = None
    _boxes = []

    def __init__(self):
        gobject.GObject.__init__(self,
                                 shadow_type=Gtk.ShadowType.NONE,
                                 hscrollbar_policy=Gtk.PolicyType.NEVER,
                                 vscrollbar_policy=Gtk.PolicyType.AUTOMATIC)

        self.set_border_width(12)

        self._categories = {}
        self._boxes = []

        self.connect('size-allocate', self.rebuild_boxes)

        self._box = Gtk.VBox(spacing=6)

        for category, category_name in MODULE_LOADER.get_categories():
            modules = MODULE_LOADER.get_modules_by_category(category)
            if modules:
                category_box = CategoryBox(modules=modules, category_name=category_name)
                self._connect_signals(category_box)
                self._boxes.append(category_box)
                self._box.pack_start(category_box, False, False, 0)

        viewport = Gtk.Viewport(shadow_type=Gtk.ShadowType.NONE)
        viewport.add(self._box)
        self.add(viewport)

    def _connect_signals(self, category_box):
        for button in category_box.get_buttons():
            button.connect('clicked', self.on_button_clicked)

    def on_button_clicked(self, widget):
        log.info('Button clicked')
        module = widget.get_module()
        self.emit('module_selected', module.get_name())


    def rebuild_boxes(self, widget, request):
        ncols = request.width / 220
        width = ncols * (220 + 2 * 4) + 40
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


class JumpManager(object):
    '''Manage the page and modules, they are all in the notebook'''

    def __init__(self):
        self._overview_index = None
        self._tweaks_index = None
        self._wait_index = None
        self.__next_module = None
        self._current_module_index = None

        # the module name and page index: 'Compiz': 2
        self._loaded_modules = {}
        # reversed dict: 2: 'CompizClass'
        self._modules_index = {}

    def get_current_index(self):
        pass

    def can_backwards(self):
        return self.current_module_index != None and \
               self._current_module_index != self._tweaks_index

    def can_forward(self):
        return self.__next_module != None and \
               self.__next_module != self._current_module_index

    def get_backwards_index(self):
        self.__next_module = self._current_module_index
        self._current_module_index = self._tweaks_index
        return self._tweaks_index

    def get_forward_index(self):
        index = self.__next_module
        self.__next_module = None
        self._current_module_index = index
        return index

    def module_is_loaded(self, name):
        return name in self._loaded_modules

    def store_current_module(self, name, module, index):
        log.info('store_current_module: %s, %s, %s' % (name, module, index))
        self._loaded_modules[name] = index
        self._current_module_index = index
        self._modules_index[index] = module
        self.__next_module = index

    def get_module_and_index(self, name):
        index = self._loaded_modules[name]

        return self._modules_index[index], index

    def get_module_from_index(self, index):
        return self._modules_index[index]

    def get_current_module(self):
        return self._modules_index[self.current_module_index]

    @property
    def overview_index(self):
        return self._overview_index

    @overview_index.setter
    def overview_index(self, index):
        self._overview_index = index

    @property
    def tweaks_index(self):
        return self._tweaks_index

    @tweaks_index.setter
    def tweaks_index(self, index):
        self._tweaks_index = index

    @property
    def wait_index(self):
        return self._wait_index

    @wait_index.setter
    def wait_index(self, index):
        self._wait_index = index

    @property
    def current_module_index(self):
        return self._current_module_index

    @current_module_index.setter
    def current_module_index(self, index):
        self._current_module_index = index


class UbuntuTweakApp(Unique.App):
    _window = None

    def __init__(self, name='com.ubuntu-tweak.Tweak', startup_id=''):
        Unique.App.__init__(self, name=name, startup_id=startup_id)
        self.connect('message-received', self.on_message_received)

    def set_window(self, window):
        self._window = window
        self.watch_window(self._window.mainwindow)

    def on_message_received(self, app, command, message, time):
        log.debug("on_message_received: command: %s, message: %s, time: %s" % (
            command, message, time))
        if command == Unique.Command.ACTIVATE:
            self._window.present()
        elif command == Unique.Command.OPEN:
            self._window.create_module(message.get_text())

        return False

    def run(self):
        Gtk.main()


class UbuntuTweakWindow(GuiBuilder):
    def __init__(self, module=''):
        GuiBuilder.__init__(self, file_name='mainwindow.ui')

        Gtk.rc_parse(os.path.join(DATA_DIR, 'theme/ubuntu-tweak.rc'))

        module_window = ModuleWindow()
        clip_page = ClipPage().get_object('hbox1')

        self.jumper = JumpManager()

        self.jumper.overview_index = self.notebook.append_page(clip_page, Gtk.Label())
        self.jumper.tweaks_index = self.notebook.append_page(module_window, Gtk.Label())
        self.jumper.wait_index = self.notebook.append_page(self._crete_wait_page(),
                                                           Gtk.Label())

        # Always show welcome page at first
        self.mainwindow.connect('realize', self._initialize_ui_states)
        module_window.connect('module_selected', self.on_module_selected)

        self.mainwindow.show_all()
        self.link_button.hide()

        if module:
            self.tweaks_button.set_active(True)
            self.create_module(module)

    def _initialize_ui_states(self, widget):
        self.notebook.set_current_page(self.jumper.overview_index)
        self.overview_button.set_active(True)
        self.search_entry.grab_focus()

    def _crete_wait_page(self):
        vbox = Gtk.VBox()

        label = Gtk.Label()
        label.set_markup("<span size=\"xx-large\">%s</span>" % \
                        _('Please wait a moment...'))
        label.set_justify(Gtk.Justification.FILL)
        vbox.pack_start(label, False, False, 50)
        hbox = Gtk.HBox()
        vbox.pack_start(hbox, False, False, 0)

        return vbox

    def on_mainwindow_destroy(self, widget):
        Gtk.main_quit()

    def on_preference_button_clicked(self, widget):
        #TODO and FIXME, it can only show once
        self.aboutdialog.set_version(VERSION)
        self.aboutdialog.set_transient_for(self.mainwindow)
        self.aboutdialog.run()

    def on_module_selected(self, widget, name):
        log.debug('Select module: %s' % name)

        if self.jumper.module_is_loaded(name):
            module, index = self.jumper.get_module_and_index(name)
            self.jumper.store_current_module(name, module, index)
            self.set_current_module(module, index)
        else:
            self.notebook.set_current_page(self.jumper.wait_index)
            self.create_module(name)

    def set_current_module(self, module=None, index=None):
        if index:
            self.notebook.set_current_page(index)

        if module:
            self.module_image.set_from_pixbuf(module.get_pixbuf(size=48))
            self.title_label.set_markup('<b><big>%s</big></b>' % module.get_title())
            self.description_label.set_text(module.get_description())
            if module.get_url():
                self.link_button.set_uri(module.get_url())
                self.link_button.set_label(module.get_url_title())
                self.link_button.show()
            else:
                self.link_button.hide()

            self.update_jump_buttons()
        else:
            # no module, so back to logo
            self.module_image.set_from_pixbuf(icon.get_from_name('ubuntu-tweak', size=48))
            self.title_label.set_markup('')
            self.description_label.set_text('')
            self.link_button.hide()

    def create_module(self, name):
        log.debug('Create module: %s' % name)
        try:
            module = MODULE_LOADER.get_module(name)
            page = module()
        except KeyError, e:
            dialog = ErrorDialog(title=_('No module named "%s"') % name,
                                 message=_('Please ensure you have entered the correct module name.'))
            dialog.launch()
            return False
        except Exception, e:
            log.error(e)
            module = create_broken_module_class(name)
            page = module()

        #TODO
        page.show_all()
        index = self.notebook.append_page(page, Gtk.Label(label=name))
        self.set_current_module(module, index)
        self.jumper.store_current_module(name, module, index)
        self.update_jump_buttons()

    def update_jump_buttons(self, disable=False):
        #TODO toggle jump and module jump
        if not disable:
            if self.jumper.can_backwards():
                self.back_button.set_sensitive(True)
            else:
                self.back_button.set_sensitive(False)

            if self.jumper.can_forward():
                self.next_button.set_sensitive(True)
            else:
                self.next_button.set_sensitive(False)
        else:
            self.back_button.set_sensitive(False)
            self.next_button.set_sensitive(False)

    def on_back_button_clicked(self, widget):
        index = self.jumper.get_backwards_index()
        log.debug("Try to backwards to: %d" % index)
        self.notebook.set_current_page(index)
        try:
            module = self.jumper.get_module_from_index(index)
            self.set_current_module(module, index)
        except KeyError:
            self.set_current_module(None)

        self.update_jump_buttons()

    def on_next_button_clicked(self, widget):
        index = self.jumper.get_forward_index()
        log.debug("Try to forward to: %d" % index)
        self.notebook.set_current_page(index)
        try:
            module = self.jumper.get_module_from_index(index)
            self.set_current_module(module, index)
        except KeyError:
            self.set_current_module(None)

        self.update_jump_buttons()

    def on_overview_button_toggled(self, widget):
        if widget.get_active():
            self.update_jump_buttons(disable=True)
            self.set_current_module(None)
            self.notebook.set_current_page(self.jumper.overview_index)

    def on_tweaks_button_toggled(self, widget):
        if widget.get_active():
            self.update_jump_buttons()
            if self.jumper.current_module_index:
                self.set_current_module(index=self.jumper.current_module_index)
            else:
                self.notebook.set_current_page(self.jumper.tweaks_index)

    def present(self):
        self.mainwindow.present()
