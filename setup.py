#!/usr/bin/env python

import os
import sys
import shutil

INSTALLED_FILES = "installed_files"
PREFIX = '/usr'
APP_DIR = os.path.join(PREFIX, 'share', 'ubuntu-tweak')
BIN_DIR = os.path.join(PREFIX, 'bin')
BIN_FILEs = ['script-worker', 'ubuntu-tweak', 'ubuntu-tweak-dbus']
DESKTOP_FILE = os.path.join(PREFIX, 'share', 'applications', 'ubuntu-tweak.desktop')
LOCALES = []
MOFILES = []

def make_policykit(install = True):
    conf = 'policykit/com.ubuntu-tweak.Mechanism.conf'
    conf_dist = '/etc/dbus-1/system.d/com.ubuntu-tweak.Mechanism.conf'
    policy = 'policykit/com.ubuntu-tweak.mechanism.policy'
    policy_dist = '/usr/share/PolicyKit/policy/com.ubuntu-tweak.mechanism.policy'
    service = 'policykit/com.ubuntu_tweak.Mechanism.service'
    service_dist = '/usr/share/dbus-1/system-services/com.ubuntu_tweak.Mechanism.service'
    if os.path.exists(conf_dist):
        os.remove(conf_dist)

    if os.path.exists(policy_dist):
        os.remove(policy_dist)

    if os.path.exists(service_dist):
        os.remove(service_dist)

    if install:
        shutil.copy(conf, conf_dist)
        shutil.copy(policy, policy_dist)
        shutil.copy(service, service_dist)

def removeall(dir_file):
    if not os.path.exists(dir_file): return
    if os.path.isdir(dir_file):
        for root, dirs, files in os.walk(dir_file, topdown=False):
            for name in files:
                filepath = os.path.join(root, name)
                os.remove(filepath)
            for name in dirs:
                filepath = os.path.join(root, name)
                removeall(filepath)
        os.rmdir(dir_file)
    else:
        os.unlink(dir_file)

    make_policykit(False)
    return

def install():
    if os.path.exists(APP_DIR):
        removeall(APP_DIR)
    for file in BIN_FILEs:
        fullpath = os.path.join(BIN_DIR, file)
        if os.path.exists(fullpath):
            os.remove(fullpath)
        shutil.copy(file, fullpath)

    make_policykit()

    shutil.copytree('src', APP_DIR)
    if os.path.exists(DESKTOP_FILE):
        os.remove(DESKTOP_FILE)
    shutil.copy('ubuntu-tweak.desktop', os.path.join(PREFIX, 'share', 'applications'))

    build()
    for file in MOFILES:
        dest = '/usr/share/' + '/'.join([i for i in file.split('/')[1:4]])
        shutil.copy(file, dest)

    print "Installed Successfully"

def uninstall():
    removeall(APP_DIR)
    for file in BIN_FILEs:
        fullpath = os.path.join(BIN_DIR, file)
        if os.path.exists(fullpath):
            os.remove(fullpath)

    for file in BIN_FILEs:
        fullpath = os.path.join(BIN_DIR, file)
        if os.path.exists(fullpath):
            os.remove(fullpath)

    if os.path.exists(DESKTOP_FILE):
        os.remove(DESKTOP_FILE)
    
    build(True)
    for file in LOCALES:
        if os.path.exists(file):
            os.remove(file)
    print "Uninstalled Successfully"

def build(NOBUILD = False):
    podir = os.path.join (os.path.realpath ("."), "po")
    buildcmd = "msgfmt -o build/locale/%s/LC_MESSAGES/ubuntu-tweak.mo po/%s.po"
    mopath = "build/locale/%s/LC_MESSAGES/ubuntu-tweak.mo"
    destpath = "/usr/share/locale/%s/LC_MESSAGES"
    for name in os.listdir (podir):
        if name[-2:] == "po":
            dname = name.split('-')[2].split('.')[0]
            name = name[:-3]
            if not os.path.isdir("build/locale/%s/LC_MESSAGES" % dname):
                os.makedirs("build/locale/%s/LC_MESSAGES" % dname)
            if not NOBUILD:
                os.system (buildcmd % (dname, name))
            LOCALES.append(os.path.join(destpath % dname, "ubuntu-tweak.mo"))
            MOFILES.append(mopath % dname)

ops = ("install", "uninstall", "build")

if len(sys.argv) < 2 or sys.argv[1] not in ops:
    print "Please specify operation : %s" % " | ".join (ops)
    raise SystemExit

args = sys.argv[1]
if args == "install":
    install()
elif args == "uninstall":
    uninstall()
elif args == "build":
    build()
