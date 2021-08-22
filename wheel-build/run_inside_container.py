#!/opt/python/cp39-cp39/bin/python3
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

from os import environ, execl
from pathlib import Path
from shutil import copy
from subprocess import PIPE, CalledProcessError, run
from typing import List

yum_packages: List[str] = [
    'gettext-autopoint', 'gperf',
]

# env
# export PATH="/opt/python/cp39-cp39/bin:${PATH}"

# util-linux
# AL_OPTS="-I/usr/share/aclocal/" ./autogen.sh
# ./configure
#   --prefix '/usr/local' --libdir '/usr/local/lib64'
#   --enable-symvers
#   --with-pkgconfigdir '/usr/share/pkgconfig/'

# Ninja
# ./configure.py --boostrap
# cp ./ninja /usr/local/bin

# systemd
# export PKG_CONFIG_PATH="/usr/local/lib64/pkgconfig"
# meson setup build -Dstatic-libsystemd=pic

# PYTHON_SDBUS_USE_STATIC_LINK=1

ROOT_DIR = Path('/root')
NPROC = '4'
PYTHON_VERSIONS = ['cp39-cp39', 'cp38-cp38', 'cp37-cp37m']

BASIC_C_FLAGS: List[str] = [
    '-O2', '-fno-plt', '-D_FORTIFY_SOURCE=2',
    '-fstack-clash-protection',
]


def setup_env() -> None:
    python_bin_paths = (f"/opt/python/{x}/bin" for x in PYTHON_VERSIONS)

    environ['PATH'] = f"{':'.join(python_bin_paths)}:{environ['PATH']}"
    environ['PYTHON_SDBUS_USE_STATIC_LINK'] = '1'

    audit_wheel_arch = environ['AUDITWHEEL_ARCH']

    if audit_wheel_arch == 'x86_64':
        BASIC_C_FLAGS.extend(
            (
                '-march=x86-64', '-mtune=generic',
                '-fcf-protection',  # cf-protection only available on x86_64
            )
        )
    elif audit_wheel_arch == 'aarch64':
        BASIC_C_FLAGS.extend(('-march=armv8-a', '-mtune=generic'))
    else:
        print('PYTHON-SDBUS: Unknown arch')

    new_cflags = ' '.join(BASIC_C_FLAGS)
    environ['CFLAGS'] = new_cflags
    environ['CXXFLAGS'] = new_cflags

    nproc = run(
        ['nproc'],
        stdout=PIPE,
        text=True,
        check=True,
    )

    global NPROC
    NPROC = nproc.stdout.splitlines()[0]


def install_packages() -> None:
    run(
        ['yum', 'install', '--assumeyes'] + yum_packages,
        check=True,
    )


def install_ninja() -> None:
    ninja_src_path = ROOT_DIR / 'src_ninja'
    ninja_boot_strap_path = ninja_src_path / 'configure.py'

    run(
        [ninja_boot_strap_path, '--bootstrap'],
        cwd=ninja_src_path,
        check=True,
    )

    copy(ninja_src_path / 'ninja', '/usr/local/bin')


def install_meson() -> None:
    run(
        ['pip3', 'install', 'meson'],
        check=True,
    )


def install_util_linux() -> None:
    util_linux_src_path = ROOT_DIR / 'src_util_linux'

    run(
        [util_linux_src_path / 'autogen.sh'],
        cwd=util_linux_src_path,
        env={'AL_OPTS': '-I/usr/share/aclocal/', **environ},
        check=True,
    )

    run(
        [
            util_linux_src_path / 'configure',
            '--prefix', '/usr/local',
            '--libdir', '/usr/local/lib64',
            '--enable-symvers',
        ],
        cwd=util_linux_src_path,
        check=True,
    )

    run(
        ['make', '--jobs', NPROC, 'install'],
        cwd=util_linux_src_path,
        check=True,
    )


def install_libcap() -> None:
    libcap_src_path = ROOT_DIR / 'src_libcap'

    run(
        ['make', '--jobs', NPROC, 'install'],
        cwd=libcap_src_path,
        check=True,
    )


def install_systemd() -> None:
    systemd_src_path = ROOT_DIR / 'src_systemd'
    systemd_build_path = ROOT_DIR / 'build_systemd'

    run(
        ['meson', 'setup',
         systemd_build_path, systemd_src_path,
         '-Dstatic-libsystemd=pic',
         '--buildtype', 'plain',
         '-Db_lto=true', '-Db_pie=true',
         ],
        env={**environ, 'PKG_CONFIG_PATH': '/usr/local/lib64/pkgconfig'},
        check=True,
    )

    run(
        ['ninja', 'install'],
        cwd=systemd_build_path,
        check=True,
    )


def compile_extension() -> None:
    python_sdbus_src_path = ROOT_DIR / 'python-sdbus'
    setup_py_path = python_sdbus_src_path / 'setup.py'
    build_dir_path = python_sdbus_src_path / 'build'
    dist_dir_path = python_sdbus_src_path / 'dist'
    repaired_wheels_path = ROOT_DIR / 'wheels'

    run(
        [
            'python3.8', setup_py_path,
            'build', 'bdist_wheel',
            '--py-limited-api', 'cp37',
        ],
        cwd=python_sdbus_src_path,
        check=True,
        env={**environ, 'PYTHON_SDBUS_USE_LIMITED_API': '1'},
    )

    run(
        ['rm', '--recursive', build_dir_path],
        cwd=python_sdbus_src_path,
        check=True,
    )

    # Repair wheels
    for wheel in dist_dir_path.iterdir():
        run(
            [
                'auditwheel', 'repair',
                '--plat', environ['AUDITWHEEL_PLAT'],
                '--strip',
                '--wheel-dir', repaired_wheels_path,
                wheel,
            ],
            check=True,
        )


def drop_to_shell() -> None:
    execl('/bin/sh', '/bin/sh')


def main() -> None:
    setup_env()
    install_packages()

    install_ninja()
    install_meson()

    install_util_linux()
    install_libcap()
    install_systemd()

    compile_extension()


if __name__ == '__main__':
    try:
        main()
    except CalledProcessError:
        drop_to_shell()
