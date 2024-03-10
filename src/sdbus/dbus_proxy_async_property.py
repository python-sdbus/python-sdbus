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

from inspect import iscoroutinefunction
from types import FunctionType
from typing import TYPE_CHECKING, Awaitable, Generic, TypeVar, cast, overload
from weakref import ref as weak_ref

from .dbus_common_elements import (
    DbusBindedAsync,
    DbusPropertyCommon,
    DbusPropertyOverride,
    DbusRemoteObjectMeta,
    DbusSomethingAsync,
)

if TYPE_CHECKING:
    from typing import Any, Callable, Generator, Optional, Type, Union

    from .dbus_proxy_async_interface_base import DbusInterfaceBaseAsync
    from .sd_bus_internals import SdBusMessage


T = TypeVar('T')


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
        self.property_setter_is_public: bool = True

        self.__doc__ = property_getter.__doc__

    @overload
    def __get__(
        self,
        obj: None,
        obj_class: Type[DbusInterfaceBaseAsync],
    ) -> DbusPropertyAsync[T]:
        ...

    @overload
    def __get__(
        self,
        obj: DbusInterfaceBaseAsync,
        obj_class: Type[DbusInterfaceBaseAsync],
    ) -> DbusPropertyAsyncBaseBind[T]:
        ...

    def __get__(
        self,
        obj: Optional[DbusInterfaceBaseAsync],
        obj_class: Optional[Type[DbusInterfaceBaseAsync]] = None,
    ) -> Union[DbusPropertyAsyncBaseBind[T], DbusPropertyAsync[T]]:
        if obj is not None:
            dbus_meta = obj._dbus
            if isinstance(dbus_meta, DbusRemoteObjectMeta):
                return DbusPropertyAsyncProxyBind(self, dbus_meta)
            else:
                return DbusPropertyAsyncLocalBind(self, obj)
        else:
            return self

    def setter(self,
               new_set_function: Callable[
                   [Any, T],
                   None],
               ) -> None:
        assert self.property_setter is None, "Setter already defined"
        assert not iscoroutinefunction(new_set_function), (
            "Property setter can't be coroutine",
        )
        self.property_setter = new_set_function

    def setter_private(
        self,
        new_set_function: Callable[
            [Any, T],
            None],
    ) -> None:
        assert self.property_setter is None, "Setter already defined"
        assert not iscoroutinefunction(new_set_function), (
            "Property setter can't be coroutine",
        )
        self.property_setter = new_set_function
        self.property_setter_is_public = False


class DbusPropertyAsyncBaseBind(DbusBindedAsync, Awaitable[T]):
    def __await__(self) -> Generator[Any, None, T]:
        return self.get_async().__await__()

    async def get_async(self) -> T:
        raise NotImplementedError

    async def set_async(self, complete_object: T) -> None:
        raise NotImplementedError


class DbusPropertyAsyncProxyBind(DbusPropertyAsyncBaseBind[T]):
    def __init__(
        self,
        dbus_property: DbusPropertyAsync[T],
        proxy_meta: DbusRemoteObjectMeta,
    ):
        self.dbus_property = dbus_property
        self.proxy_meta = proxy_meta

        self.__doc__ = dbus_property.__doc__

    async def get_async(self) -> T:
        bus = self.proxy_meta.attached_bus
        new_get_message = (
            bus.new_property_get_message(
                self.proxy_meta.service_name,
                self.proxy_meta.object_path,
                self.dbus_property.interface_name,
                self.dbus_property.property_name,
            )
        )
        reply_message = await bus.call_async(new_get_message)
        # Get method returns variant but we only need contents of variant
        return cast(T, reply_message.get_contents()[1])

    async def set_async(self, complete_object: T) -> None:
        bus = self.proxy_meta.attached_bus
        new_set_message = (
            bus.new_property_set_message(
                self.proxy_meta.service_name,
                self.proxy_meta.object_path,
                self.dbus_property.interface_name,
                self.dbus_property.property_name,
            )
        )
        new_set_message.append_data(
            'v',
            (self.dbus_property.property_signature, complete_object),
        )
        await bus.call_async(new_set_message)


class DbusPropertyAsyncLocalBind(DbusPropertyAsyncBaseBind[T]):
    def __init__(
        self,
        dbus_property: DbusPropertyAsync[T],
        local_object: DbusInterfaceBaseAsync,
    ):
        self.dbus_property = dbus_property
        self.local_object_ref = weak_ref(local_object)

        self.__doc__ = dbus_property.__doc__

    async def get_async(self) -> T:
        local_object = self.local_object_ref()
        if local_object is None:
            raise RuntimeError("Local object no longer exists!")

        return self.dbus_property.property_getter(local_object)

    async def set_async(self, complete_object: T) -> None:
        if self.dbus_property.property_setter is None:
            raise RuntimeError("Property has no setter")

        local_object = self.local_object_ref()
        if local_object is None:
            raise RuntimeError("Local object no longer exists!")

        self.dbus_property.property_setter(
            local_object,
            complete_object,
        )

        try:
            properties_changed = getattr(
                local_object,
                "properties_changed",
            )
        except AttributeError:
            ...
        else:
            properties_changed.emit(
                (
                    self.dbus_property.interface_name,
                    {
                        self.dbus_property.property_name: (
                            self.dbus_property.property_signature,
                            complete_object,
                        ),
                    },
                    []
                )
            )

    def _dbus_reply_get(self, message: SdBusMessage) -> None:
        local_object = self.local_object_ref()
        if local_object is None:
            raise RuntimeError("Local object no longer exists!")

        reply_data: Any = self.dbus_property.property_getter(local_object)
        message.append_data(self.dbus_property.property_signature, reply_data)

    def _dbus_reply_set(self, message: SdBusMessage) -> None:
        local_object = self.local_object_ref()
        if local_object is None:
            raise RuntimeError("Local object no longer exists!")

        assert self.dbus_property.property_setter is not None
        data_to_set_to: Any = message.get_contents()

        self.dbus_property.property_setter(local_object, data_to_set_to)

        try:
            properties_changed = getattr(
                local_object,
                "properties_changed",
            )
        except AttributeError:
            ...
        else:
            properties_changed.emit(
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
            "Property getter can't be coroutine",
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
        return cast(DbusPropertyAsync[T], DbusPropertyOverride(new_property))

    return new_decorator
