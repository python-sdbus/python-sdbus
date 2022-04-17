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
from subprocess import PIPE, run
from tempfile import TemporaryDirectory

SYSTEMD_VERSION = '249.11'
UTIL_LINUX_VERSION = '2.37'
NINJA_VERSION = '1.10.2'
LIBCAP_VERSION = '2.63'


def create_archive(build_root: Path, output_file: Path) -> None:
    run(
        ['tar', '--create', '--file', str(output_file.absolute()), '.'],
        cwd=build_root.resolve(),
        check=True,
    )


def download_and_unpack_source(target_dir: Path, url: str) -> None:
    target_dir.mkdir(exist_ok=True)  # TODO: maybe delete folder

    with TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        dowload_tar_path = tmpdir_path / 'donwload.tar.gz'

        run(
            ['curl', '--fail', '--location',
             url, '--output', str(dowload_tar_path)],
            check=True,
        )

        run(
            ['tar',
             '--directory', str(target_dir),
             '--strip-components=1',
             '--extract', '--file', str(dowload_tar_path)],
            check=True,
        )


def download_systemd_source(build_dir: Path) -> None:
    systemd_download_url = (
        "https://github.com/systemd/systemd-stable/"
        f"archive/refs/tags/v{SYSTEMD_VERSION}.tar.gz"
    )
    systemd_src_dir = build_dir / "src_systemd"
    systemd_src_dir.mkdir(exist_ok=True)

    util_linux_url = (
        "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/"
        f"v{UTIL_LINUX_VERSION}/util-linux-{UTIL_LINUX_VERSION}.tar.xz"
    )
    util_linux_src_dir = build_dir / "src_util_linux"

    ninja_src_url = (
        "https://github.com/ninja-build/ninja/"
        f"archive/refs/tags/v{NINJA_VERSION}.tar.gz"
    )
    ninja_src_dir = build_dir / "src_ninja"

    libcap_src_url = (
        "https://kernel.org/pub/linux/libs/security/"
        f"linux-privs/libcap2/libcap-{LIBCAP_VERSION}.tar.xz"
    )
    libcap_src_dir = build_dir / 'src_libcap'

    download_and_unpack_source(systemd_src_dir, systemd_download_url)
    download_and_unpack_source(util_linux_src_dir, util_linux_url)
    download_and_unpack_source(ninja_src_dir, ninja_src_url)
    download_and_unpack_source(libcap_src_dir, libcap_src_url)


def copy_git_ls_files(source_root: Path, build_root: Path) -> None:
    git_ls = run(
        ['git', 'ls-files'],
        stdout=PIPE,
        cwd=source_root.resolve(),
        text=True,
        check=True,
    )

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
    download_systemd_source(build_dir)

    create_archive(build_dir, output_file)


if __name__ == '__main__':
    main()
