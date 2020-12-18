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
from typing import (TYPE_CHECKING, Any, Callable, Coroutine, Dict, Generator,
                    Generic, Iterator, List, Optional, Sequence, Tuple, Type,
                    TypeVar, cast)

from .sd_bus_internals import SdBus, SdBusInterface, SdBusMessage, sd_bus_open

if TYPE_CHECKING:
    from .sd_bus_internals import DbusCompleteTypes

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


class DbusBind:
    def __init__(self) -> None:
        self.attached_bus: Optional[SdBus] = None
        self.remote_service_name: Optional[str] = None
        self.remote_object_path: Optional[str] = None
        self.remote_interface_name: Optional[str] = None
        self.parent_interface: Optional[DbusInterfaceBase] = None
        self.binded = False

    def __get__(self,
                obj: object,
                obj_type: Optional[Type[object]] = None
                ) -> Any:
        assert isinstance(obj, DbusInterfaceBase)
        self.parent_interface = obj
        return self

    def bind(
        self,
        bus: SdBus,
            service_name: str,
            object_path: str,
            interface_name: str,
    ) -> None:

        self.attached_bus = bus
        self.remote_service_name = service_name
        self.remote_object_path = object_path
        self.remote_interface_name = interface_name
        self.binded = True


class DbusMethod(DbusBind):

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

    def bind(
            self,
            bus: SdBus,
            service_name: str,
            object_path: str,
            interface_name: str,
    ) -> None:
        super().bind(
            bus,
            service_name,
            object_path,
            interface_name,
        )

        async def dbus_call(*args: Any
                            ) -> DbusCompleteTypes:
            new_call_message = bus.new_method_call_message(
                service_name, object_path,
                interface_name, self.method_name,
            )
            if args:
                new_call_message.append_data(self.input_signature, *args)

            reply_message = await bus.call_async(new_call_message)
            return reply_message.get_contents()

        self.dbus_method = dbus_call

    async def _call_dbus(self, *args: Any, **kwargs: Any) -> Any:
        assert self.attached_bus is not None
        assert self.remote_service_name is not None
        assert self.remote_object_path is not None
        assert self.remote_interface_name is not None
        new_call_message = self.attached_bus.new_method_call_message(
            self.remote_service_name, self.remote_object_path,
            self.remote_interface_name, self.method_name,
        )
        if args:
            new_call_message.append_data(self.input_signature, *args)

        reply_message = await self.attached_bus.call_async(new_call_message)
        return reply_message.get_contents()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if not self.binded:
            return self.original_method(self.parent_interface, *args, **kwargs)
        else:
            return self._call_dbus(*args, **kwargs)

    async def _call_from_dbus(self, request_message: SdBusMessage) -> None:
        request_data = request_message.get_contents()

        reply_message = request_message.create_reply()

        possible_overwrite = getattr(self.parent_interface,
                                     self.original_method.__name__)

        if possible_overwrite is self:
            local_method = self.original_method.__get__(self.parent_interface,
                                                        None)
        else:
            local_method = possible_overwrite

        if isinstance(request_data, tuple):
            reply_data = await local_method(*request_data)
        elif request_data is None:
            reply_data = await local_method()
        else:
            reply_data = await local_method(request_data)

        if isinstance(reply_data, tuple):
            reply_message.append_data(self.result_signature, *reply_data)
        elif reply_data is not None:
            reply_message.append_data(self.result_signature, reply_data)

        reply_message.send()

    def serve(
        self,
        outer_self: DbusInterfaceBase,
    ) -> Callable[[SdBusMessage], Coroutine[Any, Any, None]]:
        if self.binded:
            raise ValueError("Can't serve binded method")

        return self._call_from_dbus


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


class DbusProperty(DbusBind, Generic[T]):
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

    def __await__(self) -> Generator[Any, None, T]:
        if not self.binded:
            raise NotImplementedError
        else:
            return self.get_coro().__await__()

    async def get_coro(self) -> T:
        assert self.attached_bus is not None
        assert self.remote_service_name is not None
        assert self.remote_object_path is not None
        assert self.remote_interface_name is not None
        new_call_message = self.attached_bus.new_property_get_message(
            self.remote_service_name, self.remote_object_path,
            self.remote_interface_name, self.property_name,
        )

        reply_message = await self.attached_bus.call_async(new_call_message)
        return cast(T, reply_message.get_contents()[1])

    async def set_coro(self, complete_object: T) -> None:
        assert self.attached_bus is not None
        assert self.remote_service_name is not None
        assert self.remote_object_path is not None
        assert self.remote_interface_name is not None
        new_call_message = self.attached_bus.new_property_set_message(
            self.remote_service_name, self.remote_object_path,
            self.remote_interface_name, self.property_name,
        )

        new_call_message.append_data(
            'v', (self.property_signature, complete_object))

        await self.attached_bus.call_async(new_call_message)


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

        namespace['_dbus_interface_name'] = interface_name
        namespace['_dbus_serving_enabled'] = serving_enabled
        new_cls = super().__new__(cls, name, bases, namespace)

        return cast(DbusInterfaceMeta, new_cls)


class DbusInterfaceBase(metaclass=DbusInterfaceMeta):
    _dbus_interface_name: Optional[str]
    _dbus_serving_enabled: bool

    def __init__(self) -> None:
        self.activated_interfaces: List[SdBusInterface] = []

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

    async def start_serving(
            self, bus: SdBus, object_path: str) -> None:

        interfaces_list: List[SdBusInterface] = []

        for mro_entry in self._yield_dbus_mro():

            assert mro_entry._dbus_interface_name is not None

            if not mro_entry._dbus_serving_enabled:
                continue

            class_dict = mro_entry.__dict__

            new_interface = SdBusInterface()

            for method_def in class_dict.values():
                if isinstance(method_def, DbusMethod):
                    new_interface.add_method(
                        method_def.method_name,
                        method_def.input_signature,
                        method_def.input_args_names,
                        method_def.result_signature,
                        method_def.result_args_names,
                        method_def.flags,
                        method_def.serve(self),
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

        for mro_entry in self._yield_dbus_mro():
            assert mro_entry._dbus_interface_name is not None
            class_dict = mro_entry.__dict__

            for attr_value in class_dict.values():
                if not isinstance(attr_value, DbusBind):
                    continue

                attr_value.bind(bus, service_name, object_path,
                                mro_entry._dbus_interface_name)

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
