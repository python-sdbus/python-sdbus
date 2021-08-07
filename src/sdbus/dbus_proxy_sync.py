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

from inspect import iscoroutinefunction
from types import FunctionType
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    cast,
)

from .dbus_common import (
    DbusMethodCommon,
    DbusSomethingAsync,
    DbusSomethingSync,
    _check_sync_in_async_env,
    _method_name_converter,
    get_default_bus,
)
from .sd_bus_internals import SdBus

DEFAULT_BUS: Optional[SdBus] = None


T_input = TypeVar('T_input')
T_result = TypeVar('T_result')
T_obj = TypeVar('T_obj')


class DbusBinded:
    ...


class DbusMethodSync(DbusMethodCommon, DbusSomethingSync):
    def __get__(self,
                obj: DbusInterfaceBase,
                obj_class: Optional[Type[DbusInterfaceBase]] = None,
                ) -> Callable[..., Any]:
        return DbusMethodSyncBinded(self, obj)


class DbusMethodSyncBinded(DbusBinded):
    def __init__(self,
                 dbus_method: DbusMethodSync,
                 interface: DbusInterfaceBase):
        self.dbus_method = dbus_method
        self.interface = interface

        self.__doc__ = dbus_method.__doc__

    def _call_dbus_sync(self, *args: Any) -> Any:
        assert self.dbus_method.interface_name is not None
        new_call_message = self.interface._attached_bus. \
            new_method_call_message(
                self.interface._remote_service_name,
                self.interface._remote_object_path,
                self.dbus_method.interface_name,
                self.dbus_method.method_name,
            )
        if args:
            new_call_message.append_data(
                self.dbus_method.input_signature, *args)

        reply_message = self.interface._attached_bus.call(
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
) -> Callable[[T_input], T_input]:
    assert not isinstance(input_signature, FunctionType), (
        "Passed function to decorator directly. "
        "Did you forget () round brackets?"
    )

    def dbus_method_decorator(original_method: T_input) -> T_input:
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

        return cast(T_input, new_wrapper)

    return dbus_method_decorator


T = TypeVar('T')


class DbusProperty(DbusSomethingSync, Generic[T]):
    def __init__(
            self,
            property_name: str,
            property_signature: str,
            property_getter: Callable[[DbusInterfaceBase],
                                      T],
            property_setter: Optional[
                Callable[[DbusInterfaceBase, T],
                         None]],
            flags: int,

    ) -> None:
        super().__init__()
        self.property_name = property_name
        self.property_signature = property_signature
        self.property_getter = property_getter
        self.property_setter = property_setter
        self.flags = flags

        self.__doc__ = property_getter.__doc__


class DbusPropertySync(DbusProperty[T]):
    def __get__(self,
                obj: DbusInterfaceBase,
                obj_class: Optional[Type[DbusInterfaceBase]] = None,
                ) -> T:
        assert _check_sync_in_async_env(), (
            "Used sync __get__ method in async environment. "
            "This is probably an error as it will block "
            "other asyncio methods for considerable time."
        )
        assert self.interface_name is not None

        new_call_message = obj._attached_bus. \
            new_property_get_message(
                obj._remote_service_name,
                obj._remote_object_path,
                self.interface_name,
                self.property_name,
            )

        reply_message = obj._attached_bus. \
            call(new_call_message)
        return cast(T, reply_message.get_contents()[1])

    def __set__(self, obj: DbusInterfaceBase, value: T) -> None:
        assert _check_sync_in_async_env(), (
            "Used sync __set__ method in async environment. "
            "This is probably an error as it will block "
            "other asyncio methods for considerable time."
        )

        if not self.property_signature:
            raise AttributeError('Dbus property is read only')

        assert obj._attached_bus is not None
        assert obj._remote_service_name is not None
        assert obj._remote_object_path is not None
        assert self.property_name is not None
        assert self.interface_name is not None
        new_call_message = obj._attached_bus. \
            new_property_set_message(
                obj._remote_service_name,
                obj._remote_object_path,
                self.interface_name,
                self.property_name,
            )

        new_call_message.append_data(
            'v', (self.property_signature, value))

        obj._attached_bus.call(new_call_message)


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
        nonlocal property_name

        if property_name is None:
            property_name = ''.join(
                _method_name_converter(
                    cast(FunctionType, function).__name__
                )
            )

        new_wrapper: DbusPropertySync[T] = DbusPropertySync(
            property_name,
            property_signature,
            function,
            None,
            flags,
        )

        return new_wrapper

    return property_decorator


class DbusInterfaceMeta(type):
    def __new__(cls, name: str,
                bases: Tuple[type, ...],
                namespace: Dict[str, Any],
                interface_name: Optional[str] = None,
                serving_enabled: bool = True,
                ) -> DbusInterfaceMeta:

        declared_interfaces = set()
        # Set interface name
        for key, value in namespace.items():
            assert not isinstance(value, DbusSomethingAsync), (
                "Can't mix async methods in sync interface."
            )

            if isinstance(value, DbusSomethingSync):
                value.interface_name = interface_name
                value.serving_enabled = serving_enabled
                declared_interfaces.add(key)

        super_declared_interfaces = set()
        for base in bases:
            if issubclass(base, DbusInterfaceBase):
                super_declared_interfaces.update(
                    base._dbus_declared_interfaces)

        for key in super_declared_interfaces & namespace.keys():
            raise TypeError("Attempted to overload dbus definition"
                            " sync interfaces do not support overloading")

        namespace['_dbus_declared_interfaces'] = declared_interfaces

        new_cls = super().__new__(cls, name, bases, namespace)

        return new_cls


class DbusInterfaceBase(metaclass=DbusInterfaceMeta):
    _dbus_declared_interfaces: Set[str]
    _dbus_serving_enabled: bool

    def __init__(
            self,
            service_name: str,
            object_path: str,
            bus: Optional[SdBus] = None, ) -> None:
        self._remote_service_name = service_name
        self._remote_object_path = object_path
        self._attached_bus: SdBus = (
            bus if bus is not None
            else get_default_bus())


class DbusPeerInterface(
    DbusInterfaceBase,
    interface_name='org.freedesktop.DBus.Peer',
    serving_enabled=False,
):

    @dbus_method(method_name='Ping')
    def dbus_ping(self) -> None:
        raise NotImplementedError

    @dbus_method(method_name='GetMachineId')
    def dbus_machine_id(self) -> str:
        raise NotImplementedError


class DbusIntrospectable(
    DbusInterfaceBase,
    interface_name='org.freedesktop.DBus.Introspectable',
    serving_enabled=False,
):

    @dbus_method(method_name='Introspect')
    def dbus_introspect(self) -> str:
        raise NotImplementedError


class DbusInterfaceCommon(
        DbusPeerInterface, DbusIntrospectable):
    ...


class DbusObjectManagerInterface(
    DbusInterfaceCommon,
    interface_name='org.freedesktop.DBus.ObjectManager',
    serving_enabled=False,
):
    @dbus_method(result_signature='a{oa{sa{sv}}}')
    def get_managed_objects(
            self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        raise NotImplementedError
