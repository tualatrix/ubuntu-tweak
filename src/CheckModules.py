#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Ubuntu Tweak - PyGTK based desktop configure tool
#
# Copyright (C) 2007-2008 TualatriX <tualatrix@gmail.com>
#
# Ubuntu Tweak is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Ubuntu Tweak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ubuntu Tweak; if not, write to the Free Software Foundation, Inc.,

__all__ = ('NO_HARDY', 'NO_APT', 'NO_COMPIZ', 'CF_VERSION_ERROR', 'GNOME_VESION')

from common.SystemInfo import GnomeVersion, SystemInfo

NO_HARDY = 'Mint' not in SystemInfo.distro and '8.04' not in SystemInfo.distro
GNOME_VESION = int(GnomeVersion.minor)

try:
    import apt_pkg
    NO_APT = False
except ImportError:
    NO_APT = True

try:
    import compizconfig as ccs
    import ccm
    NO_COMPIZ = False
    if ccm.Version >= "0.7.4":
        CF_VERSION_ERROR = False
    else:
        CF_VERSION_ERROR = True
except ImportError:
    NO_COMPIZ = True
    CF_VERSION_ERROR = False
