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

from .test_read_write_dbus_types import (
    TestDbusTypes,
)

from .test_sd_bus_async import (
    TestPing,
    TestInterface,
    TestProxy,
)

from .common_test_util import TempDbusTest

from resource import getrusage, RUSAGE_SELF
from unittest import SkipTest
from os import environ


async def test_strings() -> None:
    t = TestDbusTypes()
    t.setUp()
    await t.asyncSetUp()

    start_mem = getrusage(RUSAGE_SELF).ru_maxrss

    for _ in range(1_000_000):
        t.create_message()
        t.test_strings()

        current_usage = getrusage(RUSAGE_SELF).ru_maxrss
        if current_usage > start_mem * 2:
            raise RuntimeError('Leaking memory')

ENABLE_LEAK_TEST_VAR = 'PYTHON_SDBUS_TEST_LEAKS'


def leak_test_enabled() -> None:
    if not environ.get(ENABLE_LEAK_TEST_VAR):
        raise SkipTest(
            'Leak tests not enabled, set '
            f"{ENABLE_LEAK_TEST_VAR} env variable"
            'to 1 to enable.'
        )


class LeakTests(TempDbusTest):
    def setUp(self) -> None:
        super().setUp()
        self.start_mem = getrusage(RUSAGE_SELF).ru_maxrss

    def check_memory(self) -> None:
        current_usage = getrusage(RUSAGE_SELF).ru_maxrss
        if current_usage > self.start_mem * 2:
            raise RuntimeError('Leaking memory')

    def test_read_write_dbus_types(self) -> None:
        leak_test_enabled()

        for _ in range(1_000_000):
            TestDbusTypes.test_unsigned(self)
            TestDbusTypes.test_signed(self)
            TestDbusTypes.test_strings(self)
            TestDbusTypes.test_double(self)
            TestDbusTypes.test_bool(self)
            TestDbusTypes.test_array(self)
            TestDbusTypes.test_empty_array(self)
            TestDbusTypes.test_array_compound(self)
            TestDbusTypes.test_nested_array(self)
            TestDbusTypes.test_struct(self)
            TestDbusTypes.test_dict(self)
            TestDbusTypes.test_empty_dict(self)
            TestDbusTypes.test_dict_nested_array(self)
            TestDbusTypes.test_variant(self)
            TestDbusTypes.test_array_of_variant(self)
            TestDbusTypes.test_array_of_dict(self)
            TestDbusTypes.test_array_of_struct(self)
            TestDbusTypes.test_dict_of_struct(self)
            TestDbusTypes.test_struct_with_dict(self)
            TestDbusTypes.test_dict_of_array(self)
            TestDbusTypes.test_array_of_array(self)
            TestDbusTypes.test_sealed_message_append(self)

            self.check_memory()

    async def test_ping(self) -> None:
        leak_test_enabled()

        for _ in range(1_000_000):
            await TestPing.test_ping(self)
            self.check_memory()

    async def test_object(self) -> None:
        leak_test_enabled()
        await self.bus.request_name_async("org.example.test", 0)

        for _ in range(20_000):
            await TestProxy.test_method_kwargs(self)
            await TestProxy.test_method(self)
            await TestProxy.test_subclass(self)
            await TestProxy.test_bad_subclass(self)
            await TestProxy.test_properties(self)
            await TestProxy.test_signal(self)
            await TestProxy.test_exceptions(self)
            # await TestProxy.test_no_reply_method(self)
            await TestProxy.test_interface_remove(self)
            TestProxy.test_docstring(self)

            self.check_memory()
