import os
import glob
import logging

from lxml import etree
from gi.repository import Gio

log = logging.getLogger('GSetting')

class Schema(object):
    cached_schema = {}
    cached_schema_tree = {}

    @classmethod
    def load_schema(cls, schema_id):
        if schema_id in cls.cached_schema:
            return cls.cached_schema[schema_id]

        schema_defaults = {}

        for schema_path in glob.glob('/usr/share/glib-2.0/schemas/*'):
            if not schema_path.endswith('.gschema.xml') and not schema_path.endswith('.enums.xml'):
                continue

            if schema_path in cls.cached_schema_tree:
                tree = cls.cached_schema_tree[schema_path]
            else:
                tree = etree.parse(open(schema_path))

            for schema_node in tree.findall('schema'):
                if schema_node.attrib.get('id') == schema_id:
                    for key_node in schema_node.findall('key'):
                        if key_node.findall('default'):
                            log.debug("Find the default value of %s/%s: %s" % \
                                    (schema_id,
                                     key_node.attrib['name'],
                                     key_node.find('default').text))

                            schema_defaults[key_node.attrib['name']] = cls.parse_value(key_node)
                else:
                    continue

                cls.cached_schema[schema_id] = schema_defaults
        return schema_defaults

    @classmethod
    def parse_value(cls, key_node):
        log.debug("Try to get type for value: %s" % key_node.items())
        value = key_node.find('default').text

        #TODO enum type
        if key_node.attrib.get('type'):
            type = key_node.attrib['type']

            if type == 'b':
                if value == 'true':
                    return True
                else:
                    return False

        return value


class GSetting(object):

    def __init__(self, key=None, default=None, type=None):
        parts = key.split('.')
        self.schema_id, self.key = '.'.join(parts[:-1]), parts[-1]

        self.type = type
        self.default = default
        self.schema_defaults = Schema.load_schema(self.schema_id)
        log.debug("Got the schema_defaults: %s" % self.schema_defaults)
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
                self.settings.set_string(self.key, value)
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
        if self.key in self.schema_defaults:
            return self.schema_defaults[self.key]
        else:
            raise NotImplemented
