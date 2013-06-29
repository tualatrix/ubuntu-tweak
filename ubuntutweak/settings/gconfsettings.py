import glob
import logging

from gi.repository import GConf

from ubuntutweak.policykit.dbusproxy import proxy

log = logging.getLogger('GconfSetting')

class GconfSetting(object):
    """
    The base class of an option, client is shared by all subclass
    Every Setting hold a key and a value
    """

    client = GConf.Client.get_default()
    schema_override = {}

    def __init__(self, key=None, default=None, type=None):
        if not self.schema_override:
            self.load_override()

        self.key = key
        self.type = type
        self.default = default
        log.debug("Got the schema_default: %s for key: %s" % \
                    (self.default, self.key))

        if default and self.get_value() is None:
            self.set_value(default)

        if self.get_dir():
            self.client.add_dir(self.get_dir(), GConf.ClientPreloadType.PRELOAD_NONE)

    def load_override(self):
        for override in glob.glob('/usr/share/gconf/defaults/*'):
            try:
                for line in open(override):
                    splits = line.split()
                    key, value = splits[0], ' '.join(splits[1:])

                    if value == 'true':
                        value = True
                    elif value == 'false':
                        value = False
                    else:
                        if value.startswith('"') and value.endswith('"'):
                            value = eval(value)

                    self.schema_override[key] = value
            except Exception, e:
                log.error('Exception (%s) while processing override' % e)

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
            if gconfvalue.type == GConf.ValueType.LIST:
                final_list = []
                if gconfvalue.get_list_type() == GConf.ValueType.STRING:
                    for item in gconfvalue.get_list():
                        final_list.append(item.get_string())
                return final_list
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
        if self.type and type(value) != self.type:
            value = self.type(value)

        gconfvalue = GConf.Value()

        if type(value) == bool:
            gconfvalue.type = GConf.ValueType.BOOL
            gconfvalue.set_bool(value)
        elif type(value) == str:
            gconfvalue.type = GConf.ValueType.STRING
            gconfvalue.set_string(value)
        elif type(value) == int:
            gconfvalue.type = GConf.ValueType.INT
            gconfvalue.set_int(int(value))
        elif type(value) == float:
            gconfvalue.type = GConf.ValueType.FLOAT
            gconfvalue.set_float(value)

        self.client.set(self.key, gconfvalue)

    def unset(self):
        self.client.unset(self.key)

    def connect_notify(self, func, data=None):
        self.client.notify_add(self.key, func, data)

    def get_schema_value(self):
        if not self.default:
            if self.key in self.schema_override:
                value = self.schema_override[self.key]
                if self.type and self.type != type(value):
                    log.debug("get_schema_value: %s, the type is wrong, so convert force" % value)
                    return self.type(value)
                return value

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
        else:
            return self.default


class UserGconfSetting(GconfSetting):
    def get_value(self, user):
        data = str(proxy.get_user_gconf(user, self.key))
        log.debug('UserGconfSetting get the value from proxy: %s', data)
        if data == 'true':
            return True
        elif data == 'false':
            return False
        else:
            return data

    def set_value(self, user, value):
        if value:
            if type(value) == bool:
                proxy.set_user_gconf(user, self.key, 'true', 'bool', '')
            elif type(value) == str:
                proxy.set_user_gconf(user, self.key, value, 'string', '')
        else:
            proxy.set_user_gconf(user, self.key, 'false', 'bool', '')
