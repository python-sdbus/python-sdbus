# Copyright (C) 2020  igo95862

# This file is part of py_sd_bus

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

from typing import Any, Dict, List, Optional, Tuple

from ..dbus_proxy import (DbusInterfaceCommon, DbusSignal, dbus_method,
                          dbus_property_async, dbus_signal, get_bus)
from ..sd_bus_internals import SdBus


class FreedesktopDbus(DbusInterfaceCommon,
                      interface_name='org.freedesktop.DBus'):

    def __init__(self, bus: Optional[SdBus] = None):
        super().__init__()
        self.bus: SdBus = bus if bus is not None else get_bus()
        self._connect(
            self.bus,
            'org.freedesktop.DBus',
            '/org/freedesktop/DBus'
        )

    @dbus_method()
    async def get_id(self) -> str:
        raise NotImplementedError

    @dbus_property_async('as')
    async def features(self) -> List[str]:
        raise NotImplementedError

    name_acquired: DbusSignal[str] = DbusSignal('NameAcquired')
    name_lost: DbusSignal[str] = DbusSignal('NameLost')
    name_owner_changed: DbusSignal[Tuple[str, str, str]] = \
        DbusSignal('NameOwnerChanged')


class NotificationsInterface(DbusInterfaceCommon,
                             interface_name='org.freedesktop.Notifications'
                             ):

    @dbus_method('u')
    async def close_notification(self, notif_id: int) -> None:
        raise NotImplementedError

    @dbus_method()
    async def get_capabilities(self) -> List[str]:
        raise NotImplementedError

    @dbus_method()
    async def get_server_infomation(self) -> Tuple[str, str, str, str]:
        raise NotImplementedError

    @dbus_method("susssasa{sv}i")
    async def notify(
            self,
            app_name: str,
            replaces_id: int,
            app_icon: str,
            summary: str,
            body: str,
            actions: List[str],
            hints: Dict[str, Tuple[str, Any]],
            expire_timeout: int, ) -> int:

        raise NotImplementedError

    @dbus_signal()
    def action_invoked(self) -> Tuple[int, int]:
        raise NotImplementedError

    @dbus_signal()
    def notification_closed(self) -> Tuple[int, int]:
        raise NotImplementedError


class FreedesktopNotifications(NotificationsInterface):
    def __init__(self, bus: Optional[SdBus] = None) -> None:
        super().__init__()
        self.bus: SdBus = bus if bus is not None else get_bus()
        self._connect(
            self.bus,
            'org.freedesktop.Notifications',
            '/org/freedesktop/Notifications'
        )
