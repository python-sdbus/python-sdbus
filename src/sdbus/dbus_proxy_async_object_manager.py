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

from functools import partial
from typing import TYPE_CHECKING

from .dbus_common_elements import DbusLocalObjectMeta
from .dbus_common_funcs import get_default_bus
from .dbus_proxy_async_interface_base import (
    DbusExportHandle,
    DbusInterfaceBaseAsync,
)
from .dbus_proxy_async_interfaces import DbusInterfaceCommonAsync
from .dbus_proxy_async_method import dbus_method_async
from .dbus_proxy_async_signal import dbus_signal_async

if TYPE_CHECKING:
    from typing import Any, Callable, Dict, List, Optional, Tuple

    from .sd_bus_internals import SdBus, SdBusSlot


class DbusObjectManagerExportHandle(DbusExportHandle):
    def __init__(
        self,
        local_meta: DbusLocalObjectMeta,
        remove_object_call: Callable[[], None],
    ):
        super().__init__(local_meta)
        self.remove_object_call = remove_object_call

    def stop(self) -> None:
        super().stop()
        self.remove_object_call()


class DbusObjectManagerInterfaceAsync(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.DBus.ObjectManager',
    serving_enabled=False,
):
    def __init__(self) -> None:
        super().__init__()
        self._object_manager_slot: Optional[SdBusSlot] = None
        self._managed_object_to_path: Dict[DbusInterfaceBaseAsync, str] = {}

    @dbus_method_async(result_signature='a{oa{sa{sv}}}')
    async def get_managed_objects(
            self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        raise NotImplementedError

    @dbus_signal_async('oa{sa{sv}}')
    def interfaces_added(self) -> Tuple[str, Dict[str, Dict[str, Any]]]:
        raise NotImplementedError

    @dbus_signal_async('oao')
    def interfaces_removed(self) -> Tuple[str, List[str]]:
        raise NotImplementedError

    def export_to_dbus(
        self,
        object_path: str,
        bus: Optional[SdBus] = None,
    ) -> DbusExportHandle:
        if bus is None:
            bus = get_default_bus()

        export_handle = super().export_to_dbus(
            object_path,
            bus,
        )
        slot = bus.add_object_manager(object_path)
        self._object_manager_slot = slot
        export_handle._dbus_slots.append(slot)
        return export_handle

    def export_with_manager(
        self,
        object_path: str,
        object_to_export: DbusInterfaceBaseAsync,
        bus: Optional[SdBus] = None,
    ) -> DbusObjectManagerExportHandle:
        if self._object_manager_slot is None:
            raise RuntimeError('ObjectManager not intitialized')

        if bus is None:
            bus = get_default_bus()

        object_to_export.export_to_dbus(
            object_path,
            bus,
        )
        meta = object_to_export._dbus
        if not isinstance(meta, DbusLocalObjectMeta):
            raise TypeError
        handle = DbusObjectManagerExportHandle(
            meta,
            partial(self.remove_managed_object, object_to_export),
        )
        bus.emit_object_added(object_path)
        self._managed_object_to_path[object_to_export] = object_path

        return handle

    def remove_managed_object(
            self,
            managed_object: DbusInterfaceBaseAsync) -> None:
        if self._dbus.attached_bus is None:
            raise RuntimeError('Object manager not exported')

        removed_path = self._managed_object_to_path.pop(managed_object)
        self._dbus.attached_bus.emit_object_removed(removed_path)
