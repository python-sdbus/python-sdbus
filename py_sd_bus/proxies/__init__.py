# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2020, 2021 igo95862

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

from ..dbus_proxy_sync import DbusInterfaceCommon, dbus_method, dbus_property
from ..sd_bus_internals import SdBus


class FreedesktopDbus(DbusInterfaceCommon,
                      interface_name='org.freedesktop.DBus'):

    def __init__(self, bus: Optional[SdBus] = None):
        super().__init__(
            'org.freedesktop.DBus',
            '/org/freedesktop/DBus',
            bus,
        )

    @dbus_method()
    def get_id(self) -> str:
        raise NotImplementedError

    @dbus_property()
    def features(self) -> List[str]:
        raise NotImplementedError


class FreedesktopNotifications(DbusInterfaceCommon,
                               interface_name='org.freedesktop.Notifications'
                               ):
    def __init__(self, bus: Optional[SdBus] = None) -> None:
        super().__init__(
            'org.freedesktop.Notifications',
            '/org/freedesktop/Notifications',
            bus,
        )

    @dbus_method('u')
    def close_notification(self, notif_id: int) -> None:
        raise NotImplementedError

    @dbus_method()
    def get_capabilities(self) -> List[str]:
        raise NotImplementedError

    @dbus_method()
    def get_server_infomation(self) -> Tuple[str, str, str, str]:
        raise NotImplementedError

    @dbus_method('susssasa{sv}i')
    def notify(
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
