import logging

from gi.repository import Gio

log = logging.getLogger('GioSetting')


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
        variant = self.settings.get_value(self.key)

        if variant is not None:
            type_string = variant.get_type_string()
            if type_string == 'b':
                return variant.get_boolean()
            elif type_string == 's':
                return variant.get_string()
            elif type_string == 'as':
                return variant.get_strv()
        else:
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
        variant = self.settings.get_value(self.key)

        if variant is not None:
            type_string = variant.get_type_string()
            if type_string == 'b':
                return self.settings.set_boolean(self.key, bool(value))
            elif type_string == 's':
                return self.settings.set_string(self.key, str(value))
            elif type_string == 'as':
                #TODO should check the value is like "['xx']"
                return self.settings.set_strv(self.key, eval(value))

    def connect_notify(self, func, data=None):
        self.settings.connect("changed::%s" % self.key, func, data)

    def unset(self):
        self.settings.reset(self.key)

    def get_schema_value(self):
        raise NotImplemented
