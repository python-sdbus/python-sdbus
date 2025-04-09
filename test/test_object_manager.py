# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2020-2022 igo95862

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

from sdbus.exceptions import DbusUnknownObjectError
from sdbus.unittest import IsolatedDbusTestCase
from sdbus.utils import (
    parse_get_managed_objects,
    parse_interfaces_added,
    parse_interfaces_removed,
)

from sdbus import (
    DbusInterfaceCommonAsync,
    DbusObjectManagerInterfaceAsync,
    dbus_method_async,
    dbus_property_async,
)

HELLO_WORLD = 'Hello World!'
TEST_NUMBER = 1000


class ObjectManagerTestInterface(
    DbusObjectManagerInterfaceAsync,
    interface_name='org.test.objectmanager',
):
    @dbus_method_async(
        result_signature='s',
    )
    async def get_hello_world(self) -> str:
        return HELLO_WORLD


OBJECT_MANAGER_PATH = '/object_manager'
CONNECTION_NAME = 'org.example.test'

MANAGED_INTERFACE_NAME = 'org.test.testing'


class ManagedInterface(
    DbusInterfaceCommonAsync,
    interface_name=MANAGED_INTERFACE_NAME,
):

    @dbus_property_async('x')
    def test_int(self) -> int:
        return TEST_NUMBER


MANAGED_PATH = '/object_manager/test'


