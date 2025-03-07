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

from argparse import SUPPRESS, Action, ArgumentParser
from dataclasses import dataclass, field
from pathlib import Path
from sys import stdout
from typing import TYPE_CHECKING

from .interface_generator import (
    generate_py_file,
    interfaces_from_file,
    interfaces_from_str,
)

if TYPE_CHECKING:
    from typing import Optional

    from .interface_generator import DbusInterfaceIntrospection


@dataclass
class RenameMember:
    new_name: Optional[str] = None
    current_arg: Optional[str] = None
    arg_renames: dict[str, str] = field(default_factory=dict)


@dataclass
class RenameInterface:
    new_name: Optional[str] = None
    current_member: Optional[RenameMember] = None
    methods: dict[str, RenameMember] = field(default_factory=dict)
    properties: dict[str, RenameMember] = field(default_factory=dict)
    signals: dict[str, RenameMember] = field(default_factory=dict)


@dataclass
class RenameRoot:
    current_interface: Optional[RenameInterface] = None
    interfaces: dict[str, RenameInterface] = field(default_factory=dict)


rename_root = RenameRoot()


# def rename_args(member_rename):
#     ...


def rename_members(
    interface: DbusInterfaceIntrospection,
    interface_rename: RenameInterface,
) -> None:
    for m_member in interface.methods:
        m_rename = interface_rename.methods.get(m_member.method_name)
        if m_rename is None:
            continue

        if m_rename.new_name is not None:
            m_member.python_name = m_rename.new_name

    for p_member in interface.properties:
        p_rename = interface_rename.properties.get(p_member.method_name)
        if p_rename is None:
            continue

        if p_rename.new_name is not None:
            p_member.python_name = p_rename.new_name

    for s_member in interface.signals:
        s_rename = interface_rename.signals.get(s_member.method_name)
        if s_rename is None:
            continue

        if s_rename.new_name is not None:
            s_member.python_name = s_rename.new_name


def rename_interfaces(
    interfaces: list[DbusInterfaceIntrospection]
) -> None:
    for interface in interfaces:
        dbus_interface_name = interface.interface_name
        this_interface_rename = rename_root.interfaces.get(dbus_interface_name)
        if this_interface_rename is None:
            continue

        if this_interface_rename.new_name is not None:
            interface.python_name = this_interface_rename.new_name

        rename_members(interface, this_interface_rename)


def run_gen_from_connection(
    connection_name: str,
    object_paths: list[str],
    system: bool,
    imports_header: bool,
    do_async: bool,
) -> None:
    connection_name = connection_name
    object_paths = object_paths

    from .dbus_proxy_sync_interfaces import DbusInterfaceCommon

    if system:
        from .default_bus import set_default_bus
        from .sd_bus_internals import sd_bus_open_system
        set_default_bus(sd_bus_open_system())

    interfaces: list[DbusInterfaceIntrospection] = []
    for object_path in object_paths:
        connection = DbusInterfaceCommon(connection_name, object_path)
        itrospection = connection.dbus_introspect()
        interfaces.extend(interfaces_from_str(itrospection))

    rename_interfaces(interfaces)

    stdout.write(
        generate_py_file(
            interfaces,
            imports_header,
            do_async,
        )
    )


def run_gen_from_file(
    filenames: list[str],
    imports_header: bool,
    do_async: bool,
) -> None:
    interfaces: list[DbusInterfaceIntrospection] = []

    for file in filenames:
        interfaces.extend(interfaces_from_file(file))

    rename_interfaces(interfaces)

    stdout.write(
        generate_py_file(
            interfaces,
            imports_header,
            do_async,
        )
    )


class ActionSelectInterface(Action):
    def __call__(
        self,
        parser: ArgumentParser,
        namespace: object,
        values: object,
        option_string: Optional[str] = None,
    ) -> None:
        if not isinstance(values, str):
            raise TypeError(
                f"Expected --select-interface to be string, got {values!r}"
            )

        interface_rename = rename_root.interfaces.get(values)

        if interface_rename is None:
            interface_rename = RenameInterface()
            rename_root.interfaces[values] = interface_rename

        rename_root.current_interface = interface_rename


class ActionSelectMethod(Action):
    def __call__(
        self,
        parser: ArgumentParser,
        namespace: object,
        values: object,
        option_string: Optional[str] = None,
    ) -> None:
        if not isinstance(values, str):
            raise TypeError(
                f"Expected --select-method to be string, got {values!r}"
            )

        current_interface = rename_root.current_interface
        if current_interface is None:
            raise ValueError(
                "No D-Bus interface selected. "
                "Use --select-interface option."
            )

        method_rename = current_interface.methods.get(values)

        if method_rename is None:
            method_rename = RenameMember()
            current_interface.methods[values] = method_rename

        current_interface.current_member = method_rename


