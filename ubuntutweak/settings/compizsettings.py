import logging

import ccm
import compizconfig

log = logging.getLogger('CompizSetting')

class CompizPlugin:
    context = compizconfig.Context()

    def __init__(self, name):
        self._plugin = self.context.Plugins[name]

    @classmethod
    def set_plugin_active(cls, name, active):
        try:
            plugin = cls.context.Plugins[name]
            plugin.Enabled = int(active)
            cls.context.Write()
        except:
            pass

    @classmethod
    def get_plugin_active(cls, name):
        try:
            plugin = cls.context.Plugins[name]
            return bool(plugin.Enabled)
        except:
            return False

    def set_enabled(self, bool):
        self._plugin.Enabled = int(bool)
        self.save()

    def get_enabled(self):
        return self._plugin.Enabled

    def save(self):
        self.context.Write()

    def resolve_conflict(self):
        conflicts = self.get_enabled() and self._plugin.DisableConflicts or \
                                           self._plugin.EnableConflicts
        conflict = ccm.PluginConflict(self._plugin, conflicts)
        return conflict.Resolve()

    @classmethod
    def is_available(cls, name, setting):
        return cls.context.Plugins.has_key(name) and \
               cls.context.Plugins[name].Screen.has_key(setting)

    def create_setting(self, key, target):
        settings = self._plugin.Screen

        if type(settings) == list:
            return settings[0][key]
        else:
            return settings[key]


class CompizSetting(object):
    def __init__(self, key, target=''):
        plugin_name, setting_name = key.split('.')
        self.key = key
        self._plugin = CompizPlugin(plugin_name)

        if not self._plugin.get_enabled():
            self._plugin.set_enabled(True)

        self._setting = self._plugin.create_setting(setting_name, target)

    def set_value(self, value):
        self._setting.Value = value
        self._plugin.save()

    def get_value(self):
        return self._setting.Value

    def is_default_and_enabled(self):
        return self._setting.Value == self._setting.DefaultValue and \
                self._plugin.get_enabled()

    def reset(self):
        self._setting.Reset()
        self._plugin.save()

    def resolve_conflict(self):
        return self._plugin.resolve_conflict()

    def get_schema_value(self):
        return self._setting.DefaultValue
