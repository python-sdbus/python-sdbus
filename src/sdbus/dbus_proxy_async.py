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

from asyncio import Queue
from copy import deepcopy
from inspect import getmembers, iscoroutinefunction
from types import FunctionType, MethodType
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Dict,
    Generator,
    Generic,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    cast,
)
from weakref import ref as weak_ref
from weakref import ref as weakref

from .dbus_common import (
    DbusMethodCommon,
    DbusSomethingAsync,
    DbusSomethingSync,
    _method_name_converter,
    get_default_bus,
)
from .dbus_exceptions import DbusFailedError
from .sd_bus_internals import (
    DbusNoReplyFlag,
    SdBus,
    SdBusInterface,
    SdBusMessage,
)

T_input = TypeVar('T_input')
T_result = TypeVar('T_result')
T_obj = TypeVar('T_obj')


class DbusBindedAsync:
    ...


class DbusMethodAsync(DbusMethodCommon, DbusSomethingAsync):
    def __get__(self,
                obj: DbusInterfaceBaseAsync,
                obj_class: Optional[Type[DbusInterfaceBaseAsync]] = None,
                ) -> Callable[..., Any]:
        return DbusMethodAsyncBinded(self, obj)


class DbusMethodAsyncBinded(DbusBindedAsync):
    def __init__(self,
                 dbus_method: DbusMethodAsync,
                 interface: DbusInterfaceBaseAsync):
        self.dbus_method = dbus_method
        self.interface_ref = weakref(interface)

        self.__doc__ = dbus_method.__doc__

    async def _call_dbus_async(self, *args: Any) -> Any:
        interface = self.interface_ref()
        assert interface is not None

        assert interface._attached_bus is not None
        assert interface._remote_service_name is not None
        assert interface._remote_object_path is not None
        assert self.dbus_method.interface_name is not None
        new_call_message = interface._attached_bus. \
            new_method_call_message(
                interface._remote_service_name,
                interface._remote_object_path,
                self.dbus_method.interface_name,
                self.dbus_method.method_name,
            )

        if args:
            new_call_message.append_data(
                self.dbus_method.input_signature, *args)

        if self.dbus_method.flags & DbusNoReplyFlag:
            new_call_message.expect_reply = False
            new_call_message.send()
            return

        reply_message = await interface._attached_bus.call_async(
            new_call_message)
        return reply_message.get_contents()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        interface = self.interface_ref()
        assert interface is not None

        if interface._is_binded:

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

            return self._call_dbus_async(*rebuilt_args)
        else:
            return self.dbus_method.original_method(
                interface, *args, **kwargs)

    async def _call_from_dbus(
            self,
            request_message: SdBusMessage) -> None:
        interface = self.interface_ref()
        assert interface is not None

        request_data = request_message.get_contents()

        local_method = self.dbus_method.original_method.__get__(
            interface, None)

        try:
            if isinstance(request_data, tuple):
                reply_data = await local_method(*request_data)
            elif request_data is None:
                reply_data = await local_method()
            else:
                reply_data = await local_method(request_data)
        except DbusFailedError as e:
            if not request_message.expect_reply:
                return

            error_message = request_message.create_error_reply(
                e.dbus_error_name,
                str(e.args[0]) if e.args else "",
            )
            error_message.send()
            return

        if not request_message.expect_reply:
            return

        reply_message = request_message.create_reply()

        if isinstance(reply_data, tuple):
            reply_message.append_data(
                self.dbus_method.result_signature, *reply_data)
        elif reply_data is not None:
            reply_message.append_data(
                self.dbus_method.result_signature, reply_data)

        reply_message.send()


def dbus_method_async(
    input_signature: str = "",
    result_signature: str = "",
    flags: int = 0,
    result_args_names: Sequence[str] = (),
    input_args_names: Sequence[str] = (),
    method_name: Optional[str] = None,
) -> Callable[[T_input], T_input]:

    assert not isinstance(input_signature, FunctionType), (
        "Passed function to decorator directly. "
        "Did you forget () round brackets?"
    )

    def dbus_method_decorator(original_method: T_input) -> T_input:
        assert isinstance(original_method, FunctionType)
        assert iscoroutinefunction(original_method), (
            "Expected coroutine function. ",
            "Maybe you forgot 'async' keyword?",
        )
        new_wrapper = DbusMethodAsync(
            original_method=original_method,
            method_name=method_name,
            input_signature=input_signature,
            result_signature=result_signature,
            result_args_names=result_args_names,
            input_args_names=input_args_names,
            flags=flags,
        )

        return cast(T_input, new_wrapper)

    return dbus_method_decorator


