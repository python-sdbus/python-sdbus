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

from setuptools import Extension, setup

long_description = '''python-sdbus is the dbus library
based on sd-bus that aims to implement moderns Python features such as
Asyncio and Type hints while providing intuitive way of defining interfaces
and connecting to remote objects.

See the
[documentation](https://python-sdbus.readthedocs.io/en/latest/index.html)
for tutorial and API reference.

Also includes a
[repository](https://python-sdbus.readthedocs.io/en/latest/proxies.html)
of well-known DBus interfaces such as Notifications interface.

Here is example code:

`example_interface.py` file:

```
from sdbus import (DbusInterfaceCommonAsync, dbus_method_async,
                   dbus_property_async, dbus_signal_async)

# This is file only contains interface definition for easy import
# in server and client files

class ExampleInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.example.interface'
):
    @dbus_method_async(
        input_signature='s',
        result_signature='s',
    )
    async def upper(self, string: str) -> str:
        return string.upper()

    @dbus_property_async(
        property_signature='s',
    )
    def hello_world(self) -> str:
        return 'Hello, World!'

    @dbus_signal_async(
        signal_signature='i'
    )
    def clock(self) -> int:
        raise NotImplementedError
```

`example_server.py` file:

```
from asyncio import get_event_loop, sleep
from random import randint
from time import time

from example_interface import ExampleInterface

from sdbus import request_default_bus_name_async

loop = get_event_loop()

export_object = ExampleInterface()


async def clock() -> None:
    """
    This coroutine will sleep a random time and emit
    a signal with current clock
    """
    while True:
        await sleep(randint(2, 7))  # Sleep a random time
        current_time = int(time())  # The interface we defined uses integers
        export_object.clock.emit(current_time)


async def startup() -> None:
    """Preform async startup actions"""
    # Acquire a known name on the bus
    # Client will use that name to connect to this server
    await request_default_bus_name_async('org.example.test')
    # Export the object to dbus
    await export_object.start_serving('/')


loop.run_until_complete(startup())
loop.create_task(clock())
loop.run_forever()
```

`example_client.py` file:

```
from asyncio import get_event_loop

from example_interface import ExampleInterface

# Create a new binded object
example_object = ExampleInterface.new_connect('org.example.test', '/')


async def print_clock() -> None:
    # Use async for loop to print clock signals we recieve
    async for x in example_object.clock:
        print('Got clock: ', x)


async def call_upper() -> None:
    s = 'test string'
    s_after = await example_object.upper(s)

    print('Initial string: ', s)
    print('After call: ', s_after)


async def get_hello_world() -> None:
    print('Remote property: ', await example_object.hello_world)

loop = get_event_loop()

loop.create_task(call_upper())
loop.create_task(print_clock())
loop.create_task(get_hello_world())

loop.run_forever()
```
'''

setup(
    name='sdbus',
    description='Modern DBus python binds. Based on sd-bus from libsystemd.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='0.7.0',
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
    packages=['sdbus'],
    python_requires='>=3.8',
    ext_modules=[
        Extension(
            'sdbus.sd_bus_internals',
            ['sdbus/sd_bus_internals.c', ],
            libraries=['systemd', ],
        )
    ],
)
