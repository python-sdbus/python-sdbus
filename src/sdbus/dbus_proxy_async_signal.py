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

from asyncio import Queue
from types import FunctionType
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Callable,
    Generic,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    cast,
)
from weakref import ref as weak_ref

from .dbus_common_elements import (
    DbusBindedAsync,
    DbusSingalCommon,
    DbusSomethingAsync,
)
from .dbus_common_funcs import get_default_bus
from .sd_bus_internals import SdBus, SdBusMessage

T = TypeVar('T')


if TYPE_CHECKING:
    from .dbus_proxy_async_interface_base import DbusInterfaceBaseAsync


class DbusSignalAsync(DbusSomethingAsync, DbusSingalCommon, Generic[T]):

    def __get__(self,
                obj: Optional[DbusInterfaceBaseAsync],
                obj_class: Optional[Type[DbusInterfaceBaseAsync]] = None,
                ) -> DbusSignalBinded[T]:
        return DbusSignalBinded(self, obj)


class DbusSignalBinded(Generic[T], DbusBindedAsync):
    def __init__(self,
                 dbus_signal: DbusSignalAsync[T],
                 interface: Optional[DbusInterfaceBaseAsync]):
        self.dbus_signal = dbus_signal
        self.interface_ref = (
            weak_ref(interface)
            if interface is not None
            else None
        )

        self.__doc__ = dbus_signal.__doc__

    async def _get_dbus_queue(self) -> Queue[SdBusMessage]:
        assert self.interface_ref is not None, (
            "Called method from class?"
        )
        interface = self.interface_ref()
        assert interface is not None

        assert interface._attached_bus is not None
        assert interface._remote_service_name is not None
        assert interface._remote_object_path is not None
        assert self.dbus_signal.interface_name is not None
        assert self.dbus_signal.signal_name is not None

        return await interface._attached_bus.get_signal_queue_async(
            interface._remote_service_name,
            interface._remote_object_path,
            self.dbus_signal.interface_name,
            self.dbus_signal.signal_name,
        )

    def _cleanup_local_queue(
            self,
            queue_ref: weak_ref[Queue[T]]) -> None:
        assert self.interface_ref is not None, (
            "Called method from class?"
        )
        interface = self.interface_ref()
        assert interface is not None

        interface._local_signal_queues[self.dbus_signal].remove(queue_ref)

    def _get_local_queue(self) -> Queue[T]:
        assert self.interface_ref is not None, (
            "Called method from class?"
        )
        interface = self.interface_ref()
        assert interface is not None

        try:
            list_of_queues = interface._local_signal_queues[
                self.dbus_signal]
        except KeyError:
            list_of_queues = []
            interface._local_signal_queues[
                self.dbus_signal] = list_of_queues

        new_queue: Queue[T] = Queue()

        list_of_queues.append(weak_ref(new_queue, self._cleanup_local_queue))

        return new_queue

    async def catch(self) -> AsyncGenerator[T, None]:
        assert self.interface_ref is not None, (
            "Called method from class?"
        )
        interface = self.interface_ref()
        assert interface is not None

        if interface._is_binded:
            message_queue = await self._get_dbus_queue()

            while True:
                next_signal_message = await message_queue.get()
                yield cast(T, next_signal_message.get_contents())
        else:
            data_queue = self._get_local_queue()

            while True:
                next_data = await data_queue.get()
                yield next_data

    __aiter__ = catch

    async def catch_anywhere(
            self,
            service_name: Optional[str] = None,
            bus: Optional[SdBus] = None,
    ) -> AsyncGenerator[Tuple[str, T], None]:
        if service_name is None:
            if self.interface_ref is not None:
                interface = self.interface_ref()
                assert interface is not None
                if interface._remote_service_name is None:
                    raise NotImplementedError(
                        'catch_anywhere not implemented for '
                        'local objects'
                    )

                service_name = interface._remote_service_name
            else:
                raise ValueError(
                    'Called catch_anywhere from class '
                    'but service name was not provided'
                )

        if bus is None:
            if self.interface_ref is not None:
                interface = self.interface_ref()
                assert interface is not None
                assert interface._attached_bus is not None
                bus = interface._attached_bus
            else:
                bus = get_default_bus()

        message_queue = await bus.get_signal_queue_async(
            service_name,
            None,
            self.dbus_signal.interface_name,
            self.dbus_signal.signal_name,
        )

        while True:
            next_signal_message = await message_queue.get()
            signal_path = next_signal_message.path
            assert signal_path is not None
            yield (
                signal_path,
                cast(T, next_signal_message.get_contents())
            )

    def _emit_message(self, args: T) -> None:
        assert self.interface_ref is not None, (
            "Called method from class?"
        )
        interface = self.interface_ref()
        assert interface is not None

        assert interface._attached_bus is not None
        assert interface._serving_object_path is not None
        assert self.dbus_signal.interface_name is not None
        assert self.dbus_signal.signal_name is not None

        signal_message = interface._attached_bus.new_signal_message(
            interface._serving_object_path,
            self.dbus_signal.interface_name,
            self.dbus_signal.signal_name,
        )

        if ((not self.dbus_signal.signal_signature.startswith('('))
            and
                isinstance(args, tuple)):
            signal_message.append_data(
                self.dbus_signal.signal_signature, *args)
        else:
            signal_message.append_data(
                self.dbus_signal.signal_signature, args)

        signal_message.send()

    def emit(self, args: T) -> None:
        assert self.interface_ref is not None, (
            "Called method from class?"
        )
        interface = self.interface_ref()
        assert interface is not None

        if interface._activated_interfaces:
            self._emit_message(args)

        try:
            list_of_queues = interface._local_signal_queues[self.dbus_signal]
        except KeyError:
            return

        for local_queue_ref in list_of_queues:
            local_queue = local_queue_ref()
            assert local_queue is not None
            local_queue.put_nowait(args)


def dbus_signal_async(
        signal_signature: str = '',
        signal_args_names: Sequence[str] = (),
        flags: int = 0,
        signal_name: Optional[str] = None,
) -> Callable[
    [Callable[[Any], T]],
    DbusSignalAsync[T]
]:
    assert not isinstance(signal_signature, FunctionType), (
        "Passed function to decorator directly. "
        "Did you forget () round brackets?"
    )

    def signal_decorator(
            pseudo_function: Callable[[Any], T]) -> DbusSignalAsync[T]:

        assert isinstance(pseudo_function, FunctionType)
        return DbusSignalAsync(
            signal_name,
            signal_signature,
            signal_args_names,
            flags,
            pseudo_function,
        )

    return signal_decorator
