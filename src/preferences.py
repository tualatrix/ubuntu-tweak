# Ubuntu Tweak - PyGTK based desktop configure tool
#
# Copyright (C) 2007-2008 TualatriX <tualatrix@gmail.com>
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

import os
import gtk
import gobject
from common.consts import *
from common.gui import GuiWorker
from common.config import TweakSettings
from common.utils import set_label_for_stock_button
from common.factory import WidgetFactory

class PreferencesDialog:
    def __init__(self):
        self.worker = GuiWorker('preferences.glade')
        self.dialog = self.worker.get_widget('preferences_dialog')

        self.setup_window_preference()
        self.setup_color_preference()
        self.setup_launch_function()
        self.setup_other_features()

    def setup_window_preference(self):
        table = self.worker.get_widget('table1')

        height, width = TweakSettings.get_window_size()

        win_width = WidgetFactory.create('GconfSpinButton',
                                        key = 'window_width', 
                                        min = 640, max = 1280, step = 1)
        win_width.show()
        win_width.connect('value-changed', self.on_value_changed)
        table.attach(win_width, 1, 3, 0, 1)

        win_height = WidgetFactory.create('GconfSpinButton',
                                          key = 'window_height', 
                                          min = 480, max = 1280, step = 1)
        win_height.show()
        win_height.connect('value-changed', self.on_value_changed)
        table.attach(win_height, 1, 3, 1, 2)

        toolbar_size = WidgetFactory.create('GconfSpinButton',
                                            key = 'toolbar_size', 
                                            min = 100, max = 500, step = 1)
        toolbar_size.show()
        toolbar_size.connect('value-changed', self.on_value_changed)
        table.attach(toolbar_size, 1, 3, 2, 3)

    def setup_color_preference(self):
        colorbutton = self.worker.get_widget('colorbutton')
        colorbutton.set_color(TweakSettings.get_toolbar_color(True))
        colorbutton.connect('color-set', self.on_color_set)

        reset_button = self.worker.get_widget('reset_button')
        set_label_for_stock_button(reset_button, _('Reset'))
        reset_button.connect('clicked', self.on_reset_clicked, colorbutton)

    def setup_launch_function(self):
        from mainwindow import MODULES
        from mainwindow import MODULE_ID, MODULE_LOGO, MODULE_TITLE
        function_box = self.worker.get_widget('function_box')

        module_list = []
        for module in MODULES:
            if module[-1] == 2:
                module_list.append(module)

        model = gtk.ListStore(
                gobject.TYPE_INT,
                gtk.gdk.Pixbuf,
                gobject.TYPE_STRING)

        iter = model.append(None)
        model.set(iter,
                MODULE_ID, 0,
                MODULE_LOGO, None,
                MODULE_TITLE, _('None')
        )
        for module in module_list:
            icon = gtk.gdk.pixbuf_new_from_file(os.path.join(DATA_DIR, 'pixmaps', module[MODULE_LOGO])).scale_simple(18, 18, gtk.gdk.INTERP_NEAREST)

            iter = model.append(None)

            model.set(iter,
                    MODULE_ID, module[MODULE_ID],
                    MODULE_LOGO, icon,
                    MODULE_TITLE, module[MODULE_TITLE],
            )

        function_box.set_model(model)
        textcell = gtk.CellRendererText()
        pixbufcell = gtk.CellRendererPixbuf()
        function_box.pack_start(pixbufcell, False)
        function_box.pack_start(textcell, True)
        function_box.add_attribute(textcell, 'text', MODULE_TITLE)
        function_box.add_attribute(pixbufcell, 'pixbuf', MODULE_LOGO)
        id = TweakSettings.get_default_launch()
        for i, row in enumerate(model):
            _id = model.get_value(row.iter, MODULE_ID)
            if id == _id:
                function_box.set_active(i)
        function_box.connect('changed', self.on_launch_changed)

    def setup_other_features(self):
        vbox = self.worker.get_widget('vbox5')

        button = WidgetFactory.create('GconfCheckButton', 
                                      label = _('Enable the Automate Update'), 
                                      key = 'check_update',
                                      default = True)
        vbox.pack_start(button, False, False, 0)

        button = WidgetFactory.create('GconfCheckButton', 
                                      label = _('Show Donate Natiffcation'), 
                                      key = 'show_donate_notify',
                                      default = True)
        vbox.pack_start(button, False, False, 0)

        vbox.show_all()

    def on_launch_changed(self, widget):
        index = widget.get_active()
        liststore = widget.get_model()
        iter = liststore.get_iter(index)
        id = liststore.get_value(iter, 0)
        TweakSettings.set_default_launch(id)

    def on_color_set(self, widget):
        TweakSettings.set_toolbar_color(widget.get_color().to_string())
    
    def on_reset_clicked(self, widget, colorbutton):
        color = gtk.gdk.Color(32767, 32767, 32767)
        colorbutton.set_color(color)
        TweakSettings.set_toolbar_color(color.to_string())

    def on_value_changed(self, widget):
        TweakSettings.need_save = False

    def run(self):
        self.dialog.run()

    def destroy(self):
        self.dialog.destroy()
