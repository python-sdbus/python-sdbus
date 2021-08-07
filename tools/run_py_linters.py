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

from os import environ
from pathlib import Path
from subprocess import run
from argparse import ArgumentParser


source_root = Path(environ['MESON_SOURCE_ROOT'])
build_dir = Path(environ['MESON_BUILD_ROOT'])

tools_dir = source_root / 'tools'
src_dir = source_root / 'src'
test_dir = source_root / 'test'
wheel_build_dir = source_root / 'wheel-build'

all_python_dirs = [src_dir, tools_dir, test_dir, wheel_build_dir]

mypy_cache_dir = build_dir / '.mypy_cache'


def run_mypy(path: Path) -> None:
    print(f"Running mypy on {path}")
    run(
        args=(
            'mypy', '--strict',
            '--cache-dir', mypy_cache_dir,
            '--python-version', '3.8',
            '--namespace-packages',
            path,
        ),
        check=True,
        env={'MYPYPATH': str(src_dir.absolute()), **environ},
    )


def linter_main() -> None:
    run(
        args=('flake8', *all_python_dirs),
        check=True,
    )

    for x in [tools_dir, test_dir, wheel_build_dir,
              src_dir / 'sdbus', src_dir / 'sdbus_block',
              src_dir / 'sdbus_async']:
        run_mypy(x)


def formater_main() -> None:
    ...


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        'mode',
        choices=('lint', 'format'),
    )

    args = parser.parse_args()

    mode = args.mode

    if mode == 'lint':
        linter_main()
    elif mode == 'format':
        formater_main()
    else:
        raise ValueError('Unknown mode', mode)


if __name__ == '__main__':
    main()
