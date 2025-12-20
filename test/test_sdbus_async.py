# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2020-2023 igo95862

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

from asyncio import Event, get_running_loop
from asyncio import run as asyncio_run
from asyncio import sleep, wait_for
from asyncio.subprocess import create_subprocess_exec
from typing import TYPE_CHECKING
from unittest import SkipTest

from sdbus.exceptions import (
    DbusFailedError,
    DbusFileExistsError,
    DbusNoReplyError,
    DbusPropertyReadOnlyError,
    DbusUnknownObjectError,
    SdBusLibraryError,
    SdBusUnmappedMessageError,
)
from sdbus.sd_bus_internals import (
    DBUS_ERROR_TO_EXCEPTION,
    DbusPropertyEmitsChangeFlag,
)
from sdbus.unittest import IsolatedDbusTestCase
from sdbus.utils.parse import parse_properties_changed

from sdbus import (
    DbusInterfaceCommonAsync,
    DbusNoReplyFlag,
    dbus_method_async,
    dbus_method_async_override,
    dbus_property_async,
    dbus_property_async_override,
    dbus_signal_async,
    get_current_message,
)

if TYPE_CHECKING:
    from sdbus.dbus_proxy_async_interfaces import (
        DBUS_PROPERTIES_CHANGED_TYPING,
    )
else:
    DBUS_PROPERTIES_CHANGED_TYPING = None


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


TEST_INTERFACE_NAME = "org.test.test"


class TestInterface(
    DbusInterfaceCommonAsync,
    interface_name=TEST_INTERFACE_NAME,
):

    def __init__(self) -> None:
        super().__init__()
        self.test_string = 'test_property'
        self.test_string_read = 'read'
        self.test_no_reply_string = 'no'
        self.property_private = 100
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

    @dbus_property_async("x")
    def test_property_private(self) -> int:
        return self.property_private

    @test_property_private.setter_private
    def test_private_setter(self, new_value: int) -> None:
        self.property_private = new_value

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
    def test_signal(self) -> tuple[str, str]:
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

    @dbus_method_async()
    async def raise_python_exc(self) -> None:
        raise ValueError("Test!")

    @dbus_method_async('s', flags=DbusNoReplyFlag)
    async def no_reply_method(self, new_value: str) -> None:
        self.no_reply_sync.set()

    @dbus_property_async("s")
    def test_constant_property(self) -> str:
        return "a"

    @dbus_method_async(
        result_signature='(ss)'
    )
    async def test_struct_return(self) -> tuple[str, str]:
        return ('hello', 'world')

    @dbus_method_async(
        result_signature='(ss)'
    )
    async def test_struct_return_workaround(self) -> tuple[tuple[str, str]]:
        return (('hello', 'world'), )

    @dbus_method_async()
    async def looong_method(self) -> None:
        await sleep(100)

    @dbus_signal_async()
    def empty_signal(self) -> None:
        raise NotImplementedError

    @dbus_method_async()
    async def returns_none_method(self) -> None:
        return

    @dbus_method_async(
        input_signature="(iiii)",
        result_signature="i",
    )
    async def takes_struct_method(
        self,
        int_struct: tuple[int, int, int, int],
    ) -> int:
        a, b, c, d = int_struct
        return a*b*c*d

    @dbus_method_async("s", "x")
    async def return_length(self, input_str: str) -> int:
        return len(input_str)


class DbusErrorTest(DbusFailedError):
    dbus_error_name = 'org.example.Error'


class DbusErrorUnmappedLater(DbusFailedError):
    dbus_error_name = 'org.example.Nothing'


TEST_SERVICE_NAME = 'org.example.test'


