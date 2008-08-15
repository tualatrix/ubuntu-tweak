import os
import gtk
import shutil
import gobject
from gnome import ui
import gnomevfs
from LookupIcon import get_icon_with_type
from Dialogs import ErrorDialog

(
    DIR_ICON,
    DIR_TITLE,
    DIR_PATH,
    DIR_EDITABLE,
) = range(4)

class DirView(gtk.TreeView):
    TARGETS = [
            ('text/plain', 0, 1),
            ('TEXT', 0, 2),
            ('STRING', 0, 3),
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

        change_item = gtk.MenuItem(_('Create folder'))
        menu.append(change_item)
        change_item.connect('activate', self.on_create_folder)

        change_item = gtk.MenuItem(_('Rename'))
        menu.append(change_item)
        change_item.connect('activate', self.on_rename_item)

        change_item = gtk.MenuItem(_('Delete'))
        menu.append(change_item)
        change_item.connect('activate', self.on_delete_item)

        return menu

    def create_file_name(self, filename, count):
        if filename in os.listdir(self.dir):
            if filename[-1].isdigit():
                filename = filename[:-1] + str(count)
            else:
                filename = filename + ' %d' % count
            count = count + 1
            self.create_file_name(filename, count)
        else:
            self.tempname = filename

    def on_create_folder(self, widget):
        iter = self.model.append(self.model.get_iter_first())
        column = self.get_column(0)
        path = self.model.get_path(iter)

        self.create_file_name(_('Input the dir name'), 1)
        filename = self.tempname
        del self.tempname
        newdir = os.path.join(self.dir, filename)
        os.mkdir(newdir)

        self.model.set(iter,
                DIR_ICON, get_icon_with_type(newdir, 24),
                DIR_TITLE, filename,
                DIR_PATH, newdir,
                DIR_EDITABLE, True)

        self.set_cursor(path, focus_column = column, start_editing = True)

    def on_rename_item(self, widget):
        model, iter = self.get_selection().get_selected()
        filepath = model.get_value(iter, DIR_PATH)

        if filepath != self.dir:
            model.set_value(iter, DIR_EDITABLE, True)

            column = self.get_column(0)
            path = self.model.get_path(iter)
            self.set_cursor(path, focus_column = column, start_editing = True)
        else:
            ErrorDialog(_("Can't rename the root folder")).launch()

    def on_delete_item(self, widget):
        model, iter = self.get_selection().get_selected()
        filepath = model.get_value(iter, DIR_PATH)

        if filepath != self.dir:
            if os.path.isdir(filepath):
                shutil.rmtree(filepath)
            else:
                os.remove(filepath)

            self.update_model()
        else:
            ErrorDialog(_("Can't delete the root folder")).launch()

    def on_cellrenderer_edited(self, cellrenderertext, path, new_text):
        iter = self.model.get_iter_from_string(path)
        filepath = self.model.get_value(iter, DIR_PATH)
        old_text = self.model.get_value(iter, DIR_TITLE)

        if old_text == new_text or new_text not in os.listdir(os.path.dirname(filepath)):
            newpath = os.path.join(os.path.dirname(filepath), new_text)
            os.rename(filepath, newpath)
            self.model.set(iter,
                           DIR_TITLE, new_text,
                           DIR_PATH, newpath,
                           DIR_EDITABLE, False)
        else:
            ErrorDialog(_("Can't rename!\n\nThere's file in it")).launch()

    def on_drag_data_get(self, treeview, context, selection, target_id, etime):
        treeselection = self.get_selection()
        model, iter = treeselection.get_selected()
        data = model.get_value(iter, DIR_PATH)

        selection.set(selection.target, 8, data)

    def on_drag_data_received(self, treeview, context, x, y, selection, info, etime):
        '''If the source is coming from internal, then move it, or copy it.'''
        source_widget = context.get_source_widget()

        try:
            path, position = treeview.get_dest_row_at_pos(x, y)
            iter = self.model.get_iter(path)
        except:
            iter = self.model.get_iter_first()

        if source_widget:
            source_widget.get_data('source')
            file_action = 'move'
            dir_action = 'move'
        else:
            file_action = 'copy'
            dir_action = 'copytree'

        target = self.model.get_value(iter, DIR_PATH)
        source = selection.data
        if source.startswith('file:///'):
            source = gnomevfs.format_uri_for_display(source.strip())

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

    def update_model(self):
        self.model.clear()

        iter = self.__setup_root_model()
        self.__update_model(self.dir, iter)

        self.expand_all()

    def __create_model(self):
        model = gtk.TreeStore(
                        gtk.gdk.Pixbuf,
                        gobject.TYPE_STRING,
                        gobject.TYPE_STRING,
                        gobject.TYPE_BOOLEAN)

        return model

    def __setup_root_model(self):
        iter = self.model.append(None)
        pixbuf = get_icon_with_type(self.dir, 24)

        self.model.set(iter,
                DIR_ICON, pixbuf,
                DIR_TITLE, os.path.basename(self.dir),
                DIR_PATH, self.dir,
                DIR_EDITABLE, False)

        return iter

    def __update_model(self, dir, iter):
        for item in os.listdir(dir):
            fullname = os.path.join(dir, item)
            pixbuf = get_icon_with_type(fullname, 24)

            child_iter = self.model.append(iter)
            self.model.set(child_iter,
                              DIR_ICON, pixbuf,
                              DIR_TITLE, os.path.basename(fullname),
                              DIR_PATH, fullname, 
                              DIR_EDITABLE, False)

            if os.path.isdir(fullname):
                self.__update_model(fullname, child_iter)

    def __add_columns(self):
        column = gtk.TreeViewColumn()
        column.set_spacing(5)

        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, pixbuf = DIR_ICON)

        renderer = gtk.CellRendererText()
        renderer.connect('edited', self.on_cellrenderer_edited)
        column.pack_start(renderer, True)
        column.set_attributes(renderer, text = DIR_TITLE, editable = DIR_EDITABLE)

        self.append_column(column)
        
