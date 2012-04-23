import logging

log = logging.getLogger('ConfigSetting')


from ubuntutweak.settings.common import RawConfigSetting, Schema

class ConfigSetting(RawConfigSetting):
    '''Key: /etc/lightdm/lightdm.conf::UserManager#load-users
    '''

    schema_path = '/usr/share/glib-2.0/schemas'

    def __init__(self, key=None, default=None, type=None):
        self._path = key.split('::')[0]
        self._type = type
        self._default = default
        self.key = key
        self._section = key.split('::')[1].split('#')[0]
        self._option = key.split('::')[1].split('#')[1]

        if self.is_override_schema(self._path):
            self._path = self.build_schema_path(self._path)
            self.key = self.build_schema_path(self.key)
            log.debug("is override schema, so update path to %s" % self._path)
            self.schema_default = default or Schema.load_schema(self._section, self._option)
            log.debug("schema_default is %s" % self.schema_default)

        log.debug("Build ConfigSetting for path: %s\n"
                  "\tkey: %s\n"
                  "\tdefault: %s, type: %s\n" % (self._path,
                                                 self.key,
                                                 self._default, 
                                                 self._type))

        RawConfigSetting.__init__(self, self._path, type=self._type)

    def build_schema_path(self, path):
        if not path.startswith(self.schema_path):
            return '%s/%s' % (self.schema_path, path)
        else:
            return path

    def set_value(self, value):
        super(ConfigSetting, self).set_value(self._section, self._option, value)

    def get_value(self):
        try:
            value = super(ConfigSetting, self).get_value(self._section, self._option)

            log.debug("ConfigSetting.get_value: %s, %s, %s" % (value, self._default, hasattr(self, 'schema_default')))
            return value
        except Exception, e:
            log.error(e)

            if self._default != None or hasattr(self, 'schema_default'):
                return self._default or getattr(self, 'schema_default')
            if self._type == int:
                return 0
            elif self._type == float:
                return 0.0
            elif self._type == bool:
                return False
            elif self._type == str:
                return ''
            else:
                return None

    def get_key(self):
        return self.key

    def is_override_schema(self, path=None):
        test_path = path or self._path
        return test_path.endswith('override')


class SystemConfigSetting(ConfigSetting):
    def set_value(self, value):
        # Because backend/daemon will use ConfigSetting , proxy represents the
        # daemon, so lazy import the proxy here to avoid backend to call proxy
        from ubuntutweak.policykit.dbusproxy import proxy
        value = self._type_convert_set(value)

        proxy.set_config_setting(self.get_key(), value)

        self.init_configparser()
