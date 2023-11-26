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

from argparse import ArgumentParser
from pathlib import Path
from sys import stdout
from typing import TYPE_CHECKING

from .interface_generator import (
    generate_py_file,
    interfaces_from_file,
    interfaces_from_str,
)

if TYPE_CHECKING:
    from typing import List, Optional

    from .interface_generator import DbusInterfaceIntrospection


def run_gen_from_connection(
    connection_name: str,
    object_paths: List[str],
    system: bool,
    imports_header: bool,
    do_async: bool,
) -> None:
    connection_name = connection_name
    object_paths = object_paths

    from .dbus_proxy_sync_interfaces import DbusInterfaceCommon

    if system:
        from .dbus_common_funcs import set_default_bus
        from .sd_bus_internals import sd_bus_open_system
        set_default_bus(sd_bus_open_system())

    interfaces: List[DbusInterfaceIntrospection] = []
    for object_path in object_paths:
        connection = DbusInterfaceCommon(connection_name, object_path)
        itrospection = connection.dbus_introspect()
        interfaces.extend(interfaces_from_str(itrospection))

    stdout.write(
        generate_py_file(
            interfaces,
            imports_header,
            do_async,
        )
    )


def run_gen_from_file(
    filenames: List[str],
    imports_header: bool,
    do_async: bool,
) -> None:
    interfaces: List[DbusInterfaceIntrospection] = []

    for file in filenames:
        interfaces.extend(interfaces_from_file(file))

    stdout.write(
        generate_py_file(
            interfaces,
            imports_header,
            do_async,
        )
    )


def generator_main(args: Optional[List[str]] = None) -> None:

    main_arg_parser = ArgumentParser()
    subparsers = main_arg_parser.add_subparsers()

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
