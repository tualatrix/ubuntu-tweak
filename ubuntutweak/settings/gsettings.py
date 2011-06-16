import logging

from gi.repository import Gio

log = logging.getLogger('GSetting')

class GSetting(object):

    def __init__(self, key=None, default=None, type=None):
        parts = key.split('.')
        self.schema, self.key = '.'.join(parts[:-1]), parts[-1]

        self.type = type
        self.default = default
        self.settings = Gio.Settings(self.schema)

        if self.key not in self.settings.list_keys():
            log.error("No key (%s) in %s" % (self.key, self.schema))

        if default and self.get_value() == None:
            self.set_value(default)

    def get_value(self):
        try:
            return self.settings[self.key]
        except KeyError, e:
            log.error(e)

            if self.type == int:
                return 0
            elif self.type == float:
                return 0.0
            elif self.type == bool:
                return False
            elif self.type == str:
                return ''
            else:
                return None

    def set_value(self, value):
        try:
            self.settings[self.key] = value
        except KeyError, e:
            log.error(e)

    def connect_notify(self, func, data=None):
        self.settings.connect("changed::%s" % self.key, func, data)

    def unset(self):
        self.settings.reset(self.key)

    def get_schema_value(self):
        raise NotImplemented
