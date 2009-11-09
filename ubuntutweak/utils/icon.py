import os
import gtk

__all__ = (
    'get_with_name',
)

icontheme = gtk.icon_theme_get_default()

def get_with_list(list, size):
    pixbuf = None
    for name in list:
        try:
            pixbuf = icontheme.load_icon(name, size, 0)
        except:
            continue

    if pixbuf is None:
        return get_with_name('name', size=size)
    else:
        return pixbuf

def get_with_name(name, alter='gtk-execute', size=24):
    try:
        pixbuf = icontheme.load_icon(name, size, 0)
    except:
        pixbuf = icontheme.load_icon(alter, size, 0)

    if pixbuf.get_height() != size:
        return pixbuf.scale_simple(size, size, gtk.gdk.INTERP_BILINEAR)

    return pixbuf

def get_with_file(file, size=24):
    try:
        return gtk.gdk.pixbuf_new_from_file_at_size(file, size, size)
    except:
        return get_with_name('gtk-execute', size)