(
    FLAT_ICON,
    FLAT_TITLE,
    FLAT_PATH,
) = range(3)

class FlatView(gtk.TreeView):
    TARGETS = [
        ('text/plain', 0, 1),
        ('TEXT', 0, 2),
        ('STRING', 0, 3),
        ]

    def __init__(self, dir, exclude_dir = None):
        gtk.TreeView.__init__(self)
        self.set_rules_hint(True)
        self.dir = dir
        self.exclude_dir = exclude_dir

        self.model = gtk.ListStore(
                        gtk.gdk.Pixbuf,
                        gobject.TYPE_STRING,
                        gobject.TYPE_STRING)

        self.set_model(self.model)
        self.__create_model()
        self.__add_columns()

        self.enable_model_drag_source( gtk.gdk.BUTTON1_MASK,
                        self.TARGETS,
                        gtk.gdk.ACTION_DEFAULT|
                        gtk.gdk.ACTION_MOVE)
        self.enable_model_drag_dest(self.TARGETS,
                        gtk.gdk.ACTION_DEFAULT)

        self.connect("drag_data_get", self.on_drag_data_get_data)
        self.connect("drag_data_received", self.on_drag_data_received_data)

    def on_drag_data_get_data(self, treeview, context, selection, target_id, etime):
        treeselection = self.get_selection()
        model, iter = treeselection.get_selected()
        data = model.get_value(iter, FLAT_PATH)

        selection.set(selection.target, 8, data)

    def on_drag_data_received_data(self, treeview, context, x, y, selection, info, etime):
        source_widget = context.get_source_widget()

        try:
            path, position = treeview.get_dest_row_at_pos(x, y)
            iter = self.model.get_iter(path)
        except:
            iter = self.model.get_iter_first()

        if source_widget:
            return
        else:
            file_action = 'move'
            dir_action = 'move'

        target = self.model.get_value(iter, DIR_PATH)
        source = selection.data
        print target, source

        if source.startswith('file:///'):
            source = gnomevfs.format_uri_for_display(source.strip())

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

        self.__create_model()

    def __create_model(self):
        self.model.clear()

        dir = self.dir
        self.exist_lsit = []
        if self.exclude_dir:
            for root, dirs, files in os.walk(self.exclude_dir):
                if files:
                    self.exist_lsit.extend(files)

        for item in os.listdir(dir):
            fullname = os.path.join(dir, item)
            title = os.path.basename(fullname)
            if title in self.exist_lsit: continue
            pixbuf = get_icon_with_type(fullname, 24)

            iter = self.model.append(None)
            self.model.set(iter,
                           FLAT_ICON, pixbuf,
                           FLAT_TITLE, title,
                           FLAT_PATH, fullname) 

    def __add_columns(self):
        column = gtk.TreeViewColumn()
        column.set_spacing(5)

        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, pixbuf = FLAT_ICON)

        renderer = gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.set_attributes(renderer, text = FLAT_TITLE)

        self.append_column(column)
