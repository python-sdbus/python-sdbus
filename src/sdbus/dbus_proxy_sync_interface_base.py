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

from itertools import chain
from typing import TYPE_CHECKING
from weakref import WeakKeyDictionary, WeakValueDictionary

from .dbus_common_elements import (
    DbusClassMeta,
    DbusInterfaceMetaCommon,
    DbusRemoteObjectMeta,
    DbusSomethingAsync,
    DbusSomethingCommon,
)
from .dbus_proxy_sync_method import DbusMethodSync
from .dbus_proxy_sync_property import DbusPropertySync

if TYPE_CHECKING:
    from typing import (
        Any,
        Dict,
        Iterable,
        Iterator,
        Optional,
        Set,
        Tuple,
        Type,
    )

    from .sd_bus_internals import SdBus


DBUS_CLASS_TO_META: WeakKeyDictionary[
    type, DbusClassMeta] = WeakKeyDictionary()
DBUS_INTERFACE_NAME_TO_CLASS: WeakValueDictionary[
    str, DbusInterfaceMetaSync] = WeakValueDictionary()


class DbusInterfaceMetaSync(DbusInterfaceMetaCommon):

    @staticmethod
    def _check_collisions(
        new_class_name: str,
        attr_names: Set[str],
        reserved_attr_names: Set[str],
    ) -> None:

        possible_collisions = attr_names & reserved_attr_names
        if possible_collisions:
            raise ValueError(
                f"Interface {new_class_name!r} redefines reserved "
                f"D-Bus attribute names: {possible_collisions!r}"
            )

    @staticmethod
    def _collect_dbus_to_python_attr_names(
        new_class_name: str,
        base_classes: Iterable[type],
    ) -> Set[str]:
        all_python_dbus_attrs: Set[str] = set()
        possible_collisions: Set[str] = set()

        for c in base_classes:
            dbus_meta = DBUS_CLASS_TO_META.get(c)
            if dbus_meta is None:
                continue

            base_python_dbus_attrs = set(
                dbus_meta.python_attr_to_dbus_member.keys()
            )

            possible_collisions.update(
                base_python_dbus_attrs & all_python_dbus_attrs
            )

            all_python_dbus_attrs.update(
                base_python_dbus_attrs
            )

        if possible_collisions:
            raise ValueError(
                f"Interface {new_class_name!r} has a reserved D-Bus "
                f"attribute name collision: {possible_collisions!r}"
            )

        return all_python_dbus_attrs

    @staticmethod
    def _map_dbus_elements(
        attr_name: str,
        attr: Any,
        meta: DbusClassMeta,
    ) -> None:
        if not isinstance(attr, DbusSomethingCommon):
            return

        if isinstance(attr, DbusSomethingAsync):
            raise TypeError(
                f"Can't mix async methods in sync interface: {attr_name!r}"
            )

        if isinstance(attr, DbusMethodSync):
            meta.dbus_member_to_python_attr[attr.method_name] = attr_name
            meta.python_attr_to_dbus_member[attr_name] = attr.method_name
        elif isinstance(attr, DbusPropertySync):
            meta.dbus_member_to_python_attr[attr.property_name] = attr_name
            meta.python_attr_to_dbus_member[attr_name] = attr.property_name
        else:
            raise TypeError(f"Unknown D-Bus element: {attr!r}")

    def __new__(cls, name: str,
                bases: Tuple[type, ...],
                namespace: Dict[str, Any],
                interface_name: Optional[str] = None,
                serving_enabled: bool = True,
                ) -> DbusInterfaceMetaSync:

        if interface_name in DBUS_INTERFACE_NAME_TO_CLASS:
            raise ValueError(
                f"D-Bus interface of the name {interface_name!r} was "
                "already created."
            )

        all_mro_bases: Set[Type[Any]] = set(
            chain.from_iterable((c.__mro__ for c in bases))
        )
        reserved_attr_names = cls._collect_dbus_to_python_attr_names(
            name, all_mro_bases,
        )
        cls._check_collisions(name, set(namespace.keys()), reserved_attr_names)

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
                cls._map_dbus_elements(attr_name, attr, dbus_class_meta)

        return new_cls


class DbusInterfaceBase(metaclass=DbusInterfaceMetaSync):

    def __init__(
        self,
        service_name: str,
        object_path: str,
        bus: Optional[SdBus] = None,
    ):
        self._dbus = DbusRemoteObjectMeta(service_name, object_path, bus)

    @classmethod
    def _dbus_iter_interfaces_meta(
        cls,
    ) -> Iterator[Tuple[str, DbusClassMeta]]:

        for base in cls.__mro__:
            meta = DBUS_CLASS_TO_META.get(base)
            if meta is None:
                continue

            yield meta.interface_name, meta
