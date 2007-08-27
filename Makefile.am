## Process this file with automake to produce Makefile.in
## Created by Anjuta - will be overwritten
## If you don't want it to overwrite it,
## 	Please disable it in the Anjuta project configuration

SUBDIRS = po src pixmaps scripts

ubuntu_tweakdocdir = ${prefix}/@NO_PREFIX_PACKAGE_DOC_DIR@
ubuntu_tweakdoc_DATA = \
	README\
	COPYING\
	AUTHORS\
	ChangeLog\
	INSTALL\
	NEWS\
	TODO

EXTRA_DIST = $(ubuntu_tweakdoc_DATA)

gnomemenudir = $(prefix)/@NO_PREFIX_PACKAGE_MENU_DIR@
gnomemenu_DATA = ubuntu-tweak.desktop

# Copy all the spec files. Of cource, only one is actually used.
dist-hook:
	for specfile in *.spec; do \
		if test -f $$specfile; then \
			cp -p $$specfile $(distdir); \
		fi \
	done

