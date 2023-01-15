# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2023 igo95862

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

from typing import Any, Dict, Literal, Type, Union

from .dbus_common_funcs import _parse_properties_vardict
from .dbus_proxy_async_interface_base import DbusInterfaceBaseAsync
from .dbus_proxy_async_interfaces import DBUS_PROPERTIES_CHANGED_TYPING


def parse_properties_changed(
        interface: Union[DbusInterfaceBaseAsync, Type[DbusInterfaceBaseAsync]],
        properties_changed_data: DBUS_PROPERTIES_CHANGED_TYPING,
        on_unknown_member: Literal['error', 'ignore', 'reuse'] = 'error',
) -> Dict[str, Any]:
    changed_properties_data = properties_changed_data[1]

    for invalidated_property in properties_changed_data[2]:
        changed_properties_data[invalidated_property] = ('0', None)

    return _parse_properties_vardict(
        interface._dbus_to_python_name_map,
        properties_changed_data[1],
        on_unknown_member,
    )


__all__ = (
    'parse_properties_changed',
)
