import os
import tempfile
import unittest

from ubuntutweak.settings.configsettings import ConfigSetting

class TestConfigSettings(unittest.TestCase):
    def setUp(self):
        self.unity_greeter_override_file = tempfile.NamedTemporaryFile(delete=False)
        self.unity_greeter_override_file.write("[com.canonical.unity-greeter]\n"
        "draw-grid = true\n"
        "play-ready-sound = false\n"
        "background = '/usr/share/backgrounds/The_Forbidden_City_by_Daniel_Mathis.jpg'\n")
        self.unity_greeter_override_file.close()
        self.unity_greeter_override_path = self.unity_greeter_override_file.name

    def test_config_settings(self):
        # draw grid
        draw_grid_setting_key = "%s::%s#%s" % (self.unity_greeter_override_path, 'com.canonical.unity-greeter', 'draw-grid')

        self.draw_grid_setting = ConfigSetting(draw_grid_setting_key, type=bool)
        self.assertEqual(True, self.draw_grid_setting.get_value())
        self.draw_grid_setting.set_value(False)
        self.assertEqual(False, self.draw_grid_setting.get_value())

        #try again the fuzz type
        self.draw_grid_setting = ConfigSetting(draw_grid_setting_key)
        self.assertEqual(False, self.draw_grid_setting.get_value())
        self.draw_grid_setting.set_value(True)
        self.assertEqual(True, self.draw_grid_setting.get_value())

        #play sound
        play_sound_key = self.get_key('play-ready-sound')
        self.play_sound_setting = ConfigSetting(play_sound_key)
        self.assertEqual(False, self.play_sound_setting.get_value())

        #background
        background_setting = ConfigSetting(self.get_key('background'), type=str)
        self.assertEqual('/usr/share/backgrounds/The_Forbidden_City_by_Daniel_Mathis.jpg', background_setting.get_value())
        #try again the fuzz type for str
        background_setting = ConfigSetting(self.get_key('background'))
        self.assertEqual("'/usr/share/backgrounds/The_Forbidden_City_by_Daniel_Mathis.jpg'", background_setting.get_value())

    def get_key(self, key):
        return "%s::%s#%s" % (self.unity_greeter_override_path, 'com.canonical.unity-greeter', key)


if __name__ == '__main__':
    unittest.main()