T = TypeVar('T')


class DbusProperty(DbusSomethingAsync, Generic[T]):
    def __init__(
            self,
            property_name: str,
            property_signature: str,
            property_getter: Callable[[DbusInterfaceBaseAsync],
                                      T],
            property_setter: Optional[
                Callable[[DbusInterfaceBaseAsync, T],
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


class DbusPropertyAsync(DbusProperty[T]):
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
        self.interface_ref = weakref(interface)

        self.__doc__ = dbus_property.__doc__

    def __await__(self) -> Generator[Any, None, T]:
        return self.get_async().__await__()

    async def get_async(self) -> T:
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
        interface = self.interface_ref()
        assert interface is not None

        reply_data: Any = self.dbus_property.property_getter(interface)
        message.append_data(self.dbus_property.property_signature, reply_data)

    def _reply_set_sync(self, message: SdBusMessage) -> None:
        interface = self.interface_ref()
        assert interface is not None

        assert self.dbus_property.property_setter is not None
        data_to_set_to: Any = message.get_contents()

        self.dbus_property.property_setter(interface, data_to_set_to)

    async def set_async(self, complete_object: T) -> None:
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

        nonlocal property_name

        if property_name is None:
            property_name = ''.join(
                _method_name_converter(
                    cast(FunctionType, function).__name__
                )
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


class DbusSignal(Generic[T], DbusSomethingAsync):
    def __init__(
        self,
        original_function: Callable[[Any], T],
        signal_name: str,
        signature: str = "",
        args_names: Sequence[str] = (),
        flags: int = 0,
    ):
        super().__init__()
        self.original_function = original_function
        self.signal_name = signal_name
        self.signature = signature
        self.args_names = args_names
        self.flags = flags

        self.__doc__ = original_function.__doc__

    def __get__(self,
                obj: DbusInterfaceBaseAsync,
                obj_class: Optional[Type[DbusInterfaceBaseAsync]] = None,
                ) -> DbusSignalBinded[T]:
        return DbusSignalBinded(self, obj)


class DbusSignalBinded(Generic[T], DbusBindedAsync):
    def __init__(self,
                 dbus_signal: DbusSignal[T],
                 interface: DbusInterfaceBaseAsync):
        self.dbus_signal = dbus_signal
        self.interface_ref = weakref(interface)

        self.__doc__ = dbus_signal.__doc__

    async def _get_dbus_queue(self) -> Queue[SdBusMessage]:
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
        interface = self.interface_ref()
        assert interface is not None

        interface._local_signal_queues[self.dbus_signal].remove(queue_ref)

    def _get_local_queue(self) -> Queue[T]:
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

    async def __aiter__(self) -> AsyncGenerator[T, None]:

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

    def _emit_message(self, args: T) -> None:
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

        if ((not self.dbus_signal.signature.startswith('('))
            and
                isinstance(args, tuple)):
            signal_message.append_data(self.dbus_signal.signature, *args)
        else:
            signal_message.append_data(self.dbus_signal.signature, args)

        signal_message.send()

    def emit(self, args: T) -> None:
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
    DbusSignal[T]
]:
    assert not isinstance(signal_signature, FunctionType), (
        "Passed function to decorator directly. "
        "Did you forget () round brackets?"
    )

    def signal_decorator(pseudo_function: Callable[[Any], T]) -> DbusSignal[T]:
        nonlocal signal_name

        if signal_name is None:
            signal_name = ''.join(
                _method_name_converter(
                    cast(FunctionType, pseudo_function).__name__
                )
            )

        return DbusSignal(
            pseudo_function,
            signal_name, signal_signature,
            signal_args_names, flags,
        )

    return signal_decorator


class DbusOverload:
    def __init__(self, original: T):
        self.original = original
        self.setter_overload: Optional[Callable[[Any, T], None]] = None

    def setter(self, new_setter: Optional[Callable[[Any, T], None]]) -> None:
        self.setter_overload = new_setter


def dbus_method_async_override() -> Callable[[T], T]:

    def new_decorator(
            new_function: T) -> T:
        return cast(T, DbusOverload(new_function))

    return new_decorator


def dbus_property_async_override() -> Callable[
    [Callable[[Any], T]],
        DbusPropertyAsync[T]]:

    def new_decorator(
            new_property: Callable[[Any], T]) -> DbusPropertyAsync[T]:
        return cast(DbusPropertyAsync[T], DbusOverload(new_property))

    return new_decorator


class DbusInterfaceMetaAsync(type):
    def __new__(cls, name: str,
                bases: Tuple[type, ...],
                namespace: Dict[str, Any],
                interface_name: Optional[str] = None,
                serving_enabled: bool = True,
                ) -> DbusInterfaceMetaAsync:

        declared_interfaces = set()
        # Set interface name
        for key, value in namespace.items():
            assert not isinstance(value, DbusSomethingSync), (
                "Can't mix sync methods in async interface."
            )

            if isinstance(value, DbusSomethingAsync):
                value.interface_name = interface_name
                value.serving_enabled = serving_enabled
                declared_interfaces.add(key)

        super_declared_interfaces = set()
        for base in bases:
            if issubclass(base, DbusInterfaceBaseAsync):
                super_declared_interfaces.update(
                    base._dbus_declared_interfaces)

        for key in super_declared_interfaces & namespace.keys():
            value = namespace[key]
            if isinstance(value, DbusOverload):
                for base in bases:
                    try:
                        sc_dbus_def = base.__dict__[key]
                        break
                    except KeyError:
                        continue

                assert isinstance(sc_dbus_def, DbusSomethingAsync)
                new_dbus_def = deepcopy(sc_dbus_def)
                if isinstance(new_dbus_def, DbusMethodAsync):
                    new_dbus_def.original_method = cast(
                        MethodType, value.original)
                elif isinstance(new_dbus_def, DbusPropertyAsync):
                    new_dbus_def.property_getter = cast(
                        Callable[[DbusInterfaceBaseAsync], Any],
                        value.original)
                    if value.setter_overload is not None:
                        new_dbus_def.property_setter = value.setter_overload
                else:
                    raise TypeError('Unknown overload')

                namespace[key] = new_dbus_def
                declared_interfaces.add(key)
            else:
                raise TypeError("Attempted to overload dbus definition"
                                " without using @dbus_overload decorator")

        namespace['_dbus_declared_interfaces'] = declared_interfaces

        namespace['_dbus_interface_name'] = interface_name
        namespace['_dbus_serving_enabled'] = serving_enabled
        new_cls = super().__new__(cls, name, bases, namespace)

        return new_cls


class DbusInterfaceBaseAsync(metaclass=DbusInterfaceMetaAsync):
    _dbus_declared_interfaces: Set[str]
    _dbus_interface_name: Optional[str]
    _dbus_serving_enabled: bool

    # TODO: make all attributes start with _
    def __init__(self) -> None:
        self._activated_interfaces: List[SdBusInterface] = []
        self._is_binded: bool = False
        self._remote_service_name: Optional[str] = None
        self._remote_object_path: Optional[str] = None
        self._attached_bus: Optional[SdBus] = None
        self._serving_object_path: Optional[str] = None
        self._local_signal_queues: \
            Dict[DbusSignal[Any], List[weak_ref[Queue[Any]]]] = {}

    async def start_serving(self,
                            object_path: str,
                            bus: Optional[SdBus] = None,
                            ) -> None:

        from warnings import warn
        warn("start_serving is deprecated in favor of export_to_dbus",
             DeprecationWarning)
        self.export_to_dbus(object_path, bus)

    def export_to_dbus(
        self,
        object_path: str,
        bus: Optional[SdBus] = None,
    ) -> None:

        if bus is None:
            bus = get_default_bus()
        # TODO: Being able to serve multiple buses and object
        self._attached_bus = bus
        self._serving_object_path = object_path
        # TODO: can be optimized with a single loop
        interface_map: Dict[str, List[DbusBindedAsync]] = {}

        for key, value in getmembers(self):
            assert not isinstance(value, DbusSomethingAsync)

            if isinstance(value, DbusMethodAsyncBinded):
                interface_name = value.dbus_method.interface_name
                if not value.dbus_method.serving_enabled:
                    continue
            elif isinstance(value, DbusPropertyAsyncBinded):
                interface_name = value.dbus_property.interface_name
                if not value.dbus_property.serving_enabled:
                    continue
            elif isinstance(value, DbusSignalBinded):
                interface_name = value.dbus_signal.interface_name
                if not value.dbus_signal.serving_enabled:
                    continue
            else:
                continue

            assert interface_name is not None

            try:
                interface_member_list = interface_map[interface_name]
            except KeyError:
                interface_member_list = []
                interface_map[interface_name] = interface_member_list

            interface_member_list.append(value)

        for interface_name, member_list in interface_map.items():
            new_interface = SdBusInterface()
            for dbus_something in member_list:
                if isinstance(dbus_something, DbusMethodAsyncBinded):
                    new_interface.add_method(
                        dbus_something.dbus_method.method_name,
                        dbus_something.dbus_method.input_signature,
                        dbus_something.dbus_method.input_args_names,
                        dbus_something.dbus_method.result_signature,
                        dbus_something.dbus_method.result_args_names,
                        dbus_something.dbus_method.flags,
                        dbus_something._call_from_dbus,
                    )
                elif isinstance(dbus_something, DbusPropertyAsyncBinded):
                    getter = dbus_something._reply_get_sync

                    setter = (dbus_something._reply_set_sync
                              if dbus_something.dbus_property.property_setter
                              is not None
                              else None)

                    new_interface.add_property(
                        dbus_something.dbus_property.property_name,
                        dbus_something.dbus_property.property_signature,
                        getter,
                        setter,
                        dbus_something.dbus_property.flags,
                    )
                elif isinstance(dbus_something, DbusSignalBinded):
                    new_interface.add_signal(
                        dbus_something.dbus_signal.signal_name,
                        dbus_something.dbus_signal.signature,
                        dbus_something.dbus_signal.args_names,
                        dbus_something.dbus_signal.flags,
                    )
                else:
                    raise TypeError

            bus.add_interface(new_interface, object_path,
                              interface_name)
            self._activated_interfaces.append(new_interface)

    def _connect(
        self,
        service_name: str,
        object_path: str,
        bus: Optional[SdBus] = None,
    ) -> None:

        self._is_binded = True
        self._attached_bus = bus if bus is not None else get_default_bus()
        self._remote_service_name = service_name
        self._remote_object_path = object_path

    @classmethod
    def new_connect(
        cls: Type[T_input],
        service_name: str,
        object_path: str,
        bus: Optional[SdBus] = None,
    ) -> T_input:

        new_object = cls.__new__(cls)
        assert isinstance(new_object, DbusInterfaceBaseAsync)
        new_object._connect(service_name, object_path, bus)
        assert isinstance(new_object, cls)
        return new_object


class DbusPeerInterfaceAsync(
    DbusInterfaceBaseAsync,
    interface_name='org.freedesktop.DBus.Peer',
    serving_enabled=False,
):

    @dbus_method_async(method_name='Ping')
    async def dbus_ping(self) -> None:
        raise NotImplementedError

    @dbus_method_async(method_name='GetMachineId')
    async def dbus_machine_id(self) -> str:
        raise NotImplementedError


class DbusIntrospectableAsync(
    DbusInterfaceBaseAsync,
    interface_name='org.freedesktop.DBus.Introspectable',
    serving_enabled=False,
):

    @dbus_method_async(method_name='Introspect')
    async def dbus_introspect(self) -> str:
        raise NotImplementedError


class DbusPropertiesInterfaceAsync(
    DbusInterfaceBaseAsync,
    interface_name='org.freedesktop.DBus.Properties',
    serving_enabled=False,
):
    @dbus_signal_async('sa{sv}as')
    def properties_changed(self) -> Tuple[str,
                                          Dict[str, Tuple[str, Any]],
                                          List[str]]:
        ...


class DbusInterfaceCommonAsync(
        DbusPeerInterfaceAsync, DbusPropertiesInterfaceAsync,
        DbusIntrospectableAsync):
    ...


class DbusObjectManagerInterfaceAsync(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.DBus.ObjectManager',
    serving_enabled=False,
):
    @dbus_method_async(result_signature='a{oa{sa{sv}}}')
    async def get_managed_objects(
            self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        raise NotImplementedError

    @dbus_signal_async('oa{sa{sv}}')
    def interfaces_added(self) -> Tuple[str, Dict[str, Dict[str, Any]]]:
        raise NotImplementedError

    @dbus_signal_async('oao')
    def interfaces_removed(self) -> Tuple[str, List[str]]:
        raise NotImplementedError
