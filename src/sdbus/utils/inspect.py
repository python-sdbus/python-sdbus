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
from ..dbus_proxy_async_interface_base import DbusInterfaceBaseAsync
from ..dbus_proxy_sync_interface_base import DbusInterfaceBase
from ..default_bus import get_default_bus

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
    """Return the D-Bus path of an object.

    If called on a D-Bus proxy returns path of the proxied object.

    If called on a local D-Bus object returns the exported D-Bus path.
    If object is not exported raises ``LookupError``.

    If called on an object that is unrelated to D-Bus raises ``TypeError``.

    The object's path is inspected in the context of the given bus and if the
    object is attached to a different bus the ``LookupError`` will be raised.
    If the bus argument is not given or is ``None`` the default bus will be
    checked against.

    :param obj:
        Object to inspect.
    :param bus:
        Bus to inspect against.
        If not given or is ``None`` the default bus will be used.
    :returns:
        D-Bus path of the object.

    *New in version 0.13.0.*
    """
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
