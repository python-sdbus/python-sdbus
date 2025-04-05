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

from ..dbus_common_funcs import _parse_properties_vardict
from ..dbus_proxy_async_interface_base import (
    DBUS_CLASS_TO_META,
    DBUS_INTERFACE_NAME_TO_CLASS,
    DbusInterfaceBaseAsync,
)
from ..dbus_proxy_sync_interface_base import DbusInterfaceBase

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any, Literal, Optional, Union

    from ..dbus_proxy_async_interfaces import DBUS_PROPERTIES_CHANGED_TYPING

    InterfacesBaseClasses = Union[DbusInterfaceBaseAsync, DbusInterfaceBase]
    InterfacesBaseTypes = type[InterfacesBaseClasses]
    InterfacesInputElements = Union[InterfacesBaseClasses, InterfacesBaseTypes]
    InterfacesInput = Union[
        InterfacesInputElements,
        Iterable[InterfacesInputElements],
    ]
    InterfacesToClassMap = dict[
        frozenset[str],
        InterfacesBaseTypes,
    ]
    OnUnknownMember = Literal['error', 'ignore', 'reuse']
    OnUnknownInterface = Literal['error', 'none']
    ParseGetManaged = dict[
        str,
        tuple[
            Optional[InterfacesBaseTypes],
            dict[str, Any],
        ],
    ]


def _interfaces_input_to_types(
    interfaces: InterfacesInput,
) -> tuple[InterfacesBaseTypes, ...]:
    if isinstance(
        interfaces,
        (DbusInterfaceBaseAsync, DbusInterfaceBase, type)
    ):
        return (
            interfaces if isinstance(interfaces, type) else type(interfaces),
        )
    else:
        return tuple(i if isinstance(i, type) else type(i) for i in interfaces)


def parse_properties_changed(
    interface: InterfacesInputElements,
    properties_changed_data: DBUS_PROPERTIES_CHANGED_TYPING,
    on_unknown_member: OnUnknownMember = 'error',
) -> dict[str, Any]:
    """Parse data from :py:meth:`properties_changed \
    <sdbus.DbusInterfaceCommonAsync.properties_changed>` signal.

    Parses changed properties from a single D-Bus object. The object's
    interface class must be known in advance and passed as a first
    argument.

    Member names will be translated to python defined names.
    Invalidated properties will have a value of None.

    :param interface:
        Takes either D-Bus interface class or its object.
    :param properties_changed_data:
        Tuple caught from signal.
    :param on_unknown_member:
        If an unknown D-Bus property was encountered either raise
        an ``"error"`` (default), ``"ignore"`` the property
        or ``"reuse"`` the D-Bus name for the member.
    :returns:
        Dictionary of changed properties with keys translated to python
        names. Invalidated properties will have value of None.
    """
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
    interfaces: tuple[InterfacesBaseTypes, ...],
) -> InterfacesToClassMap:

    interfaces_to_class_map: InterfacesToClassMap = {}

    for interface in interfaces:
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
    use_subset: bool,
) -> Optional[InterfacesBaseTypes]:
    class_set = frozenset(interface_names_iter) - SKIP_INTERFACES
    if use_subset:
        for interface_available in sorted(
            interfaces_to_class_map.keys(),
            key=len,
            reverse=True,
        ):
            if interface_available.issubset(class_set):
                class_set = interface_available
                break

    try:
        return interfaces_to_class_map[class_set]
    except KeyError:
        if raise_key_error:
            raise

        return None


def _get_member_map_from_class(
    python_class: Optional[InterfacesBaseTypes],
) -> dict[str, dict[str, str]]:
    if python_class is None:
        return {}
    else:
        return {
            interface_name: meta.dbus_member_to_python_attr
            for interface_name, meta in
            python_class._dbus_iter_interfaces_meta()
        }


