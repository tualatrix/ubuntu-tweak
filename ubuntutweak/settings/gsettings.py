import os
import logging

from gi.repository import Gio

from ubuntutweak.settings.common import Schema

log = logging.getLogger('GSetting')


class GSetting(object):

    def __init__(self, key=None, default=None, type=None):
        parts = key.split('.')
        self.schema_id, self.key = '.'.join(parts[:-1]), parts[-1]

        self.type = type
        self.default = default
        self.schema_default = self.default or Schema.load_schema(self.schema_id, self.key)
        log.debug("Got the schema_default: %s for key: %s.%s" % \
                  (self.schema_default, self.schema_id, self.key))
        self.settings = Gio.Settings(self.schema_id)

        if self.key not in self.settings.list_keys():
            log.error("No key (%s) for schema %s" % (self.key, self.schema_id))

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
        log.debug("The the value for type: %s and value: %s" % (self.type, value))
        try:
            if self.type == str:
                self.settings.set_string(self.key, str(value))
            elif self.type == int:
                self.settings.set_int(self.key, int(value))
            elif self.type == float:
                self.settings.set_double(self.key, value)
            else:
                self.settings[self.key] = value
        except KeyError, e:
            log.error(e)

    def connect_notify(self, func, data=None):
        self.settings.connect("changed::%s" % self.key, func, data)

    def unset(self):
        self.settings.reset(self.key)

    def get_schema_value(self):
        if self.schema_default is not None:
            return self.schema_default
        else:
            raise NotImplemented
