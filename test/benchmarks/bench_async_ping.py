# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2024 igo95862

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

from asyncio import gather
from asyncio import run as asyncio_run
from time import perf_counter

import pyperf  # type: ignore
from sdbus.unittest import _isolated_dbus

from sdbus import DbusInterfaceCommonAsync


def bench_async_ping_gather(loops: int) -> float:
    with _isolated_dbus() as bus:
        dbus_interface = DbusInterfaceCommonAsync.new_proxy(
            "org.freedesktop.DBus",
            "/org/freedesktop/DBus",
            bus,
        )

        async def run_ping_gather() -> float:

            gather_ping = gather(
                *(dbus_interface.dbus_ping() for _ in range(loops))
            )
            start = perf_counter()

            await gather_ping

            return perf_counter() - start

        return asyncio_run(run_ping_gather())


def bench_async_ping(loops: int) -> float:
    with _isolated_dbus() as bus:
        dbus_interface = DbusInterfaceCommonAsync.new_proxy(
            "org.freedesktop.DBus",
            "/org/freedesktop/DBus",
            bus,
        )

        async def run_ping() -> float:
            start = perf_counter()

            for _ in range(loops):
                await dbus_interface.dbus_ping()

            return perf_counter() - start

        return asyncio_run(run_ping())


def main() -> None:
    runner = pyperf.Runner()
    runner.bench_time_func('sdbus_async_ping', bench_async_ping)
    runner.bench_time_func('sdbus_async_ping_gather', bench_async_ping_gather)


if __name__ == "__main__":
    main()
