# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2020, 2021 igo95862

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

from asyncio import Event, get_running_loop, wait_for
from asyncio.subprocess import create_subprocess_exec
from typing import Tuple

from sdbus.sd_bus_internals import DBUS_ERROR_TO_EXCEPTION, SdBus

from sdbus import (
    DbusFailedError,
    DbusFileExistsError,
    DbusInterfaceCommonAsync,
    DbusNoReplyFlag,
    DbusUnknownObjectError,
    SdBusUnmappedMessageError,
    dbus_method_async,
    dbus_method_async_override,
    dbus_property_async,
    dbus_property_async_override,
    dbus_signal_async,
)

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


class TestInterface(DbusInterfaceCommonAsync,
                    interface_name='org.test.test',
                    ):

    def __init__(self) -> None:
        super().__init__()
        self.test_string = 'test_property'
        self.test_string_read = 'read'
        self.test_no_reply_string = 'no'
        self.no_reply_sync = Event()

    @dbus_method_async("s", "s")
    async def upper(self, string: str) -> str:
        """Uppercase the input"""
        return string.upper()

    @dbus_method_async(result_signature='x')
    async def test_int(self) -> int:
        return 1

    @dbus_method_async(result_signature='x', result_args_names=('an_int', ))
    async def int_annotated(self) -> int:
        return 1

    @dbus_property_async("s")
    def test_property(self) -> str:
        """Test property"""
        return self.test_string

    @test_property.setter
    def test_property_set(self, new_property: str) -> None:
        self.test_string = new_property

    @dbus_property_async("s")
    def test_property_read_only(self) -> str:
        return self.test_string_read

    @dbus_method_async("sb", "s")
    async def kwargs_function(
            self,
            input: str = 'test',
            is_upper: bool = True) -> str:
        if is_upper:
            return input.upper()
        else:
            return input.lower()

    @dbus_method_async("sb", "s", 0, ('string_result', ))
    async def kwargs_function_annotated(
            self,
            input: str = 'test',
            is_upper: bool = True) -> str:
        if is_upper:
            return input.upper()
        else:
            return input.lower()

    @dbus_signal_async('ss')
    def test_signal(self) -> Tuple[str, str]:
        """Test signal"""
        raise NotImplementedError

    @dbus_method_async()
    async def raise_base_exception(self) -> None:
        raise DbusFailedError('Test error')

    @dbus_method_async()
    async def raise_derived_exception(self) -> None:
        raise DbusFileExistsError('Test error 2')

    @dbus_method_async()
    async def raise_custom_error(self) -> None:
        raise DbusErrorTest('Custom')

    @dbus_method_async()
    async def raise_and_unmap_error(self) -> None:
        try:
            DBUS_ERROR_TO_EXCEPTION.pop('org.example.Nothing')
        except KeyError:
            ...

        raise DbusErrorUnmappedLater('Should be unmapped')

    @dbus_method_async('s', flags=DbusNoReplyFlag)
    async def no_reply_method(self, new_value: str) -> None:
        self.no_reply_sync.set()


class DbusErrorTest(DbusFailedError):
    dbus_error_name = 'org.example.Error'


class DbusErrorUnmappedLater(DbusFailedError):
    dbus_error_name = 'org.example.Nothing'


def initialize_object(bus: SdBus) -> Tuple[TestInterface, TestInterface]:
    test_object = TestInterface()
    test_object.export_to_dbus('/', bus)

    test_object_connection = TestInterface.new_connect(
        "org.example.test", '/', bus)

    return test_object, test_object_connection


