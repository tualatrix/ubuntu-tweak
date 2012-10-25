import os
import unittest

from ubuntutweak.admins.quicklists import NewDesktopEntry

class TestQuicklists(unittest.TestCase):
    def setUp(self):
        os.system('cp /usr/share/applications/google-chrome.desktop %s' %os.path.join(NewDesktopEntry.user_folder, 'google-chrome.desktop'))
        self.entry = NewDesktopEntry('/usr/share/applications/ubuntu-tweak.desktop')
        self.admin_gruop = 'Admins Shortcut Group'
        self.admin_name = 'Admins'
        self.admin_exec = 'ubuntu-tweak -f admins'
        self.admin_env = 'Unity'

        self.chrome_entry = NewDesktopEntry(os.path.join(NewDesktopEntry.user_folder, 'google-chrome.desktop'))
        self.entry3 = NewDesktopEntry('/usr/share/applications/empathy.desktop')

    def test_quicklists(self):
        print self.entry3.groups()
        print self.entry3.get('Actions')
        print self.entry3.get('X-Ayatana-Desktop-Shortcuts')
        self.assertEqual(6, len(self.entry.groups()))
        self.assertEqual(5, len(self.entry.get_actions()))
        self.assertEqual(self.admin_name, self.entry.get('Name', self.admin_gruop))
        self.assertEqual(self.admin_exec, self.entry.get('Exec', self.admin_gruop))
        self.assertEqual('Unity', self.entry.get('TargetEnvironment', self.admin_gruop))
        self.assertEqual(False, self.entry.is_user_desktop_file())
        self.assertEqual(False, self.entry.can_reset())

        self.assertEqual(True, self.chrome_entry.is_user_desktop_file())
        self.assertEqual(True, self.chrome_entry.can_reset())

        #test reorder
        current_order = self.chrome_entry.get_actions()
        new_order = list(reversed(current_order))
        self.chrome_entry.reorder_actions(new_order)
        self.assertEqual(new_order, self.chrome_entry.get_actions())

        #remove action
        self.chrome_entry.remove_action('NewIncognito')
        self.assertEqual(['NewWindow'], self.chrome_entry.get_actions())
        self.chrome_entry.remove_action('NewWindow')
        self.assertEqual([], self.chrome_entry.get_actions())

        # test reset
        self.chrome_entry.reset()
        self.assertEqual(['NewWindow', 'NewIncognito'], self.chrome_entry.get_actions())


if __name__ == '__main__':
    unittest.main()
