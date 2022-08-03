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

from asyncio import Event, get_running_loop, sleep, wait_for
from asyncio.subprocess import create_subprocess_exec
from typing import Tuple
from unittest import SkipTest

from sdbus.dbus_common_funcs import PROPERTY_FLAGS_MASK, count_bits
from sdbus.sd_bus_internals import (
    DBUS_ERROR_TO_EXCEPTION,
    DbusDeprecatedFlag,
    DbusPropertyConstFlag,
    DbusPropertyEmitsChangeFlag,
    is_interface_name_valid,
)
from sdbus.unittest import IsolatedDbusTestCase

from sdbus import (
    DbusFailedError,
    DbusFileExistsError,
    DbusInterfaceCommonAsync,
    DbusNoReplyFlag,
    DbusUnknownObjectError,
    SdBusLibraryError,
    SdBusUnmappedMessageError,
    dbus_method_async,
    dbus_method_async_override,
    dbus_property_async,
    dbus_property_async_override,
    dbus_signal_async,
    get_current_message,
)


class TestPing(IsolatedDbusTestCase):

    async def test_ping_with_busctl(self) -> None:
        try:
            busctl_process = await create_subprocess_exec(
                '/usr/bin/busctl',
                '--user',
                'call',
                'org.freedesktop.DBus', '/org/freedesktop/DBus',
                'org.freedesktop.DBus.Peer', 'Ping',
            )
        except FileNotFoundError:
            raise SkipTest('busctl not installed')

        return_code = await busctl_process.wait()
        self.assertEqual(return_code, 0)

    async def test_ping(self) -> None:
        m = self.bus.new_method_call_message(
            'org.freedesktop.DBus', '/org/freedesktop/DBus',
            'org.freedesktop.DBus.Peer', 'Ping',
        )
        r = await self.bus.call_async(m)
        self.assertIsNone(r.get_contents())


class TestRequestName(IsolatedDbusTestCase):
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

    @dbus_method_async(result_signature='s')
    async def get_sender(self) -> str:
        message = get_current_message()
        return message.sender or ''

    @dbus_method_async(result_signature='x')
    async def test_int(self) -> int:
        return 1

    @dbus_method_async(result_signature='x', result_args_names=('an_int', ))
    async def int_annotated(self) -> int:
        return 1

    @dbus_property_async(
        "s",
        flags=DbusPropertyEmitsChangeFlag,
    )
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

    @dbus_property_async("s")
    def test_constant_property(self) -> str:
        return "a"

    @dbus_method_async(
        result_signature='(ss)'
    )
    async def test_struct_return(self) -> Tuple[str, str]:
        return ('hello', 'world')

    @dbus_method_async(
        result_signature='(ss)'
    )
    async def test_struct_return_workaround(self) -> Tuple[Tuple[str, str]]:
        return (('hello', 'world'), )

    @dbus_method_async()
    async def looong_method(self) -> None:
        await sleep(100)


class DbusErrorTest(DbusFailedError):
    dbus_error_name = 'org.example.Error'


class DbusErrorUnmappedLater(DbusFailedError):
    dbus_error_name = 'org.example.Nothing'


TEST_SERVICE_NAME = 'org.example.test'


def initialize_object() -> Tuple[TestInterface, TestInterface]:
    test_object = TestInterface()
    test_object.export_to_dbus('/')

    test_object_connection = TestInterface.new_proxy(
        TEST_SERVICE_NAME, '/')

    return test_object, test_object_connection


