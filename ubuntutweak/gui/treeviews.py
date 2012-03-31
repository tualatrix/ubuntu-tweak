import os
import logging
import shutil

from gi.repository import Gtk, Gdk, Gio, GObject, GdkPixbuf

from ubuntutweak.gui.dialogs import ErrorDialog
from ubuntutweak.utils import icon

log = logging.getLogger("treeviews")

def get_local_path(url):
    return Gio.file_parse_name(url.strip()).get_path()

class CommonView(object):
    TARGETS = [
            ('text/plain', 0, 1),
            ('TEXT', 0, 2),
            ('STRING', 0, 3),
            ]

    def enable_drag_and_drop(self):
        self.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK,
                                      self.TARGETS,
                                      Gdk.DragAction.COPY)
        self.enable_model_drag_dest([], Gdk.DragAction.COPY)
        self.drag_dest_add_text_targets()
        self.drag_source_add_text_targets()

    def is_same_object(self, context):
        return context.get_source_window() is not self.get_window()


class DirView(Gtk.TreeView, CommonView):
    __gsignals__ = {
        'deleted': (GObject.SignalFlags.RUN_FIRST, None, ())
    }

    (DIR_ICON,
     DIR_TITLE,
     DIR_PATH,
     DIR_EDITABLE) = range(4)


    def __init__(self, dir):
        GObject.GObject.__init__(self)

        self.set_rules_hint(True)
        self.dir = dir
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

        self.model = self._create_model()
        self.set_model(self.model)

        iter = self._setup_root_model()
        self.do_update_model(self.dir, iter)

        self._add_columns()
        self.set_size_request(180, -1)
        self.expand_all()

        self.enable_drag_and_drop()

        self.connect('drag_data_get', self.on_drag_data_get)
        self.connect('drag_data_received', self.on_drag_data_received)

        menu = self._create_popup_menu()
        menu.show_all()
        self.connect('button_press_event', self.button_press_event, menu)
        self.connect('key-press-event', self.on_key_press_event)

    def on_key_press_event(self, widget, event):
        if event.keyval == 65535:
            self.on_delete_item(widget)

    def button_press_event(self, widget, event, menu):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            menu.popup(None, None, None, None, event.button, event.time)
        return False

    def _create_popup_menu(self):
        menu = Gtk.Menu()

        change_item = Gtk.MenuItem(label=_('Create folder'))
        menu.append(change_item)
        change_item.connect('activate', self.on_create_folder)

        change_item = Gtk.MenuItem(label=_('Rename'))
        menu.append(change_item)
        change_item.connect('activate', self.on_rename_item)

        change_item = Gtk.MenuItem(label=_('Delete'))
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

        self.model.set_value(iter, self.DIR_ICON, icon.get_from_name('folder', 24))
        self.model.set_value(iter, self.DIR_TITLE, filename)
        self.model.set_value(iter, self.DIR_PATH, newdir)
        self.model.set_value(iter, self.DIR_EDITABLE, True)

        self.set_cursor(path, column, True)

    def on_rename_item(self, widget):
        model, iter = self.get_selection().get_selected()
        filepath = model.get_value(iter, self.DIR_PATH)

        if filepath != self.dir:
            model.set_value(iter, self.DIR_EDITABLE, True)

            column = self.get_column(0)
            path = self.model.get_path(iter)
            self.set_cursor(path, column, True)
        else:
            ErrorDialog(_("Can't rename the root folder")).launch()

    def on_delete_item(self, widget):
        model, iter = self.get_selection().get_selected()
        if not iter:
            return
        filepath = model.get_value(iter, self.DIR_PATH)

        if filepath != self.dir:
            if os.path.isdir(filepath):
                shutil.rmtree(filepath)
            else:
                os.remove(filepath)

            self.emit('deleted')
            self.update_model()
        else:
            ErrorDialog(_("Can't delete the root folder")).launch()

    def on_cellrenderer_edited(self, cellrenderertext, path, new_text):
        iter = self.model.get_iter_from_string(path)
        filepath = self.model.get_value(iter, self.DIR_PATH)
        old_text = self.model.get_value(iter, self.DIR_TITLE)

        if old_text == new_text or new_text not in os.listdir(os.path.dirname(filepath)):
            newpath = os.path.join(os.path.dirname(filepath), new_text)
            os.rename(filepath, newpath)
            self.model.set_value(iter, self.DIR_TITLE, new_text)
            self.model.set_value(iter, self.DIR_PATH, newpath)
            self.model.set_value(iter, self.DIR_EDITABLE, False)
        else:
            ErrorDialog(_("Can't rename!\n\nThere are files in it!")).launch()

    def on_drag_data_get(self, treeview, context, selection, target_id, etime):
        treeselection = self.get_selection()
        model, iter = treeselection.get_selected()
        data = model.get_value(iter, self.DIR_PATH)
        log.debug("on_drag_data_get: %s" % data)

        if data != self.dir:
            selection.set(selection.get_target(), 8, data)

    def on_drag_data_received(self, treeview, context, x, y, selection, info, etime):
        '''If the source is coming from internal, then move it, or copy it.'''
        source = selection.get_data()

        if source:
            try:
                path, position = treeview.get_dest_row_at_pos(x, y)
                iter = self.model.get_iter(path)
            except:
                try:
                    iter = self.model.get_iter_first()
                except:
                    iter = self.model.append(None)

            target = self.model.get_value(iter, self.DIR_PATH)

            if self.is_same_object(context):
                file_action = 'move'
                dir_action = 'move'
            else:
                file_action = 'copy'
                dir_action = 'copytree'

            if '\r\n' in source:
                file_list = source.split('\r\n')
                for file in file_list:
                    if file:
                        self.file_operate(file, dir_action, file_action, target)
            else:
                self.file_operate(source, dir_action, file_action, target)

            self.update_model()
            context.finish(True, False, etime)
        else:
            context.finish(False, False, etime)

    def file_operate(self, source, dir_action, file_action, target):
        source = get_local_path(source)

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

    def update_model(self):
        self.model.clear()

        iter = self._setup_root_model()
        self.do_update_model(self.dir, iter)

        self.expand_all()

    def _create_model(self):
        model = Gtk.TreeStore(GdkPixbuf.Pixbuf,
                              GObject.TYPE_STRING,
                              GObject.TYPE_STRING,
                              GObject.TYPE_BOOLEAN)

        return model

    def _setup_root_model(self):
        pixbuf = icon.guess_from_path(self.dir, 24)

        iter = self.model.append(None, (pixbuf, os.path.basename(self.dir),
                                 self.dir, False))

        return iter

    def do_update_model(self, dir, iter):
        for item in os.listdir(dir):
            fullname = os.path.join(dir, item)
            pixbuf = icon.guess_from_path(fullname, 24)

            child_iter = self.model.append(iter,
                                           (pixbuf, os.path.basename(fullname),
                                            fullname, False))

            if os.path.isdir(fullname):
                self.do_update_model(fullname, child_iter)

    def _add_columns(self):
        try:
            self.type
        except:
            column = Gtk.TreeViewColumn()
        else:
            column = Gtk.TreeViewColumn(self.type)

        column.set_spacing(5)

        renderer = Gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.add_attribute(renderer, 'pixbuf', self.DIR_ICON)

        renderer = Gtk.CellRendererText()
        renderer.connect('edited', self.on_cellrenderer_edited)
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', self.DIR_TITLE)
        column.add_attribute(renderer, 'editable', self.DIR_EDITABLE)

        self.append_column(column)


