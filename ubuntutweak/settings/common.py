import glob
import logging
import ConfigParser

from lxml import etree

log = logging.getLogger('CommonSetting')

class RawConfigSetting(object):
    '''Just pass the file path'''
    def __init__(self, path):
        self._type = type

        self._path = path

        self.init_configparser()

    def init_configparser(self):
        self._configparser = ConfigParser.ConfigParser()
        self._configparser.read(self._path)

    def sections(self):
        return self._configparser.sections()

    def options(self, section):
        return self._configparser.options(section)

    def get_value(self, section, option):
        value = self._configparser.get(section, option)
        #TODO deal with list
        if value == 'true':
            return True
        elif value == 'false':
            return False
        elif value.startswith('"') or value.startswith("'"):
            return eval(value)
        else:
            return value


class Schema(object):
    cached_schema = {}
    cached_schema_tree = {}
    cached_override = {}

    @classmethod
    def load_override(cls):
        for override in glob.glob('/usr/share/glib-2.0/schemas/*.gschema.override'):
            cs = RawConfigSetting(override)
            for section in cs.sections():
                cls.cached_override[section] = {}
                for option in cs.options(section):
                    cls.cached_override[section][option] = cs.get_value(section, option)

    @classmethod
    def load_schema(cls, schema_id, key):
        if not cls.cached_override:
            cls.load_override()

        if schema_id in cls.cached_override and \
                key in cls.cached_override[schema_id]:
            return cls.cached_override[schema_id][key]

        if schema_id in cls.cached_schema and \
                key in cls.cached_schema[schema_id]:
            return cls.cached_schema[schema_id][key]

        schema_defaults = {}

        for schema_path in glob.glob('/usr/share/glib-2.0/schemas/*'):
            if not schema_path.endswith('.gschema.xml') and not schema_path.endswith('.enums.xml'):
                #TODO deal with enums
                continue

            if schema_path in cls.cached_schema_tree:
                tree = cls.cached_schema_tree[schema_path]
            else:
                tree = etree.parse(open(schema_path))

            for schema_node in tree.findall('schema'):
                if schema_node.attrib.get('id') == schema_id:
                    for key_node in schema_node.findall('key'):
                        if key_node.findall('default'):
                            schema_defaults[key_node.attrib['name']] = cls.parse_value(key_node)
                else:
                    continue

                cls.cached_schema[schema_id] = schema_defaults
        if key in schema_defaults:
            return schema_defaults[key]
        else:
            return None

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
            elif type == 'i':
                return int(value)
            elif type == 'd':
                return float(value)
            elif type == 'as':
                return eval(value)

        return eval(value)