class ActionSelectProperty(Action):
    def __call__(
        self,
        parser: ArgumentParser,
        namespace: object,
        values: object,
        option_string: Optional[str] = None,
    ) -> None:
        if not isinstance(values, str):
            raise TypeError(
                f"Expected --select-property to be string, got {values!r}"
            )

        current_interface = rename_root.current_interface
        if current_interface is None:
            raise ValueError(
                "No D-Bus interface selected. "
                "Use --select-interface option."
            )

        property_rename = current_interface.properties.get(values)

        if property_rename is None:
            property_rename = RenameMember()
            current_interface.properties[values] = property_rename

        current_interface.current_member = property_rename


class ActionSelectSignal(Action):
    def __call__(
        self,
        parser: ArgumentParser,
        namespace: object,
        values: object,
        option_string: Optional[str] = None,
    ) -> None:
        if not isinstance(values, str):
            raise TypeError(
                f"Expected --select-signal to be string, got {values!r}"
            )

        current_interface = rename_root.current_interface
        if current_interface is None:
            raise ValueError(
                "No D-Bus interface selected. "
                "Use --select-interface option."
            )

        signal_rename = current_interface.signals.get(values)

        if signal_rename is None:
            signal_rename = RenameMember()
            current_interface.signals[values] = signal_rename

        current_interface.current_member = signal_rename


class ActionSetName(Action):
    def __call__(
        self,
        parser: ArgumentParser,
        namespace: object,
        values: object,
        option_string: Optional[str] = None,
    ) -> None:
        if not isinstance(values, str):
            raise TypeError(
                f"Expected --set-name to be string, got {values!r}"
            )

        current_interface = rename_root.current_interface
        current_member = (
            current_interface.current_member
            if current_interface is not None
            else None
        )

        if current_member is not None:
            current_member.new_name = values
            return

        if current_interface is not None:
            current_interface.new_name = values
            return

        raise ValueError(
            "No D-Bus element to rename. "
            "Use --select-* options to select element."
        )


def generator_main(args: Optional[list[str]] = None) -> None:

    main_arg_parser = ArgumentParser(
        prog="sdbus",
    )
    subparsers = main_arg_parser.add_subparsers(
        required=True,
        title="subcommands",
    )

    generate_from_file_parser = subparsers.add_parser('gen-from-file')
    generate_from_file_parser.set_defaults(func=run_gen_from_file)

    generate_from_connection = subparsers.add_parser('gen-from-connection')
    generate_from_connection.set_defaults(func=run_gen_from_connection)

    # Common options
    for subparser in (generate_from_file_parser, generate_from_connection):
        subparser.add_argument(
            "--no-imports-header", action="store_false",
            dest="imports_header",
            help="Do NOT include 'import' header",
        )
        subparser.add_argument(
            "--imports-header", action="store_true", default=True,
            dest="imports_header",
            help="Include 'import' header (default)",
        )

        subparser.add_argument(
            "--async", action="store_true", default=True,
            dest="do_async",
            help="Generate async interfaces (default)",
        )
        subparser.add_argument(
            "--block", action="store_false",
            dest="do_async",
            help="Generate blocking interfaces",
        )
        subparser.add_argument(
            "--select-interface",
            action=ActionSelectInterface,
            default=SUPPRESS,
            help="Select D-Bus interface to adjust"
        )
        subparser.add_argument(
            "--select-method",
            action=ActionSelectMethod,
            default=SUPPRESS,
            help="Select D-Bus method to adjust"
        )
        subparser.add_argument(
            "--select-property",
            action=ActionSelectProperty,
            default=SUPPRESS,
            help="Select D-Bus property to adjust"
        )
        subparser.add_argument(
            "--select-signal",
            action=ActionSelectSignal,
            default=SUPPRESS,
            help="Select D-Bus signal to adjust"
        )
        subparser.add_argument(
            "--set-name",
            action=ActionSetName,
            default=SUPPRESS,
            help="Select D-Bus interface to adjust"
        )

    generate_from_file_parser.add_argument(
        'filenames', type=Path, nargs='+',
        help="Paths to interface XML introspection files"
    )

    generate_from_connection.add_argument(
        'connection_name',
        help=(
            'Name of the service connection to extract introspection. '
            "For example, 'org.freedesktop.systemd1' for systemd."
        )
    )
    generate_from_connection.add_argument(
        'object_paths',
        nargs='+',
        help=(
            'Object paths that the introspection will be extracted. '
            'One or more.'
        )
    )
    generate_from_connection.add_argument(
        '--system',
        help='Use system D-Bus instead of session.',
        action='store_true',
    )

    args_dict = vars(main_arg_parser.parse_args(args))
    func = args_dict.pop("func")
    func(**args_dict)


if __name__ == "__main__":
    generator_main()
