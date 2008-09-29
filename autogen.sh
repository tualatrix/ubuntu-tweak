#!/bin/sh
set -e
set -x

autopoint  --force
libtoolize --automake --copy --force
aclocal -I m4 --force
autoheader --force
automake --add-missing --copy --force
autoconf --force
./configure --enable-maintainer-mode $*
