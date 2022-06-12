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

from asyncio import get_running_loop, wait_for
from typing import Any

from sdbus.unittest import IsolatedDbusTestCase

from sdbus import (
    DbusFailedError,
    DbusInterfaceCommonAsync,
    dbus_method_async,
    dbus_property_async,
    request_default_bus_name_async,
)

HELLO_WORLD = 'Hello, world!'


class InterfaceWithErrors(
    DbusInterfaceCommonAsync,
    interface_name='org.example.test',
):
    @dbus_property_async('s')
    def test_str(self) -> str:
        raise RuntimeError

    @dbus_method_async(result_signature='s')
    async def hello_error(self) -> str:
        raise AttributeError

    @dbus_method_async(result_signature='s')
    async def hello_world(self) -> str:
        return HELLO_WORLD


class TestLowLevelErrors(IsolatedDbusTestCase):
    async def test_low_level_error(self) -> None:
        await request_default_bus_name_async('org.test')
        test_object = InterfaceWithErrors()
        test_object.export_to_dbus('/')

        test_object_connection = InterfaceWithErrors.new_proxy(
            'org.test', '/')

        loop = get_running_loop()

        def silence_exceptions(*args: Any, **kwrags: Any) -> None:
            ...

        loop.set_exception_handler(silence_exceptions)

        with self.assertRaises(DbusFailedError) as cm:
            await wait_for(test_object_connection.test_str.get_async(),
                           timeout=1)

        should_be_dbus_failed = cm.exception
        self.assertIs(should_be_dbus_failed.__class__, DbusFailedError)

        await test_object_connection.hello_world()