class TestProxy(TempDbusTest):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        await self.bus.request_name_async("org.example.test", 0)

        test_object = TestInterface()
        test_object.export_to_dbus('/', self.bus)
        test_object_connection = TestInterface.new_connect(
            "org.example.test", '/', self.bus)

        await test_object_connection.dbus_ping()

    async def test_method_kwargs(self) -> None:
        test_object, test_object_connection = initialize_object(self.bus)

        self.assertEqual(
            'TEST',
            await test_object_connection.kwargs_function(
                'test', True)
        )

        self.assertEqual(
            'TEST',
            await test_object_connection.kwargs_function())

        self.assertEqual(
            'test',
            await test_object_connection.kwargs_function(
                is_upper=False))

        self.assertEqual(
            'ASD',
            await test_object_connection.kwargs_function('asd'))

        self.assertEqual(
            'ASD',
            await test_object_connection.kwargs_function(input='asd'))

        self.assertEqual(
            'asd',
            await test_object_connection.kwargs_function(
                'ASD', is_upper=False))

        self.assertEqual(
            'asd',
            await test_object_connection.kwargs_function(
                input='ASD', is_upper=False))

    async def test_method(self) -> None:
        test_object, test_object_connection = initialize_object(self.bus)

        test_string = 'asdafsrfgdrtuhrytuj'

        self.assertEqual(test_string.upper(),
                         await test_object.upper(test_string))

        self.assertEqual(1, await test_object_connection.test_int())

        self.assertEqual(
            test_string.upper(),
            await test_object_connection.upper(test_string))

    async def test_subclass(self) -> None:
        test_object, test_object_connection = initialize_object(self.bus)

        test_var = ['asdasd']

        class TestInheritnce(TestInterface):
            @dbus_method_async_override()
            async def test_int(self) -> int:
                return 2

            @dbus_property_async_override()
            def test_property(self) -> str:
                return test_var[0]

            @test_property.setter
            def test_property_setter(self, var: str) -> None:
                nonlocal test_var
                test_var.insert(0, var)

        test_subclass = TestInheritnce()

        test_subclass.export_to_dbus('/subclass', self.bus)

        self.assertEqual(await test_subclass.test_int(), 2)

        test_subclass_connection = TestInheritnce.new_connect(
            "org.example.test", '/subclass', self.bus)

        self.assertEqual(await test_subclass_connection.test_int(), 2)

        self.assertEqual(test_var[0], await test_subclass.test_property)

        await test_subclass.test_property.set_async('12345')

        self.assertEqual(test_var[0], await test_subclass.test_property)
        self.assertEqual('12345', await test_subclass.test_property)

    async def test_bad_subclass(self) -> None:
        def bad_call() -> None:
            class TestInheritnce(TestInterface):
                async def test_int(self) -> int:
                    return 2

        self.assertRaises(TypeError, bad_call)

    async def test_properties(self) -> None:
        test_object, test_object_connection = initialize_object(self.bus)

        self.assertEqual(
            'test_property',
            await test_object.test_property.get_async())

        self.assertEqual(
            'test_property', await test_object.test_property)

        self.assertEqual(
            await wait_for(test_object_connection.test_property, 0.5),
            await test_object.test_property)

        self.assertEqual(
            'test_property',
            await wait_for(test_object_connection.test_property, 0.5))

        self.assertEqual(
            await test_object.test_property_read_only,
            await wait_for(
                test_object_connection.test_property_read_only, 0.5))

        new_string = 'asdsgrghdthdth'

        await wait_for(
            test_object_connection.test_property.set_async(
                new_string),
            0.5)

        self.assertEqual(
            new_string, await test_object.test_property)

        self.assertEqual(
            new_string,
            await wait_for(test_object_connection.test_property, 0.5)
        )

    async def test_signal(self) -> None:
        test_object, test_object_connection = initialize_object(self.bus)

        loop = get_running_loop()

        test_tuple = ('sgfsretg', 'asd')

        ai_dbus = test_object_connection.test_signal.__aiter__()
        aw_dbus = ai_dbus.__anext__()
        q = test_object.test_signal._get_local_queue()

        loop.call_at(0, test_object.test_signal.emit, test_tuple)

        self.assertEqual(test_tuple, await wait_for(aw_dbus, timeout=1))

        self.assertEqual(test_tuple, await wait_for(q.get(), timeout=1))

    async def test_exceptions(self) -> None:
        test_object, test_object_connection = initialize_object(self.bus)

        async def first_test() -> None:
            await test_object_connection.raise_base_exception()

        loop = get_running_loop()

        t1 = loop.create_task(first_test())

        try:
            await wait_for(t1, timeout=1)
        except DbusFailedError:
            ...

        self.assertRaises(DbusFailedError, t1.result)

        async def second_test() -> None:
            await test_object_connection.raise_derived_exception()

        t2 = loop.create_task(second_test())

        try:
            await wait_for(t2, timeout=1)
        except DbusFileExistsError:
            ...

        self.assertRaises(DbusFileExistsError, t2.result)

        async def third_test() -> None:
            await test_object_connection.raise_custom_error()

        t3 = loop.create_task(third_test())

        try:
            await wait_for(t3, timeout=1)
        except DbusFailedError:
            ...

        self.assertRaises(DbusErrorTest, t3.result)

        def bad_exception_error_name_used() -> None:
            class BadDbusError(DbusFailedError):
                dbus_error_name = 'org.freedesktop.DBus.Error.NoMemory'

        self.assertRaises(ValueError, bad_exception_error_name_used)

        def bad_exception_no_error_name() -> None:
            class BadDbusError(DbusFailedError):
                ...

        self.assertRaises(TypeError, bad_exception_no_error_name)

        async def test_unmapped_expection() -> None:
            await test_object_connection.raise_and_unmap_error()

        t4 = loop.create_task(test_unmapped_expection())

        try:
            await wait_for(t4, timeout=1)
        except SdBusUnmappedMessageError:
            ...

        self.assertRaises(SdBusUnmappedMessageError, t4.result)

    async def test_no_reply_method(self) -> None:
        test_object, test_object_connection = initialize_object(self.bus)

        await wait_for(test_object_connection.no_reply_method('yes'),
                       timeout=1)

        await wait_for(test_object.no_reply_sync.wait(), timeout=1)

    async def test_interface_remove(self) -> None:
        test_object, test_object_connection = initialize_object(self.bus)

        from gc import collect

        del test_object

        collect()

        loop = get_running_loop()

        t = loop.create_task(test_object_connection.dbus_introspect())

        try:
            await wait_for(t, timeout=0.2)
        except DbusUnknownObjectError:
            ...

        self.assertRaises(DbusUnknownObjectError, t.result)

    def test_docstring(self) -> None:
        test_object, test_object_connection = initialize_object(self.bus)

        from pydoc import getdoc

        self.assertTrue(getdoc(test_object.upper))

        self.assertTrue(getdoc(test_object_connection.upper))

        self.assertTrue(getdoc(test_object.test_property))

        self.assertTrue(
            getdoc(test_object_connection.test_property))

        self.assertTrue(getdoc(test_object.test_signal))

        self.assertTrue(
            getdoc(test_object_connection.test_signal))
