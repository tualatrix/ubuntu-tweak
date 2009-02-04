#!/bin/sh
set -e
set -x

libtoolize --automake --copy --force
aclocal -I m4 --force
automake --add-missing --copy --force
autoconf --force
./configure
