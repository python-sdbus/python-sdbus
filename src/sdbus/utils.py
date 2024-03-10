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

from typing import TYPE_CHECKING

from .dbus_common_funcs import _parse_properties_vardict
from .dbus_proxy_async_interface_base import (
    DBUS_CLASS_TO_META,
    DBUS_INTERFACE_NAME_TO_CLASS,
    DbusInterfaceBaseAsync,
)

if TYPE_CHECKING:
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

    from .dbus_proxy_async_interfaces import DBUS_PROPERTIES_CHANGED_TYPING

    InterfacesInputElements = Union[
        DbusInterfaceBaseAsync,
        Type[DbusInterfaceBaseAsync],
    ]
    InterfacesInput = Union[
        InterfacesInputElements,
        Iterable[InterfacesInputElements],
    ]
    InterfacesToClassMap = Dict[FrozenSet[str], Type[DbusInterfaceBaseAsync]]
    OnUnknownMember = Literal['error', 'ignore', 'reuse']
    OnUnknownInterface = Literal['error', 'none']
    ParseGetManaged = Dict[
        str,
        Tuple[Optional[Type[DbusInterfaceBaseAsync]], Dict[str, Any]],
    ]


def parse_properties_changed(
        interface: InterfacesInputElements,
        properties_changed_data: DBUS_PROPERTIES_CHANGED_TYPING,
        on_unknown_member: OnUnknownMember = 'error',
) -> Dict[str, Any]:
    interface_name, changed_properties, invalidated_properties = (
        properties_changed_data
    )

    meta = DBUS_CLASS_TO_META[DBUS_INTERFACE_NAME_TO_CLASS[interface_name]]

    for invalidated_property in invalidated_properties:
        changed_properties[invalidated_property] = ('0', None)

    return _parse_properties_vardict(
        meta.dbus_member_to_python_attr,
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
    interfaces: InterfacesInput,
) -> InterfacesToClassMap:

    if isinstance(interfaces,
                  (DbusInterfaceBaseAsync, type)):
        interfaces_iter = iter((interfaces, ))
    else:
        interfaces_iter = iter(interfaces)

    interfaces_to_class_map: InterfacesToClassMap = {}

    for interface in interfaces_iter:
        interface_names_set = frozenset(
            interface_name for interface_name, _ in
            interface._dbus_iter_interfaces_meta()
            if interface_name not in SKIP_INTERFACES
        )
        interfaces_to_class_map[interface_names_set] = (
            interface if isinstance(interface, type)
            else type(interface)
        )

    return interfaces_to_class_map


def _get_class_from_interfaces(
    interfaces_to_class_map: InterfacesToClassMap,
    interface_names_iter: Iterable[str],
    raise_key_error: bool,
) -> Optional[Type[DbusInterfaceBaseAsync]]:
    class_set = frozenset(interface_names_iter) - SKIP_INTERFACES
    try:
        return interfaces_to_class_map[class_set]
    except KeyError:
        if raise_key_error:
            raise

        return None


def _get_member_map_from_class(
    python_class: Optional[Type[DbusInterfaceBaseAsync]],
) -> Dict[str, Dict[str, str]]:
    if python_class is None:
        return {}
    else:
        return {
            interface_name: meta.dbus_member_to_python_attr
            for interface_name, meta in
            python_class._dbus_iter_interfaces_meta()
        }


def _translate_and_merge_members(
    properties_data: Dict[str, Dict[str, Any]],
    dbus_to_python_map: Dict[str, Dict[str, str]],
    on_unknown_member: OnUnknownMember,
) -> Dict[str, Any]:
    python_properties: Dict[str, Any] = {}
    for interface_name, properties in properties_data.items():
        interface_member_map = dbus_to_python_map.get(
            interface_name, {},
        )
        python_properties.update(
            _parse_properties_vardict(
                interface_member_map,
                properties,
                on_unknown_member,
            )
        )

    return python_properties


def parse_interfaces_added(
    interfaces: InterfacesInput,
    interfaces_added_data: Tuple[str, Dict[str, Dict[str, Any]]],
    on_unknown_interface: OnUnknownInterface = 'error',
    on_unknown_member: OnUnknownMember = 'error',
) -> Tuple[str, Optional[Type[DbusInterfaceBaseAsync]], Dict[str, Any]]:

    interfaces_to_class_map = _create_interfaces_map(interfaces)

    path, properties_data = interfaces_added_data

    python_class = (
        _get_class_from_interfaces(
            interfaces_to_class_map,
            properties_data.keys(),
            on_unknown_interface == "error",
        )
    )
    dbus_to_python_member_map = _get_member_map_from_class(python_class)
    python_properties: Dict[str, Any] = {}
    for interface_name, properties in properties_data.items():
        interface_member_map = dbus_to_python_member_map.get(
            interface_name, {},
        )
        python_properties.update(
            _parse_properties_vardict(
                interface_member_map,
                properties,
                on_unknown_member,
            )
        )

    return (
        path,
        python_class,
        _translate_and_merge_members(
            properties_data,
            dbus_to_python_member_map,
            on_unknown_member,
        ),
    )


def parse_interfaces_removed(
    interfaces: InterfacesInput,
    interfaces_removed_data: Tuple[str, List[str]],
    on_unknown_interface: OnUnknownInterface = 'error',
) -> Tuple[str, Optional[Type[DbusInterfaceBaseAsync]]]:

    interfaces_to_class_map = _create_interfaces_map(interfaces)

    path, interfaces_removed = interfaces_removed_data

    python_class = (
        _get_class_from_interfaces(
            interfaces_to_class_map,
            interfaces_removed,
            on_unknown_interface == "error",
        )
    )

    return path, python_class


def parse_get_managed_objects(
    interfaces: InterfacesInput,
    managed_objects_data: Dict[str, Dict[str, Dict[str, Any]]],
    on_unknown_interface: OnUnknownInterface = 'error',
    on_unknown_member: OnUnknownMember = 'error',
) -> ParseGetManaged:

    interfaces_to_class_map = _create_interfaces_map(interfaces)

    managed_objects_map: ParseGetManaged = {}

    for path, properties_data in managed_objects_data.items():
        python_class = (
            _get_class_from_interfaces(
                interfaces_to_class_map,
                properties_data.keys(),
                on_unknown_interface == "error",
            )
        )
        dbus_to_python_member_map = _get_member_map_from_class(python_class)

        managed_objects_map[path] = (
            python_class,
            _translate_and_merge_members(
                properties_data,
                dbus_to_python_member_map,
                on_unknown_member,
            ),
        )

    return managed_objects_map


__all__ = (
    'parse_properties_changed',
    'parse_interfaces_added',
    'parse_interfaces_removed',
    'parse_get_managed_objects',
)
