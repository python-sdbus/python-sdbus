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
from subprocess import run, PIPE
from argparse import ArgumentParser
from pathlib import Path
from shutil import copy


def copy_git_ls_files(source_root: Path, build_root: Path) -> None:
    git_ls = run(
        ['git', 'ls-files'],
        stdout=PIPE,
        cwd=source_root.resolve(),
        text=True,
    )

    git_ls.check_returncode()

    for file_relative_source_str in git_ls.stdout.splitlines():
        orig_file_path = source_root / file_relative_source_str
        copy_file_path = build_root / "python-sdbus" / file_relative_source_str
        if not orig_file_path.exists():
            raise ValueError('Path does not exist', orig_file_path)

        if orig_file_path.is_dir():
            continue
        else:
            copy_file_path.parent.mkdir(parents=True, exist_ok=True)
            copy(orig_file_path, copy_file_path.parent)


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        '--build-dir',
        type=Path,
        required=True,
    )
    parser.add_argument(
        '--output-file',
        type=Path,
        required=True,
    )
    parser.add_argument(
        '--source-root',
        type=Path,
        required=True,
    )
    args = parser.parse_args()

    build_dir = args.build_dir
    output_file = args.output_file
    source_root = args.source_root

    copy_git_ls_files(source_root, build_dir)


if __name__ == '__main__':
    main()
