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

from .test_read_write_dbus_types import TestDbusTypes

from asyncio import run
from resource import getrusage, RUSAGE_SELF


async def test_strings() -> None:
    t = TestDbusTypes()
    t.setUp()
    await t.asyncSetUp()

    start_mem = getrusage(RUSAGE_SELF).ru_maxrss

    for _ in range(1_000_000):
        t.create_message()
        t.test_strings()

        current_usage = getrusage(RUSAGE_SELF).ru_maxrss
        if current_usage > start_mem * 2:
            raise RuntimeError('Leaking memory')


def test():
    run(test_strings())
