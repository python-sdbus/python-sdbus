# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2025 igo95862

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

from time import perf_counter

import pyperf  # type: ignore
from sdbus.unittest import _isolated_dbus

from sdbus import DbusInterfaceCommonAsync, dbus_method_async


class ExampleInterface(
    DbusInterfaceCommonAsync,
    interface_name="org.example.interface"
):
    @dbus_method_async(
        input_signature="s",
        result_signature="s",
    )
    async def upper(self, string: str) -> str:
        return string.upper()


def bench_dbus_object_export_stop(loops: int) -> float:
    with _isolated_dbus() as bus:
        example_object = ExampleInterface()

        start = perf_counter()

        for _ in range(loops):
            example_object = ExampleInterface()
            handle = example_object.export_to_dbus("/", bus=bus)
            handle.stop()

        return perf_counter() - start


def bench_dbus_object_export_gc(loops: int) -> float:
    with _isolated_dbus() as bus:
        example_object = ExampleInterface()

        start = perf_counter()

        for _ in range(loops):
            example_object = ExampleInterface()
            example_object.export_to_dbus("/", bus=bus)

        return perf_counter() - start


def main() -> None:
    runner = pyperf.Runner()
    runner.bench_time_func("sdbus_dbus_object_export_stop",
                           bench_dbus_object_export_stop)
    runner.bench_time_func("sdbus_dbus_object_export_gc",
                           bench_dbus_object_export_gc)


if __name__ == "__main__":
    main()
