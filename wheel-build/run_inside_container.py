#!/opt/python/cp39-cp39/bin/python3
# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2020, 2021 igo95862

# This file is part of python-sdbus

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

from __future__ import annotations

from os import environ
from typing import List

yum_packages: List[str] = [
    'gettext-autopoint', 'gperf',
]

# env
# export PATH="/opt/python/cp39-cp39/bin:${PATH}"

# util-linux
# AL_OPTS="-I/usr/share/aclocal/" ./autogen.sh
# ./configure
#   --prefix '/usr/local' --libdir '/usr/local/lib64'
#   --enable-symvers
#   --with-pkgconfigdir '/usr/share/pkgconfig/'


# export PKG_CONFIG_PATH="/usr/local/lib64/pkgconfig"

# Ninja
# ./configure.py --boostrap
# cp ./ninja /usr/local/bin

# systemd
# meson setup build -Dstatic-libsystemd=pic

# PYTHON_SDBUS_USE_STATIC_LINK=1


def setup_env() -> None:
    environ['PATH'] = f"/opt/python/cp39-cp39/bin:{environ['PATH']}"


def main() -> None:
    setup_env()


if __name__ == '__main__':
    main()
