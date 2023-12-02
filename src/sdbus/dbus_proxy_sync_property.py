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
from typing import TYPE_CHECKING, Generic, TypeVar, cast

from .dbus_common_elements import DbusPropertyCommon, DbusSomethingSync
from .dbus_common_funcs import _check_sync_in_async_env

if TYPE_CHECKING:
    from typing import Any, Callable, Optional, Type

    from .dbus_proxy_sync_interface_base import DbusInterfaceBase


T = TypeVar('T')


class DbusPropertySync(DbusPropertyCommon, DbusSomethingSync, Generic[T]):
    def __init__(
            self,
            property_name: Optional[str],
            property_signature: str,
            property_getter: Callable[[DbusInterfaceBase],
                                      T],
            property_setter: Optional[
                Callable[[DbusInterfaceBase, T],
                         None]],
            flags: int,

    ) -> None:
        assert isinstance(property_getter, FunctionType)
        super().__init__(
            property_name,
            property_signature,
            flags,
            property_getter,
        )
        self.property_getter = property_getter
        self.property_setter = property_setter

        self.__doc__ = property_getter.__doc__

    def __get__(self,
                obj: DbusInterfaceBase,
                obj_class: Optional[Type[DbusInterfaceBase]] = None,
                ) -> T:
        assert _check_sync_in_async_env(), (
            "Used sync __get__ method in async environment. "
            "This is probably an error as it will block "
            "other asyncio methods for considerable time."
        )

        new_call_message = (
            obj._dbus.attached_bus.new_property_get_message(
                obj._dbus.service_name,
                obj._dbus.object_path,
                self.interface_name,
                self.property_name,
            )
        )

        reply_message = obj._dbus.attached_bus.call(new_call_message)
        return cast(T, reply_message.get_contents()[1])

    def __set__(self, obj: DbusInterfaceBase, value: T) -> None:
        assert _check_sync_in_async_env(), (
            "Used sync __set__ method in async environment. "
            "This is probably an error as it will block "
            "other asyncio methods for considerable time."
        )

        if not self.property_signature:
            raise AttributeError('D-Bus property is read only')

        new_call_message = (
            obj._dbus.attached_bus.new_property_set_message(
                obj._dbus.service_name,
                obj._dbus.object_path,
                self.interface_name,
                self.property_name,
            )
        )

        new_call_message.append_data(
            'v', (self.property_signature, value))

        obj._dbus.attached_bus.call(new_call_message)


def dbus_property(
    property_signature: str = "",
    flags: int = 0,
    property_name: Optional[str] = None,
) -> Callable[
    [Callable[[Any], T]],
        DbusPropertySync[T]]:
    assert not isinstance(property_signature, FunctionType), (
        "Passed function to decorator directly. "
        "Did you forget () round brackets?"
    )

    def property_decorator(
        function: Callable[..., Any]
    ) -> DbusPropertySync[T]:
        assert not iscoroutinefunction(function), "Expected regular function"

        new_wrapper: DbusPropertySync[T] = DbusPropertySync(
            property_name,
            property_signature,
            function,
            None,
            flags,
        )

        return new_wrapper

    return property_decorator
