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
from shutil import copy
from subprocess import run
from tempfile import TemporaryDirectory

MANYLINUX_VERSION = 'manylinux2014'


def run_podman(
        archive: Path,
        source_root: Path,
        arch: str,) -> None:
    wheels_root = source_root / 'dist'

    with TemporaryDirectory() as tmpdir:
        run(
            ['tar', '--extract',
             '--directory', tmpdir,
             '--file', str(archive)],
        ).check_returncode()
        run(
            ['podman', 'run',
             '--arch', arch,
             '--tty', '--interactive',
             '--volume', '.:/root',
             f"quay.io/pypa/{MANYLINUX_VERSION}_{arch}",
             '/root/python-sdbus/wheel-build/run_inside_container.py',
             ],
            cwd=tmpdir,
        ).check_returncode()

        wheels_root.mkdir(exist_ok=True)
        for wheel in (Path(tmpdir) / 'wheels').iterdir():
            copy(wheel, wheels_root)


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        '--archive',
        type=Path,
        required=True,
    )
    parser.add_argument(
        '--source-root',
        type=Path,
        required=True,
    )
    parser.add_argument(
        '--arch',
        type=str,
        choices=['x86_64', 'aarch64'],
        default='x86_64',
    )

    args = parser.parse_args()
    run_podman(
        args.archive,
        args.source_root,
        args.arch,
    )


if __name__ == '__main__':
    main()
