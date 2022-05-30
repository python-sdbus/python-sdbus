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

from asyncio import get_running_loop, sleep, wait_for
from typing import Any, Dict, List, Tuple

from sdbus.unittest import IsolatedDbusTestCase

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
    interface_name='org.test.test',
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
        loop = get_running_loop()
        await self.bus.request_name_async(CONNECTION_NAME, 0)

        object_manager = ObjectManagerTestInterface()
        object_manager.export_to_dbus(OBJECT_MANAGER_PATH)

        object_manager_connection = ObjectManagerTestInterface.new_proxy(
            CONNECTION_NAME, OBJECT_MANAGER_PATH)

        self.assertEqual(
            await object_manager_connection.get_hello_world(),
            HELLO_WORLD)

        async def catch_interfaces_added() -> Tuple[str,
                                                    Dict[str,
                                                         Dict[str, Any]]]:
            async for x in object_manager_connection.interfaces_added:
                return x

            raise RuntimeError

        catch_added_task = loop.create_task(catch_interfaces_added())

        async def catch_interfaces_removed() -> Tuple[str, List[str]]:
            async for x in object_manager_connection.interfaces_removed:
                return x

            raise RuntimeError

        catch_removed_task = loop.create_task(catch_interfaces_removed())

        await sleep(0)

        managed_object = ManagedInterface()

        object_manager.export_with_manager(MANAGED_PATH, managed_object)

        caught_added = await wait_for(catch_added_task, timeout=0.5)

        added_path, added_attributes = caught_added

        self.assertEqual(added_path, MANAGED_PATH)

        self.assertEqual(
            added_attributes[
                MANAGED_INTERFACE_NAME][
                    'TestInt'][1],
            TEST_NUMBER,
        )

        object_manager.remove_managed_object(managed_object)

        path_removed, interfaces_removed = await wait_for(
            catch_removed_task, timeout=1)

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
