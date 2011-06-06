import logging


import gobject
from gi.repository import Gtk, Pango

from ubuntutweak.gui import GuiBuilder
from ubuntutweak.utils import icon

log = logging.getLogger('Janitor')


class JanitorPage(Gtk.VBox, GuiBuilder):
    i = 0

    def __init__(self):
        gobject.GObject.__init__(self)
        self.set_border_width(6)
        GuiBuilder.__init__(self, 'janitorpage.ui')

        self.hbox1.reparent(self)
        self.setup_ui_tasks()

        self.update_model()
        self.janitor_treeview.connect('realize', lambda tv: tv.expand_all())
        self.show_all()

    def setup_ui_tasks(self):
        icon_renderer = self.get_object('icon_renderer')
        self.janitor_column.set_cell_data_func(icon_renderer, self.logo_column_view_func)

    def logo_column_view_func(self, cell_layout, renderer, model, iter, func):
        pixbuf = model.get_value(iter, 1)
        if pixbuf == None:
            renderer.set_property("visible", False)
        else:
            renderer.set_property("visible", True)

    def update_model(self):
        #TODO
        iter = self.janitor_model.append(None, (None,
                                                icon.get_from_name('ubuntu-logo', size=32),
                                                'System'))

        self.janitor_model.append(iter, (False, None, 'Apt Cache'))
        self.janitor_model.append(iter, (False, None, 'Unneeded Pakcages'))
        self.janitor_model.append(iter, (False, None, 'Package Configs'))
        self.janitor_model.append(iter, (False, None, 'Old Kernel'))

        iter = self.janitor_model.append(None, (None,
                                                icon.get_from_name('system-users', size=32),
                                                'User'))

        self.janitor_model.append(iter, (False, None, 'Thumbnails cache'))
