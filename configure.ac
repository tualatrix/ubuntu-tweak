AC_INIT([ubuntu-tweak], [0.4.9.2], [tualatrix@gmail.com])
AM_INIT_AUTOMAKE

AM_PROG_CC_C_O

DBUS_REQUIRED=1.1.2
DBUS_GLIB_REQUIRED=0.74
GLIB_REQUIRED=2.4.0
POLICYKIT_REQUIRED=0.5

PKG_PROG_PKG_CONFIG([0.19])

dnl Check Python
AM_PATH_PYTHON([2.5])
if test "x$PYTHON" = "x:"; then
    AC_MSG_ERROR([Python not found])
fi

dnl Pygtk
PKG_CHECK_MODULES(TWEAK,
    gtk+-2.0                >= 2.10
    pygtk-2.0               >= 2.10
    pygobject-2.0           >= 2.10
    gnome-python-2.0        >= 2.10
)
AC_SUBST(PYGTK_CFLAGS)
AC_SUBST(PYGTK_LIBS)
PYGTK_DEFS=`$PKG_CONFIG --variable=defsdir pygtk-2.0`
AC_SUBST(PYGTK_DEFS)

dnl Define Getext
GETTEXT_PACKAGE=ubuntu-tweak
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED([GETTEXT_PACKAGE],["$GETTEXT_PACKAGE"], [Gettext package])

AM_GNU_GETTEXT([external])
AM_GNU_GETTEXT_VERSION(0.16.1)

AC_SUBST(PYTHON)

AS_AC_EXPAND(DATADIR, "${datadir}")
AC_SUBST(DATADIR)
AS_AC_EXPAND(DATADIR, "${DATADIR}")

dnl where is DBus system.d directory? 
AC_ARG_WITH(dbus_sys, [  --with-dbus-sys=<dir>   where D-BUS system.d directory is]) 
 
if ! test -z "$with_dbus_sys" ; then 
	DBUS_SYSTEMD_DIR="$with_dbus_sys" 
else 
	DBUS_SYSTEMD_DIR="${EXPANDED_SYSCONFDIR}/dbus-1/system.d" 
fi 
AC_SUBST(DBUS_SYSTEMD_DIR) 

dnl check for DBus
PKG_CHECK_MODULES([DBUS], [dbus-1 >= $DBUS_REQUIRED])
AC_SUBST([DBUS_CFLAGS])
AC_SUBST([DBUS_LIBS])

dnl check for the dispatcher deps
PKG_CHECK_MODULES(DAEMON, [dbus-glib-1 >= $DBUS_GLIB_REQUIRED
			       glib-2.0    >= $GLIB_REQUIRED ])
DAEMON_CFLAGS="-DDBUS_API_SUBJECT_TO_CHANGE $DAEMON_CFLAGS"
AC_SUBST(DAEMON_LIBS)
AC_SUBST(DAEMON_CFLAGS)

dnl check for PolicyKit
PKG_CHECK_MODULES(POLKIT, [polkit-dbus >= $POLICYKIT_REQUIRED])
AC_SUBST(POLKIT_LIBS)
AC_SUBST(POLKIT_CFLAGS)

AC_CONFIG_FILES([ 
    Makefile
    po/Makefile.in
    src/Makefile
    src/common/Makefile
    src/common/consts.py
    src/common/widgets/Makefile
    src/common/policykit/Makefile
    src/backends/Makefile
    daemon/Makefile
    daemon/com.ubuntu_tweak.daemon.service
    daemon/com.ubuntu_tweak.daemon.packageconfig.service
    daemon/com.ubuntu_tweak.daemon.getconfig.service
    data/Makefile
    data/appcates/Makefile
    data/aptkeys/Makefile
    data/applogos/Makefile
    data/pixmaps/Makefile
    data/scripts/Makefile
    data/templates/Makefile
    data/gui/Makefile
    icons/Makefile
    icons/icons/Makefile
    icons/icons/16x16/Makefile
    icons/icons/22x22/Makefile
    icons/icons/24x24/Makefile
    icons/icons/32x32/Makefile
    icons/icons/36x36/Makefile
    icons/icons/48x48/Makefile
    icons/icons/64x64/Makefile
    icons/icons/96x96/Makefile
    icons/icons/128x128/Makefile
    scripts/Makefile
    scripts/ubuntu-tweak
    scripts/script-worker
])

AC_OUTPUT

echo
echo $PACKAGE $VERSION
echo

echo Prefix............... : $prefix

echo
echo "Now type make to compile"
echo
