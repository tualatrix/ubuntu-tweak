import unittest

from ubuntutweak.settings.gsettings import Schema
from ubuntutweak.settings.gconfsettings import GconfSetting

class TestSchema(unittest.TestCase):
    def setUp(self):
        self.interface_schema = 'org.gnome.desktop.interface'
        self.gtk_theme_key = 'gtk-theme'

        self.light_theme = '/apps/metacity/general/button_layout'
        self.title_font = '/apps/metacity/general/titlebar_font'

    def test_schema(self):
        self.assertEqual('Ambiance', Schema.load_schema(self.interface_schema, self.gtk_theme_key))
        self.assertEqual('close,minimize,maximize:', GconfSetting(self.light_theme).get_schema_value())
        self.assertEqual('Ubuntu Bold 11', GconfSetting(self.title_font).get_schema_value())

if __name__ == '__main__':
    unittest.main()
