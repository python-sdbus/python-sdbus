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
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generator,
    Generic,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    cast,
)
from weakref import ref as weak_ref

from .dbus_common_elements import (
    DbusBindedAsync,
    DbusOverload,
    DbusPropertyCommon,
    DbusSomethingAsync,
)
from .sd_bus_internals import SdBusMessage

T = TypeVar('T')


if TYPE_CHECKING:
    from .dbus_proxy_async_interface_base import DbusInterfaceBaseAsync
    from .dbus_proxy_async_signal import DbusSignalBinded


DBUS_PROPERTIES_CHANGED_TYPING = Tuple[str,
                                       Dict[str, Tuple[str, Any]],
                                       List[str]]


class DbusPropertyAsync(DbusSomethingAsync, DbusPropertyCommon, Generic[T]):
    def __init__(
            self,
            property_name: Optional[str],
            property_signature: str,
            property_getter: Callable[[DbusInterfaceBaseAsync],
                                      T],
            property_setter: Optional[
                Callable[[DbusInterfaceBaseAsync, T],
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
        self.property_getter: Callable[
            [DbusInterfaceBaseAsync], T] = property_getter
        self.property_setter: Optional[
            Callable[[DbusInterfaceBaseAsync, T],
                     None]] = property_setter

        self.properties_changed_signal: \
            Optional[DbusSignalBinded[DBUS_PROPERTIES_CHANGED_TYPING]] = None

        self.__doc__ = property_getter.__doc__

    def __get__(self,
                obj: DbusInterfaceBaseAsync,
                obj_class: Optional[Type[DbusInterfaceBaseAsync]] = None,
                ) -> DbusPropertyAsyncBinded:
        return DbusPropertyAsyncBinded(self, obj)

    def setter(self,
               new_set_function: Callable[
                   [Any, T],
                   None]
               ) -> None:
        assert not iscoroutinefunction(new_set_function), (
            "Property setter can't be coroutine",
        )
        self.property_setter = new_set_function


class DbusPropertyAsyncBinded(DbusBindedAsync):
    def __init__(self,
                 dbus_property: DbusPropertyAsync[T],
                 interface: DbusInterfaceBaseAsync):
        self.dbus_property = dbus_property
        self.interface_ref = (
            weak_ref(interface)
            if interface is not None
            else None
        )

        self.__doc__ = dbus_property.__doc__

    def __await__(self) -> Generator[Any, None, T]:
        return self.get_async().__await__()

    async def get_async(self) -> T:
        assert self.interface_ref is not None
        interface = self.interface_ref()
        assert interface is not None

        if not interface._is_binded:
            return self.dbus_property.property_getter(
                interface)

        assert interface._attached_bus is not None
        assert interface._remote_service_name is not None
        assert interface._remote_object_path is not None
        assert self.dbus_property.property_name is not None
        assert self.dbus_property.interface_name is not None
        new_call_message = interface._attached_bus. \
            new_property_get_message(
                interface._remote_service_name,
                interface._remote_object_path,
                self.dbus_property.interface_name,
                self.dbus_property.property_name,
            )

        reply_message = await interface._attached_bus. \
            call_async(new_call_message)
        # Get method returns variant but we only need contents of variant
        return cast(T, reply_message.get_contents()[1])

    def _reply_get_sync(self, message: SdBusMessage) -> None:
        assert self.interface_ref is not None
        interface = self.interface_ref()
        assert interface is not None

        reply_data: Any = self.dbus_property.property_getter(interface)
        message.append_data(self.dbus_property.property_signature, reply_data)

    def _reply_set_sync(self, message: SdBusMessage) -> None:
        assert self.interface_ref is not None
        interface = self.interface_ref()
        assert interface is not None

        assert self.dbus_property.property_setter is not None
        data_to_set_to: Any = message.get_contents()

        self.dbus_property.property_setter(interface, data_to_set_to)

        if self.dbus_property.properties_changed_signal is not None:
            assert self.dbus_property.interface_name is not None
            self.dbus_property.properties_changed_signal.emit(
                (
                    self.dbus_property.interface_name,
                    {
                        self.dbus_property.property_name: (
                            self.dbus_property.property_signature,
                            data_to_set_to,
                        ),
                    },
                    []
                )
            )

    async def set_async(self, complete_object: T) -> None:
        assert self.interface_ref is not None
        interface = self.interface_ref()
        assert interface is not None

        if not interface._is_binded:
            if self.dbus_property.property_setter is None:
                raise ValueError('Property has no setter')

            self.dbus_property.property_setter(
                interface, complete_object)

            return

        assert interface._attached_bus is not None
        assert interface._remote_service_name is not None
        assert interface._remote_object_path is not None
        assert self.dbus_property.property_name is not None
        assert self.dbus_property.interface_name is not None
        new_call_message = interface._attached_bus. \
            new_property_set_message(
                interface._remote_service_name,
                interface._remote_object_path,
                self.dbus_property.interface_name,
                self.dbus_property.property_name,
            )

        new_call_message.append_data(
            'v', (self.dbus_property.property_signature, complete_object))

        await interface._attached_bus.call_async(new_call_message)


def dbus_property_async(
        property_signature: str = "",
        flags: int = 0,
        property_name: Optional[str] = None,
) -> Callable[
    [Callable[[Any], T]],
        DbusPropertyAsync[T]]:

    assert not isinstance(property_signature, FunctionType), (
        "Passed function to decorator directly. "
        "Did you forget () round brackets?"
    )

    def property_decorator(
        function: Callable[..., Any]
    ) -> DbusPropertyAsync[T]:

        assert not iscoroutinefunction(function), (
            "Property setter can't be coroutine",
        )

        new_wrapper: DbusPropertyAsync[T] = DbusPropertyAsync(
            property_name,
            property_signature,
            function,
            None,
            flags,
        )

        return new_wrapper

    return property_decorator


def dbus_property_async_override() -> Callable[
    [Callable[[Any], T]],
        DbusPropertyAsync[T]]:

    def new_decorator(
            new_property: Callable[[Any], T]) -> DbusPropertyAsync[T]:
        return cast(DbusPropertyAsync[T], DbusOverload(new_property))

    return new_decorator
