import logging

from gi.repository import GObject, Gtk

log = logging.getLogger('gui.containers')

class BasePack(Gtk.VBox):
    def __init__(self, label):
        GObject.GObject.__init__(self)
        self.set_border_width(5)

        if label:
            title = Gtk.MenuItem(label=label)
            title.select()
            self.pack_start(title, False, False, 0)


class BaseListPack(BasePack):
    def __init__(self, title):
        BasePack.__init__(self, title)

        hbox = Gtk.HBox()
        hbox.set_border_width(5)
        self.pack_start(hbox, True, False, 0)

        label = Gtk.Label(label=" ")
        hbox.pack_start(label, False, False, 0)

        self.vbox = Gtk.VBox()
        hbox.pack_start(self.vbox, True, True, 0)


class SinglePack(BasePack):
    def __init__(self, title, widget):
        BasePack.__init__(self, title)

        self.pack_start(widget, True, True, 10)


class ListPack(BaseListPack):
    def __init__(self, title, widgets, padding=6):
        BaseListPack.__init__(self, title)
        self.items = []

        if widgets:
            for widget in widgets:
                if widget: 
                    if widget.get_parent():
                        widget.unparent()
                    self.vbox.pack_start(widget, False, False, padding)
                    self.items.append(widget)
        else:
            self = None


class EasyTable(Gtk.Table):
    def __init__(self, items=[], xpadding=6, ypadding=6):
        GObject.GObject.__init__(self)

        columns = 1
        for i, item in enumerate(items):
            rows = i + 1
            if len(item) > columns:
                columns = len(item)

        self.set_property('n-rows', rows)
        self.set_property('n-columns', columns)

        for item in items:
            if item is not None:
                top_attach = items.index(item)

                if issubclass(item.__class__, Gtk.Widget):
                    self.attach(item, 0, columns, top_attach,
                                top_attach + 1, ypadding=ypadding)
                else:
                    for widget in item:
                        if widget:
                            left_attch = item.index(widget)

                            if type(widget) == Gtk.Label:
                                widget.set_alignment(0, 0.5)

                            if left_attch == 1:
                                self.attach(widget, left_attch,
                                            left_attch + 1, top_attach,
                                            top_attach + 1, xpadding=xpadding,
                                            ypadding=ypadding)
                            else:
                                self.attach(widget, left_attch,
                                            left_attch + 1, top_attach,
                                            top_attach + 1, Gtk.AttachOptions.FILL,
                                            ypadding=ypadding)



class TablePack(BaseListPack):
    def __init__(self, title, items):
        BaseListPack.__init__(self, title)

        table = EasyTable(items, xpadding=12)

        self.vbox.pack_start(table, True, True, 0)

class GridPack(Gtk.Grid):
    def __init__(self, *items):
        GObject.GObject.__init__(self)

        self._column = 1
        for i, item in enumerate(items):
            rows = i + 1
            if hasattr(item, '__len__') and len(item) > self._column:
                self._column = len(item)

        log.debug("There are totally %d columns" % self._column)

        self.set_property('row-spacing', 6)
        self.set_property('column-spacing', 6)
        self.set_property('margin-left', 15)
        self.set_property('margin-right', 15)
        self.set_property('margin-top', 5)
        self._items = items

        self._insert_items()

        self.connect('size-allocate', self.on_grid_size_allocate)

    def on_grid_size_allocate(self, widget, allocation):
        size_list = []
        for item in self._items:
            if not issubclass(item.__class__, Gtk.Widget):
                for widget in item:
                    if widget and type(widget) != Gtk.Label and \
                        widget.get_property('hexpand') and \
                        not hasattr(widget, 'get_default_value') and \
                        not issubclass(widget.__class__, Gtk.Switch):
                            width = widget.get_allocation().width
#                            log.debug("Do width calculate for child: %s, %d" % (widget, width))
                            size_list.append(width)

        if size_list:
            max_size = max(size_list)

        if size_list and max_size * len(size_list) != sum(size_list):
            for item in self._items:
                if not issubclass(item.__class__, Gtk.Widget):
                    for widget in item:
                        if widget and type(widget) != Gtk.Label and \
                            widget.get_property('hexpand') and \
                            not hasattr(widget, 'get_default_value') and \
                            not issubclass(widget.__class__, Gtk.Switch):
#                                log.debug("Set new width for child: %s with: %d" % (widget, max_size))
                                widget.set_size_request(max_size, -1)

    def _insert_items(self):
        for top_attach, item in enumerate(self._items):
            log.debug("Found item: %s" % str(item))
            if item is not None:
                if issubclass(item.__class__, Gtk.Widget):
                    if issubclass(item.__class__, Gtk.Separator):
                        item.set_size_request(-1, 20)
                        left = 0
                        top = top_attach + 1
                        width = self._column
                        height = 1
                    elif issubclass(item.__class__, Gtk.CheckButton) or \
                         issubclass(item.__class__, Gtk.Box):
                        left = 1
                        top = top_attach + 1
                        width = 1
                        height = 1
                    else:
                        left = getattr(item, '_ut_left', 0)
                        top = top_attach + 1
                        width = self._column
                        height = 1

                    log.debug("Attach item: %s to Grid: %s,%s,%s,%s\n" % \
                              (str(item), left, top, width, height))
                    self.attach(item, left, top, width, height)
                else:
                    for left_attch, widget in enumerate(item):
                        if widget:
                            if type(widget) == Gtk.Label:
                                widget.set_property('halign', Gtk.Align.END)
                                widget.set_property('hexpand', True)
                            else:
                                if issubclass(widget.__class__, Gtk.Switch) or \
                                issubclass(widget.__class__, Gtk.CheckButton) or \
                                hasattr(widget, 'get_default_value'):
                                    #so this is reset button

                                    log.debug("Set the widget(%s) Align START" % widget)
                                    widget.set_property('halign', Gtk.Align.START)
                                else:
                                    log.debug("Set the widget(%s) width to 200" % widget)
                                    # The initial value is 200, but maybe larger in gird_size_allocate
                                    widget.set_size_request(200, -1)
                                    # If widget is not the last column, so not set the  Align START, just make it fill the space
                                    if left_attch + 1 == self._column:
                                        widget.set_property('halign', Gtk.Align.START)
                                # If widget is not the last column, so not set the  hexpand to True, so it will not take the same size of column as others
                                if left_attch + 1 == self._column:
                                    widget.set_property('hexpand', True)

                            log.debug("Attach widget: %s to Grid: %s,%s,1,1\n" % (str(widget), left_attch, top_attach + 1))
                            self.attach(widget, 
                                        left_attch,
                                        top_attach + 1,
                                        1, 1)
