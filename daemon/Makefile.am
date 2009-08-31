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
