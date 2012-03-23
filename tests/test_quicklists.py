import unittest

from ubuntutweak.admins.quicklists import NewDesktopEntry

class TestQuicklists(unittest.TestCase):
    def setUp(self):
        self.entry = NewDesktopEntry('/usr/share/applications/ubuntu-tweak.desktop')
        self.admin_gruop = 'Admins Shortcut Group'
        self.admin_name = 'Admins'
        self.admin_exec = 'ubuntu-tweak -f admins'
        self.admin_env = 'Unity'

    def test_quicklists(self):
        self.assertEqual(5, len(self.entry.groups()))
        self.assertEqual(4, len(self.entry.get_shortcut_groups()))
        self.assertEqual(self.admin_name, self.entry.get('Name', self.admin_gruop))
        self.assertEqual(self.admin_exec, self.entry.get('Exec', self.admin_gruop))
        self.assertEqual('Unity', self.entry.get('TargetEnvironment', self.admin_gruop))

if __name__ == '__main__':
    unittest.main()