def _translate_and_merge_members(
    properties_data: dict[str, dict[str, Any]],
    dbus_to_python_map: dict[str, dict[str, str]],
    on_unknown_member: OnUnknownMember,
) -> dict[str, Any]:
    python_properties: dict[str, Any] = {}
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
    interfaces_added_data: tuple[str, dict[str, dict[str, Any]]],
    on_unknown_interface: OnUnknownInterface = 'error',
    on_unknown_member: OnUnknownMember = 'error',
    *,
    use_interface_subsets: bool = False,
) -> tuple[str, Optional[InterfacesBaseTypes], dict[str, Any]]:
    """Parse data from :py:meth:`interfaces_added \
    <sdbus.DbusObjectManagerInterfaceAsync.interfaces_added>` signal.

    Takes the possible interface classes and the signal data.
    Returns the path of new object, the class of the
    added object (if it matched one of passed interface classes)
    and the dictionary of python named properties and their values.

    The passed interfaces can be async or blocking, the class
    or an instantiated object, a single item or an iterable of interfaces.

    :param interfaces:
        Possible interfaces that were added.
    :param interfaces_added_data:
        Tuple caught from signal.
    :param on_unknown_interface:
        If an unknown D-Bus interface was encountered either raise
        an ``"error"`` (default) or return ``"none"`` instead of
        interface class.
    :param on_unknown_member:
        If an unknown D-Bus property was encountered either raise
        an ``"error"`` (default), ``"ignore"`` the property
        or ``"reuse"`` the D-Bus name for the member.
    :param use_interface_subsets:
        Use the subset of interfaces as a valid match. For example,
        the class that implements ``org.example.foo`` would be matched
        with an data consising of both ``org.example.foo`` and
        ``org.example.bar``. The classes implementing more interfaces
        will have higher priority over the ones implementing fewer.
    :returns:
        Path of new added object, object's class (or ``None``) and dictionary
        of python translated members and their values.
    """
    interfaces_types = _interfaces_input_to_types(interfaces)
    interfaces_to_class_map = _create_interfaces_map(interfaces_types)

    path, properties_data = interfaces_added_data

    python_class = (
        _get_class_from_interfaces(
            interfaces_to_class_map,
            properties_data.keys(),
            on_unknown_interface == "error",
            use_interface_subsets,
        )
    )
    dbus_to_python_member_map = _get_member_map_from_class(python_class)
    python_properties: dict[str, Any] = {}
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
    interfaces_removed_data: tuple[str, list[str]],
    on_unknown_interface: OnUnknownInterface = 'error',
    *,
    use_interface_subsets: bool = False,
) -> tuple[str, Optional[InterfacesBaseTypes]]:
    """Parse data from :py:meth:`interfaces_added \
    <sdbus.DbusObjectManagerInterfaceAsync.interfaces_removed>` signal.

    Takes the possible interface classes and the signal data.
    Returns the path and the matched class of removed object.
    (if it matched one of passed interface classes)

    The passed interfaces can be async or blocking, the class
    or an instantiated object, a single item or an iterable of interfaces.

    :param interfaces:
        Possible interfaces that were removed.
    :param interfaces_added_data:
        Tuple caught from signal.
    :param on_unknown_member:
        If an unknown D-Bus interface was encountered either raise an
        ``"error"`` (default) or return ``"none"`` instead of interface class.
    :param use_interface_subsets:
        Use the subset of interfaces as a valid match. For example,
        the class that implements ``org.example.foo`` would be matched
        with an data consising of both ``org.example.foo`` and
        ``org.example.bar``. The classes implementing more interfaces
        will have higher priority over the ones implementing fewer.
    :returns:
        Path of removed object and object's class (or ``None``).
    """
    interfaces_types = _interfaces_input_to_types(interfaces)
    interfaces_to_class_map = _create_interfaces_map(interfaces_types)

    path, interfaces_removed = interfaces_removed_data

    python_class = (
        _get_class_from_interfaces(
            interfaces_to_class_map,
            interfaces_removed,
            on_unknown_interface == "error",
            use_interface_subsets,
        )
    )

    return path, python_class


def parse_get_managed_objects(
    interfaces: InterfacesInput,
    managed_objects_data: dict[str, dict[str, dict[str, Any]]],
    on_unknown_interface: OnUnknownInterface = 'error',
    on_unknown_member: OnUnknownMember = 'error',
    *,
    use_interface_subsets: bool = False,
) -> ParseGetManaged:
    """Parse data from :py:meth:`get_managed_objects \
    <sdbus.DbusObjectManagerInterfaceAsync.get_managed_objects>` call.

    Takes the possible interface classes and the method's returned data.
    Returns a dictionary where keys a paths of the managed objects and
    value is a tuple of class of the object and dictionary of its python
    named properties and their values.

    The passed interfaces can be async or blocking, the class
    or an instantiated object, a single item or an iterable of interfaces.

    :param interfaces:
        Possible interfaces of the managed objects.
    :param managed_objects_data:
        Data returned by ``get_managed_objects`` call.
    :param on_unknown_interface:
        If an unknown D-Bus interface was encountered either raise an
        ``"error"`` (default) or return ``"none"`` instead of interface class.
    :param on_unknown_member:
        If an unknown D-Bus property was encountered either raise
        an ``"error"`` (default), ``"ignore"`` the property
        or ``"reuse"`` the D-Bus name for the member.
    :param use_interface_subsets:
        Use the subset of interfaces as a valid match. For example,
        the class that implements ``org.example.foo`` would be matched
        with an data consising of both ``org.example.foo`` and
        ``org.example.bar``. The classes implementing more interfaces
        will have higher priority over the ones implementing fewer.
    :returns:
        Dictionary where keys are paths and values are tuples of managed
        objects classes and their properties data.

    *New in version 0.12.0.*
    """
    interfaces_types = _interfaces_input_to_types(interfaces)
    interfaces_to_class_map = _create_interfaces_map(interfaces_types)

    managed_objects_map: ParseGetManaged = {}

    for path, properties_data in managed_objects_data.items():
        python_class = (
            _get_class_from_interfaces(
                interfaces_to_class_map,
                properties_data.keys(),
                on_unknown_interface == "error",
                use_interface_subsets,
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
