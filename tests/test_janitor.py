import os
import shutil
import unittest

from ubuntutweak.janitors.oldkernel_plugin import OldKernelPlugin

class TestJanitorFunctions(unittest.TestCase):
    def setUp(self):
        self.oldkernel_plugin = OldKernelPlugin()
        self.oldkernel_plugin.current_kernel_version = '2.6.38-10'

    def test_oldkernel(self):
        self.assertTrue(self.oldkernel_plugin.is_old_kernel_package('linux-headers-2.6.35-28'))
        self.assertTrue(self.oldkernel_plugin.is_old_kernel_package('linux-image-2.6.38-9-generic'))
        self.assertFalse(self.oldkernel_plugin.is_old_kernel_package('linux-image-2.6.38-10'))
        self.assertFalse(self.oldkernel_plugin.is_old_kernel_package('linux-image-2.6.38-11'))

if __name__ == '__main__':
    unittest.main()
