import unittest

from ubuntutweak.main import UbuntuTweakWindow
from ubuntutweak.settings.gsettings import GSetting

class TestRecently(unittest.TestCase):
    def setUp(self):
        self.window = UbuntuTweakWindow()
        self.window.loaded_modules = {}
        self.window.modules_index = {}
        self.window.navigation_dict = {'tweaks': [None, None]}
        self.setting = GSetting('com.ubuntu-tweak.tweak.rencently-used')

    def test_recently(self):
        self.setting.set_value([])
        self.assertEqual(self.setting.get_value(), [])

        self.window._load_module('Icon')
        self.assertEqual(self.setting.get_value(), ['Icon'])

        self.window._load_module('Nautilus')
        self.assertEqual(self.setting.get_value(), ['Nautilus', 'Icon'])

    def tearDown(self):
        self.setting.set_value([])
        del self.window

if __name__ == '__main__':
    unittest.main()
