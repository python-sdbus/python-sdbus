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

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List

from .interface_generator import (
    DbusInterfaceIntrospection,
    generate_async_py_file,
    interfaces_from_file,
)


def run_gen_from_file(namespace: Namespace) -> None:
    interfaces: List[DbusInterfaceIntrospection] = []

    for file in namespace.filenames:
        interfaces.extend(interfaces_from_file(file))

    print(
        generate_async_py_file(
            interfaces, namespace.no_imports_header))


def generator_main() -> None:

    main_arg_parser = ArgumentParser()
    subparsers = main_arg_parser.add_subparsers()

    generate_from_file_parser = subparsers.add_parser('gen-from-file')
    generate_from_file_parser.set_defaults(func=run_gen_from_file)

    generate_from_file_parser.add_argument(
        'filenames', type=Path, nargs='+')

    generate_from_file_parser.add_argument(
        '--no-imports-header', action='store_false', default=True,
        help="Do NOT include 'import' header",
    )

    args = main_arg_parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    generator_main()
