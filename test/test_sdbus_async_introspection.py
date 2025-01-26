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

from sdbus.unittest import IsolatedDbusTestCase

from sdbus import DbusInterfaceCommonAsync, dbus_method_async

TEST_SERVICE_NAME = 'org.example.test'


def initialize_object(
    interface_class: type[DbusInterfaceCommonAsync],
) -> tuple[DbusInterfaceCommonAsync, DbusInterfaceCommonAsync]:
    test_object = interface_class()
    test_object.export_to_dbus('/')

    test_object_connection = interface_class.new_proxy(
        TEST_SERVICE_NAME, '/')

    return test_object, test_object_connection


class TestIntrospection(IsolatedDbusTestCase):

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        await self.bus.request_name_async("org.example.test", 0)

    async def test_method_arg_names_none(self) -> None:
        class TestInterface(
            DbusInterfaceCommonAsync,
            interface_name="org.test.intro1",
        ):
            @dbus_method_async(
                input_signature="ss",
                result_signature="i",
            )
            async def login(
                self,
                user_name: str,
                pin_code: str,
            ) -> int:
                return 0

        obj, rem = initialize_object(TestInterface)

        introspection = await rem.dbus_introspect()
        self.assertNotIn('name="user_name"', introspection)
        self.assertNotIn('name="result"', introspection)
        self.assertNotIn('name="pin_code"', introspection)

    async def test_method_arg_names_result_names_only(self) -> None:
        class TestInterface(
            DbusInterfaceCommonAsync,
            interface_name="org.test.intro2",
        ):
            @dbus_method_async(
                input_signature="ss",
                result_signature="i",
                result_args_names=("result",)
            )
            async def login(
                self,
                user_name: str,
                pin_code: str,
            ) -> int:
                return 0

        obj, rem = initialize_object(TestInterface)

        introspection = await rem.dbus_introspect()
        self.assertIn('name="user_name"', introspection)
        self.assertIn('name="result"', introspection)
        self.assertIn('name="pin_code"', introspection)

    async def test_method_arg_names_full(self) -> None:
        class TestInterface(
            DbusInterfaceCommonAsync,
            interface_name="org.test.intro3",
        ):
            @dbus_method_async(
                input_signature="ss",
                input_args_names=("UserName", "PinCode"),
                result_signature="i",
                result_args_names=("Result",)
            )
            async def login(
                self,
                user_name: str,
                pin_code: str,
            ) -> int:
                return 0

        obj, rem = initialize_object(TestInterface)

        introspection = await rem.dbus_introspect()
        self.assertIn('name="UserName"', introspection)
        self.assertIn('name="Result"', introspection)
        self.assertIn('name="PinCode"', introspection)

    async def test_method_arg_names_no_return_args(self) -> None:
        class TestInterface(
            DbusInterfaceCommonAsync,
            interface_name="org.test.intro4",
        ):
            @dbus_method_async(
                input_signature="ss",
                result_args_names=(),
            )
            async def login(
                self,
                user_name: str,
                pin_code: str,
            ) -> None:
                return None

        obj, rem = initialize_object(TestInterface)

        introspection = await rem.dbus_introspect()
        self.assertIn('name="user_name"', introspection)
        self.assertIn('name="pin_code"', introspection)
