import logging

from gi.repository import GObject, Gtk, Pango

from ubuntutweak.gui import GuiBuilder
from ubuntutweak.utils import icon

log = logging.getLogger('apps')

class AppObject(object):
    name = ''
    icon_name = ''

    def __init__(self, name, icon_name):
        self.name = name
        self.icon_name = icon_name


class AppButton(Gtk.Button):

    _app = None

    def __init__(self, app):
        GObject.GObject.__init__(self)

        log.info('Creating AppButton: %s' % app)

        self.set_relief(Gtk.ReliefStyle.NONE)

        self._app = app

        hbox = Gtk.HBox(spacing=6)
        self.add(hbox)

        image = Gtk.Image.new_from_pixbuf(icon.get_from_name(app.icon_name, size=48))
        hbox.pack_start(image, False, False, 0)

        label = Gtk.Label(label=app.name)
        label.set_alignment(0, 0.5)
        label.set_line_wrap(True)
        label.set_line_wrap_mode(Pango.WrapMode.WORD)
        label.set_size_request(90, -1)
        hbox.pack_start(label, False, False, 0)

    def get_app(self):
        return self._app


class AppCategoryBox(Gtk.VBox):
    _apps = None
    _buttons = None
    _current_cols = 0
    _current_apps = 0

    def __init__(self, apps=None, category='', category_name=''):
        GObject.GObject.__init__(self)

        self._apps = apps

        self.set_spacing(6)

        header = Gtk.HBox()
        header.set_spacing(12)
        label = Gtk.Label()
        label.set_markup("<span color='#aaa' size='x-large' weight='640'>%s</span>" % category_name)
        header.pack_start(label, False, False, 0)

        self._table = Gtk.Table()

        self._buttons = []
        for app in self._apps:
            self._buttons.append(AppButton(app))

        self.pack_start(header, False, False, 0)
        self.pack_start(self._table, False, False, 0)

    def get_apps(self):
        return self._apps

    def get_buttons(self):
        return self._buttons

    def rebuild_table (self, ncols, force=False):
        if (not force and ncols == self._current_cols and
                len(self._apps) == self._current_apps):
            return
        self._current_cols = ncols
        self._current_apps = len(self._apps)

        children = self._table.get_children()
        if children:
            for child in children:
                self._table.remove(child)

        row = 0
        col = 0
        for button in self._buttons:
            if button.get_app() in self._apps:
                self._table.attach(button, col, col + 1, row, row + 1, 0,
                                   xpadding=4, ypadding=2)
                col += 1
                if col == ncols:
                    col = 0
                    row += 1
        self.show_all()


class AppsView(Gtk.ScrolledWindow):

    def __init__(self):
        GObject.GObject.__init__(self,
                                 shadow_type=Gtk.ShadowType.NONE,
                                 hscrollbar_policy=Gtk.PolicyType.NEVER,
                                 vscrollbar_policy=Gtk.PolicyType.AUTOMATIC)
        self.set_border_width(12)

        self._categories = {}
        self._boxes = []

        self._box = Gtk.VBox(spacing=6)

        category_box = AppCategoryBox(apps=(AppObject('Leafpad', 'leafpad'),
                                            AppObject('Ubuntu Tweak', 'ubuntu-tweak'),
                                            AppObject('Terminal', 'gnome-terminal'),
                                            AppObject('Evolution', 'evolution'),
                                            AppObject('Pagico', 'pagico'),
                                            ),
                       category_name='Text')
        self._connect_signals(category_box)
        self._boxes.append(category_box)
        self._box.pack_start(category_box, False, False, 0)

        category_box = AppCategoryBox(apps=(AppObject('Shutter', 'shutter'),
                                            AppObject('LibreOffice Writer', 'libreoffice-writer'),
                                            AppObject('Firefox', 'firefox'),
                                            ),
                       category_name='Utils')
        self._connect_signals(category_box)
        self._boxes.append(category_box)
        self._box.pack_start(category_box, False, False, 0)

        viewport = Gtk.Viewport(shadow_type=Gtk.ShadowType.NONE)
        viewport.add(self._box)
        self.add(viewport)
        self.connect('size-allocate', self.rebuild_boxes)

    def _connect_signals(self, category_box):
        for button in category_box.get_buttons():
            button.connect('clicked', self.on_button_clicked)

    def on_button_clicked(self, widget):
        log.info('Button clicked')
        module = widget.get_module()
        self.emit('module_selected', module.get_name())


    def rebuild_boxes(self, widget, request):
        ncols = request.width / 148 # 48 + 72 + 6 + 4
        width = ncols * (148 + 2 * 4) + 40
        if width > request.width:
            ncols -= 1

        pos = 0
        last_box = None
        children = self._box.get_children()
        for box in self._boxes:
            modules = box.get_apps()
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


class AppsPage(Gtk.VBox, GuiBuilder):
    def __init__(self):
        GObject.GObject.__init__(self)
        GuiBuilder.__init__(self, 'appspage.ui')

        self.hpaned1.reparent(self)
        self.hpaned1.add2(AppsView())

        self.update_model()
        self.show_all()

    def update_model(self):
        self.category_model.append(None, (0, 'Featured'))
        self.category_model.append(None, (1, 'New Added'))
        iter = self.category_model.append(None, (2, 'All Apps'))
        self.category_model.append(iter, (3, 'Desktop'))
        self.category_model.append(iter, (4, 'Email'))
        self.category_model.append(None, (1, 'All Installed'))
