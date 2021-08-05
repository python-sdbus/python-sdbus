[![Total alerts](https://img.shields.io/lgtm/alerts/g/igo95862/python-sdbus.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/igo95862/python-sdbus/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/igo95862/python-sdbus.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/igo95862/python-sdbus/context:python)
[![Documentation Status](https://readthedocs.org/projects/python-sdbus/badge/?version=latest)](https://python-sdbus.readthedocs.io/en/latest/?badge=latest)

# Modern Python library for D-Bus

Features:

* Asyncio and blocking calls.
* Type hints. (`mypy --strict` compatible)
* No Python 2 legacy.
* Based on fast sd-bus from systemd.
* Unified client/server interface classes. Write interface once!
* Dbus methods can have keyword and default arguments.

See the
[documentation](https://python-sdbus.readthedocs.io/en/latest/index.html)
for tutorial and API reference.

### List of implemented interfaces

* D-Bus (built-in)
* [Freedesktop Notifications](https://github.com/igo95862/python-sdbus-notifications)
* [Network Manager](https://github.com/igo95862/python-sdbus-networkmanager)

More incoming. (NetworkManager, secrets... )

## Requirements

### Binary package from PyPI

* Python 3.8 or higher. (3.7 might work but is not supported)
* `x86_64` or `aarch64` architecture.
* glibc 2.17 or higher. (released in 2014)
* pip 19.3 or higher.

Starting with version `0.8rc2` the libsystemd is statically
linked and is not required.

Pass `--only-binary ':all:'` to pip to ensure that it
installs binary package.

`i686`, `ppc64le` and `s390x` can be supported if there is a
demand. Please open an issue if you are interested in those
platforms.

### Source package or compiling from source

* Python 3.8 or higher.
* Python headers. (`python3-dev` package on ubuntu)
* GCC.
* libsystemd. (comes with systemd)
* libsystemd headers. (`libsystemd-dev` package on ubuntu)
* Python setuptools.

Systemd version should be higher than 246.

### Optional dependencies

* Jinja2 for code generator.
* Sphinx for autodoc.

## Installation

### PyPI

URL: https://pypi.org/project/sdbus/

`pip install --only-binary ':all:' sdbus`

### AUR

URL: https://aur.archlinux.org/packages/python-sdbus-git/

## Example code

Interface `example_interface.py` file:

```python
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

Server `example_server.py` file:

```python
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
    """Perform async startup actions"""
    # Acquire a known name on the bus
    # Client will use that name to connect to this server
    await request_default_bus_name_async('org.example.test')
    # Export the object to dbus
    export_object.export_to_dbus('/')


loop.run_until_complete(startup())
task_clock = loop.create_task(clock())
loop.run_forever()
```

Client `example_client.py` file:

```python
from asyncio import get_event_loop

from example_interface import ExampleInterface

# Create a new binded object
example_object = ExampleInterface.new_connect('org.example.test', '/')


async def print_clock() -> None:
    # Use async for loop to print clock signals we receive
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

# Always binds your tasks to a variable
task_upper = loop.create_task(call_upper())
task_clock = loop.create_task(print_clock())
task_hello_world = loop.create_task(get_hello_world())

loop.run_forever()
```
