
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

from asyncio import get_running_loop
from contextvars import ContextVar
from typing import Iterator

from .sd_bus_internals import (
    DbusPropertyConstFlag,
    DbusPropertyEmitsChangeFlag,
    DbusPropertyEmitsInvalidationFlag,
    DbusPropertyExplicitFlag,
    SdBus,
    sd_bus_open,
)

DEFAULT_BUS: ContextVar[SdBus] = ContextVar('DEFAULT_BUS')

PROPERTY_FLAGS_MASK = (
    DbusPropertyConstFlag | DbusPropertyEmitsChangeFlag |
    DbusPropertyEmitsInvalidationFlag | DbusPropertyExplicitFlag
)


def count_bits(i: int) -> int:
    return bin(i).count('1')


def _is_property_flags_correct(flags: int) -> bool:
    num_of_flag_bits = count_bits(PROPERTY_FLAGS_MASK & flags)
    return (0 <= num_of_flag_bits <= 1)


def get_default_bus() -> SdBus:
    try:
        return DEFAULT_BUS.get()
    except LookupError:
        new_bus = sd_bus_open()
        DEFAULT_BUS.set(new_bus)
        return new_bus


def set_default_bus(new_default: SdBus) -> None:
    DEFAULT_BUS.set(new_default)


async def request_default_bus_name_async(
        new_name: str,
        flags: int = 0,) -> None:
    default_bus = get_default_bus()
    await default_bus.request_name_async(new_name, flags)


async def request_default_bus_name(
        new_name: str,
        flags: int = 0,) -> None:
    default_bus = get_default_bus()
    default_bus.request_name(new_name, flags)


def _method_name_converter(python_name: str) -> Iterator[str]:
    char_iter = iter(python_name)
    # Name starting with upper case letter
    try:
        first_char = next(char_iter)
    except StopIteration:
        return

    yield first_char.upper()

    upper_next_one = False
    for c in char_iter:
        # Every under score remove and uppercase next one
        if c != '_':
            if upper_next_one:
                yield c.upper()
                upper_next_one = False
            else:
                yield c
        else:
            upper_next_one = True


def _check_sync_in_async_env() -> bool:
    try:
        get_running_loop()
        return False
    except RuntimeError:
        return True
