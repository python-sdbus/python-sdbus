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
from subprocess import DEVNULL, PIPE, CalledProcessError
from subprocess import run as subprocess_run
from typing import List, Optional, Tuple

from setuptools import Extension, setup

with open('./README.md') as f:
    long_description = f.read()

c_macros: List[Tuple[str, Optional[str]]] = []


def get_libsystemd_version() -> Tuple[int, int, int]:
    process = subprocess_run(
        args=('ldconfig', '-f', '/dev/null', '-C', '/dev/null',
              '-v', '-N', '-X'),
        stderr=DEVNULL,
        stdout=PIPE,
    )

    try:
        process.check_returncode()
    except CalledProcessError:
        return 0, 0, 0

    result_str = process.stdout.decode('utf-8')

    for line in result_str.splitlines():
        if 'libsystemd.so' in line:
            version_str = line.split('libsystemd.so')[-1]
            semver_strs = version_str.split('.')
            return (
                int(semver_strs[1]),
                int(semver_strs[2]),
                int(semver_strs[3]),
            )

    return 0, 0, 0


if not environ.get('PYTHON_SDBUS_USE_IGNORE_SYSTEMD_VERSION'):
    LIBSYSTEMD_MAJOR, LIBSYSTEMD_MINOR, LIBSYTEMD_PATCH \
        = get_libsystemd_version()

    if LIBSYSTEMD_MAJOR <= 0 and LIBSYSTEMD_MINOR < 29:
        c_macros.append(('LIBSYSTEMD_NO_VALIDATION_FUNCS', None))

link_arguments: List[str] = ['-lsystemd']

if environ.get('PYTHON_SDBUS_USE_STATIC_LINK'):
    # Link statically against libsystemd and libcap
    link_arguments = ['-Wl,-Bstatic', '-lsystemd', '-lcap',
                      '-Wl,-Bdynamic', '-lrt', '-lpthread']

link_arguments.append('-flto')

compile_arguments: List[str] = ['-flto']

use_limited_api = False

if environ.get('PYTHON_SDBUS_USE_LIMITED_API'):
    c_macros.append(('Py_LIMITED_API', '0x03070000'))
    use_limited_api = True


if __name__ == '__main__':
    setup(
        name='sdbus',
        description=('Modern Python D-Bus library. '
                     'Based on sd-bus from libsystemd.'),
        long_description=long_description,
        long_description_content_type='text/markdown',
        version='0.8.2',
        url='https://github.com/igo95862/python-sdbus',
        author='igo95862',
        author_email='igo95862@yandex.ru',
        license='LGPL-2.1-or-later',
        keywords='dbus ipc linux freedesktop',
        project_urls={
            'Documentation': 'https://python-sdbus.readthedocs.io/en/latest/',
            'Source': 'https://github.com/igo95862/python-sdbus/',
            'Tracker': 'https://github.com/igo95862/python-sdbus/issues/',
        },
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            (
                'License :: OSI Approved :: '
                'GNU Lesser General Public License v2 or later (LGPLv2+)'
            ),
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 3 :: Only',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
        packages=['sdbus',
                  # 'sdbus_async', 'sdbus_block',
                  'sdbus_async.dbus_daemon', 'sdbus_block.dbus_daemon',
                  ],
        package_dir={
            'sdbus': 'src/sdbus',
            'sdbus_async.dbus_daemon': 'src/sdbus_async/dbus_daemon',
            'sdbus_block.dbus_daemon': 'src/sdbus_block/dbus_daemon',
        },
        package_data={
            'sdbus': [
                'py.typed',
                'sd_bus_internals.pyi',
            ],
            'sdbus_async.dbus_daemon': [
                'py.typed',
            ],
            'sdbus_block.dbus_daemon': [
                'py.typed',
            ],
        },
        python_requires='>=3.7',
        ext_modules=[
            Extension(
                'sdbus.sd_bus_internals',
                [
                    'src/sdbus/sd_bus_internals.c',
                    'src/sdbus/sd_bus_internals_bus.c',
                    'src/sdbus/sd_bus_internals_funcs.c',
                    'src/sdbus/sd_bus_internals_interface.c',
                    'src/sdbus/sd_bus_internals_message.c',
                ],
                extra_compile_args=compile_arguments,
                extra_link_args=link_arguments,
                define_macros=c_macros,
                py_limited_api=use_limited_api,
            )
        ],
    )
