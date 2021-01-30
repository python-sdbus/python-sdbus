Asyncio quick start
+++++++++++++++++++++

Interface classes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Python-sdbus works by declaring interface classes.

Interface classes for async IO should be derived from :py:class:`DbusInterfaceCommonAsync`.

The class constructor takes ``interface_name`` keyword to determine the dbus interface name for all
dbus elements declared in the class body.

Example::

    class ExampleInterface(DbusInterfaceCommonAsync,
                           interface_name='org.example.myinterface'
                           ):
        ...

Interface class body should contain the definitions of methods, properties and
signals using decorators such as
:py:func:`dbus_method_async`, :py:func:`dbus_property_async` and
:py:func:`dbus_signal_async`.


Example::

    class ExampleInterface(DbusInterfaceCommonAsync,
                           interface_name='org.example.myinterface'
                           ):
        # Method that takes an integer and mutltiplies it by 2
        @dbus_method_async('i', 'i')
        async def double_int(self, an_int: int) -> None:
            return an_int * 2

        # Read only property of str
        @dbus_property_async('s')
        def read_string(self) -> int:
            return 'Test'

        # Signal with a list of strings
        @dbus_signal_async('as')
        def str_signal(self) -> List[str]:
            raise NotImplementedError

Connecting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:py:class:`DbusInterfaceCommonAsync` provides two methods for connecting to remote objects.

:py:meth:`new_connect` class method bypasses the class ``__init__`` and returns connected object. 

:py:meth:`_connect` should be used inside the ``__init__`` methods if your class is remote only.

See API reference down bellow.

Serving objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:py:class:`DbusInterfaceCommonAsync` provides :py:meth:`start_serving` method
that will export the object to the dbus. After calling it the object
becomes visible on dbus for other processes to call.

Example using ExampleInterface from before ::

    loop = get_event_loop()

    b = get_default_bus()

    i = ExampleInterface()

    async def start() -> None:
        # Acquire a name on the bus
        await b.request_name_async('org.example.test', 0)
        # Start serving at / path
        await i.start_serving('/')

    loop.run_until_complete(start())
    loop.run_forever()

Connection transparency
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The interface objects are designed to be transparent to their connection
status. This means if the object not connected to remote the calls to decorated
methods will still work in the local scope.

This is the call to local object: ::

    i = ExampleInterface()
    
    async def test() -> None:
        print(await i.double_int(5))  # Will print 10

This is a call to remote object at ``'org.example.test'`` service name
and ``'/'`` path: ::

    i = ExampleInterface.new_connect('org.example.test', '/')
    
    async def test() -> None:
        print(await i.double_int(5))  # Will print 10

Multiple interfaces
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A dbus object can have multiple interfaces with different methods and properties.

To implement this define multiple interface classes and do a
multiple inheritance on all interfaces the object has.

Example: ::

    class ExampleInterface(DbusInterfaceCommonAsync,
                           interface_name='org.example.myinterface'
                           ):

        @dbus_method_async('i', 'i')
        async def double_int(self, an_int: int) -> None:
            return an_int * 2


    class TestInterface(DbusInterfaceCommonAsync,
                        interface_name='org.example.test'
                        ):

        @dbus_method_async('as', 's')
        async def join_str(self, str_array: List[str]) -> str:
            return ''.join(str_array)

    
    class MultipleInterfaces(TestInterface, ExampleInterface):
        ...

``MultipleInterfaces`` class will have both ``test_method`` and ``example_method``
that will be wired to correct interface names. (``org.example.myinterface``
and ``org.example.test`` respectively)