class TestObjectManager(IsolatedDbusTestCase):
    async def test_object_manager(self) -> None:
        await self.bus.request_name_async(CONNECTION_NAME, 0)

        object_manager = ObjectManagerTestInterface()
        object_manager.export_to_dbus(OBJECT_MANAGER_PATH)

        object_manager_connection = ObjectManagerTestInterface.new_proxy(
            CONNECTION_NAME, OBJECT_MANAGER_PATH)

        self.assertEqual(
            await object_manager_connection.get_hello_world(),
            HELLO_WORLD)

        managed_object = ManagedInterface()

        async with self.assertDbusSignalEmits(
            object_manager_connection.interfaces_added
        ) as added_interfaces_catch:
            object_manager.export_with_manager(MANAGED_PATH, managed_object)

        caught_added = added_interfaces_catch.output[0]

        added_path, added_attributes = caught_added

        self.assertEqual(added_path, MANAGED_PATH)

        self.assertEqual(
            added_attributes[
                MANAGED_INTERFACE_NAME][
                    'TestInt'][1],
            TEST_NUMBER,
        )

        with self.subTest("Test interfaces added parser"):
            parse_interfaces_added(ManagedInterface, caught_added)

        async with self.assertDbusSignalEmits(
            object_manager_connection.interfaces_removed
        ) as removed_interfaces_catch:
            object_manager.remove_managed_object(managed_object)

        path_removed, interfaces_removed = removed_interfaces_catch.output[0]

        self.assertEqual(path_removed, MANAGED_PATH)

        self.assertIn(MANAGED_INTERFACE_NAME, interfaces_removed)

    def test_expot_with_no_manager(self) -> None:
        object_manager = ObjectManagerTestInterface()

        managed_object = ManagedInterface()

        self.assertRaises(
            RuntimeError,
            object_manager.export_with_manager,
            MANAGED_PATH,
            managed_object,
        )

    async def test_parse_interfaces_added_removed(self) -> None:
        MANAGED_TWO_INTERFACE_NAME = MANAGED_INTERFACE_NAME + 'Two'

        class ManagedTwoInterface(
            ManagedInterface,
            interface_name=MANAGED_TWO_INTERFACE_NAME,
        ):

            @dbus_property_async('s')
            def test_str(self) -> str:
                return 'test'

        await self.bus.request_name_async(CONNECTION_NAME, 0)

        object_manager = DbusObjectManagerInterfaceAsync()
        object_manager.export_to_dbus(OBJECT_MANAGER_PATH)

        object_manager_connection = DbusObjectManagerInterfaceAsync.new_proxy(
            CONNECTION_NAME, OBJECT_MANAGER_PATH)

        managed_object = ManagedTwoInterface()

        async with self.assertDbusSignalEmits(
            object_manager_connection.interfaces_added
        ) as added_interfaces_catch:
            object_manager.export_with_manager(MANAGED_PATH, managed_object)

        caught_added = added_interfaces_catch.output[0]

        with self.subTest('Parse added class'):
            path, python_class, python_properties = (
                parse_interfaces_added(ManagedTwoInterface, caught_added)
            )

            self.assertEqual(path, MANAGED_PATH)
            self.assertEqual(python_class, ManagedTwoInterface)
            self.assertIn('test_str', python_properties)
            self.assertIn('test_int', python_properties)

        with self.subTest('Parse added object'):
            path, python_class, python_properties = (
                parse_interfaces_added(managed_object, caught_added)
            )

            self.assertEqual(path, MANAGED_PATH)
            self.assertEqual(python_class, ManagedTwoInterface)
            self.assertIn('test_str', python_properties)
            self.assertIn('test_int', python_properties)

        with self.subTest('Parse added iterable'):
            path, python_class, python_properties = (
                parse_interfaces_added(
                    (ManagedInterface, ManagedTwoInterface),
                    caught_added)
            )

            self.assertEqual(path, MANAGED_PATH)
            self.assertEqual(python_class, ManagedTwoInterface)
            self.assertIn('test_str', python_properties)
            self.assertIn('test_int', python_properties)

        with self.subTest('Parse added unknown'):
            with self.assertRaises(KeyError):
                path, python_class, python_properties = (
                    parse_interfaces_added(
                        ManagedInterface,
                        caught_added)
                )

            with self.assertRaises(KeyError):
                path, python_class, python_properties = (
                    parse_interfaces_added(
                        ManagedInterface,
                        caught_added,
                        on_unknown_interface='none',
                    )
                )

            path, python_class, python_properties = (
                parse_interfaces_added(
                    ManagedInterface,
                    caught_added,
                    on_unknown_interface='none',
                    on_unknown_member='reuse',
                )
            )

            self.assertEqual(path, MANAGED_PATH)
            self.assertIsNone(python_class)
            self.assertIn('TestStr', python_properties)
            self.assertIn('TestInt', python_properties)

        get_managed_data = (
            await object_manager_connection.get_managed_objects()
        )
        with self.subTest('Parse get managed objects class'):
            managed_dict = (
                parse_get_managed_objects(
                    ManagedTwoInterface,
                    get_managed_data,
                )
            )

            self.assertIn(MANAGED_PATH, managed_dict)
            managed_class, managed_properties = (
                managed_dict[MANAGED_PATH]
            )
            self.assertEqual(managed_class, ManagedTwoInterface)
            self.assertIn('test_str', managed_properties)
            self.assertIn('test_int', managed_properties)

        with self.subTest('Parse get managed objects object'):
            managed_dict = (
                parse_get_managed_objects(
                    managed_object,
                    get_managed_data,
                )
            )

            self.assertIn(MANAGED_PATH, managed_dict)
            managed_class, managed_properties = (
                managed_dict[MANAGED_PATH]
            )
            self.assertEqual(managed_class, ManagedTwoInterface)
            self.assertIn('test_str', managed_properties)
            self.assertIn('test_int', managed_properties)

        with self.subTest('Parse get managed objects iterable'):
            managed_dict = (
                parse_get_managed_objects(
                    (ManagedInterface, ManagedTwoInterface),
                    get_managed_data,
                )
            )

            self.assertIn(MANAGED_PATH, managed_dict)
            managed_class, managed_properties = (
                managed_dict[MANAGED_PATH]
            )
            self.assertEqual(managed_class, ManagedTwoInterface)
            self.assertIn('test_str', managed_properties)
            self.assertIn('test_int', managed_properties)

        with self.subTest('Parse get managed objects unknown'):
            with self.assertRaises(KeyError):
                managed_dict = (
                    parse_get_managed_objects(
                        ManagedInterface,
                        get_managed_data,
                    )
                )

            with self.assertRaises(KeyError):
                managed_dict = (
                    parse_get_managed_objects(
                        ManagedInterface,
                        get_managed_data,
                        on_unknown_interface='none',
                    )
                )

            managed_dict = (
                parse_get_managed_objects(
                    ManagedInterface,
                    get_managed_data,
                    on_unknown_interface='none',
                    on_unknown_member='reuse',
                )
            )
            path, python_class, python_properties = (
                parse_interfaces_added(
                    ManagedInterface,
                    caught_added,
                    on_unknown_interface='none',
                    on_unknown_member='reuse',
                )
            )

            self.assertIn(MANAGED_PATH, managed_dict)
            managed_class, managed_properties = (
                managed_dict[MANAGED_PATH]
            )
            self.assertIsNone(managed_class)
            self.assertIn('TestStr', managed_properties)
            self.assertIn('TestInt', managed_properties)

        async with self.assertDbusSignalEmits(
            object_manager_connection.interfaces_removed
        ) as removed_interfaces_catch:
            object_manager.remove_managed_object(managed_object)

        interfaces_removed_data = removed_interfaces_catch.output[0]

        with self.subTest('Parse removed class'):
            path, python_class = (
                parse_interfaces_removed(
                    ManagedTwoInterface,
                    interfaces_removed_data,
                )
            )

            self.assertEqual(path, MANAGED_PATH)
            self.assertEqual(python_class, ManagedTwoInterface)

        with self.subTest('Parse removed unknown'):
            with self.assertRaises(KeyError):
                path, python_class = (
                    parse_interfaces_removed(
                        ManagedInterface,
                        interfaces_removed_data,
                    )
                )

            path, python_class = (
                parse_interfaces_removed(
                    ManagedInterface,
                    interfaces_removed_data,
                    on_unknown_interface='none',
                )
            )

            self.assertEqual(path, MANAGED_PATH)
            self.assertIsNone(python_class)

    async def test_main_export_handle(self) -> None:
        await self.bus.request_name_async(CONNECTION_NAME, 0)

        object_manager = ObjectManagerTestInterface()

        object_manager_connection = ObjectManagerTestInterface.new_proxy(
            CONNECTION_NAME, OBJECT_MANAGER_PATH)

        with object_manager.export_to_dbus(OBJECT_MANAGER_PATH):
            self.assertIsInstance(
                await object_manager_connection.get_managed_objects(),
                dict,
            )

        with self.assertRaises(DbusUnknownObjectError):
            self.assertIsInstance(
                await object_manager_connection.get_managed_objects(),
                dict,
            )

    async def test_secondary_export_handle(self) -> None:
        await self.bus.request_name_async(CONNECTION_NAME, 0)

        object_manager = ObjectManagerTestInterface()

        object_manager_connection = ObjectManagerTestInterface.new_proxy(
            CONNECTION_NAME, OBJECT_MANAGER_PATH)
        object_manager.export_to_dbus(OBJECT_MANAGER_PATH)

        managed_object = ManagedInterface()
        managed_proxy = ManagedInterface.new_proxy(
            CONNECTION_NAME, MANAGED_PATH,
        )

        async with self.assertDbusSignalEmits(
            object_manager_connection.interfaces_added
        ) as added, self.assertDbusSignalEmits(
            object_manager_connection.interfaces_removed
        ) as removed, object_manager.export_with_manager(
            MANAGED_PATH, managed_object,
        ):
            self.assertEqual(
                await managed_proxy.test_int,
                TEST_NUMBER,
            )

        self.assertEqual(added.output[0][0], MANAGED_PATH)

        removed_path, removed_interfaces = removed.output[0]
        self.assertEqual(removed_path, MANAGED_PATH)
        self.assertIn(MANAGED_INTERFACE_NAME, removed_interfaces)

        with self.assertRaises(DbusUnknownObjectError):
            await managed_proxy.test_int
