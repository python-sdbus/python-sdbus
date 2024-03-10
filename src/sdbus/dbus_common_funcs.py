
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

from asyncio import Future, get_running_loop
from contextvars import ContextVar
from typing import TYPE_CHECKING
from warnings import warn

from .sd_bus_internals import (
    DbusPropertyConstFlag,
    DbusPropertyEmitsChangeFlag,
    DbusPropertyEmitsInvalidationFlag,
    DbusPropertyExplicitFlag,
    NameAllowReplacementFlag,
    NameQueueFlag,
    NameReplaceExistingFlag,
    sd_bus_open,
)

if TYPE_CHECKING:
    from typing import Any, Dict, Generator, Iterator, Literal, Mapping, Tuple

    from .sd_bus_internals import SdBus

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


def _prepare_request_name_flags(
        allow_replacement: bool,
        replace_existing: bool,
        queue: bool,
) -> int:
    return (
        (NameAllowReplacementFlag if allow_replacement else 0)
        +
        (NameReplaceExistingFlag if replace_existing else 0)
        +
        (NameQueueFlag if queue else 0)
    )


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
        allow_replacement: bool = False,
        replace_existing: bool = False,
        queue: bool = False,
) -> None:
    default_bus = get_default_bus()
    await default_bus.request_name_async(
        new_name,
        _prepare_request_name_flags(
            allow_replacement,
            replace_existing,
            queue,
        )
    )


class _DeprecationAwaitable:
    def __await__(self) -> Generator[Future[None], None, None]:
        warn(
            (
                'Awaiting on request_default_bus_name'
                'is deprecated and will be removed.'
            ),
            DeprecationWarning,
        )
        f: Future[None] = Future()
        f.set_result(None)
        yield from f


def request_default_bus_name(
        new_name: str,
        allow_replacement: bool = False,
        replace_existing: bool = False,
        queue: bool = False,
) -> _DeprecationAwaitable:
    default_bus = get_default_bus()
    default_bus.request_name(
        new_name,
        _prepare_request_name_flags(
            allow_replacement,
            replace_existing,
            queue,
        )
    )
    return _DeprecationAwaitable()


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


def _parse_properties_vardict(
        properties_name_map: Mapping[str, str],
        properties_vardict: Dict[str, Tuple[str, Any]],
        on_unknown_member: Literal['error', 'ignore', 'reuse'],
) -> Dict[str, Any]:

    properties_translated: Dict[str, Any] = {}

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
