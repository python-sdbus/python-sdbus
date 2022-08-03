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
from copy import deepcopy
from inspect import getmembers
from types import MethodType
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    cast,
)
from warnings import warn
from weakref import ref as weak_ref

from .dbus_common_elements import (
    DbusBindedAsync,
    DbusInterfaceMetaCommon,
    DbusOverload,
    DbusSomethingAsync,
    DbusSomethingSync,
)
from .dbus_common_funcs import get_default_bus
from .dbus_proxy_async_method import DbusMethodAsync, DbusMethodAsyncBinded
from .dbus_proxy_async_property import (
    DbusPropertyAsync,
    DbusPropertyAsyncBinded,
)
from .dbus_proxy_async_signal import DbusSignalAsync, DbusSignalBinded
from .sd_bus_internals import SdBus, SdBusInterface

T_input = TypeVar('T_input')


class DbusInterfaceMetaAsync(DbusInterfaceMetaCommon):
    def __new__(cls, name: str,
                bases: Tuple[type, ...],
                namespace: Dict[str, Any],
                interface_name: Optional[str] = None,
                serving_enabled: bool = True,
                ) -> DbusInterfaceMetaAsync:

        dbus_served_interfaces_names = (
            {interface_name}
            if serving_enabled and interface_name is not None
            else set()
        )
        dbus_to_python_name_map: Dict[str, str] = {}
        dbus_declared_members: Dict[str, DbusSomethingAsync] = {}
        superclass_members: Dict[str, DbusSomethingAsync] = {}

        for base in bases:
            if issubclass(base, DbusInterfaceBaseAsync):
                dbus_to_python_name_map.update(
                    base._dbus_to_python_name_map
                )
                dbus_served_interfaces_names.update(
                    base._dbus_served_interfaces_names
                )

                superclass_members.update(
                    base._dbus_declared_members
                )

        for key, value in namespace.items():
            assert not isinstance(value, DbusSomethingSync), (
                "Can't mix sync methods in async interface."
            )

            if isinstance(value, DbusSomethingAsync):
                value.interface_name = interface_name
                value.serving_enabled = serving_enabled
                dbus_declared_members[key] = value

            if isinstance(value, DbusMethodAsync):
                dbus_to_python_name_map[value.method_name] = key
            elif isinstance(value, DbusPropertyAsync):
                dbus_to_python_name_map[value.property_name] = key
            elif isinstance(value, DbusSignalAsync):
                dbus_to_python_name_map[value.signal_name] = key

            try:
                super_dbus_def = superclass_members[key]
            except KeyError:
                if isinstance(value, DbusOverload):
                    raise TypeError(
                        f"No D-Bus member '{key}' to overload with."
                    )
            else:
                if not isinstance(value, DbusOverload):
                    raise TypeError(
                        "Attempted to overload dbus definition"
                        " without using @dbus_overload decorator"
                    )

                if isinstance(super_dbus_def, DbusMethodAsync):
                    new_method_def = deepcopy(super_dbus_def)
                    new_method_def.original_method = cast(
                        MethodType, value.original)

                    namespace[key] = new_method_def
                elif isinstance(super_dbus_def, DbusPropertyAsync):
                    new_property_def = deepcopy(super_dbus_def)
                    new_property_def.property_getter = cast(
                        Callable[[DbusInterfaceBaseAsync], Any],
                        value.original)
                    if value.setter_overload is not None:
                        new_property_def.property_setter = (
                            value.setter_overload
                        )

                    namespace[key] = new_property_def
                else:
                    raise TypeError('Unknown D-Bus overload')

        dbus_declared_members.update(superclass_members)

        namespace['_dbus_served_interfaces_names'] = \
            dbus_served_interfaces_names
        namespace['_dbus_to_python_name_map'] = dbus_to_python_name_map
        namespace['_dbus_interface_name'] = interface_name
        namespace['_dbus_serving_enabled'] = serving_enabled
        namespace['_dbus_declared_members'] = dbus_declared_members
        new_cls = super().__new__(
            cls, name, bases, namespace,
            interface_name,
            serving_enabled,
        )

        return cast(DbusInterfaceMetaAsync, new_cls)


class DbusInterfaceBaseAsync(metaclass=DbusInterfaceMetaAsync):
    _dbus_interface_name: Optional[str]
    _dbus_serving_enabled: bool
    _dbus_to_python_name_map: Dict[str, str]
    _dbus_served_interfaces_names: Set[str]
    _dbus_declared_members: Dict[str, DbusSomethingAsync]

    def __init__(self) -> None:
        self._activated_interfaces: List[SdBusInterface] = []
        self._is_binded: bool = False
        self._remote_service_name: Optional[str] = None
        self._remote_object_path: Optional[str] = None
        self._attached_bus: Optional[SdBus] = None
        self._serving_object_path: Optional[str] = None
        self._local_signal_queues: \
            Dict[DbusSignalAsync[Any], List[weak_ref[Queue[Any]]]] = {}

    async def start_serving(self,
                            object_path: str,
                            bus: Optional[SdBus] = None,
                            ) -> None:

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
                        dbus_something.dbus_signal.signal_signature,
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
        self._proxify(
            service_name,
            object_path,
            bus,
        )

    def _proxify(
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
        warn(
            ("new_connect is deprecated in favor of equivalent new_proxy."
             "Will be removed in version 1.0.0"),
            DeprecationWarning,
        )
        new_object = cls.__new__(cls)
        assert isinstance(new_object, DbusInterfaceBaseAsync)
        new_object._proxify(service_name, object_path, bus)
        assert isinstance(new_object, cls)
        return new_object

    @classmethod
    def new_proxy(
        cls: Type[T_input],
        service_name: str,
        object_path: str,
        bus: Optional[SdBus] = None,
    ) -> T_input:

        new_object = cls.__new__(cls)
        assert isinstance(new_object, DbusInterfaceBaseAsync)
        new_object._proxify(service_name, object_path, bus)
        assert isinstance(new_object, cls)
        return new_object
