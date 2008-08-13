import os
import gtk
import shutil
import gobject
from gnome import ui
from LookupIcon import get_icon_with_type
from Dialogs import ErrorDialog

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

        menu = self.__create_popup_menu()
        menu.show_all()
        self.connect('button_press_event', self.button_press_event, menu)

    def button_press_event(self, widget, event, menu):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            menu.popup(None, None, None, event.button, event.time)
        return False

    def __create_popup_menu(self):
        menu = gtk.Menu()

#        change_item = gtk.MenuItem(_('Create folder'))
#        menu.append(change_item)
#        change_item.connect('activate', self.on_create_folder)

        change_item = gtk.MenuItem(_('Delete'))
        menu.append(change_item)
        change_item.connect('activate', self.on_delete_item)

        return menu

    def on_create_folder(self, widget):
        pass

    def on_delete_item(self, widget):
        model, iter = self.get_selection().get_selected()
        filepath = model.get_value(iter, COLUMN_PATH)

        if filepath != self.dir:
            if os.path.isdir(filepath):
                shutil.rmtree(filepath)
            else:
                os.remove(filepath)

            self.update_model()
        else:
            ErrorDialog(_("Can't delete the root folder")).launch()


    def on_drag_data_get(self, treeview, context, selection, target_id, etime):
        treeselection = self.get_selection()
        model, iter = treeselection.get_selected()
        data = model.get_value(iter, COLUMN_PATH)

        selection.set(selection.target, 8, data)
        treeview.set_data('source', 'internal')

    def on_drag_data_received(self, treeview, context, x, y, selection, info, etime):
        '''If the source is coming from internal, then move it, or copy it.'''
        source_widget = context.get_source_widget()

        try:
            path, position = treeview.get_dest_row_at_pos(x, y)
            iter = self.model.get_iter(path)
        except:
            iter = self.model.get_iter_first()

        try:
            if source_widget:
                source_widget.get_data('source')
                file_action = 'move'
                dir_action = 'move'
            else:
                file_action = 'copy'
                dir_action = 'copytree'

            target = self.model.get_value(iter, COLUMN_PATH)
            source = selection.data

            if os.path.isdir(target) and not os.path.isdir(source):
                if os.path.dirname(source) != target:
                    if os.path.isdir(source):
                        getattr(shutil, dir_action)(source, target)
                    else:
                        getattr(shutil, file_action)(source, target)
            elif os.path.isdir(target) and os.path.isdir(source):
                target = os.path.join(target, os.path.basename(source))
                getattr(shutil, dir_action)(source, target)
            elif os.path.dirname(target) != os.path.dirname(source):
                if not os.path.isdir(target):
                    target = os.path.dirname(target)

                if os.path.isdir(source):
                    target = os.path.join(target, os.path.basename(source))
                    getattr(shutil, dir_action)(source, target)
                else:
                    getattr(shutil, file_action)(source, target)

            self.update_model()
        except:
            pass

    def update_model(self):
        self.model.clear()

        iter = self.__setup_root_model()
        self.__update_model(self.dir, iter)

        self.expand_all()

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
                COLUMN_PATH, self.dir)

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
