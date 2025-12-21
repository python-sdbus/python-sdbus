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
from subprocess import DEVNULL, PIPE
from subprocess import run as subprocess_run
from typing import Optional

from setuptools import Extension, setup

c_macros: list[tuple[str, Optional[str]]] = []


def get_libsystemd_version() -> int:
    process = subprocess_run(
        args=('pkg-config', '--modversion', 'libsystemd'),
        stderr=DEVNULL,
        stdout=PIPE,
        check=True,
        text=True,
    )

    result_str = process.stdout
    # Version can either be like 250 or 250.10
    first_component = result_str.split(".")[0]

    return int(first_component)


if not environ.get('PYTHON_SDBUS_USE_IGNORE_SYSTEMD_VERSION'):
    systemd_version = get_libsystemd_version()

    if systemd_version < 246:
        c_macros.append(('LIBSYSTEMD_NO_VALIDATION_FUNCS', None))

    if systemd_version < 248:
        c_macros.append(('LIBSYSTEMD_NO_OPEN_USER_MACHINE', None))


def get_link_arguments() -> list[str]:
    process = subprocess_run(
        args=('pkg-config', '--libs-only-l', 'libsystemd'),
        stderr=DEVNULL,
        stdout=PIPE,
        check=True,
    )

    result_str = process.stdout.decode('utf-8')

    return result_str.rstrip(' \n').split(' ')


link_arguments: list[str] = get_link_arguments()

if environ.get('PYTHON_SDBUS_USE_STATIC_LINK'):
    # Link statically against libsystemd and libcap
    link_arguments = ['-Wl,-Bstatic', *link_arguments, '-lcap',
                      '-Wl,-Bdynamic', '-lrt', '-lpthread']

link_arguments.append('-flto')

compile_arguments: list[str] = ['-flto']

use_limited_api = False

if environ.get('PYTHON_SDBUS_USE_LIMITED_API'):
    c_macros.append(('Py_LIMITED_API', '0x03090000'))
    use_limited_api = True


if __name__ == '__main__':
    with open('./README.md') as f:
        long_description = f.read()

    setup(
        name='sdbus',
        description=('Modern Python D-Bus library. '
                     'Based on sd-bus from libsystemd.'),
        long_description=long_description,
        long_description_content_type='text/markdown',
        version='0.14.2',
        url='https://github.com/python-sdbus/python-sdbus',
        author='igo95862',
        author_email='igo95862@yandex.ru',
        license='LGPL-2.1-or-later',
        keywords='dbus ipc linux freedesktop',
        project_urls={
            'Documentation': 'https://python-sdbus.readthedocs.io/en/latest/',
            'Source': 'https://github.com/python-sdbus/python-sdbus/',
            'Tracker': 'https://github.com/python-sdbus/python-sdbus/issues/',
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
        packages=[
            'sdbus',
            'sdbus.utils',
            'sdbus_async.dbus_daemon',
            'sdbus_block.dbus_daemon',
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
                'sd_bus_internals.h',
            ],
            'sdbus_async.dbus_daemon': [
                'py.typed',
            ],
            'sdbus_block.dbus_daemon': [
                'py.typed',
            ],
        },
        python_requires='>=3.9',
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
