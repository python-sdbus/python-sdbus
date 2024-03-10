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

from gc import collect
from unittest import TestCase
from unittest import main as unittest_main

from sdbus.dbus_common_funcs import PROPERTY_FLAGS_MASK, count_bits

from sdbus import (
    DbusDeprecatedFlag,
    DbusInterfaceCommonAsync,
    DbusPropertyConstFlag,
    DbusPropertyEmitsChangeFlag,
    dbus_method_async,
    dbus_method_async_override,
    dbus_property_async,
    dbus_signal_async,
)

from .common_test_util import skip_if_no_asserts, skip_if_no_name_validations


class TestInterface(
    DbusInterfaceCommonAsync,
    interface_name="org.example.good",
):
    @dbus_method_async(result_signature="i")
    async def test_int(self) -> int:
        return 1


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

    def test_property_flags(self) -> None:
        self.assertEqual(0, PROPERTY_FLAGS_MASK & DbusDeprecatedFlag)
        self.assertEqual(
            1,
            count_bits(
                PROPERTY_FLAGS_MASK
                & (DbusDeprecatedFlag | DbusPropertyEmitsChangeFlag)
            ),
        )
        self.assertEqual(
            2,
            count_bits(
                PROPERTY_FLAGS_MASK
                & (
                    DbusDeprecatedFlag
                    | DbusPropertyConstFlag
                    | DbusPropertyEmitsChangeFlag
                )
            ),
        )

        with self.subTest("Test incorrect flags"), self.assertRaisesRegex(
            AssertionError,
            "^Incorrect number of Property flags",
        ):
            skip_if_no_asserts()

            class InvalidPropertiesFlags(
                DbusInterfaceCommonAsync, interface_name="org.test.invalidprop"
            ):
                @dbus_property_async(
                    "s",
                    flags=DbusPropertyConstFlag | DbusPropertyEmitsChangeFlag,
                )
                def test_constant(self) -> str:
                    return "a"

        with self.subTest("Valid properties flags"):

            class ValidPropertiesFlags(
                DbusInterfaceCommonAsync, interface_name="org.test.validprop"
            ):
                @dbus_property_async(
                    "s",
                    flags=DbusDeprecatedFlag | DbusPropertyEmitsChangeFlag,
                )
                def test_constant(self) -> str:
                    return "a"

    def test_bad_subclass(self) -> None:
        with self.assertRaises(ValueError):

            class TestInheritence(TestInterface):
                async def test_int(self) -> int:
                    return 2

        with self.assertRaises(ValueError):

            class TestInheritence2(TestInterface):
                @dbus_method_async_override()
                async def test_unrelated(self) -> int:
                    return 2

    def test_dbus_elements_without_interface_name(self) -> None:
        with self.assertRaisesRegex(TypeError, "without interface name"):

            class NoInterfaceName(DbusInterfaceCommonAsync):
                @dbus_method_async()
                async def example(self) -> None:
                    ...

    def test_dbus_elements_without_interface_name_subclass(self) -> None:
        with self.assertRaisesRegex(TypeError, "without interface name"):

            class NoInterfaceName(TestInterface):
                @dbus_method_async()
                async def example(self) -> None:
                    ...

    def test_shared_parent_class(self) -> None:
        class One(TestInterface):
            ...

        class Two(TestInterface):
            ...

        class Shared(One, Two):
            ...

    def test_combined_collision(self) -> None:

        class One(
            DbusInterfaceCommonAsync,
            interface_name="org.example.foo",
        ):
            @dbus_method_async()
            async def example(self) -> None:
                ...

        class Two(
            DbusInterfaceCommonAsync,
            interface_name="org.example.bar",
        ):
            @dbus_method_async()
            async def example(self) -> None:
                ...

        with self.assertRaisesRegex(ValueError, "collision"):
            class Combined(One, Two):
                ...

    def test_class_cleanup(self) -> None:
        class One(
            DbusInterfaceCommonAsync,
            interface_name="org.example.foo1",
        ):
            ...

        with self.assertRaises(ValueError):
            class Two(
                DbusInterfaceCommonAsync,
                interface_name="org.example.foo1",
            ):
                ...

        del One
        collect()  # Let weak refs be processed

        class After(
            DbusInterfaceCommonAsync,
            interface_name="org.example.foo1",
        ):
            ...


if __name__ == "__main__":
    unittest_main()
