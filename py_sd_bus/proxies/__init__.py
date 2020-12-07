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

from typing import List, Optional

from ..dbus_proxy import DbusInterfaceCommon, dbus_property
from ..sd_bus_internals import SdBus


class FreedesktopDbus(DbusInterfaceCommon,
                      interface_name='org.freedesktop.DBus'):

    @classmethod
    def connect_to_dbus(cls, bus: Optional[SdBus] = None,) -> FreedesktopDbus:
        new_connection = cls.connect(
            service_name='org.freedesktop.DBus',
            object_path='/org/freedesktop/DBus',
            bus=bus,
        )
        assert isinstance(new_connection, FreedesktopDbus)
        return new_connection

    @dbus_property()
    async def features(self) -> List[str]:
        raise NotImplementedError
