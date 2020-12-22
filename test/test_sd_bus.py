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

from py_sd_bus.dbus_proxy import (DbusInterfaceCommon, dbus_method,
                                  dbus_overload, dbus_property)

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


class TestInterface(DbusInterfaceCommon,
                    interface_name='org.test.test',
                    ):

    def __init__(self) -> None:
        super().__init__()
        self.test_string = 'test_property'
        self.test_string_read = 'read'

    @dbus_method(input_signature="s", result_signature="s")
    async def upper(self, string: str) -> str:
        return string.upper()

    @dbus_method(result_signature='x')
    async def test_int(self) -> int:
        return 1

    @dbus_property("s")
    def test_property(self) -> str:
        return self.test_string

    @test_property.setter
    def test_property_set(self, new_property: str) -> None:
        self.test_string = new_property

    @dbus_property("s")
    def test_property_read_only(self) -> str:
        return self.test_string_read


class TestProxy(TempDbusTest):
    async def test_proxy(self) -> None:
        test_string = 'asdarfaetfwsergtdhfgyhjtygji'

        await self.bus.request_name_async("org.example.test", 0)

        test_object = TestInterface()
        await test_object.start_serving(self.bus, '/')
        test_object_connection = TestInterface.new_connect(
            self.bus, "org.example.test", '/', )

        await test_object_connection.ping()

        with self.subTest("Test python-to-python"):
            self.assertEqual(test_string.upper(),
                             await test_object.upper(test_string))

        with self.subTest("Test python-dbus-python"):
            self.assertEqual(1, await test_object_connection.test_int())

            self.assertEqual(test_string.upper(),
                             await test_object_connection.upper(test_string))

    async def test_subclass(self) -> None:
        await self.bus.request_name_async("org.example.test", 0)

        class TestInheritnce(TestInterface):
            @dbus_overload
            async def test_int(self) -> int:
                return 2

        test_object = TestInheritnce()

        await test_object.start_serving(self.bus, '/')

        with self.subTest('Subclass test: python-python'):
            self.assertEqual(await test_object.test_int(), 2)

        test_object_connection = TestInheritnce.new_connect(
            self.bus, "org.example.test", '/', )

        with self.subTest('Subclass test: python-dbus-python'):
            self.assertEqual(await test_object_connection.test_int(), 2)

    async def test_properties(self) -> None:
        await self.bus.request_name_async("org.example.test", 0)
        test_object = TestInterface()

        await test_object.start_serving(self.bus, '/')

        test_object_connection = TestInterface.new_connect(
            self.bus, "org.example.test", '/', )

        with self.subTest('Property read: python-python'):
            self.assertEqual(
                'test_property', await test_object.test_property.get_async())

            self.assertEqual(
                'test_property', await test_object.test_property)

        with self.subTest('Property read: python-dbus-python'):
            self.assertEqual(
                await test_object_connection.test_property,
                await test_object.test_property)

            self.assertEqual(
                'test_property',
                await test_object_connection.test_property)

            self.assertEqual(
                await test_object.test_property_read_only,
                await test_object_connection.test_property_read_only)

        with self.subTest('Property write'):
            new_string = 'asdsgrghdthdth'

            await test_object_connection.test_property.set_async(new_string)

            self.assertEqual(
                new_string, await test_object.test_property)

            self.assertEqual(
                new_string,
                await test_object_connection.test_property)
