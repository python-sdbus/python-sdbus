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

from typing import (
    Any,
    Dict,
    FrozenSet,
    Iterable,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    Union,
)

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


SKIP_INTERFACES = frozenset((
    'org.freedesktop.DBus.Properties',
    'org.freedesktop.DBus.Introspectable',
    'org.freedesktop.DBus.Peer',
    'org.freedesktop.DBus.ObjectManager',
))


def _create_interfaces_map(
    interfaces_iter: Iterable[
        Union[
            DbusInterfaceBaseAsync,
            Type[DbusInterfaceBaseAsync],
        ]
    ]
) -> Dict[FrozenSet[str], Type[DbusInterfaceBaseAsync]]:
    interfaces_to_class_map: Dict[
        FrozenSet[str],
        Type[DbusInterfaceBaseAsync],
    ] = {}

    for interface in interfaces_iter:
        if (
            isinstance(interface, DbusInterfaceBaseAsync)
        ):
            interfaces_to_class_map[
                frozenset(interface._dbus_served_interfaces_names)
            ] = type(interface)
        elif (
                isinstance(interface, type)
                and
                issubclass(interface, DbusInterfaceBaseAsync)
        ):
            interfaces_to_class_map[
                frozenset(interface._dbus_served_interfaces_names)
            ] = interface
        else:
            raise TypeError('Expected D-Bus interface, got: ', interface)

    return interfaces_to_class_map


def parse_interfaces_added(
    interfaces: Union[
        Union[
            DbusInterfaceBaseAsync,
            Type[DbusInterfaceBaseAsync],
        ],
        Iterable[
            Union[
                DbusInterfaceBaseAsync,
                Type[DbusInterfaceBaseAsync],
            ],
        ],
    ],
    interfaces_added_data: Tuple[str, Dict[str, Dict[str, Any]]],
    on_unknown_interface: Literal['error', 'none'] = 'error',
    on_unknown_member: Literal['error', 'ignore', 'reuse'] = 'error',
) -> Tuple[str, Optional[Type[DbusInterfaceBaseAsync]], Dict[str, Any]]:

    if isinstance(interfaces,
                  (DbusInterfaceBaseAsync, type)):
        interfaces_iter = iter((interfaces, ))
    else:
        interfaces_iter = iter(interfaces)

    interfaces_to_class_map = _create_interfaces_map(interfaces_iter)

    path, properties_data = interfaces_added_data

    class_set = frozenset(properties_data.keys()) - SKIP_INTERFACES
    try:
        python_class = interfaces_to_class_map[class_set]
        dbus_to_python_member_map = python_class._dbus_to_python_name_map
    except KeyError:
        if on_unknown_interface == 'error':
            raise

        python_class = None
        dbus_to_python_member_map = {}

    python_properties: Dict[str, Any] = {}
    for _, properties in properties_data.items():
        python_properties.update(
            _parse_properties_vardict(
                dbus_to_python_member_map,
                properties,
                on_unknown_member,
            )
        )

    return path, python_class, python_properties


def parse_interfaces_removed(
    interfaces: Union[
        Union[
            DbusInterfaceBaseAsync,
            Type[DbusInterfaceBaseAsync],
        ],
        Iterable[
            Union[
                DbusInterfaceBaseAsync,
                Type[DbusInterfaceBaseAsync],
            ],
        ],
    ],
    interfaces_removed_data: Tuple[str, List[str]],
    on_unknown_interface: Literal['error', 'none'] = 'error',
) -> Tuple[str, Optional[Type[DbusInterfaceBaseAsync]]]:
    if isinstance(interfaces,
                  (DbusInterfaceBaseAsync, type)):
        interfaces_iter = iter((interfaces, ))
    else:
        interfaces_iter = iter(interfaces)

    interfaces_to_class_map = _create_interfaces_map(interfaces_iter)

    path, interfaces_removed = interfaces_removed_data

    class_set = frozenset(interfaces_removed) - SKIP_INTERFACES
    try:
        python_class = interfaces_to_class_map[class_set]
    except KeyError:
        if on_unknown_interface == 'error':
            raise

        python_class = None

    return path, python_class


__all__ = (
    'parse_properties_changed',
    'parse_interfaces_added',
)
