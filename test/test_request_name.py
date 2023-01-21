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

from asyncio import get_running_loop, sleep, wait_for
from unittest import main

from sdbus.exceptions import (
    SdBusLibraryError,
    SdBusRequestNameAlreadyOwnerError,
    SdBusRequestNameError,
    SdBusRequestNameExistsError,
    SdBusRequestNameInQueueError,
)
from sdbus.sd_bus_internals import NameAllowReplacementFlag, NameQueueFlag
from sdbus.unittest import IsolatedDbusTestCase
from sdbus_async.dbus_daemon import FreedesktopDbus

from sdbus import (
    request_default_bus_name,
    request_default_bus_name_async,
    sd_bus_open_user,
)

TEST_BUS_NAME = 'com.example.test'
TEST_BUS_NAME_regex_match = TEST_BUS_NAME.replace('.', r'\.')


class TestRequestNameLowLevel(IsolatedDbusTestCase):
    def test_request_name_exception_tree(self) -> None:
        # Test that SdBusRequestNameError is super class
        # of other request name exceptions
        self.assertTrue(
            issubclass(
                SdBusRequestNameAlreadyOwnerError,
                SdBusRequestNameError,
            )
        )
        self.assertTrue(
            issubclass(
                SdBusRequestNameExistsError,
                SdBusRequestNameError,
            )
        )
        self.assertTrue(
            issubclass(
                SdBusRequestNameInQueueError,
                SdBusRequestNameError,
            )
        )
        # Test the opposite
        self.assertFalse(
            issubclass(
                SdBusRequestNameAlreadyOwnerError,
                SdBusRequestNameExistsError,
            )
        )
        self.assertFalse(
            issubclass(
                SdBusRequestNameInQueueError,
                SdBusRequestNameExistsError,
            )
        )
        self.assertFalse(
            issubclass(
                SdBusRequestNameInQueueError,
                SdBusRequestNameAlreadyOwnerError,
            )
        )

    async def test_name_exists_async(self) -> None:
        extra_bus = sd_bus_open_user()
        await self.bus.request_name_async(TEST_BUS_NAME, 0)

        with self.assertRaises(SdBusRequestNameExistsError):
            await wait_for(
                extra_bus.request_name_async(TEST_BUS_NAME, 0),
                timeout=1,
            )

    async def test_name_already_async(self) -> None:
        await self.bus.request_name_async(TEST_BUS_NAME, 0)

        with self.assertRaises(SdBusRequestNameAlreadyOwnerError):
            await wait_for(
                self.bus.request_name_async(TEST_BUS_NAME, 0),
                timeout=1,
            )

    async def test_name_queued_async(self) -> None:
        extra_bus = sd_bus_open_user()
        await self.bus.request_name_async(TEST_BUS_NAME, 0)

        with self.assertRaises(SdBusRequestNameInQueueError):
            await wait_for(
                extra_bus.request_name_async(TEST_BUS_NAME, NameQueueFlag),
                timeout=1,
            )

    async def test_name_other_error_async(self) -> None:
        extra_bus = sd_bus_open_user()
        extra_bus.close()

        with self.assertRaises(SdBusLibraryError):
            await wait_for(
                extra_bus.request_name_async(TEST_BUS_NAME, 0),
                timeout=1,
            )

    def test_name_exists_block(self) -> None:
        extra_bus = sd_bus_open_user()
        self.bus.request_name(TEST_BUS_NAME, 0)

        with self.assertRaisesRegex(
            SdBusRequestNameExistsError,
            TEST_BUS_NAME_regex_match,
        ):
            extra_bus.request_name(TEST_BUS_NAME, 0)

    def test_name_already_block(self) -> None:
        self.bus.request_name(TEST_BUS_NAME, 0)

        with self.assertRaisesRegex(
            SdBusRequestNameAlreadyOwnerError,
            TEST_BUS_NAME_regex_match,
        ):
            self.bus.request_name(TEST_BUS_NAME, 0)

    def test_name_queued_block(self) -> None:
        extra_bus = sd_bus_open_user()
        self.bus.request_name(TEST_BUS_NAME, 0)

        with self.assertRaisesRegex(
            SdBusRequestNameInQueueError,
            TEST_BUS_NAME_regex_match,
        ):
            extra_bus.request_name(TEST_BUS_NAME, NameQueueFlag)

    def test_name_other_error_block(self) -> None:
        extra_bus = sd_bus_open_user()
        extra_bus.close()
        with self.assertRaises(SdBusLibraryError):
            extra_bus.request_name(TEST_BUS_NAME, 0)


class TestRequestNameBlock(IsolatedDbusTestCase):
    def test_request_name_replacement(self) -> None:
        extra_bus = sd_bus_open_user()
        extra_bus.request_name(TEST_BUS_NAME, NameAllowReplacementFlag)

        with self.assertRaises(SdBusRequestNameExistsError):
            request_default_bus_name(TEST_BUS_NAME)

        request_default_bus_name(
            TEST_BUS_NAME,
            replace_existing=True,
        )


class TestRequestNameAsync(IsolatedDbusTestCase):
    async def test_request_name_replacement(self) -> None:
        extra_bus = sd_bus_open_user()
        await extra_bus.request_name_async(
            TEST_BUS_NAME,
            NameAllowReplacementFlag,
        )

        with self.assertRaises(SdBusRequestNameExistsError):
            await request_default_bus_name_async(TEST_BUS_NAME)

        await request_default_bus_name_async(
            TEST_BUS_NAME,
            replace_existing=True,
        )

    async def test_request_name_queue(self) -> None:
        extra_bus = sd_bus_open_user()
        await extra_bus.request_name_async(TEST_BUS_NAME, 0)

        with self.assertRaises(SdBusRequestNameInQueueError):
            await request_default_bus_name_async(
                TEST_BUS_NAME,
                queue=True,
            )

        async def catch_owner_changed() -> str:
            dbus = FreedesktopDbus()
            async for name, old, new in dbus.name_owner_changed:
                if name != TEST_BUS_NAME:
                    continue

                if old and new:
                    return new

            raise RuntimeError

        loop = get_running_loop()
        owner_changed_task = loop.create_task(catch_owner_changed())
        await sleep(0)

        extra_bus.close()

        await wait_for(owner_changed_task, timeout=0.5)

        with self.assertRaises(SdBusRequestNameAlreadyOwnerError):
            await request_default_bus_name_async(TEST_BUS_NAME)


if __name__ == '__main__':
    main()
