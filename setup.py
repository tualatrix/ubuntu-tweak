#!/usr/bin/env python

import os
import sys
from stat import *
from distutils.core import setup
from distutils.command.install import install as _install
from distutils.command.install_data import install_data as _install_data

INSTALLED_FILES = "installed_files"

class install (_install):
    def run (self):
        _install.run (self)
        outputs = self.get_outputs ()
        length = 0
        if self.root:
            length += len (self.root)
        if self.prefix:
            length += len (self.prefix)
        if length:
            for counter in xrange (len (outputs)):
                outputs[counter] = outputs[counter][length:]
        data = "\n".join (outputs)
        try:
            file = open (INSTALLED_FILES, "w")
        except:
            self.warn ("Could not write installed files list %s" % \
                       INSTALLED_FILES)
            return 
        file.write (data)
        file.close ()

class install_data (_install_data):
    def run (self):
        def chmod_data_file (file):
            try:
                os.chmod (file, S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH)
            except:
                self.warn ("Could not chmod data file %s" % file)
        _install_data.run (self)
        map (chmod_data_file, self.get_outputs ())

class uninstall (_install):

    def run (self):
        try:
            file = open (INSTALLED_FILES, "r")
        except:
            self.warn ("Could not read installed files list %s" % \
                       INSTALLED_FILES)
            return 
        files = file.readlines ()
        file.close ()
        prepend = ""
        if self.root:
            prepend += self.root
        if self.prefix:
            prepend += self.prefix
        if len (prepend):
            for counter in xrange (len (files)):
                files[counter] = prepend + files[counter].rstrip ()
        for file in files:
            print "Uninstalling %s" % file
            try:
                os.unlink (file)
            except:
                self.warn ("Could not remove file %s" % file)

ops = ("install", "build", "sdist", "uninstall", "clean")

if len (sys.argv) < 2 or sys.argv[1] not in ops:
    print "Please specify operation : %s" % " | ".join (ops)
    raise SystemExit

srcdir = os.path.join (os.path.realpath ("."), "src")
src = map(lambda i: "src/%s" % i, filter(lambda i: i[-2:] == "py", os.listdir (srcdir)))

pixmapsdir = os.path.join (os.path.realpath ("."), "src/pixmaps")
images = map(lambda i: "src/pixmaps/%s" % i, filter(lambda i: i[-3:] == "png", os.listdir(pixmapsdir)))

data_files = [
                ("/usr/share/applications", ["ubuntu-tweak.desktop"]),
		("/usr/share/ubuntu-tweak", src),
                ("/usr/share/ubuntu-tweak/pixmaps", images),
                ("/usr/bin", ["ubuntu-tweak"]),
             ]

podir = os.path.join (os.path.realpath ("."), "po")
if os.path.isdir (podir):
    buildcmd = "msgfmt -o build/locale/%s/LC_MESSAGES/ubuntu-tweak.mo po/%s.po"
    mopath = "build/locale/%s/LC_MESSAGES/ubuntu-tweak.mo"
    destpath = "share/locale/%s/LC_MESSAGES"
    for name in os.listdir (podir):
        if name[-2:] == "po":
            name = name[:-3]
            if sys.argv[1] == "build" or (sys.argv[1] == "install" and not os.path.exists (mopath % name)):
                if not os.path.isdir ("build/locale/%s/LC_MESSAGES" % name):
                    os.makedirs ("build/locale/%s/LC_MESSAGES" % name)
                os.system (buildcmd % (name, name))
            data_files.append ((destpath % name, [mopath % name]))

setup(
	name		= "ubuntu-tweak",
	version		= "0.2.5",
	description	= "Ubuntu Tweak is a tool for Ubuntu that makes it easy to configure your system and desktop settings.",
	author		= "TualatriX",
	author_email	= "tualatrix@gmail.com",
	url		= "http://ubuntu-tweak.com",
	license		= "GPL",
	data_files	= data_files,
        cmdclass         = {"uninstall" : uninstall,
                            "install" : install,
                            "install_data" : install_data}
)
