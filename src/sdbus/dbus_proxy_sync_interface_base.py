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

from typing import TYPE_CHECKING, cast

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
    from typing import Any, ClassVar, Dict, Optional, Tuple

    from .sd_bus_internals import SdBus


class DbusInterfaceMetaSync(DbusInterfaceMetaCommon):
    def __new__(cls, name: str,
                bases: Tuple[type, ...],
                namespace: Dict[str, Any],
                interface_name: Optional[str] = None,
                serving_enabled: bool = True,
                ) -> DbusInterfaceMetaSync:

        dbus_class_meta = DbusClassMeta()
        if interface_name is not None:
            dbus_class_meta.dbus_interfaces_names.add(interface_name)

        for attr_name, attr in namespace.items():
            if not isinstance(attr, DbusSomethingCommon):
                continue

            if isinstance(attr, DbusSomethingAsync):
                raise TypeError(
                    f"Can't mix async methods in sync interface: {attr_name!r}"
                )

            if isinstance(attr, DbusMethodSync):
                dbus_class_meta.dbus_member_to_python_attr[
                    attr.method_name] = attr_name
                dbus_class_meta.python_attr_to_dbus_member[
                    attr_name] = attr.method_name
            elif isinstance(attr, DbusPropertySync):
                dbus_class_meta.dbus_member_to_python_attr[
                    attr.property_name] = attr_name
                dbus_class_meta.python_attr_to_dbus_member[
                    attr_name] = attr.property_name
            else:
                raise TypeError(f"Unknown D-Bus element: {attr!r}")

        for base in bases:
            if not issubclass(base, DbusInterfaceBase):
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

            if python_attr_collision := (
                namespace.keys()
                & base._dbus_meta.python_attr_to_dbus_member.keys()
            ):
                raise TypeError(
                    f"Interface {name!r} and {base!r} have Python attribute "
                    f"collision: {python_attr_collision}"
                )
            else:
                dbus_class_meta.python_attr_to_dbus_member.update(
                    base._dbus_meta.python_attr_to_dbus_member
                )

        namespace['_dbus_meta'] = dbus_class_meta
        new_cls = super().__new__(
            cls, name, bases, namespace,
            interface_name,
            serving_enabled,
        )

        return cast(DbusInterfaceMetaSync, new_cls)


class DbusInterfaceBase(metaclass=DbusInterfaceMetaSync):
    _dbus_meta: ClassVar[DbusClassMeta]

    def __init__(
        self,
        service_name: str,
        object_path: str,
        bus: Optional[SdBus] = None,
    ):
        self._dbus = DbusRemoteObjectMeta(service_name, object_path, bus)
