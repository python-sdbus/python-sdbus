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

from asyncio import get_running_loop
from inspect import getfullargspec
from types import FunctionType
from typing import Any, Dict, Iterator, List, Optional, Sequence

from .sd_bus_internals import SdBus, sd_bus_open

DEFAULT_BUS: Optional[SdBus] = None


def get_default_bus() -> SdBus:
    global DEFAULT_BUS
    old_bus = DEFAULT_BUS
    if old_bus is None:
        new_bus = sd_bus_open()
        DEFAULT_BUS = new_bus
        return new_bus
    else:
        return old_bus


def set_default_bus(new_default: SdBus) -> None:
    global DEFAULT_BUS
    if DEFAULT_BUS is not None:
        raise RuntimeError('Default bus already exists')

    DEFAULT_BUS = new_default


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


class DbusSomethingCommon:
    def __init__(self) -> None:
        self.interface_name: Optional[str] = None
        self.serving_enabled: bool = True


class DbusSomethingAsync(DbusSomethingCommon):
    ...


class DbusSomethingSync(DbusSomethingCommon):
    ...


class DbusMethodCommon(DbusSomethingCommon):

    def __init__(
            self,
            original_method: FunctionType,
            method_name: Optional[str],
            input_signature: str,
            input_args_names: Sequence[str],
            result_signature: str,
            result_args_names: Sequence[str],
            flags: int):

        assert not isinstance(input_args_names, str), (
            "Passed a string as input args"
            " names. Did you forget to put"
            " it in to a tuple ('string', ) ?")

        assert not any(' ' in x for x in input_args_names), (
            "Can't have spaces in argument input names"
            f"Args: {input_args_names}")

        assert not any(' ' in x for x in result_args_names), (
            "Can't have spaces in argument result names."
            f"Args: {result_args_names}")

        super().__init__()
        self.original_method = original_method
        self.args_spec = getfullargspec(original_method)
        self.args_names = self.args_spec.args[1:]  # 1: because of self
        self.num_of_args = len(self.args_names)
        self.args_defaults = (
            self.args_spec.defaults
            if self.args_spec.defaults is not None
            else ())
        self.default_args_start_at = self.num_of_args - len(self.args_defaults)

        if method_name is None:
            self.method_name = ''.join(
                _method_name_converter(original_method.__name__))
        else:
            self.method_name = method_name

        self.input_signature = input_signature
        self.input_args_names: Sequence[str] = (
            self.args_names
            if result_args_names and not input_args_names
            else input_args_names)

        self.result_signature = result_signature
        self.result_args_names = result_args_names
        self.flags = flags

        self.__doc__ = original_method.__doc__

    def _rebuild_args(
            self,
            function: FunctionType,
            *args: Any,
            **kwargs: Dict[str, Any]) -> List[Any]:
        # 3 types of arguments
        # *args - should be passed directly
        # **kwargs - should be put in a proper order
        # defaults - should be retrieved and put in proper order

        # Strategy:
        # Iterate over arg names
        # Use:
        # 1. Arg
        # 2. Kwarg
        # 3. Default

        # a, b, c, d, e
        #       ^ defaults start here
        # 5 - 3 = [2]
        # ^ total args
        #     ^ number of default args
        # First arg that supports default is
        # (total args - number of default args)
        passed_args_iter = iter(args)
        default_args_iter = iter(self.args_defaults)

        new_args_list: List[Any] = []

        for i, a_name in enumerate(self.args_spec.args[1:]):
            try:
                next_arg = next(passed_args_iter)
            except StopIteration:
                next_arg = None

            if i >= self.default_args_start_at:
                next_default_arg = next(default_args_iter)
            else:
                next_default_arg = None

            next_kwarg = kwargs.get(a_name)

            if next_arg is not None:
                new_args_list.append(next_arg)
            elif next_kwarg is not None:
                new_args_list.append(next_kwarg)
            elif next_default_arg is not None:
                new_args_list.append(next_default_arg)
            else:
                raise TypeError('Could not flatten the args')

        return new_args_list
