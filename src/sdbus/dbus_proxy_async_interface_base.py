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

from collections.abc import Callable
from copy import copy
from itertools import chain
from typing import TYPE_CHECKING, Any, cast
from warnings import warn
from weakref import WeakKeyDictionary, WeakValueDictionary

from .dbus_common_elements import (
    DbusClassMeta,
    DbusInterfaceMetaCommon,
    DbusLocalObjectMeta,
    DbusMemberAsync,
    DbusMemberCommon,
    DbusMemberSync,
    DbusMethodOverride,
    DbusPropertyOverride,
    DbusRemoteObjectMeta,
)
from .dbus_proxy_async_method import DbusLocalMethodAsync, DbusMethodAsync
from .dbus_proxy_async_property import (
    DbusLocalPropertyAsync,
    DbusPropertyAsync,
)
from .dbus_proxy_async_signal import DbusLocalSignalAsync, DbusSignalAsync
from .default_bus import get_default_bus
from .sd_bus_internals import SdBusInterface

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    from typing import Optional, TypeVar, Union

    from .sd_bus_internals import SdBus, SdBusSlot

    T = TypeVar('T')
    Self = TypeVar('Self', bound="DbusInterfaceBaseAsync")
    DbusOverride = Union[DbusMethodOverride[T], DbusPropertyOverride[T]]


DBUS_CLASS_TO_META: WeakKeyDictionary[
    type, DbusClassMeta] = WeakKeyDictionary()
DBUS_INTERFACE_NAME_TO_CLASS: WeakValueDictionary[
    str, DbusInterfaceMetaAsync] = WeakValueDictionary()


