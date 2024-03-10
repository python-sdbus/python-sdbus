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

from typing import TYPE_CHECKING

from .dbus_proxy_sync_interface_base import DbusInterfaceBase
from .dbus_proxy_sync_method import dbus_method

if TYPE_CHECKING:
    from typing import Any, Dict, Literal, Tuple


class DbusPeerInterface(
    DbusInterfaceBase,
    interface_name='org.freedesktop.DBus.Peer',
    serving_enabled=False,
):

    @dbus_method(method_name='Ping')
    def dbus_ping(self) -> None:
        raise NotImplementedError

    @dbus_method(method_name='GetMachineId')
    def dbus_machine_id(self) -> str:
        raise NotImplementedError


class DbusIntrospectable(
    DbusInterfaceBase,
    interface_name='org.freedesktop.DBus.Introspectable',
    serving_enabled=False,
):

    @dbus_method(method_name='Introspect')
    def dbus_introspect(self) -> str:
        raise NotImplementedError


class DbusPropertiesInterface(
    DbusInterfaceBase,
    interface_name='org.freedesktop.DBus.Properties',
    serving_enabled=False,
):
    @dbus_method('s', 'a{sv}', method_name='GetAll')
    def _properties_get_all(
            self, interface_name: str) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError

    def properties_get_all_dict(
            self,
            on_unknown_member: Literal['error', 'ignore', 'reuse'] = 'error',
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        for interface_name, meta in self._dbus_iter_interfaces_meta():
            if not meta.serving_enabled:
                continue

            dbus_properties_data = self._properties_get_all(interface_name)
            for member_name, variant in dbus_properties_data.items():
                try:
                    python_name = meta.dbus_member_to_python_attr[member_name]
                except KeyError:
                    if on_unknown_member == 'error':
                        raise
                    elif on_unknown_member == 'ignore':
                        continue
                    elif on_unknown_member == 'reuse':
                        python_name = member_name
                    else:
                        raise ValueError

                properties[python_name] = variant[1]

        return properties


class DbusInterfaceCommon(
        DbusPeerInterface,
        DbusIntrospectable,
        DbusPropertiesInterface):
    ...


class DbusObjectManagerInterface(
    DbusInterfaceCommon,
    interface_name='org.freedesktop.DBus.ObjectManager',
    serving_enabled=False,
):
    @dbus_method(result_signature='a{oa{sa{sv}}}')
    def get_managed_objects(
            self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        raise NotImplementedError