class TestProxy(IsolatedDbusTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        await self.bus.request_name_async(TEST_SERVICE_NAME, 0)

    async def test_method_kwargs(self) -> None:
        test_object, test_object_connection = initialize_object()

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
        test_object, test_object_connection = initialize_object()

        test_string = 'asdafsrfgdrtuhrytuj'

        self.assertEqual(test_string.upper(),
                         await test_object.upper(test_string))

        self.assertEqual(1, await test_object_connection.test_int())

        self.assertEqual(
            test_string.upper(),
            await test_object_connection.upper(test_string))

        self.assertEqual(
            await wait_for(test_object.test_struct_return(), 0.5),
            await wait_for(test_object_connection.test_struct_return(), 0.5),
        )

        self.assertEqual(
            (await wait_for(
                test_object.test_struct_return_workaround(), 0.5))[0],
            await wait_for(
                test_object_connection.test_struct_return_workaround(), 0.5),
        )

        self.assertTrue(await test_object_connection.get_sender())

    async def test_subclass(self) -> None:
        test_object, test_object_connection = initialize_object()

        test_var = ['asdasd']

        class TestInheritence(TestInterface):
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

        test_subclass = TestInheritence()

        test_subclass.export_to_dbus('/subclass', self.bus)

        self.assertEqual(await test_subclass.test_int(), 2)

        test_subclass_connection = TestInheritence.new_proxy(
            TEST_SERVICE_NAME, '/subclass', self.bus)

        self.assertEqual(await test_subclass_connection.test_int(), 2)

        self.assertEqual(test_var[0], await test_subclass.test_property)

        await test_subclass.test_property.set_async('12345')

        self.assertEqual(test_var[0], await test_subclass.test_property)
        self.assertEqual('12345', await test_subclass.test_property)

        with self.subTest('Test dbus to python mapping'):
            self.assertIn(
                test_object.properties_changed.dbus_signal.signal_name,
                test_object._dbus_to_python_name_map,
            )

            self.assertIn(
                test_subclass.properties_changed.dbus_signal.signal_name,
                test_subclass._dbus_to_python_name_map,
            )

            self.assertIn(
                test_subclass.test_property.dbus_property.property_name,
                test_subclass._dbus_to_python_name_map,
            )

        with self.subTest('Tripple subclass'):
            class TestInheritenceTri(TestInheritence):
                @dbus_method_async_override()
                async def test_int(self) -> int:
                    return 3

                @dbus_property_async_override()
                def test_property(self) -> str:
                    return 'tri'

            test_subclass_tri = TestInheritenceTri()

            test_subclass_tri.export_to_dbus('/subclass/tri', self.bus)

            self.assertEqual(await test_subclass_tri.test_int(), 3)

            test_subclass_tri_connection = TestInheritenceTri.new_proxy(
                TEST_SERVICE_NAME, '/subclass/tri', self.bus)

            self.assertEqual(await test_subclass_tri_connection.test_int(), 3)

            self.assertEqual(await test_subclass_tri.test_property, 'tri')
            self.assertEqual(
                await test_subclass_tri_connection.test_property, 'tri')

    async def test_bad_subclass(self) -> None:
        with self.assertRaises(TypeError):
            class TestInheritence(TestInterface):
                async def test_int(self) -> int:
                    return 2

        with self.assertRaises(TypeError):
            class TestInheritence2(TestInterface):
                @dbus_method_async_override()
                async def test_unrelated(self) -> int:
                    return 2

    async def test_properties(self) -> None:
        test_object, test_object_connection = initialize_object()

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
        test_object, test_object_connection = initialize_object()

        loop = get_running_loop()

        test_tuple = ('sgfsretg', 'asd')

        ai_dbus = test_object_connection.test_signal.__aiter__()
        aw_dbus = ai_dbus.__anext__()
        q = test_object.test_signal._get_local_queue()

        loop.call_at(0, test_object.test_signal.emit, test_tuple)

        self.assertEqual(test_tuple, await wait_for(aw_dbus, timeout=1))

        self.assertEqual(test_tuple, await wait_for(q.get(), timeout=1))

    async def test_signal_catch_anywhere(self) -> None:
        test_object, test_object_connection = initialize_object()

        loop = get_running_loop()

        test_tuple = ('sgfsretg', 'asd')

        with self.subTest('Catch anywhere over D-Bus object'):
            async def catch_anywhere_oneshot_dbus(
            ) -> Tuple[str, Tuple[str, str]]:
                async for x in test_object_connection.test_signal\
                        .catch_anywhere():
                    return x

                raise RuntimeError

            catch_anywhere_over_dbus_task \
                = loop.create_task(catch_anywhere_oneshot_dbus())

            await sleep(0)

            test_object.test_signal.emit(test_tuple)

            self.assertEqual(
                ('/', test_tuple),
                await wait_for(catch_anywhere_over_dbus_task, timeout=1),
            )

        with self.subTest('Catch anywhere over D-Bus class'):
            async def catch_anywhere_oneshot_from_class(
            ) -> Tuple[str, Tuple[str, str]]:
                async for x in TestInterface.test_signal.catch_anywhere(
                        TEST_SERVICE_NAME, self.bus):
                    return x

                raise RuntimeError

            catch_anywhere_from_class_task \
                = loop.create_task(catch_anywhere_oneshot_from_class())

            await sleep(0)

            test_object.test_signal.emit(test_tuple)

            self.assertEqual(
                ('/', test_tuple),
                await wait_for(catch_anywhere_from_class_task, timeout=1),
            )

        with self.subTest('Catch anywhere over local object'):
            async def catch_anywhere_oneshot_local(
            ) -> Tuple[str, Tuple[str, str]]:
                async for x in test_object.test_signal.catch_anywhere():
                    return x

                raise RuntimeError

            catch_anywhere_over_local_task \
                = loop.create_task(catch_anywhere_oneshot_local())

            with self.assertRaises(NotImplementedError):
                await wait_for(
                    catch_anywhere_over_local_task,
                    timeout=1,
                )

    async def test_exceptions(self) -> None:
        test_object, test_object_connection = initialize_object()

        async def first_test() -> None:
            await test_object_connection.raise_base_exception()

        with self.assertRaises(DbusFailedError):
            await wait_for(first_test(), timeout=1)

        async def second_test() -> None:
            await test_object_connection.raise_derived_exception()

        with self.assertRaises(DbusFileExistsError):
            await wait_for(second_test(), timeout=1)

        async def third_test() -> None:
            await test_object_connection.raise_custom_error()

        with self.assertRaises(DbusErrorTest):
            await wait_for(third_test(), timeout=1)

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

        with self.assertRaises(SdBusUnmappedMessageError):
            await wait_for(test_unmapped_expection(), timeout=1)

    async def test_no_reply_method(self) -> None:
        test_object, test_object_connection = initialize_object()

        await wait_for(test_object_connection.no_reply_method('yes'),
                       timeout=1)

        await wait_for(test_object.no_reply_sync.wait(), timeout=1)

    async def test_interface_remove(self) -> None:
        test_object, test_object_connection = initialize_object()

        from gc import collect

        del test_object

        collect()

        with self.assertRaises(DbusUnknownObjectError):
            await wait_for(test_object_connection.dbus_introspect(),
                           timeout=0.2)

    def test_docstring(self) -> None:
        test_object, test_object_connection = initialize_object()

        from pydoc import getdoc

        self.assertTrue(getdoc(test_object.upper))

        self.assertTrue(getdoc(test_object_connection.upper))

        self.assertTrue(getdoc(test_object.test_property))

        self.assertTrue(
            getdoc(test_object_connection.test_property))

        self.assertTrue(getdoc(test_object.test_signal))

        self.assertTrue(
            getdoc(test_object_connection.test_signal))

    async def test_emits_properties_changed(self) -> None:
        test_object, test_object_connection = initialize_object()

        test_str = 'should_be_emited'

        loop = get_running_loop()

        async def catch_property_emit_connection() -> str:
            async for x in test_object_connection.properties_changed.catch():
                for v in x[1].values():
                    probably_str = v[1]
                    if isinstance(probably_str, str):
                        return probably_str
                    else:
                        raise TypeError
            raise ValueError

        async def catch_property_emit_local() -> str:
            async for x in test_object.properties_changed.catch():
                for v in x[1].values():
                    probably_str = v[1]
                    if isinstance(probably_str, str):
                        return probably_str
                    else:
                        raise TypeError
            raise ValueError

        t1 = loop.create_task(catch_property_emit_connection())
        t2 = loop.create_task(catch_property_emit_local())

        await test_object_connection.test_property.set_async(test_str)

        t1_result = await wait_for(t1, timeout=0.2)
        t2_result = await wait_for(t2, timeout=0.2)

        self.assertEqual(t1_result, test_str)
        self.assertEqual(t2_result, test_str)

    async def test_property_flags(self) -> None:
        self.assertEqual(0, PROPERTY_FLAGS_MASK & DbusDeprecatedFlag)
        self.assertEqual(
            1,
            count_bits(PROPERTY_FLAGS_MASK & (DbusDeprecatedFlag
                                              | DbusPropertyEmitsChangeFlag))
        )
        self.assertEqual(
            2,
            count_bits(
                PROPERTY_FLAGS_MASK & (
                    DbusDeprecatedFlag |
                    DbusPropertyConstFlag |
                    DbusPropertyEmitsChangeFlag)))

        def must_raise_value_error() -> None:
            class InvalidPropertiesFlags(
                DbusInterfaceCommonAsync,
                    interface_name='org.test.test'):
                @dbus_property_async(
                    "s",
                    flags=DbusPropertyConstFlag | DbusPropertyEmitsChangeFlag,
                )
                def test_constant(self) -> str:
                    return "a"

        self.assertRaisesRegex(
            AssertionError,
            '^Incorrect number of Property flags',
            must_raise_value_error,
        )

        def should_be_no_error() -> None:
            class ValidPropertiesFlags(
                DbusInterfaceCommonAsync,
                    interface_name='org.test.test'):
                @dbus_property_async(
                    "s",
                    flags=DbusDeprecatedFlag | DbusPropertyEmitsChangeFlag,
                )
                def test_constant(self) -> str:
                    return "a"

        should_be_no_error()

    async def test_bus_close(self) -> None:
        test_object, test_object_connection = initialize_object()

        async def too_long_wait() -> None:
            await test_object_connection.looong_method()

        self.bus.close()

        with self.assertRaises(SdBusLibraryError):
            await wait_for(too_long_wait(), timeout=1)

    async def test_singal_queue_wildcard_match(self) -> None:
        test_object, test_object_connection = initialize_object()

        message_queue = await self.bus.get_signal_queue_async(
            TEST_SERVICE_NAME,
            None, None, None)

        test_object.test_signal.emit(('test', 'signal'))

        message = await wait_for(message_queue.get(), timeout=1)
        self.assertEqual(message.member,
                         test_object.test_signal.dbus_signal.signal_name)

    async def test_class_with_string_subclass_parameter(self) -> None:
        from enum import Enum

        class InterfaceNameEnum(str, Enum):
            FOO = 'org.example.foo'
            BAR = 'org.example.bar'

        class ObjectPathEnum(str, Enum):
            FOO = '/foo'
            BAR = '/bar'

        class EnumedInterfaceAsync(
            DbusInterfaceCommonAsync,
            interface_name=InterfaceNameEnum.BAR,
        ):

            @dbus_property_async('s')
            def hello_world(self) -> str:
                return 'Hello World!'

        test_object = EnumedInterfaceAsync()
        test_object.export_to_dbus(ObjectPathEnum.FOO)

    async def test_name_validations(self) -> None:
        if not __debug__:
            raise SkipTest('Assertions are not enabled')

        try:
            is_interface_name_valid('org.test')
        except NotImplementedError:
            raise SkipTest('Validation functions not available')

        def test_bad_interface_name() -> None:
            class BadInterfaceName(
                DbusInterfaceCommonAsync,
                interface_name='0.test',
            ):
                ...

        self.assertRaisesRegex(
            AssertionError,
            '^Invalid interface name',
            test_bad_interface_name,
        )

        def test_bad_method_name() -> None:
            class BadMethodName(
                DbusInterfaceCommonAsync,
                interface_name='org.example',
            ):
                @dbus_method_async(
                    result_signature='s',
                    method_name='🤫',
                )
                async def test(self) -> str:
                    return 'test'

        self.assertRaisesRegex(
            AssertionError,
            '^Invalid method name',
            test_bad_method_name,
        )

        def test_bad_property_name() -> None:
            class BadPropertyName(
                DbusInterfaceCommonAsync,
                interface_name='org.example',
            ):
                @dbus_property_async(
                    property_signature='s',
                    property_name='🤫',
                )
                def test(self) -> str:
                    return 'test'

        self.assertRaisesRegex(
            AssertionError,
            '^Invalid property name',
            test_bad_property_name,
        )

        def test_bad_signal_name() -> None:
            class BadSignalName(
                DbusInterfaceCommonAsync,
                interface_name='org.example',
            ):
                @dbus_signal_async(
                    signal_signature='s',
                    signal_name='🤫',
                )
                def test(self) -> str:
                    raise NotImplementedError

        self.assertRaisesRegex(
            AssertionError,
            '^Invalid signal name',
            test_bad_signal_name,
        )

    async def test_properties_get_all_dict(self) -> None:
        test_object, test_object_connection = initialize_object()

        dbus_dict = await test_object_connection._properties_get_all(
            'org.test.test')

        self.assertEqual(
            await test_object.test_property,
            dbus_dict['TestProperty'][1],
        )

        self.assertEqual(
            await test_object.test_property,
            (
                await test_object_connection.properties_get_all_dict()
            )['test_property'],
        )
