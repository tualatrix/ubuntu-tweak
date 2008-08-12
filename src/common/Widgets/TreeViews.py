import gtk
import gobject
import os
from gnome import ui
from LookupIcon import get_icon_with_type

(
    COLUMN_ICON,
    COLUMN_TITLE,
    COLUMN_PATH,
) = range(3)

class DirList(gtk.TreeView):
    TARGETS = [
            ('text/plain', 0, 1),
            ]
    def __init__(self, dir):
        gtk.TreeView.__init__(self)
        self.set_rules_hint(True)
        self.dir = dir

        self.model = self.__create_model()
        self.set_model(self.model)

        iter = self.__setup_root_model()
        self.__update_model(self.dir, iter)

        self.__add_columns()
        self.set_size_request(180, -1)
        self.expand_all()

        self.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, 
                                        self.TARGETS,
                                        gtk.gdk.ACTION_DEFAULT| gtk.gdk.ACTION_MOVE)
        self.enable_model_drag_dest(self.TARGETS, gtk.gdk.ACTION_DEFAULT)

        self.connect('drag_data_get', self.on_drag_data_get)
        self.connect('drag_data_received', self.on_drag_data_received)

    def on_drag_data_get(self, treeview, context, selection, target_id, etime):
        treeselection = self.get_selection()
        model, iter = treeselection.get_selected()
        data = model.get_value(iter, COLUMN_PATH)

        selection.set(selection.target, 8, data)

    def on_drag_data_received(self, treeview, context, x, y, selection, info, etime):
        print context,x,y,selection, info, etime

    def __create_model(self):
        model = gtk.TreeStore(
                        gtk.gdk.Pixbuf,
                        gobject.TYPE_STRING,
                        gobject.TYPE_STRING)

        return model

    def __setup_root_model(self):
        iter = self.model.append(None)
        pixbuf = get_icon_with_type(self.dir, 24)

        self.model.set(iter,
                COLUMN_ICON, pixbuf,
                COLUMN_TITLE, os.path.basename(self.dir),
                COLUMN_PATH, dir)

        return iter

    def __update_model(self, dir, iter):
        for item in os.listdir(dir):
            fullname = os.path.join(dir, item)
            pixbuf = get_icon_with_type(fullname, 24)

            child_iter = self.model.append(iter)
            self.model.set(child_iter,
                              COLUMN_ICON, pixbuf,
                              COLUMN_TITLE, os.path.basename(fullname),
                              COLUMN_PATH, fullname)

            if os.path.isdir(fullname):
                self.__update_model(fullname, child_iter)

    def __add_columns(self):
        column = gtk.TreeViewColumn()
        column.set_spacing(5)

        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, pixbuf = COLUMN_ICON)

        renderer = gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.set_attributes(renderer, text = COLUMN_TITLE)

        self.append_column(column)
