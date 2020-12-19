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

from typing import Optional, List

from ..dbus_proxy import (DbusInterfaceCommon, dbus_method,
                          get_bus, dbus_property)
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

    @dbus_property(property_signature='as')
    async def features(self) -> List[str]:
        raise NotImplementedError