class FlatView(Gtk.TreeView, CommonView):
    (FLAT_ICON,
     FLAT_TITLE,
     FLAT_PATH) = range(3)

    def __init__(self, dir, exclude_dir=None):
        GObject.GObject.__init__(self)

        self.set_rules_hint(True)
        self.dir = dir
        self.exclude_dir = exclude_dir

        self.model = Gtk.ListStore(GdkPixbuf.Pixbuf,
                                   GObject.TYPE_STRING,
                                   GObject.TYPE_STRING)

        self.set_model(self.model)
        self.update_model()
        self._add_columns()

        self.enable_drag_and_drop()

        self.connect("drag_data_get", self.on_drag_data_get_data)
        self.connect("drag_data_received", self.on_drag_data_received_data)

    def on_drag_data_get_data(self, treeview, context, selection, target_id, etime):
        treeselection = self.get_selection()
        model, iter = treeselection.get_selected()
        data = model.get_value(iter, self.FLAT_PATH)
        log.debug("selection set data to %s with %s" % (selection.get_target(), data))
        selection.set(selection.get_target(), 8, data)

    def on_drag_data_received_data(self, treeview, context, x, y, selection, info, etime):
        source = selection.get_data()

        if self.is_same_object(context) and source:
            try:
                path, position = treeview.get_dest_row_at_pos(x, y)
                iter = self.model.get_iter(path)
            except:
                iter = self.model.append(None)

            target = self.dir
            source = get_local_path(source)
            file_action = 'move'
            dir_action = 'move'

            if source in os.listdir(self.dir):
                os.remove(source)
            elif os.path.isdir(target) and not os.path.isdir(source):
                if os.path.dirname(source) != target:
                    if os.path.isdir(source):
                        getattr(shutil, dir_action)(source, target)
                    else:
                        if file_action == 'move' and os.path.exists(os.path.join
                                (target, os.path.basename(source))):
                            os.remove(source)
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
            context.finish(True, False, etime)
        else:
            context.finish(False, False, etime)

    def update_model(self):
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
            if title in self.exist_lsit:
                continue
            pixbuf = icon.guess_from_path(fullname, 24)

            self.model.append((pixbuf, title, fullname))

    def _add_columns(self):
        try:
            self.type
        except:
            column = Gtk.TreeViewColumn()
        else:
            column = Gtk.TreeViewColumn(self.type)

        column.set_spacing(5)

        renderer = Gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.add_attribute(renderer, 'pixbuf', self.FLAT_ICON)

        renderer = Gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', self.FLAT_TITLE)

        self.append_column(column)
