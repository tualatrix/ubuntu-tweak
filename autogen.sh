#!/bin/sh
set -x
aclocal
autoheader
automake
autoconf
