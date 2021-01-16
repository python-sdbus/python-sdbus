# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2020, 2021 igo95862

# This file is part of py_sd_bus

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

from unittest import TestCase, main

from py_sd_bus.proxies import FreedesktopDbus
from py_sd_bus.sd_bus_internals import DbusPropertyReadOnlyError


class TestSync(TestCase):

    def test_sync(self) -> None:
        s = FreedesktopDbus()

        self.assertIsInstance(s.get_id(), str)
        self.assertIsInstance(s.features, list)

        def test_invalid_assignment() -> None:
            s.features = ['test']

        self.assertRaises(DbusPropertyReadOnlyError, test_invalid_assignment)


if __name__ == '__main__':
    main()
