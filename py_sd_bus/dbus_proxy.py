# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2020  igo95862

# This file is part of py_sd_bus

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

from types import FunctionType
from typing import (Any, Callable, Coroutine, Dict, Generator, Generic,
                    Iterator, List, Optional, Sequence, Tuple, Type, TypeVar,
                    cast)

from .sd_bus_internals import SdBus, SdBusInterface, SdBusMessage, sd_bus_open

DEFAULT_BUS: Optional[SdBus] = None


def get_bus() -> SdBus:
    global DEFAULT_BUS
    old_bus = DEFAULT_BUS
    if old_bus is None:
        new_bus = sd_bus_open()
        DEFAULT_BUS = new_bus
        return new_bus
    else:
        return old_bus


def _method_name_converter(python_name: str) -> Iterator[str]:
    char_iter = iter(python_name)
    # Name starting with upper case letter
    first_char = next(char_iter)
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


T_input = TypeVar('T_input')
T_result = TypeVar('T_result')
T_obj = TypeVar('T_obj')


class DbusSomething:
    def __init__(self) -> None:
        self.interface_name: Optional[str] = None


class DbusBinded:
    ...


class DbusMethod(DbusSomething):

    def __init__(
            self,
            async_function: FunctionType,
            method_name: Optional[str],
            input_signature: str,
            result_signature: str,
            result_args_names: Sequence[str],
            flags: int):

        super().__init__()
        self.original_method = async_function
        self.dbus_method: Optional[DbusMethodType] = None

        if method_name is None:
            self.method_name = ''.join(
                _method_name_converter(async_function.__name__))
        else:
            self.method_name = method_name

        self.input_signature = input_signature
        self.input_args_names = ""
        self.result_signature = result_signature
        self.result_args_names = result_args_names
        self.flags = flags

    def __get__(self,
                obj: DbusInterfaceBase,
                obj_class: Optional[Type[DbusInterfaceBase]] = None,
                ) -> Callable[..., Any]:
        if obj.is_binded:
            return DbusMethodBinded(self, obj)
        else:
            return self.original_method.__get__(obj, obj_class)


class DbusMethodBinded(DbusBinded):
    def __init__(self, dbus_method: DbusMethod, interface: DbusInterfaceBase):
        self.dbus_method = dbus_method
        self.interface = interface

    async def _call_dbus(self, *args: Any, **kwargs: Any) -> Any:
        assert self.interface.attached_bus is not None
        assert self.interface.remote_service_name is not None
        assert self.interface.remote_object_path is not None
        assert self.dbus_method.interface_name is not None
        new_call_message = self.interface.attached_bus.new_method_call_message(
            self.interface.remote_service_name,
            self.interface.remote_object_path,
            self.dbus_method.interface_name,
            self.dbus_method.method_name,
        )
        if args:
            new_call_message.append_data(
                self.dbus_method.input_signature, *args)

        reply_message = await self.interface.attached_bus.call_async(
            new_call_message)
        return reply_message.get_contents()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._call_dbus(*args, **kwargs)


def dbus_method(
        method_name: Optional[str] = None,
        input_signature: str = "",
        result_signature: str = "",
        result_args_names: Sequence[str] = (),
        flags: int = 0) -> Callable[[T_input], T_input]:

    def dbus_method_decorator(async_function: T_input) -> T_input:
        assert isinstance(async_function, FunctionType)
        new_wrapper = DbusMethod(
            async_function=async_function,
            method_name=method_name,
            input_signature=input_signature,
            result_signature=result_signature,
            result_args_names=result_args_names,
            flags=flags,
        )

        return cast(T_input, new_wrapper)

    return dbus_method_decorator


T = TypeVar('T')


class DbusProperty(DbusSomething, Generic[T]):
    def __init__(
            self,
            property_name: str,
            property_signature: str,
            property_args_names: Sequence[str],

    ) -> None:
        super().__init__()
        self.property_name = property_name
        self.property_signature = property_signature
        self.property_args_names = property_args_names

        self.parent: Optional[object] = None

    def __get__(self,
                obj: DbusInterfaceBase,
                obj_class: Optional[Type[DbusInterfaceBase]] = None,
                ) -> DbusPropertyBinded:
        return DbusPropertyBinded(self, obj)


class DbusPropertyBinded(DbusBinded):
    def __init__(self,
                 dbus_property: DbusProperty[T],
                 interface: DbusInterfaceBase):
        self.dbus_property = dbus_property
        self.interface = interface

    def __await__(self) -> Generator[Any, None, T]:
        if not self.interface.is_binded:
            raise NotImplementedError
        else:
            return self.get_coro().__await__()

    async def get_coro(self) -> T:
        assert self.interface.attached_bus is not None
        assert self.interface.remote_service_name is not None
        assert self.interface.remote_object_path is not None
        assert self.dbus_property.property_name is not None
        assert self.dbus_property.interface_name is not None
        new_call_message = self.interface.attached_bus. \
            new_property_get_message(
                self.interface.remote_service_name,
                self.interface.remote_object_path,
                self.dbus_property.interface_name,
                self.dbus_property.property_name,
            )

        reply_message = await self.interface.attached_bus. \
            call_async(new_call_message)
        return cast(T, reply_message.get_contents()[1])

    async def set_coro(self, complete_object: T) -> None:
        assert self.interface.attached_bus is not None
        assert self.interface.remote_service_name is not None
        assert self.interface.remote_object_path is not None
        assert self.dbus_property.property_name is not None
        assert self.dbus_property.interface_name is not None
        new_call_message = self.interface.attached_bus. \
            new_property_set_message(
                self.interface.remote_service_name,
                self.interface.remote_object_path,
                self.dbus_property.interface_name,
                self.dbus_property.property_name,
            )

        new_call_message.append_data(
            'v', (self.dbus_property.property_signature, complete_object))

        await self.interface.attached_bus.call_async(new_call_message)


