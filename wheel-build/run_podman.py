#!/usr/bin/python3
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
from tempfile import TemporaryDirectory
from subprocess import run


MANYLINUX_VERSION = 'manylinux2014_x86_64'


def run_podman(archive: Path) -> None:
    with TemporaryDirectory() as tmpdir:
        run(
            ['tar', '--extract',
             '--directory', tmpdir,
             '--file', str(archive)],
        ).check_returncode()
        run(
            ['podman', 'run',
             '--tty', '--interactive',
             '--volume', '.:/root',
             MANYLINUX_VERSION
             ],
            cwd=tmpdir,
        ).check_returncode()


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        '--archive',
        type=Path,
        required=True,
    )

    args = parser.parse_args()
    run_podman(args.archive)


if __name__ == '__main__':
    main()