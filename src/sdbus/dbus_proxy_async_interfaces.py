# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2020-2024 igo95862

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

from .dbus_common_funcs import _parse_properties_vardict
from .dbus_proxy_async_interface_base import DbusInterfaceBaseAsync
from .dbus_proxy_async_method import dbus_method_async
from .dbus_proxy_async_signal import dbus_signal_async

if TYPE_CHECKING:
    from typing import Any, Dict, List, Literal, Tuple

    DBUS_PROPERTIES_CHANGED_TYPING = (
        Tuple[
            str,
            Dict[str, Tuple[str, Any]],
            List[str],
        ]
    )


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
    def properties_changed(self) -> DBUS_PROPERTIES_CHANGED_TYPING:
        raise NotImplementedError

    @dbus_method_async('s', 'a{sv}', method_name='GetAll')
    async def _properties_get_all(
            self, interface_name: str) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError

    async def properties_get_all_dict(
            self,
            on_unknown_member: Literal['error', 'ignore', 'reuse'] = 'error',
    ) -> Dict[str, Any]:

        properties: Dict[str, Any] = {}

        for interface_name, meta in self._dbus_iter_interfaces_meta():
            if not meta.serving_enabled:
                continue

            dbus_properties_data = await self._properties_get_all(
                interface_name)

            properties.update(
                _parse_properties_vardict(
                    meta.dbus_member_to_python_attr,
                    dbus_properties_data,
                    on_unknown_member,
                )
            )

        return properties


class DbusInterfaceCommonAsync(
        DbusPeerInterfaceAsync, DbusPropertiesInterfaceAsync,
        DbusIntrospectableAsync):
    ...
