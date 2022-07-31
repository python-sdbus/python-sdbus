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

from typing import Any, Dict, Optional, Set, Tuple, cast

from .dbus_common_elements import (
    DbusInterfaceMetaCommon,
    DbusSomethingAsync,
    DbusSomethingSync,
)
from .dbus_common_funcs import get_default_bus
from .dbus_proxy_sync_method import DbusMethodSync
from .dbus_proxy_sync_property import DbusPropertySync
from .sd_bus_internals import SdBus


class DbusInterfaceMetaSync(DbusInterfaceMetaCommon):
    def __new__(cls, name: str,
                bases: Tuple[type, ...],
                namespace: Dict[str, Any],
                interface_name: Optional[str] = None,
                serving_enabled: bool = True,
                ) -> DbusInterfaceMetaSync:

        dbus_served_interfaces_names = (
            {interface_name}
            if serving_enabled and interface_name is not None
            else set()
        )
        dbus_to_python_name_map: Dict[str, str] = {}
        declared_interfaces = set()
        # Set interface name
        for key, value in namespace.items():
            assert not isinstance(value, DbusSomethingAsync), (
                "Can't mix async methods in sync interface."
            )

            if isinstance(value, DbusSomethingSync):
                value.interface_name = interface_name
                value.serving_enabled = serving_enabled
                declared_interfaces.add(key)

            if isinstance(value, DbusMethodSync):
                dbus_to_python_name_map[value.method_name] = key
            elif isinstance(value, DbusPropertySync):
                dbus_to_python_name_map[value.property_name] = key

        super_declared_interfaces = set()
        for base in bases:
            if issubclass(base, DbusInterfaceBase):
                super_declared_interfaces.update(
                    base._dbus_declared_interfaces)

                dbus_to_python_name_map.update(
                    base._dbus_to_python_name_map
                )

        for key in super_declared_interfaces & namespace.keys():
            raise TypeError("Attempted to overload dbus definition"
                            " blocking interfaces do not support overloading")

        namespace['_dbus_served_interfaces_names'] = \
            dbus_served_interfaces_names
        namespace['_dbus_declared_interfaces'] = declared_interfaces
        namespace['_dbus_to_python_name_map'] = dbus_to_python_name_map

        new_cls = super().__new__(
            cls, name, bases, namespace,
            interface_name,
            serving_enabled,
        )

        return cast(DbusInterfaceMetaSync, new_cls)


class DbusInterfaceBase(metaclass=DbusInterfaceMetaSync):
    _dbus_declared_interfaces: Set[str]
    _dbus_serving_enabled: bool
    _dbus_to_python_name_map: Dict[str, str]
    _dbus_served_interfaces_names: Set[str]

    def __init__(
            self,
            service_name: str,
            object_path: str,
            bus: Optional[SdBus] = None, ) -> None:
        self._remote_service_name = service_name
        self._remote_object_path = object_path
        self._attached_bus: SdBus = (
            bus if bus is not None
            else get_default_bus())
