import os
import unittest

from ubuntutweak.admins.quicklists import NewDesktopEntry

class TestQuicklists(unittest.TestCase):
    def setUp(self):
        self.entry = NewDesktopEntry('/usr/share/applications/ubuntu-tweak.desktop')
        self.admin_gruop = 'Admins Shortcut Group'
        self.admin_name = 'Admins'
        self.admin_exec = 'ubuntu-tweak -f admins'
        self.admin_env = 'Unity'

        self.entry2 = NewDesktopEntry(os.path.join(NewDesktopEntry.user_folder, 'gnome-terminal.desktop'))

    def test_quicklists(self):
        self.assertEqual(5, len(self.entry.groups()))
        self.assertEqual(4, len(self.entry.get_shortcut_groups()))
        self.assertEqual(self.admin_name, self.entry.get('Name', self.admin_gruop))
        self.assertEqual(self.admin_exec, self.entry.get('Exec', self.admin_gruop))
        self.assertEqual('Unity', self.entry.get('TargetEnvironment', self.admin_gruop))
        self.assertEqual(False, self.entry.is_user_desktop_file())
        self.assertEqual(False, self.entry.can_reset())

        self.assertEqual(True, self.entry2.is_user_desktop_file())
        self.assertEqual(True, self.entry2.can_reset())

if __name__ == '__main__':
    unittest.main()