class DbusInterfaceMetaAsync(DbusInterfaceMetaCommon):

    @staticmethod
    def _process_dbus_method_override(
        override_attr_name: str,
        override: DbusMethodOverride[T],
        mro_dbus_elements: dict[str, DbusMemberAsync],
    ) -> DbusMethodAsync:
        try:
            original_dbus_method = mro_dbus_elements[override_attr_name]
        except KeyError:
            raise ValueError(
                f"No D-Bus method {override_attr_name!r} found "
                f"to override."
            )

        if not isinstance(original_dbus_method, DbusMethodAsync):
            raise TypeError(
                f"Expected {DbusMethodAsync!r} got {original_dbus_method!r} "
                f"under name {override_attr_name!r}"
            )

        new_method = copy(original_dbus_method)
        new_method.original_method = (
            override.override_method  # type: ignore[assignment]
        )
        return new_method

    @staticmethod
    def _process_dbus_property_override(
        override_attr_name: str,
        override: DbusPropertyOverride[T],
        mro_dbus_elements: dict[str, DbusMemberAsync],
    ) -> DbusPropertyAsync[Any]:
        try:
            original_property = mro_dbus_elements[override_attr_name]
        except KeyError:
            raise ValueError(
                f"No D-Bus property {override_attr_name!r} found "
                f"to override."
            )

        if not isinstance(original_property, DbusPropertyAsync):
            raise TypeError(
                f"Expected {DbusMethodAsync!r} got {original_property!r} "
                f"under name {override_attr_name!r}"
            )

        new_property = copy(original_property)
        new_property.property_getter = cast(
            Callable[[DbusInterfaceBaseAsync], Any],
            override.getter_override
        )
        if override.setter_override is not None:
            new_property.property_setter = override.setter_override
            new_property.property_setter_is_public = override.is_setter_public

        return new_property

    @classmethod
    def _check_collisions(
        cls,
        new_class_name: str,
        namespace: dict[str, Any],
        mro_dbus_elements: dict[str, DbusMemberAsync],
    ) -> None:

        possible_collisions = namespace.keys() & mro_dbus_elements.keys()
        new_overrides: dict[str, DbusMemberAsync] = {}

        for attr_name, attr in namespace.items():
            if isinstance(attr, DbusMethodOverride):
                new_overrides[attr_name] = cls._process_dbus_method_override(
                    attr_name,
                    attr,
                    mro_dbus_elements,
                )
                possible_collisions.remove(attr_name)
            elif isinstance(attr, DbusPropertyOverride):
                new_overrides[attr_name] = cls._process_dbus_property_override(
                    attr_name,
                    attr,
                    mro_dbus_elements,
                )
                possible_collisions.remove(attr_name)
            else:
                continue

        if possible_collisions:
            raise ValueError(
                f"Interface {new_class_name!r} redefines reserved "
                f"D-Bus attribute names: {possible_collisions!r}"
            )

        namespace.update(new_overrides)

    @staticmethod
    def _extract_dbus_elements(
        dbus_class: type,
        dbus_meta: DbusClassMeta,
    ) -> dict[str, DbusMemberAsync]:
        dbus_elements_map: dict[str, DbusMemberAsync] = {}

        for attr_name in dbus_meta.python_attr_to_dbus_member.keys():
            dbus_element = dbus_class.__dict__.get(attr_name)
            if not isinstance(dbus_element, DbusMemberAsync):
                raise TypeError(
                    f"Expected async D-Bus element, got {dbus_element!r} "
                    f"in class {dbus_class!r}"
                )

            dbus_elements_map[attr_name] = dbus_element

        return dbus_elements_map

    @classmethod
    def _map_mro_dbus_elements(
        cls,
        new_class_name: str,
        base_classes: Iterable[type],
    ) -> dict[str, DbusMemberAsync]:
        all_python_dbus_map: dict[str, DbusMemberAsync] = {}
        possible_collisions: set[str] = set()

        for c in base_classes:
            dbus_meta = DBUS_CLASS_TO_META.get(c)
            if dbus_meta is None:
                continue

            base_dbus_elements = cls._extract_dbus_elements(c, dbus_meta)

            possible_collisions.update(
                base_dbus_elements.keys() & all_python_dbus_map.keys()
            )

            all_python_dbus_map.update(
                base_dbus_elements
            )

        if possible_collisions:
            raise ValueError(
                f"Interface {new_class_name!r} has a reserved D-Bus "
                f"attribute name collision: {possible_collisions!r}"
            )

        return all_python_dbus_map

    @staticmethod
    def _map_dbus_elements(
        attr_name: str,
        attr: Any,
        meta: DbusClassMeta,
        interface_name: str,
    ) -> None:
        if not isinstance(attr, DbusMemberCommon):
            return

        if isinstance(attr, DbusMemberSync):
            raise TypeError(
                "Can't mix blocking methods in "
                f"async interface: {attr_name!r}"
            )

        if attr.interface_name != interface_name:
            return

        if isinstance(attr, DbusMethodAsync):
            meta.dbus_member_to_python_attr[attr.method_name] = attr_name
            meta.python_attr_to_dbus_member[attr_name] = attr.method_name
        elif isinstance(attr, DbusPropertyAsync):
            meta.dbus_member_to_python_attr[attr.property_name] = attr_name
            meta.python_attr_to_dbus_member[attr_name] = attr.property_name
        elif isinstance(attr, DbusSignalAsync):
            meta.dbus_member_to_python_attr[attr.signal_name] = attr_name
            meta.python_attr_to_dbus_member[attr_name] = attr.signal_name
        else:
            raise TypeError(f"Unknown D-Bus element: {attr!r}")

    def __new__(cls, name: str,
                bases: tuple[type, ...],
                namespace: dict[str, Any],
                interface_name: Optional[str] = None,
                serving_enabled: bool = True,
                ) -> DbusInterfaceMetaAsync:

        if interface_name in DBUS_INTERFACE_NAME_TO_CLASS:
            raise ValueError(
                f"D-Bus interface of the name {interface_name!r} was "
                "already created."
            )

        all_mro_bases: set[type[Any]] = set(
            chain.from_iterable(c.__mro__ for c in bases)
        )
        reserved_dbus_map = cls._map_mro_dbus_elements(
            name, all_mro_bases,
        )
        cls._check_collisions(name, namespace, reserved_dbus_map)

        new_cls = super().__new__(
            cls, name, bases, namespace,
            interface_name,
            serving_enabled,
        )

        if interface_name is not None:
            dbus_class_meta = DbusClassMeta(interface_name, serving_enabled)
            DBUS_CLASS_TO_META[new_cls] = dbus_class_meta
            DBUS_INTERFACE_NAME_TO_CLASS[interface_name] = new_cls

            for attr_name, attr in namespace.items():
                cls._map_dbus_elements(
                    attr_name,
                    attr,
                    dbus_class_meta,
                    interface_name,
                )

        return new_cls


