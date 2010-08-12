import logging
import gconf

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from ubuntutweak.common import consts
from ubuntutweak.policykit import proxy
from ubuntutweak.common.systeminfo import GnomeVersion

log = logging.getLogger("gconfsetting")

class KeysHandler(ContentHandler):
    def __init__(self, dict):
        self.dict = dict

    def startElement(self, name, attrs):
        if name == 'key':
            if attrs.has_key('version'):
                version = attrs['version']

                if len(version.split(':')) == 2:
                        start, end = version.split(':')
                        if int(start) <= int(GnomeVersion.minor) <= int(end):
                            self.dict[attrs['name']] = attrs['value']
                else:
                    if GnomeVersion.minor == version:
                        self.dict[attrs['name']] = attrs['value']
            else:
                self.dict[attrs['name']] = attrs['value']

class GconfKeys:
    '''This class used to store the keys, it will create for only once'''
    keys = {}
    parser = make_parser()
    handler = KeysHandler(keys)
    parser.setContentHandler(handler)
    parser.parse('%s/keys.xml' % consts.DATA_DIR)

class GconfSetting(object):
    """
    The base class of an option, client is shared by all subclass
    Every Setting hold a key and a value
    """

    __client = gconf.client_get_default()

    def __init__(self, key=None, default=None, type=None):
        self.__key = key
        self.__type = type
        self.__default = default

        if default and self.get_value() is None:
            self.set_value(default)

        if self.get_dir():
            self.get_client().add_dir(self.get_dir(), gconf.CLIENT_PRELOAD_NONE)

    def get_default(self):
        return self.__default

    def set_default(self, default):
        self.__default = default

    def get_key(self):
        return self.__key

    def set_key(self, key):
        if key and not key.startswith("/"):
            key = GconfKeys.keys[key]

        self.__key = key

    def get_dir(self):
        if self.__key:
            return '/'.join(self.__key.split('/')[0: -1])
        else:
            return None

    def __get_none_value_by_type(self):
        if self.__type == int:
            return 0
        elif self.__type == float:
            return 0.0
        elif self.__type == bool:
            return False
        elif self.__type == str:
            return ''
        else:
            return None

    def get_value(self):
        try:
            if self.__type:
                return self.__type(self.__client.get_value(self.__key))
            else:
                return self.__client.get_value(self.__key)
        except:
            if self.__default is not None:
                self.set_value(self.__default)
                return self.__default
            else:
                return self.__get_none_value_by_type()

    def set_value(self, value):
        if self.__type:
            self.__client.set_value(self.__key, self.__type(value))
        else:
            self.__client.set_value(self.__key, value)

    def get_client(self):
        return self.__client

    def unset(self):
        self.__client.unset(self.__key)

    def connect_notify(self, func, data=None):
        self.__client.notify_add(self.__key, func, data)

    def get_schema_value(self):
        value = self.__client.get_default_from_schema(self.__key)
        if value:
            if value.type == gconf.VALUE_BOOL:
                return value.get_bool()
            elif value.type == gconf.VALUE_STRING:
                return value.get_string()
            elif value.type == gconf.VALUE_INT:
                return value.get_int()
            elif value.type == gconf.VALUE_FLOAT:
                return value.get_float()
        else:
            raise Exception("No schema value for %s" % self.__key)

class SystemGconfSetting(GconfSetting):
    def get_value(self):
        data = proxy.get_system_gconf(self.get_key())
        if str(data).startswith('true'):
            return True
        else:
            return False

    def set_value(self, value):
        if value:
            proxy.set_system_gconf(self.get_key(), 'true', 'bool', '')
        else:
            proxy.set_system_gconf(self.get_key(), 'false', 'bool', '')

class UserGconfSetting(GconfSetting):
    def get_value(self, user):
        data = str(proxy.get_user_gconf(user, self.get_key()))
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
                proxy.set_user_gconf(user, self.get_key(), 'true', 'bool', '')
            elif type(value) == str:
                proxy.set_user_gconf(user, self.get_key(), value, 'string', '')
        else:
            proxy.set_user_gconf(user, self.get_key(), 'false', 'bool', '')
