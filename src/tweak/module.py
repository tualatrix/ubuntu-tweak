import os
import gtk
import sys

class TweakModule:
    __name__ = ''
    __version__ = ''
    __author__ = ''
    __desc__ = ''
    __url__ = ''

    def __init__(self, path=None, domain='ubuntu-tweak'):
        assert(__name__ && __desc__)

        if path:
            self.builder = gtk.Builder()
            self.builder.set_translation_domain(domain)
            self.builder.add_from_file(path)
            self.builder.connect_signals(self)
            for o in self.builder.get_objects():
                if issubclass(type(o), gtk.Buildable):
                    name = gtk.Buildable.get_name(o)
                    setattr(self, name, o)
                else:
                    print >>sys.stderr, "WARNING: can not get name for '%s'" % o

    def reparent(self, parent):
        raise NotImplementedError
