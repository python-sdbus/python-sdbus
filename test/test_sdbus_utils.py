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

from unittest import TestCase

from sdbus.unittest import IsolatedDbusTestCase
from sdbus.utils.inspect import inspect_dbus_bus, inspect_dbus_path
from sdbus.utils.parse import parse_get_managed_objects

from sdbus import (
    DbusInterfaceCommon,
    DbusInterfaceCommonAsync,
    dbus_property,
    dbus_property_async,
    sd_bus_open_user,
)

TEST_PATH = "/test"


class FooAsync(DbusInterfaceCommonAsync, interface_name="org.foo"):
    @dbus_property_async("x")
    def foo(self) -> int:
        return 1


class BarAsync(DbusInterfaceCommonAsync, interface_name="org.bar"):
    @dbus_property_async("x")
    def bar(self) -> int:
        return 2


class FooBarAsync(FooAsync, BarAsync):
    ...


class Foo(DbusInterfaceCommon, interface_name="org.foo"):
    @dbus_property("x")
    def foo(self) -> int:
        return 1


class Bar(DbusInterfaceCommon, interface_name="org.bar"):
    @dbus_property("x")
    def bar(self) -> int:
        return 2


class FooBar(Foo, Bar):
    ...


MANAGED_OBJECTS_COMBINED = {
    "/test": {
        "org.foo": {"Foo": ("x", 1)},
        "org.bar": {"Bar": ("x", 2)},
    }
}

MANAGED_OBJECTS_SPLIT = {
    "/foo": {
        "org.foo": {"Foo": ("x", 1)},
    },
    "/bar": {
        "org.bar": {"Bar": ("x", 2)},
    },
}

MANAGED_OBJECTS_BOTH = {**MANAGED_OBJECTS_COMBINED, **MANAGED_OBJECTS_SPLIT}


