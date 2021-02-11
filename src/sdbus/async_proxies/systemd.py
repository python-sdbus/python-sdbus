# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2020, 2021 igo95862

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

from typing import Any, AsyncGenerator, List, Literal, Optional, Tuple

from .._proxies_common import (SystemdActiveState, SystemdUnitListTuple,
                               SystemdUnitStartModes, SystemdUnitStopModes)
from ..dbus_proxy_async import (DbusInterfaceCommonAsync, dbus_method_async,
                                dbus_property_async, dbus_signal_async)
from ..sd_bus_internals import SdBus, encode_object_path


class SystemdManager(
        DbusInterfaceCommonAsync,
        interface_name='org.freedesktop.systemd1.Manager'):

    def __init__(self, bus: Optional[SdBus] = None):
        super().__init__()
        self._connect(
            'org.freedesktop.systemd1',
            '/org/freedesktop/systemd1',
            bus,
        )

    @dbus_method_async()
    async def list_units(self) -> List[
            Tuple[str, str, str, str, str, str, str, int, str, str]]:

        raise NotImplementedError

    async def list_units_named(self
                               ) -> AsyncGenerator[SystemdUnitListTuple, None]:
        for x in await self.list_units():
            yield SystemdUnitListTuple(*x)

    @dbus_method_async()
    async def subscribe(self) -> None:
        raise NotImplementedError

    @dbus_method_async()
    async def unsubscribe(self) -> None:
        raise NotImplementedError

    @dbus_property_async()
    def version(self) -> str:
        raise NotImplementedError

    @dbus_signal_async()
    def unit_new(self) -> Tuple[str, str]:
        raise NotImplementedError

    @dbus_signal_async()
    def unit_removed(self) -> Tuple[str, str]:
        raise NotImplementedError


class SystemdUnit(
        DbusInterfaceCommonAsync,
        interface_name='org.freedesktop.systemd1.Unit'):

    def __init__(self, unit_name: str, bus: Optional[SdBus] = None):
        super().__init__()
        self._connect(
            'org.freedesktop.systemd1',
            encode_object_path('/org/freedesktop/systemd1/unit', unit_name),
            bus,
        )

    @dbus_method_async()
    async def freeze(self) -> None:
        raise NotImplementedError

    @dbus_method_async()
    async def thaw(self) -> None:
        raise NotImplementedError

    @dbus_method_async('si')
    async def kill(
            self,
            kill_who: Literal['main', 'controll', 'all'],
            signal: int,) -> None:
        raise NotImplementedError

    @dbus_method_async('s')
    async def reload(
            self, mode: SystemdUnitStartModes) -> str:
        raise NotImplementedError

    @dbus_method_async('s')
    async def reload_or_restart(
            self, mode: SystemdUnitStartModes) -> str:

        raise NotImplementedError

    @dbus_method_async('s')
    async def reload_or_try_restart(
            self, mode: SystemdUnitStartModes) -> str:

        raise NotImplementedError

    @dbus_method_async()
    async def reset_failed(self) -> None:
        raise NotImplementedError

    @dbus_method_async('s')
    async def restart(
            self, mode: SystemdUnitStartModes) -> str:
        raise NotImplementedError

    @dbus_method_async('ba(sv)')
    async def set_properties(
            self,
            is_runtime: bool,
            properties: List[Tuple[str, Tuple[str, Any]]]) -> None:
        raise NotImplementedError

    @dbus_method_async('s')
    async def start(self, mode: SystemdUnitStartModes) -> str:
        raise NotImplementedError

    @dbus_method_async('s')
    async def stop(self, mode: SystemdUnitStopModes) -> str:
        raise NotImplementedError

    @dbus_method_async('s')
    async def try_restart(self, mode: SystemdUnitStartModes) -> str:
        raise NotImplementedError

    @dbus_property_async()
    def active_state(self) -> SystemdActiveState:
        raise NotImplementedError

    @dbus_property_async()
    def sub_state(self) -> str:
        raise NotImplementedError


__all__ = ('SystemdManager', 'SystemdUnitListTuple', 'SystemdUnit')
