# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2020  igo95862

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
from typing import List

from py_sd_bus.dbus_proxy import (DbusInterfaceCommon, dbus_method,
                                  get_bus, dbus_property)

from py_sd_bus.sd_bus_internals import DbusPropertyReadOnlyError


class SyncDbus(DbusInterfaceCommon,
               interface_name='org.freedesktop.DBus'):

    @dbus_method()
    def get_id(self) -> str:
        raise NotImplementedError

    @dbus_property('as')
    def features(self) -> List[str]:
        raise NotImplementedError


class TestSync(TestCase):
    def setUp(self) -> None:
        self.bus = get_bus()

    def test_sync(self) -> None:
        s = SyncDbus()
        s._connect(
            self.bus,
            'org.freedesktop.DBus',
            '/org/freedesktop/DBus',
        )

        self.assertIsInstance(s.get_id(), str)
        self.assertIsInstance(s.features, list)

        def test_invalid_assignment() -> None:
            s.features = ['test']

        self.assertRaises(DbusPropertyReadOnlyError, test_invalid_assignment)


if __name__ == '__main__':
    main()
