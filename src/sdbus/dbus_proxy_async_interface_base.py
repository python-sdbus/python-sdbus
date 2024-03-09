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

from copy import copy
from inspect import getmembers
from types import MethodType
from typing import TYPE_CHECKING, Any, Callable, cast
from warnings import warn

from .dbus_common_elements import (
    DbusClassMeta,
    DbusInterfaceMetaCommon,
    DbusLocalObjectMeta,
    DbusOverload,
    DbusRemoteObjectMeta,
    DbusSomethingAsync,
    DbusSomethingCommon,
    DbusSomethingSync,
)
from .dbus_common_funcs import get_default_bus
from .dbus_proxy_async_method import DbusMethodAsync, DbusMethodAsyncLocalBind
from .dbus_proxy_async_property import (
    DbusPropertyAsync,
    DbusPropertyAsyncLocalBind,
)
from .dbus_proxy_async_signal import DbusSignalAsync, DbusSignalAsyncLocalBind
from .sd_bus_internals import SdBusInterface

if TYPE_CHECKING:
    from typing import (
        ClassVar,
        Dict,
        List,
        Optional,
        Set,
        Tuple,
        Type,
        TypeVar,
        Union,
    )

    from .dbus_common_elements import DbusBindedAsync
    from .sd_bus_internals import SdBus

    Self = TypeVar('Self', bound="DbusInterfaceBaseAsync")


class DbusInterfaceMetaAsync(DbusInterfaceMetaCommon):
    def __new__(cls, name: str,
                bases: Tuple[type, ...],
                namespace: Dict[str, Any],
                interface_name: Optional[str] = None,
                serving_enabled: bool = True,
                ) -> DbusInterfaceMetaAsync:

        dbus_class_meta = DbusClassMeta(interface_name or "")

        if interface_name is not None and serving_enabled:
            dbus_class_meta.dbus_interfaces_names.add(interface_name)

        overrides: Dict[str, DbusOverload] = {}
        unresolved_collisions: Set[str] = set()

        for attr_name, attr in namespace.items():
            if isinstance(attr, DbusOverload):
                overrides[attr_name] = attr
                continue

            if not isinstance(attr, DbusSomethingCommon):
                continue

            if isinstance(attr, DbusSomethingSync):
                raise TypeError(
                    "Can't mix blocking methods in "
                    f"async interface: {attr_name!r}"
                )

            if not serving_enabled:
                continue

            if isinstance(attr, DbusMethodAsync):
                dbus_class_meta.dbus_member_to_python_attr[
                    attr.method_name] = attr_name
                dbus_class_meta.python_attr_to_dbus_member[
                    attr_name] = attr.method_name
            elif isinstance(attr, DbusPropertyAsync):
                dbus_class_meta.dbus_member_to_python_attr[
                    attr.property_name] = attr_name
                dbus_class_meta.python_attr_to_dbus_member[
                    attr_name] = attr.property_name
            elif isinstance(attr, DbusSignalAsync):
                dbus_class_meta.dbus_member_to_python_attr[
                    attr.signal_name] = attr_name
                dbus_class_meta.python_attr_to_dbus_member[
                    attr_name] = attr.signal_name
            else:
                raise TypeError(f"Unknown D-Bus element: {attr!r}")

        for base in bases:
            if not issubclass(base, DbusInterfaceBaseAsync):
                continue

            # Update interfaces names set
            base_interfaces_names = base._dbus_meta.dbus_interfaces_names
            if dbus_interface_name_collision := (
                dbus_class_meta.dbus_interfaces_names
                & base_interfaces_names
            ):
                raise TypeError(
                    f"Interface {name!r} and {base!r} have interface name "
                    f"collision: {dbus_interface_name_collision}"
                )
            else:
                dbus_class_meta.dbus_interfaces_names.update(
                    base_interfaces_names
                )

            if dbus_member_collision := (
                dbus_class_meta.dbus_member_to_python_attr.keys()
                & base._dbus_meta.dbus_member_to_python_attr.keys()
            ):
                raise TypeError(
                    f"Interface {name!r} and {base!r} have D-Bus member "
                    f"collision: {dbus_member_collision}"
                )
            else:
                dbus_class_meta.dbus_member_to_python_attr.update(
                    base._dbus_meta.dbus_member_to_python_attr
                )

            for collision_name in (
                namespace.keys()
                & base._dbus_meta.python_attr_to_dbus_member.keys()
            ):
                try:
                    override = overrides.pop(collision_name)
                except KeyError:
                    unresolved_collisions.add(collision_name)
                    continue

                super_element = getattr(base, collision_name)
                dbus_element_override: DbusSomethingAsync
                if isinstance(super_element, DbusMethodAsync):
                    dbus_element_override = copy(super_element)
                    dbus_element_override.original_method = cast(
                        MethodType, override.original)
                elif isinstance(super_element, DbusPropertyAsync):
                    dbus_element_override = copy(super_element)
                    dbus_element_override.property_getter = cast(
                        Callable[[DbusInterfaceBaseAsync], Any],
                        override.original)
                    if override.setter_overload is not None:
                        dbus_element_override.property_setter = (
                            override.setter_overload
                        )
                        dbus_element_override.property_setter_is_public = (
                            override.is_setter_public
                        )
                else:
                    raise TypeError(
                        f"Unknown override {collision_name!r} "
                        f"with {super_element!r}"
                    )

                namespace[collision_name] = dbus_element_override

            dbus_class_meta.python_attr_to_dbus_member.update(
                base._dbus_meta.python_attr_to_dbus_member
            )

        if unresolved_collisions:
            raise TypeError(
                f"Interface {name!r} and {base!r} have Python attribute "
                f"collision: {unresolved_collisions}"
            )

        if overrides:
            raise TypeError(
                f"Interface {name!r} has unresolved overrides:",
                set(overrides.keys()),
            )

        namespace['_dbus_meta'] = dbus_class_meta
        new_cls = super().__new__(
            cls, name, bases, namespace,
            interface_name,
            serving_enabled,
        )

        return new_cls


