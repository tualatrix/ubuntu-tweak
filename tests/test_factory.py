import unittest

from gi.repository import Gtk
from ubuntutweak.factory import WidgetFactory

class TestConfigSettings(unittest.TestCase):
    def test_widget_factory(self):
        # Normal case
        user_indicator_label, user_menu_switch, reset_button = WidgetFactory.create("Switch",
                                  label='user-indicator',
                                  enable_reset=True,
                                  backend="gsettings",
                                  key='com.canonical.indicator.session.user-show-menu')

        self.assertTrue(isinstance(user_indicator_label, Gtk.Label))
        self.assertTrue(isinstance(user_menu_switch, Gtk.Switch))
        self.assertTrue(isinstance(reset_button, Gtk.Button))

        # No reset case
        user_indicator_label, user_menu_switch = WidgetFactory.create("Switch",
                                  label='user-indicator',
                                  backend="gsettings",
                                  key='com.canonical.indicator.session.user-show-menu')
        self.assertTrue(isinstance(user_indicator_label, Gtk.Label))
        self.assertTrue(isinstance(user_menu_switch, Gtk.Switch))

        # Failed case, no reset
        user_indicator_label, user_menu_switch = WidgetFactory.create("Switch",
                                  label='user-indicator',
                                  backend="gsettings",
                                  key='org.canonical.indicator.session.user-show-menu')
        self.assertFalse(user_indicator_label)
        self.assertFalse(user_menu_switch)

        # Failed case, reset
        user_indicator_label, user_menu_switch, reset_button = WidgetFactory.create("Switch",
                                  label='user-indicator',
                                  enable_reset=True,
                                  backend="gsettings",
                                  key='org.canonical.indicator.session.user-show-menu')

        self.assertFalse(user_indicator_label)
        self.assertFalse(user_menu_switch)
        self.assertFalse(reset_button)

if __name__ == '__main__':
    unittest.main()
