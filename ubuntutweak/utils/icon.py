import os
import random
import logging

from gi.repository import Gdk
from gi.repository import Gtk, Gdk, Gio

log = logging.getLogger("utils.icon")

__all__ = (
    'get_from_name',
)

icontheme = Gtk.IconTheme.get_default()

DEFAULT_SIZE = 24

def get_from_name(name='gtk-execute', alter='gtk-execute', size=DEFAULT_SIZE, force_reload=False):
    pixbuf = None

    if force_reload:
        global icontheme
        icontheme = Gtk.IconTheme.get_default()

    try:
        pixbuf = icontheme.load_icon(name, size, 0)
    except Exception, e:
        log.error(e)
        # if the alter name isn't here, so use random icon

        while not pixbuf:
            try:
                pixbuf = icontheme.load_icon(alter, size, 0)
            except Exception, e:
                log.error(e)
                icons = icontheme.list_icons()
                alter = icons[random.randint(0, len(icons) - 1)]

    if pixbuf.get_height() != size:
        return pixbuf.scale_simple(size, size, GdkPixbuf.InterpType.BILINEAR)

    return pixbuf

def get_from_list(list, size=DEFAULT_SIZE):
    pixbuf = None
    for name in list:
        try:
            pixbuf = icontheme.load_icon(name, size, 0)
        except:
            continue

    if pixbuf is None:
        return get_from_name('name', size=size)
    else:
        return pixbuf

def get_from_mime_type(mime, size=DEFAULT_SIZE):
    try:
        gicon = Gio.content_type_get_icon(mime)
        iconinfo = icontheme.choose_icon(gicon.get_names(), size, Gtk.IconLookupFlags.USE_BUILTIN)
        if not iconinfo:
            pixbuf = get_icon_with_name('application-x-executable', size)
        else:
            pixbuf = iconinfo.load_icon()

        if pixbuf.get_width() != size:
            return pixbuf.scale_simple(size, size, GdkPixbuf.InterpType.BILINEAR)
    except:
        return get_from_name(size=size)

    return pixbuf

def get_from_file(file, size):
    try:
        return GdkPixbuf.Pixbuf.new_from_file_at_size(file, size, size)
    except:
        return get_from_name(size=size)

def get_from_app(app, size=DEFAULT_SIZE):
    try:
        gicon = app.get_icon()

        if gicon:
            if isinstance(gicon, Gio.ThemedIcon):
                names = gicon.get_names()
                names_list = []
                for name in names:
                    if name.rfind('.') != -1:
                        names_list.append(name[:name.rfind('.')])
                    else:
                        names_list.append(name)

                iconinfo = icontheme.choose_icon(names_list, size, Gtk.IconLookupFlags.USE_BUILTIN)
                if iconinfo:
                    return iconinfo.load_icon()
            elif isinstance(gicon, Gio.FileIcon):
                file = app.get_icon().get_file().get_path()
                return get_from_file(file, size)

        return get_icon_with_name('application-x-executable', size)
    except:
        return get_from_name(size=size)

def guess_from_path(filepath, size=DEFAULT_SIZE):
    if os.path.isdir(filepath):
        return get_from_name('folder', size)

    try:
        mime_type = Gio.content_type_guess(filepath, open(filepath).read(10))
        return get_from_mime_type(mime_type, size)
    except Exception, e:
        print e
        return get_from_name(size=size)

if __name__ == '__main__':
    print get_from_name('ok', alter='ko')
