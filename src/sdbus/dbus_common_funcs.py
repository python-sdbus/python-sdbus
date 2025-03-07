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

from asyncio import get_running_loop
from typing import TYPE_CHECKING

from .sd_bus_internals import (
    DbusPropertyConstFlag,
    DbusPropertyEmitsChangeFlag,
    DbusPropertyEmitsInvalidationFlag,
    DbusPropertyExplicitFlag,
)

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping
    from typing import Any, Literal


PROPERTY_FLAGS_MASK = (
    DbusPropertyConstFlag | DbusPropertyEmitsChangeFlag |
    DbusPropertyEmitsInvalidationFlag | DbusPropertyExplicitFlag
)


def count_bits(i: int) -> int:
    return bin(i).count('1')


def _is_property_flags_correct(flags: int) -> bool:
    num_of_flag_bits = count_bits(PROPERTY_FLAGS_MASK & flags)
    return (0 <= num_of_flag_bits <= 1)


def _snake_case_to_camel_case_gen(snake: str) -> Iterator[str]:
    char_iter = iter(snake)
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


def snake_case_to_camel_case(snake: str) -> str:
    return "".join(_snake_case_to_camel_case_gen(snake))


def _check_sync_in_async_env() -> bool:
    try:
        get_running_loop()
        return False
    except RuntimeError:
        return True


def _parse_properties_vardict(
        properties_name_map: Mapping[str, str],
        properties_vardict: dict[str, tuple[str, Any]],
        on_unknown_member: Literal['error', 'ignore', 'reuse'],
) -> dict[str, Any]:

    properties_translated: dict[str, Any] = {}

    for member_name, variant in properties_vardict.items():
        try:
            python_name = properties_name_map[member_name]
        except KeyError:
            if on_unknown_member == 'error':
                raise
            elif on_unknown_member == 'ignore':
                continue
            elif on_unknown_member == 'reuse':
                python_name = member_name
            else:
                raise ValueError

        properties_translated[python_name] = variant[1]

    return properties_translated