class DbusInterfaceBaseAsync(metaclass=DbusInterfaceMetaAsync):
    _dbus_meta: ClassVar[DbusClassMeta]

    def __init__(self) -> None:
        self._dbus: Union[
            DbusRemoteObjectMeta, DbusLocalObjectMeta] = DbusLocalObjectMeta()

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

        local_object_meta = self._dbus
        if isinstance(local_object_meta, DbusRemoteObjectMeta):
            raise RuntimeError("Cannot export D-Bus proxies.")

        # TODO: Being able to serve multiple buses and object
        if local_object_meta.attached_bus is not None:
            raise RuntimeError(
                "Object already exported. "
                "This limitation should be fixed in future version."
            )

        if bus is None:
            bus = get_default_bus()

        local_object_meta.attached_bus = bus
        local_object_meta.serving_object_path = object_path
        # TODO: can be optimized with a single loop
        interface_map: Dict[str, List[DbusBindedAsync]] = {}

        for key, value in getmembers(self):
            assert not isinstance(value, DbusSomethingAsync)

            if isinstance(value, DbusMethodAsyncLocalBind):
                interface_name = value.dbus_method.interface_name
                if not value.dbus_method.serving_enabled:
                    continue
            elif isinstance(value, DbusPropertyAsyncLocalBind):
                interface_name = value.dbus_property.interface_name
                if not value.dbus_property.serving_enabled:
                    continue
            elif isinstance(value, DbusSignalAsyncLocalBind):
                interface_name = value.dbus_signal.interface_name
                if not value.dbus_signal.serving_enabled:
                    continue
            else:
                continue

            try:
                interface_member_list = interface_map[interface_name]
            except KeyError:
                interface_member_list = []
                interface_map[interface_name] = interface_member_list

            interface_member_list.append(value)

        for interface_name, member_list in interface_map.items():
            new_interface = SdBusInterface()
            for dbus_something in member_list:
                if isinstance(dbus_something, DbusMethodAsyncLocalBind):
                    new_interface.add_method(
                        dbus_something.dbus_method.method_name,
                        dbus_something.dbus_method.input_signature,
                        dbus_something.dbus_method.input_args_names,
                        dbus_something.dbus_method.result_signature,
                        dbus_something.dbus_method.result_args_names,
                        dbus_something.dbus_method.flags,
                        dbus_something._dbus_reply_call,
                    )
                elif isinstance(dbus_something, DbusPropertyAsyncLocalBind):
                    getter = dbus_something._dbus_reply_get
                    dbus_property = dbus_something.dbus_property

                    if (
                        dbus_property.property_setter is not None
                        and
                        dbus_property.property_setter_is_public
                    ):
                        setter = dbus_something._dbus_reply_set
                    else:
                        setter = None

                    new_interface.add_property(
                        dbus_property.property_name,
                        dbus_property.property_signature,
                        getter,
                        setter,
                        dbus_property.flags,
                    )
                elif isinstance(dbus_something, DbusSignalAsyncLocalBind):
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
            local_object_meta.activated_interfaces.append(new_interface)

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

        self._dbus = DbusRemoteObjectMeta(
            service_name,
            object_path,
            bus,
        )

    @classmethod
    def new_connect(
        cls: Type[Self],
        service_name: str,
        object_path: str,
        bus: Optional[SdBus] = None,
    ) -> Self:
        warn(
            ("new_connect is deprecated in favor of equivalent new_proxy."
             "Will be removed in version 1.0.0"),
            DeprecationWarning,
        )
        new_object = cls.__new__(cls)
        new_object._proxify(service_name, object_path, bus)
        return new_object

    @classmethod
    def new_proxy(
        cls: Type[Self],
        service_name: str,
        object_path: str,
        bus: Optional[SdBus] = None,
    ) -> Self:

        new_object = cls.__new__(cls)
        new_object._proxify(service_name, object_path, bus)
        return new_object
