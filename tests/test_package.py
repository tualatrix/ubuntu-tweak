import unittest

from ubuntutweak0.common.package import PACKAGE_WORKER

class TestPackageFunctions(unittest.TestCase):
    def setUp(self):
        self.packages = ''''linux-firmware', 'linux-headers-2.6.35-24-generic      linux-headers-generic                linux-image-generic
                linux-generic                        linux-headers-2.6.37-020637          linux-image-2.6.35-24-generic        linux-libc-dev
                linux-headers-2.6.35-24              linux-headers-2.6.37-020637-generic  linux-image-2.6.37-020637-generic    linux-sound-base'''
        PACKAGE_WORKER.current_kernel_version = '2.6.35-24'

    def test_package(self):
        self.assertFalse(PACKAGE_WORKER.is_old_kernel_package('gedit'))
        self.assertFalse(PACKAGE_WORKER.is_old_kernel_package('ubuntu-tweak'))
        self.assertFalse(PACKAGE_WORKER.is_old_kernel_package('linux-firmware'))
        self.assertFalse(PACKAGE_WORKER.is_old_kernel_package('linux-generic'))
        self.assertFalse(PACKAGE_WORKER.is_old_kernel_package('linux-image-generic'))
        self.assertFalse(PACKAGE_WORKER.is_old_kernel_package('linux-headers-2.6.37-020637'))
        self.assertFalse(PACKAGE_WORKER.is_old_kernel_package('linux-image-2.6.35-24-generic'))
        self.assertFalse(PACKAGE_WORKER.is_old_kernel_package('linux-image-2.6.35-24'))
        self.assertTrue(PACKAGE_WORKER.is_old_kernel_package('linux-image-2.6.34-24-generic'))

if __name__ == '__main__':
    unittest.main()
