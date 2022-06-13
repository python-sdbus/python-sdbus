# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2020-2022 igo95862

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

from asyncio import new_event_loop, sleep
from random import randint
from time import time

from example_interface import ExampleInterface

from sdbus import request_default_bus_name_async

loop = new_event_loop()

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
    # Clients will use that name to address this server
    await request_default_bus_name_async('org.example.test')
    # Export the object to dbus
    export_object.export_to_dbus('/')


loop.run_until_complete(startup())
task_clock = loop.create_task(clock())
loop.run_forever()
