# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2022 igo95862

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

from asyncio import get_running_loop
from unittest import SkipTest, TestCase, main

from sdbus.sd_bus_internals import (
    SdBus,
    is_interface_name_valid,
    is_member_name_valid,
    is_object_path_valid,
    is_service_name_valid,
)
from sdbus.unittest import IsolatedDbusTestCase


class TestAsyncLowLevel(IsolatedDbusTestCase):
    def test_init_bus(self) -> None:
        not_connected_bus = SdBus()
        self.assertIsNone(not_connected_bus.address)

        self.assertIsNotNone(self.bus.address)

    async def test_bus_fd_unregister_close(self) -> None:
        await self.bus.request_name_async("org.example", 0)
        bus_fd = self.bus.get_fd()

        self.bus.close()

        loop = get_running_loop()
        self.assertFalse(loop.remove_reader(bus_fd))
        self.assertFalse(loop.remove_writer(bus_fd))


class TestLowLeveApi(TestCase):
    def test_validation_funcs(self) -> None:
        try:
            self.assertTrue(
                is_interface_name_valid('org.example.test')
            )

            self.assertFalse(
                is_interface_name_valid('Not very valid 😀')
            )

            self.assertTrue(
                is_service_name_valid('org.example.test')
            )

            self.assertFalse(
                is_service_name_valid('Not very valid 😀')
            )

            self.assertTrue(
                is_member_name_valid('GetSomething')
            )

            self.assertFalse(
                is_member_name_valid('no.dots.in.member.names')
            )

            self.assertTrue(
                is_object_path_valid('/test')
            )

            self.assertFalse(
                is_object_path_valid('no.dots.in.object.paths')
            )
        except NotImplementedError:
            raise SkipTest(
                "Validation funcs not implemented. "
                "Probably too old libsystemd. (< 246)"
            )

    def test_bus_method_call_timeout(self) -> None:
        bus = SdBus()

        self.assertIsNotNone(bus.method_call_timeout_usec)

        test_timeout_usec = 10 * 10**6  # 10 seconds
        bus.method_call_timeout_usec = test_timeout_usec
        self.assertEqual(test_timeout_usec, bus.method_call_timeout_usec)

        with self.assertRaises(TypeError):
            bus.method_call_timeout_usec = "test"  # type: ignore

        with self.assertRaises(ValueError):
            del bus.method_call_timeout_usec


if __name__ == "__main__":
    main()
