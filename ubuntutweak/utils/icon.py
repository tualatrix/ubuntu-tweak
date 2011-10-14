import os
import random
import logging

from gi.repository import Gtk, Gdk, Gio, GdkPixbuf

log = logging.getLogger("utils.icon")

icontheme = Gtk.IconTheme.get_default()
icontheme.append_search_path('/usr/share/ccsm/icons')

DEFAULT_SIZE = 24

def get_from_name(name='gtk-execute', alter='gtk-execute',
                  size=DEFAULT_SIZE, force_reload=False):
    pixbuf = None

    if force_reload:
        global icontheme
        icontheme = Gtk.IconTheme.get_default()

    try:
        pixbuf = icontheme.load_icon(name, size, 0)
    except Exception, e:
        log.warning(e)
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
            pixbuf = icontheme.load_icon(name,
                                         size,
                                         Gtk.IconLookupFlags.USE_BUILTIN)
        except Exception, e:
            log.warning('get_from_list for %s failed, try next' % name)
            continue

    return pixbuf or get_from_name('application-x-executable', size=size)

def get_from_mime_type(mime, size=DEFAULT_SIZE):
    try:
        gicon = Gio.content_type_get_icon(mime)

        return get_from_list(gicon.get_names(), size=size)
    except Exception, e:
        log.error('get_from_mime_type failed: %s' % e)
        return get_from_name(size=size)

    return pixbuf

def get_from_file(file, size=DEFAULT_SIZE):
    try:
        return GdkPixbuf.Pixbuf.new_from_file_at_size(file, size, size)
    except Exception, e:
        log.error('get_from_file failed: %s' % e)
        return get_from_name(size=size)

def get_from_app(app, size=DEFAULT_SIZE):
    try:
        gicon = app.get_icon()
        pixbuf = None

        if gicon:
            if isinstance(gicon, Gio.ThemedIcon):
                return get_from_list(gicon.get_names(), size=size)
            elif isinstance(gicon, Gio.FileIcon):
                file = app.get_icon().get_file().get_path()
                return get_from_file(file, size)
        if not pixbuf:
            return get_from_name('application-x-executable', size=size)
    except Exception, e:
        log.error('get_from_app failed: %s' % e)
        return get_from_name(size=size)

def guess_from_path(filepath, size=DEFAULT_SIZE):
    if os.path.isdir(filepath):
        return get_from_name('folder', size)

    try:
        mime_type, result = Gio.content_type_guess(filepath, open(filepath).read(10))
        return get_from_mime_type(mime_type, size)
    except Exception, e:
        log.error('guess_from_path failed: %s' % e)
        return get_from_name(size=size)

if __name__ == '__main__':
    print get_from_name('ok', alter='ko')
