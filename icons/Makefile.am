SUBDIRS = icons

sysiconsdir = $(datadir)/pixmaps
sysicons_DATA = ubuntu-tweak.png

desktopdir = $(datadir)/applications
desktop_in_files = @PACKAGE@.desktop.in
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)
@INTLTOOL_DESKTOP_RULE@

EXTRA_DIST = \
	$(sysicons_DATA) \
	$(desktop_in_files) \
	$(desktop_DATA)
