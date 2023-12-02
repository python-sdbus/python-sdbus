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

from inspect import iscoroutinefunction
from types import FunctionType
from typing import TYPE_CHECKING, TypeVar, cast

from .dbus_common_elements import (
    DbusBindedSync,
    DbusMethodCommon,
    DbusSomethingSync,
)

if TYPE_CHECKING:
    from typing import Any, Callable, Optional, Sequence, Type

    from .dbus_proxy_sync_interface_base import DbusInterfaceBase

T = TypeVar('T')


class DbusMethodSync(DbusMethodCommon, DbusSomethingSync):
    def __get__(self,
                obj: DbusInterfaceBase,
                obj_class: Optional[Type[DbusInterfaceBase]] = None,
                ) -> Callable[..., Any]:
        return DbusMethodSyncBinded(self, obj)


class DbusMethodSyncBinded(DbusBindedSync):
    def __init__(self,
                 dbus_method: DbusMethodSync,
                 interface: DbusInterfaceBase):
        self.dbus_method = dbus_method
        self.interface = interface

        self.__doc__ = dbus_method.__doc__

    def _call_dbus_sync(self, *args: Any) -> Any:
        new_call_message = (
            self.interface._dbus.attached_bus.new_method_call_message(
                self.interface._dbus.service_name,
                self.interface._dbus.object_path,
                self.dbus_method.interface_name,
                self.dbus_method.method_name,
            )
        )
        if args:
            new_call_message.append_data(
                self.dbus_method.input_signature, *args)

        reply_message = self.interface._dbus.attached_bus.call(
            new_call_message)
        return reply_message.get_contents()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if len(args) == self.dbus_method.num_of_args:
            assert not kwargs, (
                "Passed more arguments than method supports"
                f"Extra args: {kwargs}")
            rebuilt_args: Sequence[Any] = args
        else:
            rebuilt_args = self.dbus_method._rebuild_args(
                self.dbus_method.original_method,
                *args,
                **kwargs)

        return self._call_dbus_sync(*rebuilt_args)


def dbus_method(
    input_signature: str = "",
    result_signature: str = "",
    flags: int = 0,
    method_name: Optional[str] = None,
) -> Callable[[T], T]:
    assert not isinstance(input_signature, FunctionType), (
        "Passed function to decorator directly. "
        "Did you forget () round brackets?"
    )

    def dbus_method_decorator(original_method: T) -> T:
        assert isinstance(original_method, FunctionType)
        assert not iscoroutinefunction(original_method), (
            "Expected NON coroutine function. ",
            "Maybe you wanted to remove 'async' keyword?",
        )
        new_wrapper = DbusMethodSync(
            original_method=original_method,
            method_name=method_name,
            input_signature=input_signature,
            result_signature=result_signature,
            result_args_names=(),
            input_args_names=(),
            flags=flags,
        )

        return cast(T, new_wrapper)

    return dbus_method_decorator
