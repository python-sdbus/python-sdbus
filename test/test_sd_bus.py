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

from asyncio.subprocess import create_subprocess_exec

from py_sd_bus.dbus_proxy import DbusInterfaceCommon, dbus_method

from .common_test_util import TempDbusTest


class TestPing(TempDbusTest):

    async def test_ping_with_busctl(self) -> None:
        busctl_process = await create_subprocess_exec(
            '/usr/bin/busctl',
            '--user',
            'call',
            'org.freedesktop.DBus', '/org/freedesktop/DBus',
            'org.freedesktop.DBus.Peer', 'Ping',
        )
        return_code = await busctl_process.wait()
        self.assertEqual(return_code, 0)

    async def test_ping(self) -> None:
        m = self.bus.new_method_call_message(
            'org.freedesktop.DBus', '/org/freedesktop/DBus',
            'org.freedesktop.DBus.Peer', 'Ping',
        )
        r = await self.bus.call_async(m)
        self.assertIsNone(r.get_contents())


class TestRequestName(TempDbusTest):
    async def test_request_name(self) -> None:
        await self.bus.request_name_async("org.example.test", 0)


class TestProxy(TempDbusTest):
    async def test_proxy(self) -> None:
        test_string = 'asdarfaetfwsergtdhfgyhjtygji'

        await self.bus.request_name_async("org.example.test", 0)

        class TestInterface(DbusInterfaceCommon,
                            interface_name='org.test.test',
                            ):

            @dbus_method(input_signature="s", result_signature="s")
            async def upper(self, string: str) -> str:
                return string.upper()

        test_object = TestInterface()
        await test_object.start_serving(self.bus, '/')
        test_object_connection = TestInterface.connect(
            "org.example.test", '/', self.bus)

        await test_object_connection.ping()

        # Test python-to-python
        self.assertEqual(test_string.upper(),
                         await test_object.upper(test_string))
        # Test python-dbus-python
        self.assertEqual(test_string.upper(),
                         await test_object_connection.upper(test_string))
