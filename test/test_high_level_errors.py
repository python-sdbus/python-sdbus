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

from sdbus.exceptions import DbusFailedError
from sdbus.unittest import IsolatedDbusTestCase

from sdbus import (
    DbusInterfaceCommonAsync,
    dbus_method_async,
    request_default_bus_name_async,
)

HELLO_WORLD = 'Hello, world!'


class DbusDeriveMethodError(DbusFailedError):
    dbus_error_name = 'org.example.Method.Error'


class IndependentError(Exception):
    ...


GOOD_STR = 'Good'


class InterfaceWithErrors(
    DbusInterfaceCommonAsync,
    interface_name='org.example.test',
):

    @dbus_method_async(result_signature='s')
    async def hello_independent_error(self) -> str:
        raise IndependentError

    @dbus_method_async(result_signature='s')
    async def hello_derrived_error(self) -> str:
        raise DbusDeriveMethodError


class TestHighLevelErrors(IsolatedDbusTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        await request_default_bus_name_async('org.test')
        self.test_object = InterfaceWithErrors()
        self.test_object.export_to_dbus('/')

        self.test_object_connection = InterfaceWithErrors.new_proxy(
            'org.test', '/')

        loop = get_running_loop()

        def silence_exceptions(*args: Any, **kwrags: Any) -> None:
            ...

        loop.set_exception_handler(silence_exceptions)

    async def test_method_indenendent_error(self) -> None:
        with self.assertRaises(DbusFailedError) as cm:
            await wait_for(
                self.test_object_connection.hello_independent_error(),
                timeout=1,
            )

        exception = cm.exception
        self.assertIs(exception.__class__, DbusFailedError)

    async def test_method_derived_error(self) -> None:
        with self.assertRaises(DbusDeriveMethodError):
            await wait_for(
                self.test_object_connection.hello_derrived_error(),
                timeout=1,
            )