def dbus_property(
        property_name: Optional[str] = None,
        property_signature: str = "",
        property_args_names: Sequence[str] = (),
) -> Callable[
    [Callable[..., Coroutine[Any, Any, T]]],
        DbusProperty[T]]:

    def property_decorator(
        function: Callable[..., Any]
    ) -> DbusProperty[T]:
        nonlocal property_name

        if property_name is None:
            property_name = ''.join(
                _method_name_converter(
                    cast(FunctionType, function).__name__
                )
            )

        new_wrapper: DbusProperty[T] = DbusProperty(
            property_name,
            property_signature,
            property_args_names,
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

        for key, value in namespace.items():
            if isinstance(value, DbusSomething):
                value.interface_name = interface_name

        namespace['_dbus_interface_name'] = interface_name
        namespace['_dbus_serving_enabled'] = serving_enabled
        new_cls = super().__new__(cls, name, bases, namespace)

        return cast(DbusInterfaceMeta, new_cls)


class DbusInterfaceBase(metaclass=DbusInterfaceMeta):
    _dbus_interface_name: Optional[str]
    _dbus_serving_enabled: bool

    def __init__(self) -> None:
        self.activated_interfaces: List[SdBusInterface] = []
        self.is_binded: bool = False
        self.remote_service_name: Optional[str] = None
        self.remote_object_path: Optional[str] = None
        self.attached_bus: Optional[SdBus] = None

        self._serve_map: Dict[str, Tuple[DbusMethod, Callable[..., Any]]] = {}

    def _yield_dbus_mro(self
                        ) -> Generator[Type[DbusInterfaceBase], None, None]:
        for mro_entry in self.__class__.__mro__:
            if not issubclass(mro_entry, DbusInterfaceBase):
                continue

            if mro_entry is DbusInterfaceBase:
                return

            if mro_entry._dbus_interface_name is None:
                continue

            yield mro_entry

    async def _call_from_dbus(
            self,
            request_message: SdBusMessage) -> None:
        request_data = request_message.get_contents()

        reply_message = request_message.create_reply()

        method_def, local_method = self._serve_map[
            request_message.get_member()]

        assert local_method is not None

        if isinstance(request_data, tuple):
            reply_data = await local_method(*request_data)
        elif request_data is None:
            reply_data = await local_method()
        else:
            reply_data = await local_method(request_data)

        if isinstance(reply_data, tuple):
            reply_message.append_data(method_def.result_signature, *reply_data)
        elif reply_data is not None:
            reply_message.append_data(method_def.result_signature, reply_data)

        reply_message.send()

    async def start_serving(
            self, bus: SdBus, object_path: str) -> None:

        interfaces_list: List[SdBusInterface] = []

        for mro_entry in self._yield_dbus_mro():

            assert mro_entry._dbus_interface_name is not None

            if not mro_entry._dbus_serving_enabled:
                continue

            class_dict = mro_entry.__dict__

            new_interface = SdBusInterface()

            for key, method_def in class_dict.items():

                if isinstance(method_def, DbusMethod):
                    self._serve_map[
                        method_def.method_name] = (
                            method_def, getattr(self, key))

                    new_interface.add_method(
                        method_def.method_name,
                        method_def.input_signature,
                        method_def.input_args_names,
                        method_def.result_signature,
                        method_def.result_args_names,
                        method_def.flags,
                        self._call_from_dbus,
                    )

            bus.add_interface(new_interface, object_path,
                              mro_entry._dbus_interface_name)
            interfaces_list.append(new_interface)

        self.activated_interfaces = interfaces_list

    def _connect(
        self,
        bus: SdBus,
        service_name: str,
        object_path: str,
    ) -> None:

        self.is_binded = True
        self.attached_bus = bus
        self.remote_service_name = service_name
        self.remote_object_path = object_path

    @ classmethod
    def new_connect(
        cls: Type[T_input],
        bus: SdBus,
        service_name: str,
        object_path: str,
    ) -> T_input:

        new_object = cls.__new__(cls)
        assert isinstance(new_object, DbusInterfaceBase)
        new_object._connect(bus, service_name, object_path)
        assert isinstance(new_object, cls)
        return new_object


DbusMethodType = Callable[[DbusInterfaceBase, Any], Coroutine[Any, Any, Any]]


class DbusPeerInterface(DbusInterfaceBase,
                        interface_name='org.freedesktop.DBus.Peer',
                        serving_enabled=False,
                        ):

    @ dbus_method()
    async def ping(self) -> None:
        raise NotImplementedError

    @ dbus_method()
    async def get_machine_id(self) -> str:
        raise NotImplementedError


class DbusIntrospectable(DbusInterfaceBase,
                         interface_name='org.freedesktop.DBus.Introspectable',
                         serving_enabled=False,
                         ):

    @ dbus_method()
    async def introspect(self) -> str:
        raise NotImplementedError


class DbusInterfaceCommon(DbusPeerInterface, DbusIntrospectable):
    ...
