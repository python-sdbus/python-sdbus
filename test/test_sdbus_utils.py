# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2024 igo95862

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

from sdbus.unittest import IsolatedDbusTestCase
from sdbus.utils.inspect import inspect_dbus_path

from sdbus import (
    DbusInterfaceCommon,
    DbusInterfaceCommonAsync,
    sd_bus_open_user,
)

TEST_PATH = "/test"


class TestSdbusUtilsInspect(IsolatedDbusTestCase):
    def test_inspect_dbus_path_block(self) -> None:
        proxy = DbusInterfaceCommon("example.org", TEST_PATH)

        self.assertEqual(inspect_dbus_path(proxy), TEST_PATH)

        new_bus = sd_bus_open_user()

        with self.assertRaisesRegex(LookupError, "is not attached to bus"):
            inspect_dbus_path(proxy, new_bus)

    def test_inspect_dbus_path_async_proxy(self) -> None:
        proxy = DbusInterfaceCommonAsync.new_proxy("example.org", TEST_PATH)

        self.assertEqual(inspect_dbus_path(proxy), TEST_PATH)

        new_bus = sd_bus_open_user()

        with self.assertRaisesRegex(LookupError, "is not attached to bus"):
            inspect_dbus_path(proxy, new_bus)

    def test_inspect_dbus_path_async_local(self) -> None:
        local_obj = DbusInterfaceCommonAsync()

        with self.assertRaisesRegex(
            LookupError, "is not exported to any D-Bus",
        ):
            inspect_dbus_path(local_obj)

        local_obj.export_to_dbus(TEST_PATH)

        self.assertEqual(inspect_dbus_path(local_obj), TEST_PATH)

        new_bus = sd_bus_open_user()

        with self.assertRaisesRegex(LookupError, "is not attached to bus"):
            inspect_dbus_path(local_obj, new_bus)
