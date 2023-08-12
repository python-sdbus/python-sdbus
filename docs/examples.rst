Examples
=======================

Asyncio client and server
++++++++++++++++++++++++++++++

In this example we create a simple example server and client.

There are 3 files:

* ``example_interface.py`` File that contains the interface definition.
* ``example_server.py`` Server.
* ``example_interface.py`` Client.


``example_interface.py`` file: ::

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

``example_server.py`` file: ::

    from asyncio import get_event_loop, sleep
    from random import randint
    from time import time

    from example_interface import ExampleInterface

    from sdbus import request_default_bus_name_async

    loop = get_event_loop()

    export_object = ExampleInterface()


    async def clock() -> None:
        """
        This coroutine will sleep a random time and emit a signal with current clock
        """
        while True:
            await sleep(randint(2, 7))  # Sleep a random time
            current_time = int(time())  # The interface we defined uses integers
            export_object.clock.emit(current_time)


    async def startup() -> None:
        """Perform async startup actions"""
        # Acquire a known name on the bus
        # Clients will use that name to address to this server
        await request_default_bus_name_async('org.example.test')
        # Export the object to D-Bus
        export_object.export_to_dbus('/')


    loop.run_until_complete(startup())
    task_clock = loop.create_task(clock())
    loop.run_forever()



``example_client.py`` file: ::

    from asyncio import get_event_loop

    from example_interface import ExampleInterface

    # Create a new proxy object
    example_object = ExampleInterface.new_proxy('org.example.test', '/')


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


Start server before client. ``python example_server.py``

In separated terminal start client. ``python example_client.py``

Use CTRL-C to close client and server.

You can also use :py:obj:`ExampleInterface` as a local object: ::

    from asyncio import run
    from example_interface import ExampleInterface

    example_object = ExampleInterface()

    async def test() -> None:
        print(await example_object.upper('test'))

        print(await example_object.hello_world)

    run(test())
