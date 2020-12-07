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

from typing import (TYPE_CHECKING, Any, Callable, Coroutine, Dict, Iterator,
                    List, Optional, Sequence, Tuple, TypeVar, cast)

from .sd_bus_internals import (SdBus, SdBusInterface, SdBusMessage,
                               sd_bus_default)

if TYPE_CHECKING:
    from .sd_bus_internals import DbusCompleteTypes


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


DbusMethodType = Callable[..., Any]


class DbusMethod:

    def __init__(
            self,
            async_function: DbusMethodType,
            method_name: Optional[str],
            input_signature: str,
            result_signature: str,
            result_args_names: Sequence[str],
            flags: int):

        self.original_method = async_function

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
            interface_name: str,
            object_path: str) -> Any:

        async def dbus_call() -> DbusCompleteTypes:
            new_call_message = bus.new_method_call_message(
                service_name, object_path,
                interface_name, self.method_name,
            )
            reply_message = await bus.call_async(new_call_message)
            return reply_message.get_contents()

        return dbus_call

    def serve(
        self,
        outer_self: DbusInterfaceBase,
    ) -> Callable[[SdBusMessage], Coroutine[Any, Any, None]]:

        async def serve_handler(request_message: SdBusMessage) -> None:
            request_data = request_message.get_contents()

            reply_message = request_message.create_reply()
            reply_data = await self.original_method(outer_self, *request_data)

            if isinstance(reply_data, tuple):
                reply_message.append_basic(self.result_signature, *reply_data)
            else:
                reply_message.append_basic(self.result_signature, reply_data)

            reply_message.send()

        return serve_handler

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.original_method(*args, **kwargs)


T_input = TypeVar('T_input')


def dbus_method(
        method_name: Optional[str] = None,
        input_signature: str = "",
        result_signature: str = "",
        result_args_names: Sequence[str] = (),
        flags: int = 0) -> Callable[[T_input], T_input]:

    def dbus_method_decorator(async_function: T_input) -> T_input:
        new_wrapper = DbusMethod(
            async_function=cast(DbusMethodType, async_function),
            method_name=method_name,
            input_signature=input_signature,
            result_signature=result_signature,
            result_args_names=result_args_names,
            flags=flags,
        )
        return cast(T_input, new_wrapper)

    return dbus_method_decorator


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

    async def start_serving(
            self, bus: SdBus, object_path: str) -> List[SdBusInterface]:

        interfaces_list: List[SdBusInterface] = []

        for mro_entry in self.__class__.__mro__:
            if not issubclass(mro_entry, DbusInterfaceBase):
                continue

            if mro_entry is DbusInterfaceBase:
                continue

            if not mro_entry._dbus_serving_enabled:
                continue

            if mro_entry._dbus_interface_name is None:
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

        return interfaces_list

    @classmethod
    def connect(
        cls,
        service_name: str = 'org.freedesktop.DBus',
        object_path: str = '/org/freedesktop/DBus',
        bus: Optional[SdBus] = None,
    ) -> DbusInterfaceBase:

        if bus is None:
            bus = sd_bus_default()

        new_object = cls.__new__(cls)

        class_mro = cls.__mro__

        for mro_entry in class_mro:
            if not issubclass(mro_entry, DbusInterfaceBase):
                continue

            if mro_entry is DbusInterfaceBase:
                break

            if mro_entry._dbus_interface_name is None:
                continue

            class_dict = mro_entry.__dict__

            for attr_key, attr_value in class_dict.items():
                if isinstance(attr_value, DbusMethod):
                    setattr(
                        new_object, attr_key, attr_value.bind(
                            bus,
                            service_name,
                            mro_entry._dbus_interface_name,
                            object_path
                        )
                    )

        assert isinstance(new_object, cls)
        return new_object


class DbusPeerInterface(DbusInterfaceBase,
                        interface_name='org.freedesktop.DBus.Peer',
                        serving_enabled=False,
                        ):

    @dbus_method()
    async def ping(self) -> None:
        raise NotImplementedError

    @dbus_method()
    async def get_machine_id(self) -> str:
        raise NotImplementedError


class DbusIntrospectable(DbusInterfaceBase,
                         interface_name='org.freedesktop.DBus.Introspectable',
                         serving_enabled=False,
                         ):

    @dbus_method()
    async def introspect(self) -> str:
        raise NotImplementedError


class DbusInterfaceCommon(DbusPeerInterface, DbusIntrospectable):
    ...
