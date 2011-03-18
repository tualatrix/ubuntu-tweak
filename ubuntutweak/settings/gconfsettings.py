import logging

from gi.repository import GConf

log = logging.getLogger('GconfSetting')

class GconfSetting(object):
    """
    The base class of an option, client is shared by all subclass
    Every Setting hold a key and a value
    """

    client = GConf.Client.get_default()

    def __init__(self, key=None, default=None, type=None):
        self.key = key
        self.type = type
        self.default = default

        if default and self.get_value() is None:
            self.set_value(default)

        if self.get_dir():
            self.client.add_dir(self.get_dir(), GConf.ClientPreloadType.PRELOAD_NONE)

    def get_dir(self):
        if self.key:
            return '/'.join(self.key.split('/')[0: -1])
        else:
            return None

    def get_value(self):
        gconfvalue = self.client.get(self.key)
        if gconfvalue:
            if gconfvalue.type == GConf.ValueType.BOOL:
                return gconfvalue.get_bool()
            if gconfvalue.type == GConf.ValueType.STRING:
                return gconfvalue.get_string()
            if gconfvalue.type == GConf.ValueType.INT:
                return gconfvalue.get_int()
            if gconfvalue.type == GConf.ValueType.FLOAT:
                return gconfvalue.get_float()
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
        gconfvalue = GConf.Value()

        if type(value) == bool:
            gconfvalue.type = GConf.ValueType.BOOL
            gconfvalue.set_bool(value)
        elif type(value) == str:
            gconfvalue.type = GConf.ValueType.STRING
            gconfvalue.set_string(value)
        elif type(value) == int:
            gconfvalue.type = GConf.ValueType.INT
            gconfvalue.set_int(value)
        elif type(value) == float:
            gconfvalue.type = GConf.ValueType.FLOAT
            gconfvalue.set_float(value)

        self.client.set(self.key, gconfvalue)

    def unset(self):
        self.client.unset(self.key)

    def connect_notify(self, func, data=None):
        self.client.notify_add(self.key, func, data)

    def get_schema_value(self):
        value = self.client.get_default_from_schema(self.key)
        if value:
            if value.type == GConf.ValueType.BOOL:
                return value.get_bool()
            elif value.type == GConf.ValueType.STRING:
                return value.get_string()
            elif value.type == GConf.ValueType.INT:
                return value.get_int()
            elif value.type == GConf.ValueType.FLOAT:
                return value.get_float()
        else:
            raise Exception("No schema value for %s" % self.key)
