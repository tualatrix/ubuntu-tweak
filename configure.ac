#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_INIT([ubuntu-tweak], [0.4.1], [tualatrix@gmail.com])
AM_INIT_AUTOMAKE([1.10 -Wall -Werror])

AC_CONFIG_HEADER(config.h)
AC_CONFIG_MACRO_DIR([m4])

PKG_PROG_PKG_CONFIG([0.19])

# Check Python
AM_PATH_PYTHON([2.5])
if test "x$PYTHON" = "x:"; then
    AC_MSG_ERROR([Python not found])
fi

# Pygtk
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

# Define Getext
GETTEXT_PACKAGE=ubuntu-tweak
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED([GETTEXT_PACKAGE],["$GETTEXT_PACKAGE"], [Gettext package])

AM_GNU_GETTEXT([external])
AM_GNU_GETTEXT_VERSION(0.16.1)

AC_SUBST(PYTHON)

AS_AC_EXPAND(DATADIR, "${datadir}")
AC_SUBST(DATADIR)
AS_AC_EXPAND(DATADIR, "${DATADIR}")

AC_CONFIG_FILES([ 
    Makefile
    po/Makefile.in
    src/Makefile
    src/common/Makefile
    src/common/Consts.py
    src/common/Widgets/Makefile
    src/common/PolicyKit/Makefile
    data/Makefile
    data/appcates/Makefile
    data/aptkeys/Makefile
    data/applogos/Makefile
    data/pixmaps/Makefile
    data/scripts/Makefile
    data/templates/Makefile
    scripts/Makefile
    scripts/ubuntu-tweak
    scripts/script-worker
    policykit/Makefile
    policykit/com.ubuntu_tweak.Mechanism.service
])

AC_OUTPUT

echo
echo $PACKAGE v$VERSION
echo

echo Prefix............... : $prefix

echo
echo "Now type make to compile"
echo
