import glob
import logging
import ConfigParser

from lxml import etree


log = logging.getLogger('CommonSetting')

class RawConfigSetting(object):
    '''Just pass the file path'''
    def __init__(self, path, type=type):
        self._type = type

        self._path = path

        self.init_configparser()

    def _type_convert_set(self, value):
        if type(value) == bool:
            if value == True:
                value = 'true'
            elif value == False:
                value = 'false'

        # This is a hard code str type, so return '"xxx"' instead of 'xxx'
        if self._type == str:
            value = "'%s'" % value

        return value

    def _type_convert_get(self, value):
        if value == 'false':
            value = False
        elif value == 'true':
            value = True

        # This is a hard code str type, so return '"xxx"' instead of 'xxx'
        if self._type == str:
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = eval(value)

        return value

    def init_configparser(self):
        self._configparser = ConfigParser.ConfigParser()
        self._configparser.read(self._path)

    def sections(self):
        return self._configparser.sections()

    def options(self, section):
        return self._configparser.options(section)

    def set_value(self, section, option, value):
        value = self._type_convert_set(value)

        if not self._configparser.has_section(section):
            self._configparser.add_section(section)

        self._configparser.set(section, option, value)
        with open(self._path, 'wb') as configfile:
            self._configparser.write(configfile)

        self.init_configparser()

    def get_value(self, section, option):
        if self._type:
            if self._type == int:
                getfunc = getattr(self._configparser, 'getint')
            elif self._type == float:
                getfunc = getattr(self._configparser, 'getfloat')
            elif self._type == bool:
                getfunc = getattr(self._configparser, 'getboolean')
            else:
                getfunc = getattr(self._configparser, 'get')

            value = getfunc(section, option)
        else:
            log.debug("No type message, so use the generic get")
            value = self._configparser.get(section, option)

        value = self._type_convert_get(value)

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
