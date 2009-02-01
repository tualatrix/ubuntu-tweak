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

import gtk
from common.gui import GuiWorker
from common.config import TweakSettings
from common.factory import Factory

class PreferencesDialog:
    def __init__(self):
        self.settings = TweakSettings()

        worker = GuiWorker('preferences.glade')
        self.dialog = worker.get_widget('preferences_dialog')

        table = worker.get_widget('table1')

        height, width = self.settings.get_window_size()

        win_width = Factory.create('gconfspinbutton',
                    'window_width', 640, 1280, 1)
        win_width.show()
        win_width.connect('value-changed', self.on_value_changed)
        table.attach(win_width, 1, 2, 0, 1)

        win_height = Factory.create('gconfspinbutton',
                    'window_height', 480, 1280, 1)
        win_height.show()
        win_height.connect('value-changed', self.on_value_changed)
        table.attach(win_height, 1, 2, 1, 2)

        toolbar_size = Factory.create('gconfspinbutton',
                    'paned_size', 100, 500, 1)
        toolbar_size.show()
        toolbar_size.connect('value-changed', self.on_value_changed)
        table.attach(toolbar_size, 1, 2, 2, 3)

    def on_value_changed(self, widget):
        TweakSettings.need_save = False

    def run(self):
        self.dialog.run()

    def destroy(self):
        self.dialog.destroy()