def initialize_object() -> tuple[TestInterface, TestInterface]:
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

        with self.subTest("Test method that returns None"):
            self.assertIsNone(
                await test_object
                .returns_none_method()  # type: ignore[func-returns-value]
            )
            self.assertIsNone(
                await test_object_connection
                .returns_none_method()   # type: ignore[func-returns-value]
            )

        with self.subTest("Test method that takes a single struct"):
            self.assertEqual(
                await test_object.takes_struct_method((2, 3, 4, 5)),
                120,
            )
            self.assertEqual(
                await test_object_connection.takes_struct_method((9, 8, 7, 6)),
                3024,
            )

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
            dbus_elements_map = (
                {
                    interface_name: meta.dbus_member_to_python_attr
                    for interface_name, meta in
                    TestInterface._dbus_iter_interfaces_meta()
                }
            )
            self.assertIn(
                "TestInt",
                dbus_elements_map[TEST_INTERFACE_NAME],
            )

            self.assertIn(
                "TestInt",
                dbus_elements_map[TEST_INTERFACE_NAME],
            )

            self.assertIn(
                "TestProperty",
                dbus_elements_map[TEST_INTERFACE_NAME],
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

        test_tuple = ('sgfsretg', 'asd')

        async with self.assertDbusSignalEmits(
                test_object.test_signal
            ) as local_signals_record, self.assertDbusSignalEmits(
                test_object_connection.test_signal
        ) as remote_signals_record:
            test_object.test_signal.emit(test_tuple)

        async with self.assertDbusSignalEmits(
                test_object.test_signal
            ) as local_signals_record, self.assertDbusSignalEmits(
                test_object_connection.test_signal
        ) as remote_signals_record:
            test_object.test_signal.emit(test_tuple)

        self.assertEqual([test_tuple], local_signals_record.output)
        self.assertEqual([test_tuple], remote_signals_record.output)

    async def test_signal_catch_anywhere(self) -> None:
        test_object, test_object_connection = initialize_object()

        loop = get_running_loop()

        test_tuple = ('sgfsretg', 'asd')

        with self.subTest('Catch anywhere over D-Bus object'):
            async def catch_anywhere_oneshot_dbus(
            ) -> tuple[str, tuple[str, str]]:
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
            ) -> tuple[str, tuple[str, str]]:
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
            ) -> tuple[str, tuple[str, str]]:
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

    async def test_signal_multiple_readers(self) -> None:
        test_object, test_object_connection = initialize_object()

        loop = get_running_loop()

        test_tuple = ('sgfsretg', 'asd')

        async def reader_one() -> tuple[str, str]:
            async for x in test_object_connection.test_signal.catch():
                return test_tuple

            raise RuntimeError

        async def reader_two() -> tuple[str, str]:
            async for x in test_object_connection.test_signal.catch():
                return test_tuple

            raise RuntimeError

        t1 = loop.create_task(reader_one())
        t2 = loop.create_task(reader_two())

        loop.call_at(0, test_object.test_signal.emit, test_tuple)

        self.assertEqual(test_tuple, await wait_for(t1, timeout=1))
        self.assertEqual(test_tuple, await wait_for(t2, timeout=1))

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

    async def test_bus_close(self) -> None:
        test_object, test_object_connection = initialize_object()

        async def too_long_wait() -> None:
            await test_object_connection.looong_method()

        self.bus.close()

        with self.assertRaises(SdBusLibraryError):
            await wait_for(too_long_wait(), timeout=1)

    async def test_bus_timerfd(self) -> None:
        test_object, test_object_connection = initialize_object()

        self.bus.method_call_timeout_usec = 10_000  # 0.01 seconds

        loop = get_running_loop()

        start = loop.time()

        with self.assertRaises(DbusNoReplyError):
            await wait_for(test_object_connection.looong_method(), timeout=1)

        self.assertLess(loop.time() - start, 0.2)

    async def test_signal_queue_wildcard_match(self) -> None:
        test_object, test_object_connection = initialize_object()

        loop = get_running_loop()
        future = loop.create_future()

        slot = await self.bus.match_signal_async(
            TEST_SERVICE_NAME,
            None, None, None,
            future.set_result)

        try:
            test_object.test_signal.emit(('test', 'signal'))

            await wait_for(future, timeout=1)
            message = future.result()
            self.assertEqual(message.member, "TestSignal")
        finally:
            slot.close()

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

    async def test_properties_get_all_dict(self) -> None:
        test_object, test_object_connection = initialize_object()

        dbus_dict = await test_object_connection._properties_get_all(
            TEST_INTERFACE_NAME)

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

    async def test_empty_signal(self) -> None:
        test_object, test_object_connection = initialize_object()

        async with self.assertDbusSignalEmits(
                test_object.empty_signal
            ) as local_signals_record, self.assertDbusSignalEmits(
                test_object_connection.empty_signal
        ) as remote_signals_record:
            test_object.empty_signal.emit(None)

        self.assertEqual([None], local_signals_record.output)
        self.assertEqual([None], remote_signals_record.output)

    async def test_properties_changed(self) -> None:
        test_object, test_object_connection = initialize_object()

        test_str = 'should_be_emited'

        async with self.assertDbusSignalEmits(
            test_object_connection.properties_changed
        ) as properties_changed_catch:
            await test_object_connection.test_property.set_async(test_str)

        properties_changed_data = properties_changed_catch.output[0]

        parsed_dict_from_class = parse_properties_changed(
            TestInterface, properties_changed_data)
        self.assertEqual(
            test_str,
            parsed_dict_from_class['test_property'],
        )

        parsed_dict_from_object = parse_properties_changed(
            test_object_connection, properties_changed_data)
        self.assertEqual(
            test_str,
            parsed_dict_from_object['test_property'],
        )

        properties_changed_data[2].append('invalidated_property')
        parsed_dict_with_invalidation = parse_properties_changed(
            test_object, properties_changed_data,
            on_unknown_member='reuse',
        )
        self.assertIsNone(
            parsed_dict_with_invalidation['invalidated_property'])

    async def test_property_private_setter(self) -> None:
        test_object, test_object_connection = initialize_object()

        new_value = 200
        self.assertNotEqual(
            await test_object_connection.test_property_private,
            new_value
        )

        with self.assertRaises(DbusPropertyReadOnlyError):
            await test_object_connection.test_property_private.set_async(
                new_value)

        async with self.assertDbusSignalEmits(
            test_object_connection.properties_changed
        ) as properties_changed_catch:
            await test_object.test_property_private.set_async(new_value)

        changed_properties = properties_changed_catch.output[0]

        self.assertEqual(
            await test_object_connection.test_property_private,
            new_value
        )

        self.assertIn('TestPropertyPrivate', changed_properties[1])

    async def test_property_override_setter_private(self) -> None:

        test_int = 1

        class TestInterfacePrivateSetter(TestInterface):
            @dbus_property_async_override()
            def test_property_private(self) -> int:
                return test_int

            @test_property_private.setter_private
            def _private_setter(self, new_value: int) -> None:
                nonlocal test_int
                test_int = new_value

        test_object = TestInterfacePrivateSetter()
        test_object.export_to_dbus('/')
        test_object_connection = TestInterface.new_proxy(
            TEST_SERVICE_NAME, '/')

        self.assertEqual(
            await test_object_connection.test_property_private,
            test_int,
        )

        async def catch_properties_changed() -> int:
            async for x in test_object_connection.properties_changed:
                changed_attr = parse_properties_changed(
                    TestInterface, x)["test_property_private"]

                if not isinstance(changed_attr, int):
                    raise TypeError

                return changed_attr

            raise RuntimeError

        catch_changed_task = get_running_loop(
        ).create_task(catch_properties_changed())

        with self.assertRaises(DbusPropertyReadOnlyError):
            await test_object_connection.test_property_private.set_async(10)

        await test_object.test_property_private.set_async(10)

        self.assertEqual(
            await test_object_connection.test_property_private,
            10,
        )

        self.assertEqual(
            await test_object.test_property_private,
            test_int,
        )

        self.assertEqual(
            await wait_for(catch_changed_task, timeout=1),
            10,
        )

    async def test_interface_composition(self) -> None:
        class OneInterface(
            DbusInterfaceCommonAsync,
            interface_name="org.example.one",
        ):
            @dbus_method_async(result_signature="x")
            async def one(self) -> int:
                raise NotImplementedError

        class TwoInterface(
            DbusInterfaceCommonAsync,
            interface_name="org.example.two",
        ):
            @dbus_method_async(result_signature="t")
            async def two(self) -> int:
                return 2

        class CombinedInterface(TwoInterface, OneInterface):
            ...

        test_combined = CombinedInterface()
        test_combined_interfaces = [
            iface for iface, _ in test_combined._dbus_iter_interfaces_meta()
        ]

        # Verify the order of reported interfaces on the combined class.
        self.assertEqual(test_combined_interfaces, [
            "org.freedesktop.DBus.Peer",
            "org.freedesktop.DBus.Introspectable",
            "org.freedesktop.DBus.Properties",
            "org.example.one",
            "org.example.two",
        ])

    async def test_extremely_large_string(self) -> None:
        test_object, test_object_connection = initialize_object()

        extremely_large_string = "a" * 8423681

        remote_len = await wait_for(
            test_object_connection.return_length(
                extremely_large_string
            ),
            timeout=10,
        )

        self.assertEqual(
            remote_len,
            len(extremely_large_string),
        )

        # Check that calling regular methods still works.
        for _ in range(5):
            await test_object_connection.returns_none_method()

    async def test_export_handle(self) -> None:
        test_object = TestInterface()
        test_object_connection = TestInterface.new_proxy(
            TEST_SERVICE_NAME, '/',
        )
        with self.assertRaises(DbusUnknownObjectError):
            await test_object_connection.returns_none_method()

        with test_object.export_to_dbus("/"):
            await test_object_connection.returns_none_method()

        with self.assertRaises(DbusUnknownObjectError):
            await test_object_connection.returns_none_method()

        test_object2 = TestInterface()
        handle = test_object2.export_to_dbus("/")
        await test_object_connection.returns_none_method()
        handle.stop()

        with self.assertRaises(DbusUnknownObjectError):
            await test_object_connection.returns_none_method()

    async def test_export_handle_lifetime(self) -> None:
        test_object = TestInterface()
        test_object_connection = TestInterface.new_proxy(
            TEST_SERVICE_NAME, '/',
        )
        handle = test_object.export_to_dbus("/")
        await test_object_connection.returns_none_method()

        del test_object

        handle.stop()

        with self.assertRaises(DbusUnknownObjectError):
            await test_object_connection.returns_none_method()

        # Test idempotency
        handle.stop()
        handle.stop()

        with self.assertRaises(DbusUnknownObjectError):
            await test_object_connection.returns_none_method()

    def test_asyncio_run_different_loops(self) -> None:
        bus = self.bus

        async def test() -> None:
            dbus_object = DbusInterfaceCommonAsync.new_proxy(
                "org.freedesktop.DBus",
                "/org/freedesktop/DBus",
                bus,
            )
            await wait_for(dbus_object.dbus_ping(), timeout=1)

        with self.assertRaisesRegex(RuntimeError, "different loop"):
            asyncio_run(test())

    async def test_python_exc(self) -> None:
        test_object, test_object_connection = initialize_object()

        with self.assertRaisesRegex(ValueError, "Test!"):
            await test_object.raise_python_exc()

        with self.assertRaisesRegex(ValueError, "Test!"):
            await test_object_connection.raise_python_exc()

    async def test_empty_dbus_interface(self) -> None:
        class Empty(
            DbusInterfaceCommonAsync,
            interface_name="org.empty",
        ):
            ...

        empty_local = Empty()
        empty_local.export_to_dbus("/")
        empty_proxy = Empty.new_proxy(TEST_SERVICE_NAME, "/")

        intro = await empty_proxy.dbus_introspect()
        self.assertIn('<interface name="org.empty">', intro)
