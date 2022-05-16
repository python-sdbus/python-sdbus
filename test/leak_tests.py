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

from asyncio import (
    FIRST_EXCEPTION,
    Task,
    get_running_loop,
    sleep,
    wait,
    wait_for,
)
from os import environ
from resource import RUSAGE_SELF, getrusage
from typing import List, cast
from unittest import SkipTest

from sdbus.unittest import IsolatedDbusTestCase

from .test_read_write_dbus_types import TestDbusTypes
from .test_sd_bus_async import TestPing, TestProxy, initialize_object

ENABLE_LEAK_TEST_VAR = 'PYTHON_SDBUS_TEST_LEAKS'


def leak_test_enabled() -> None:
    if not environ.get(ENABLE_LEAK_TEST_VAR):
        raise SkipTest(
            'Leak tests not enabled, set '
            f"{ENABLE_LEAK_TEST_VAR} env variable"
            'to 1 to enable.'
        )


class LeakTests(IsolatedDbusTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.start_mem = getrusage(RUSAGE_SELF).ru_maxrss

    def check_memory(self) -> None:
        current_usage = getrusage(RUSAGE_SELF).ru_maxrss
        if current_usage > self.start_mem * 2:
            raise RuntimeError('Leaking memory')

    def test_read_write_dbus_types(self) -> None:
        leak_test_enabled()

        pseudo_test = cast(TestDbusTypes, self)

        for _ in range(1_000_000):
            TestDbusTypes.test_unsigned(pseudo_test)
            TestDbusTypes.test_signed(pseudo_test)
            TestDbusTypes.test_strings(pseudo_test)
            TestDbusTypes.test_double(pseudo_test)
            TestDbusTypes.test_bool(pseudo_test)
            TestDbusTypes.test_array(pseudo_test)
            TestDbusTypes.test_empty_array(pseudo_test)
            TestDbusTypes.test_array_compound(pseudo_test)
            TestDbusTypes.test_nested_array(pseudo_test)
            TestDbusTypes.test_struct(pseudo_test)
            TestDbusTypes.test_dict(pseudo_test)
            TestDbusTypes.test_empty_dict(pseudo_test)
            TestDbusTypes.test_dict_nested_array(pseudo_test)
            TestDbusTypes.test_variant(pseudo_test)
            TestDbusTypes.test_array_of_variant(pseudo_test)
            TestDbusTypes.test_array_of_dict(pseudo_test)
            TestDbusTypes.test_array_of_struct(pseudo_test)
            TestDbusTypes.test_dict_of_struct(pseudo_test)
            TestDbusTypes.test_struct_with_dict(pseudo_test)
            TestDbusTypes.test_dict_of_array(pseudo_test)
            TestDbusTypes.test_array_of_array(pseudo_test)
            TestDbusTypes.test_sealed_message_append(pseudo_test)

            self.check_memory()

    async def test_ping(self) -> None:
        leak_test_enabled()

        pseudo_test = cast(TestPing, self)

        for _ in range(1_000_000):
            await TestPing.test_ping(pseudo_test)
            self.check_memory()

    async def test_objects(self) -> None:
        leak_test_enabled()
        await self.bus.request_name_async("org.example.test", 0)

        pseudo_test = cast(TestProxy, self)

        for _ in range(20_000):
            await TestProxy.test_method_kwargs(pseudo_test)
            await TestProxy.test_method(pseudo_test)
            await TestProxy.test_subclass(pseudo_test)
            await TestProxy.test_bad_subclass(pseudo_test)
            await TestProxy.test_properties(pseudo_test)
            await TestProxy.test_signal(pseudo_test)
            await TestProxy.test_exceptions(pseudo_test)
            await TestProxy.test_no_reply_method(pseudo_test)
            await TestProxy.test_interface_remove(pseudo_test)
            TestProxy.test_docstring(pseudo_test)

            self.check_memory()

    async def test_single_object(self) -> None:
        leak_test_enabled()
        await self.bus.request_name_async("org.example.test", 0)

        test_object, test_object_connection = initialize_object()

        i = 0
        num_of_iterations = 10_000
        num_of_tasks = 5

        async def the_test() -> None:
            for _ in range(num_of_iterations):
                self.assertEqual(
                    'ASD',
                    await wait_for(test_object_connection.upper('asd'), 0.5))

                await sleep(0)
                self.assertEqual(
                    'test_property',
                    await wait_for(test_object_connection.test_property, 0.5))

                await sleep(0)
                await wait_for(
                    test_object_connection.test_property.set_async(
                        'test_property'), 0.5)

                await sleep(0)
                self.check_memory()

                nonlocal i
                i += 1

        tasks: List[Task[None]] = []
        loop = get_running_loop()
        for _ in range(num_of_tasks):
            tasks.append(loop.create_task(the_test()))

        done, pending = await wait(tasks, return_when=FIRST_EXCEPTION)

        self.check_memory()

        self.assertEqual(i, num_of_iterations * num_of_tasks)
