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

from sdbus import DbusInterfaceCommon, dbus_method, dbus_property

from .common_test_util import skip_if_no_name_validations


class GoodDbusInterface(
    DbusInterfaceCommon,
    interface_name="org.example.test",
):
    @dbus_method()
    def test_method(self) -> None:
        raise NotImplementedError

    @dbus_property("s")
    def test_property(self) -> str:
        return "test"


class TestBadDbusClass(TestCase):
    def test_method_name_override(self) -> None:
        with self.subTest("Method override"), self.assertRaises(ValueError):

            class BadMethodOverrideClass(GoodDbusInterface):
                def test_method(self) -> None:
                    return

        with self.subTest("D-Bus method override"), self.assertRaises(
            ValueError
        ):

            class BadDbusMethodOverrideClass(GoodDbusInterface):
                @dbus_method()
                def test_method(self) -> None:
                    return

        with self.subTest("Property override"), self.assertRaises(ValueError):

            class BadPropertyOverrideClass(GoodDbusInterface):
                def test_property(self) -> str:  # type: ignore
                    return "override"

        with self.subTest("D-Bus property override"), self.assertRaises(
            ValueError
        ):

            class BadDbusPropertyOverrideClass(GoodDbusInterface):
                @dbus_property("s")
                def test_property(self) -> str:
                    return "override"

        with self.subTest("Good new method"):

            class GoodSubclass(GoodDbusInterface):
                def new_method(self) -> int:
                    return 1

    def test_interface_collision(self) -> None:
        with self.subTest("No collision"):
            class NonInterface(GoodDbusInterface):
                def do_work(self) -> None:
                    ...

        with self.subTest("Collision"), self.assertRaises(ValueError):
            class NewExampleInterface(
                DbusInterfaceCommon,
                interface_name="org.example.test",
            ):
                ...

    def test_bad_class_names(self) -> None:
        skip_if_no_name_validations()

        with self.assertRaisesRegex(AssertionError, "^Invalid interface name"):

            class BadInterfaceName(
                DbusInterfaceCommon,
                interface_name="0.test",
            ):
                ...

        with self.assertRaisesRegex(
            AssertionError,
            "^Invalid method name",
        ):

            class BadMethodName(
                DbusInterfaceCommon,
                interface_name="org.example",
            ):
                @dbus_method(
                    result_signature="s",
                    method_name="🤫",
                )
                def test(self) -> str:
                    return "test"

        with self.assertRaisesRegex(
            AssertionError,
            "^Invalid property name",
        ):

            class BadPropertyName(
                DbusInterfaceCommon,
                interface_name="org.example",
            ):
                @dbus_property(
                    property_signature="s",
                    property_name="🤫",
                )
                def test(self) -> str:
                    return "test"

    def test_dbus_elements_without_interface_name(self) -> None:
        with self.assertRaisesRegex(TypeError, "without interface name"):

            class NoInterfaceName(DbusInterfaceCommon):
                @dbus_method()
                def example(self) -> None:
                    ...

    def test_shared_parent_class(self) -> None:
        class One(GoodDbusInterface):
            ...

        class Two(GoodDbusInterface):
            ...

        class Shared(One, Two):
            ...

    def test_combined_collision(self) -> None:

        class One(
            DbusInterfaceCommon,
            interface_name="org.example.foo",
        ):
            @dbus_method()
            def example(self) -> None:
                ...

        class Two(
            DbusInterfaceCommon,
            interface_name="org.example.bar",
        ):
            @dbus_method()
            def example(self) -> None:
                ...

        with self.assertRaisesRegex(ValueError, "collision"):
            class Combined(One, Two):
                ...

    def test_class_cleanup(self) -> None:
        class One(
            DbusInterfaceCommon,
            interface_name="org.example.foo1",
        ):
            ...

        with self.assertRaises(ValueError):
            class Two(
                DbusInterfaceCommon,
                interface_name="org.example.foo1",
            ):
                ...

        del One
        collect()  # Let weak refs be processed

        class After(
            DbusInterfaceCommon,
            interface_name="org.example.foo1",
        ):
            ...


if __name__ == "__main__":
    unittest_main()
