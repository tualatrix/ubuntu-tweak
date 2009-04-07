dbusconfdir = $(sysconfdir)/dbus-1/system.d
dbusconf_DATA = ubuntu-tweak-daemon.conf

dbusservicedir = $(datadir)/dbus-1/system-services
dbusservice_DATA = com.ubuntu_tweak.daemon.service

policyconfdir = $(datadir)/PolicyKit/policy
policyconf_DATA = com.ubuntu-tweak.daemon.policy

EXTRA_DIST = $(dbusconf_DATA) \
			 $(policyconf_DATA) \
			 com.ubuntu_tweak.daemon.service.in
