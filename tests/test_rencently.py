import unittest

from ubuntutweak.app import UbuntuTweakWindow
from ubuntutweak.settings.gsettings import GSetting

class TestRencently(unittest.TestCase):
    def setUp(self):
        self.window = UbuntuTweakWindow()
        self.setting = GSetting('com.ubuntu-tweak.tweak.rencently-used')

    def test_rencetly(self):
        self.setting.set_value([])
        self.assertEqual(self.setting.get_value(), [])

        self.window.load_module('Icon')
        self.assertEqual(self.setting.get_value(), ['Icon'])

        self.window.load_module('Nautilus')
        self.assertEqual(self.setting.get_value(), ['Nautilus', 'Icon'])

    def tearDown(self):
        self.setting.set_value([])

if __name__ == '__main__':
    unittest.main()