class TestSdbusUtilsParse(TestCase):
    def test_parse_get_managed_objects_async_combined(self) -> None:
        parsed_managed = parse_get_managed_objects(
            FooBarAsync,
            MANAGED_OBJECTS_COMBINED,
        )

        self.assertEqual(1, len(parsed_managed))

        class_type, properties_data = parsed_managed["/test"]
        self.assertEqual(FooBarAsync, class_type)
        self.assertEqual(properties_data["foo"], 1)
        self.assertEqual(properties_data["bar"], 2)

    def test_parse_get_managed_objects_block_combined(self) -> None:
        parsed_managed = parse_get_managed_objects(
            FooBar,
            MANAGED_OBJECTS_COMBINED,
        )

        self.assertEqual(1, len(parsed_managed))

        class_type, properties_data = parsed_managed["/test"]
        self.assertEqual(FooBar, class_type)
        self.assertEqual(properties_data["foo"], 1)
        self.assertEqual(properties_data["bar"], 2)

    def test_parse_get_managed_objects_async_split(self) -> None:
        parsed_managed = parse_get_managed_objects(
            [FooAsync, BarAsync],
            MANAGED_OBJECTS_SPLIT,
        )

        self.assertEqual(2, len(parsed_managed))

        class_type, properties_data = parsed_managed["/foo"]
        self.assertEqual(FooAsync, class_type)
        self.assertEqual(properties_data["foo"], 1)

        class_type, properties_data = parsed_managed["/bar"]
        self.assertEqual(BarAsync, class_type)
        self.assertEqual(properties_data["bar"], 2)

    def test_parse_get_managed_objects_block_split(self) -> None:
        parsed_managed = parse_get_managed_objects(
            [Foo, Bar],
            MANAGED_OBJECTS_SPLIT,
        )

        self.assertEqual(2, len(parsed_managed))

        class_type, properties_data = parsed_managed["/foo"]
        self.assertEqual(Foo, class_type)
        self.assertEqual(properties_data["foo"], 1)

        class_type, properties_data = parsed_managed["/bar"]
        self.assertEqual(Bar, class_type)
        self.assertEqual(properties_data["bar"], 2)

    def test_parse_get_managed_objects_unknown_interface_error(self) -> None:
        with self.assertRaisesRegex(KeyError, "org.foo"):
            parse_get_managed_objects(
                Bar,
                MANAGED_OBJECTS_SPLIT,
            )

    def test_parse_get_managed_objects_unknown_interface_none_reuse(
        self,
    ) -> None:
        parsed_managed = parse_get_managed_objects(
            {BarAsync},
            MANAGED_OBJECTS_SPLIT,
            on_unknown_interface="none",
            on_unknown_member="reuse",
        )

        class_type, properties_data = parsed_managed["/foo"]
        self.assertIsNone(class_type)
        self.assertEqual(properties_data["Foo"], 1)

        class_type, properties_data = parsed_managed["/bar"]
        self.assertEqual(BarAsync, class_type)
        self.assertEqual(properties_data["bar"], 2)

    def test_parse_get_managed_objects_unknown_member_skip(self) -> None:
        parsed_managed = parse_get_managed_objects(
            [Foo],
            MANAGED_OBJECTS_SPLIT,
            on_unknown_interface="none",
            on_unknown_member="ignore",
        )

        self.assertEqual(2, len(parsed_managed))

        class_type, properties_data = parsed_managed["/foo"]
        self.assertEqual(Foo, class_type)
        self.assertEqual(properties_data["foo"], 1)

        class_type, properties_data = parsed_managed["/bar"]
        self.assertIsNone(class_type)
        self.assertEqual(0, len(properties_data))

    def test_parse_get_managed_objects_interface_subset_single(self) -> None:
        parsed_managed = parse_get_managed_objects(
            [FooAsync],
            MANAGED_OBJECTS_COMBINED,
            on_unknown_interface="error",
            on_unknown_member="reuse",
            use_interface_subsets=True,
        )
        class_type, properties_data = parsed_managed["/test"]
        self.assertIs(class_type, FooAsync)
        self.assertEqual(properties_data["foo"], 1)
        self.assertEqual(properties_data["Bar"], 2)

    def test_parse_get_managed_objects_interface_subset_multiple(self) -> None:
        parsed_managed = parse_get_managed_objects(
            [FooAsync, FooBarAsync],
            # FooBarAsync should be prioritized then both interfaces
            # are available on the path.
            MANAGED_OBJECTS_BOTH,
            on_unknown_interface="none",
            on_unknown_member="reuse",
            use_interface_subsets=True,
        )

        class_type, _ = parsed_managed["/test"]
        self.assertIs(class_type, FooBarAsync)
        class_type, _ = parsed_managed["/foo"]
        self.assertIs(class_type, FooAsync)
        class_type, _ = parsed_managed["/bar"]
        self.assertIsNone(class_type)


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
        local_obj = FooBarAsync()

        with self.assertRaisesRegex(
            LookupError, "is not exported to any D-Bus",
        ):
            inspect_dbus_path(local_obj)

        local_obj.export_to_dbus(TEST_PATH)

        self.assertEqual(inspect_dbus_path(local_obj), TEST_PATH)

        new_bus = sd_bus_open_user()

        with self.assertRaisesRegex(LookupError, "is not attached to bus"):
            inspect_dbus_path(local_obj, new_bus)

    def test_inspect_attached_bus(self) -> None:
        proxy = DbusInterfaceCommon("example.org", TEST_PATH)

        self.assertIs(inspect_dbus_bus(proxy), self.bus)

        with self.assertRaises(TypeError):
            inspect_dbus_bus(object())  # type: ignore[arg-type]

    def test_inspect_attached_bus_async(self) -> None:
        proxy = DbusInterfaceCommonAsync.new_proxy("example.org", TEST_PATH)

        self.assertIs(inspect_dbus_bus(proxy), self.bus)

        local_obj = FooBarAsync()

        self.assertIsNone(inspect_dbus_bus(local_obj))

        local_obj.export_to_dbus("/")

        self.assertIs(inspect_dbus_bus(local_obj), self.bus)
