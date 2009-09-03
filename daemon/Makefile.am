bin_PROGRAMS = ubuntu-tweak-daemon

ubuntu_tweak_daemon_SOURCES = \
	daemon.c \
	daemon.h \
	main.c \
	$(NULL)

ubuntu_tweak_daemon_CPPFLAGS = \
	-Wall   \
	$(DAEMON_CFLAGS) \
	$(POLKIT_CFLAGS) \
	$(NULL)

ubuntu_tweak_daemon_LDADD = $(DAEMON_LIBS) $(POLKIT_LIBS)

dbusconfdir = $(sysconfdir)/dbus-1/system.d
dbusconf_DATA = ubuntu-tweak-daemon.conf

dbusservicedir = $(datadir)/dbus-1/system-services
dbusservice_DATA = com.ubuntu_tweak.daemon.service \
		   com.ubuntu_tweak.daemon.getconfig.service \
		   com.ubuntu_tweak.daemon.packageconfig.service

policyconfdir = $(datadir)/PolicyKit/policy
policyconf_DATA = com.ubuntu-tweak.daemon.policy

EXTRA_DIST = $(dbusconf_DATA) \
			 $(policyconf_DATA) \
			 com.ubuntu_tweak.daemon.service.in \
			 com.ubuntu_tweak.daemon.getconfig.service.in \
			 com.ubuntu_tweak.daemon.service.packageconfig.in
