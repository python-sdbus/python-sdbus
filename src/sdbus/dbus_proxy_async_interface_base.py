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
from itertools import chain
from types import MethodType
from typing import TYPE_CHECKING, Any, Callable, Protocol, cast
from warnings import warn
from weakref import WeakKeyDictionary, WeakValueDictionary

from .dbus_common_elements import (
    DbusClassMeta,
    DbusInterfaceMetaCommon,
    DbusLocalMemberAsync,
    DbusLocalObjectMeta,
    DbusMemberAsync,
    DbusMemberCommon,
    DbusMemberSync,
    DbusMethodOverride,
    DbusPropertyOverride,
    DbusRemoteObjectMeta,
)
from .dbus_common_funcs import get_default_bus
from .dbus_proxy_async_method import DbusMethodAsync
from .dbus_proxy_async_property import DbusPropertyAsync
from .sd_bus_internals import SdBusInterface

if TYPE_CHECKING:
    from typing import (
        Dict,
        Iterable,
        Iterator,
        List,
        Optional,
        Set,
        Tuple,
        Type,
        TypeVar,
        Union,
    )

    from .sd_bus_internals import SdBus

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
        mro_dbus_elements: Dict[str, DbusMemberAsync],
    ) -> DbusMethodAsync:
        try:
            original_method = mro_dbus_elements[override_attr_name]
        except KeyError:
            raise ValueError(
                f"No D-Bus method {override_attr_name!r} found "
                f"to override."
            )

        if not isinstance(original_method, DbusMethodAsync):
            raise TypeError(
                f"Expected {DbusMethodAsync!r} got {original_method!r} "
                f"under name {override_attr_name!r}"
            )

        new_method = copy(original_method)
        new_method.original_method = cast(MethodType, override.override_method)
        return new_method

    @staticmethod
    def _process_dbus_property_override(
        override_attr_name: str,
        override: DbusPropertyOverride[T],
        mro_dbus_elements: Dict[str, DbusMemberAsync],
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
        namespace: Dict[str, Any],
        mro_dbus_elements: Dict[str, DbusMemberAsync],
    ) -> None:

        possible_collisions = namespace.keys() & mro_dbus_elements.keys()
        new_overrides: Dict[str, DbusMemberAsync] = {}

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
    ) -> Dict[str, DbusMemberAsync]:
        dbus_elements_map: Dict[str, DbusMemberAsync] = {}

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
    ) -> Dict[str, DbusMemberAsync]:
        all_python_dbus_map: Dict[str, DbusMemberAsync] = {}
        possible_collisions: Set[str] = set()

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

        if isinstance(attr, DbusMemberAsync):
            meta.dbus_member_to_python_attr[attr.member_name] = attr_name
            meta.python_attr_to_dbus_member[attr_name] = attr.member_name
        else:
            raise TypeError(f"Unknown D-Bus element: {attr!r}")

    def __new__(cls, name: str,
                bases: Tuple[type, ...],
                namespace: Dict[str, Any],
                interface_name: Optional[str] = None,
                serving_enabled: bool = True,
                ) -> DbusInterfaceMetaAsync:

        if interface_name in DBUS_INTERFACE_NAME_TO_CLASS:
            raise ValueError(
                f"D-Bus interface of the name {interface_name!r} was "
                "already created."
            )

        all_mro_bases: Set[Type[Any]] = set(
            chain.from_iterable((c.__mro__ for c in bases))
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
    ) -> Iterator[Tuple[str, DbusClassMeta]]:

        for base in cls.__mro__:
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
        # TODO: can be optimized with a single loop
        interface_map: Dict[str, List[DbusLocalMemberAsync]] = {}

        for key, value in getmembers(self):
            assert not isinstance(value, DbusMemberAsync)

            if isinstance(value, DbusLocalMemberAsync) and \
                    value.member.serving_enabled:
                interface_name = value.member.interface_name
            else:
                continue

            try:
                interface_member_list = interface_map[interface_name]
            except KeyError:
                interface_member_list = []
                interface_map[interface_name] = interface_member_list

            interface_member_list.append(value)

        export_handle = DbusExportHandle()

        for interface_name, member_list in interface_map.items():
            new_interface = SdBusInterface()
            for dbus_something in member_list:
                dbus_something._append_to_interface(new_interface,
                                                    export_handle)
            bus.add_interface(new_interface, object_path,
                              interface_name)
            local_object_meta.activated_interfaces.append(new_interface)

            assert new_interface.slot is not None
            export_handle.append(new_interface.slot)

        return export_handle

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


class Closeable(Protocol):
    def close(self) -> None:
        ...


class DbusExportHandle:
    def __init__(self, *items: Closeable) -> None:
        self._items = list(items)

    def append(self, item: Closeable) -> None:
        self._items.append(item)

    def close(self) -> None:
        while self._items:
            self._items.pop().close()

    stop = close  # for backwards compatibility

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
        self.close()

    async def __aexit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any,
    ) -> None:
        self.close()
