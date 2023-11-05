# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2023 igo95862

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

from unittest import TestCase
from unittest import main as unittest_main

from sdbus import (
    DbusInterfaceCommonAsync,
    dbus_method_async,
    dbus_property_async,
    dbus_signal_async,
)

from .common_test_util import skip_if_no_name_validations


class TestBadAsyncDbusClass(TestCase):
    def test_name_validations(self) -> None:
        skip_if_no_name_validations()

        with self.assertRaisesRegex(
            AssertionError,
            "^Invalid interface name",
        ):

            class BadInterfaceName(
                DbusInterfaceCommonAsync,
                interface_name="0.test",
            ):
                ...

        with self.assertRaisesRegex(
            AssertionError,
            "^Invalid method name",
        ):

            class BadMethodName(
                DbusInterfaceCommonAsync,
                interface_name="org.example",
            ):
                @dbus_method_async(
                    result_signature="s",
                    method_name="🤫",
                )
                async def test(self) -> str:
                    return "test"

        with self.assertRaisesRegex(
            AssertionError,
            "^Invalid property name",
        ):

            class BadPropertyName(
                DbusInterfaceCommonAsync,
                interface_name="org.example",
            ):
                @dbus_property_async(
                    property_signature="s",
                    property_name="🤫",
                )
                def test(self) -> str:
                    return "test"

        with self.assertRaisesRegex(
            AssertionError,
            "^Invalid signal name",
        ):

            class BadSignalName(
                DbusInterfaceCommonAsync,
                interface_name="org.example",
            ):
                @dbus_signal_async(
                    signal_signature="s",
                    signal_name="🤫",
                )
                def test(self) -> str:
                    raise NotImplementedError


if __name__ == "__main__":
    unittest_main()
