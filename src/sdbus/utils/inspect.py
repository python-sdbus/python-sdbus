# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2024 igo95862

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

from ..dbus_common_elements import DbusLocalObjectMeta, DbusRemoteObjectMeta
from ..dbus_common_funcs import get_default_bus
from ..dbus_proxy_async_interface_base import DbusInterfaceBaseAsync
from ..dbus_proxy_sync_interface_base import DbusInterfaceBase

if TYPE_CHECKING:
    from typing import Optional, Union

    from ..sd_bus_internals import SdBus


def _inspect_dbus_path_proxy(
    obj: object,
    dbus_meta: DbusRemoteObjectMeta,
    bus: SdBus,
) -> str:
    if bus != dbus_meta.attached_bus:
        raise LookupError(
            f"D-Bus proxy {obj!r} at {dbus_meta.object_path!r} path "
            f"is not attached to bus {bus!r}"
        )

    return dbus_meta.object_path


def _inspect_dbus_path_local(
    obj: object,
    dbus_meta: DbusLocalObjectMeta,
    bus: SdBus,
) -> str:
    attached_bus = dbus_meta.attached_bus
    object_path = dbus_meta.serving_object_path
    if attached_bus is None or object_path is None:
        raise LookupError(
            f"Local D-Bus object {obj!r} is not exported to any D-Bus"
        )

    if bus != attached_bus:
        raise LookupError(
            f"Local D-Bus object {obj!r} at {dbus_meta.serving_object_path!r} "
            f"path is not attached to bus {bus!r}"
        )

    return object_path


def inspect_dbus_path(
    obj: Union[DbusInterfaceBase, DbusInterfaceBaseAsync],
    bus: Optional[SdBus] = None,
) -> str:
    if bus is None:
        bus = get_default_bus()

    if isinstance(obj, DbusInterfaceBase):
        return _inspect_dbus_path_proxy(obj, obj._dbus, bus)
    elif isinstance(obj, DbusInterfaceBaseAsync):
        dbus_meta = obj._dbus
        if isinstance(dbus_meta, DbusRemoteObjectMeta):
            return _inspect_dbus_path_proxy(obj, dbus_meta, bus)
        else:
            return _inspect_dbus_path_local(obj, dbus_meta, bus)
    else:
        raise TypeError(f"Expected D-Bus object got {obj!r}")


__all__ = (
    "inspect_dbus_path",
)
