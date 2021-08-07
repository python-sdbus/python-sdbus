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

from unittest import main

from sdbus_block.dbus_daemon import FreedesktopDbus

from sdbus import DbusPropertyReadOnlyError

from .common_test_util import TempDbusTest


class TestSync(TempDbusTest):

    def test_sync(self) -> None:
        self.bus.request_name('org.example.test', 0)

        s = FreedesktopDbus(self.bus)
        s.dbus_ping()
        s.dbus_introspect()
        s.dbus_machine_id()

        self.assertIsInstance(s.get_id(), str)
        self.assertIsInstance(s.features, list)
        self.assertIsInstance(
            s.get_connection_pid('org.freedesktop.DBus'), int)

        self.assertIsInstance(
            s.get_connection_uid('org.freedesktop.DBus'), int)

        def test_invalid_assignment() -> None:
            s.features = ['test']

        self.assertRaises(DbusPropertyReadOnlyError, test_invalid_assignment)

        self.assertTrue(s.get_name_owner('org.example.test'))

    def test_docstring(self) -> None:
        from pydoc import getdoc

        s = FreedesktopDbus(self.bus)

        with self.subTest('Method doc'):
            self.assertTrue(getdoc(s.get_connection_pid))

        with self.subTest('Property doc (through class dict)'):
            self.assertTrue(getdoc(s.__class__.__dict__['features']))


if __name__ == '__main__':
    main()