class DbusInterfaceBaseAsync(metaclass=DbusInterfaceMetaAsync):

    def __init__(self) -> None:
        self._dbus: Union[
            DbusRemoteObjectMeta, DbusLocalObjectMeta] = DbusLocalObjectMeta()

    @classmethod
    def _dbus_iter_interfaces_meta(
        cls,
    ) -> Iterator[tuple[str, DbusClassMeta]]:

        for base in reversed(cls.__mro__):
            meta = DBUS_CLASS_TO_META.get(base)
            if meta is None:
                continue

            yield meta.interface_name, meta

    async def start_serving(self,
                            object_path: str,
                            bus: Optional[SdBus] = None,
                            ) -> None:

        warn("start_serving is deprecated in favor of export_to_dbus",
             DeprecationWarning)
        self.export_to_dbus(object_path, bus)

    def _dbus_on_no_members_exported(self) -> None:
        raise ValueError("No D-Bus interfaces were exported")

    def export_to_dbus(
        self,
        object_path: str,
        bus: Optional[SdBus] = None,
    ) -> DbusExportHandle:
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

        for interface_name, meta in self._dbus_iter_interfaces_meta():
            if not meta.serving_enabled:
                continue

            new_interface = SdBusInterface()

            for python_attr, dbus_member in (
                meta.python_attr_to_dbus_member.items()
            ):
                dbus_something = getattr(self, python_attr)
                if isinstance(dbus_something, DbusLocalMethodAsync):
                    new_interface.add_method(
                        dbus_something.dbus_method.method_name,
                        dbus_something.dbus_method.input_signature,
                        dbus_something.dbus_method.input_args_names,
                        dbus_something.dbus_method.result_signature,
                        dbus_something.dbus_method.result_args_names,
                        dbus_something.dbus_method.flags,
                        dbus_something._dbus_reply_call,
                    )
                elif isinstance(dbus_something, DbusLocalPropertyAsync):
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
                elif isinstance(dbus_something, DbusLocalSignalAsync):
                    new_interface.add_signal(
                        dbus_something.dbus_signal.signal_name,
                        dbus_something.dbus_signal.signal_signature,
                        dbus_something.dbus_signal.args_names,
                        dbus_something.dbus_signal.flags,
                    )
                else:
                    raise TypeError(
                        "Expected D-Bus element, got: {dbus_something!r}"
                    )

            bus.add_interface(new_interface, object_path, interface_name)
            local_object_meta.activated_interfaces.append(new_interface)

        if not local_object_meta.activated_interfaces:
            self._dbus_on_no_members_exported()

        return DbusExportHandle(local_object_meta)

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
        cls: type[Self],
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
        cls: type[Self],
        service_name: str,
        object_path: str,
        bus: Optional[SdBus] = None,
    ) -> Self:

        new_object = cls.__new__(cls)
        new_object._proxify(service_name, object_path, bus)
        return new_object


class DbusExportHandle:
    def __init__(self, local_meta: DbusLocalObjectMeta):
        self._tasks = local_meta.tasks
        self._dbus_slots: list[SdBusSlot] = [
            i.slot
            for i in local_meta.activated_interfaces
            if i.slot is not None
        ]

    async def __aenter__(self) -> DbusExportHandle:
        return self

    def __enter__(self) -> DbusExportHandle:
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any,
    ) -> None:
        self.stop()

    async def __aexit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any,
    ) -> None:
        self.stop()

    def stop(self) -> None:
        for task in self._tasks:
            task.cancel("D-Bus export stopped")

        for slot in self._dbus_slots:
            slot.close()
