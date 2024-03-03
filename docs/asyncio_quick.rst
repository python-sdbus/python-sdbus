Asyncio quick start
+++++++++++++++++++++

.. py:currentmodule:: sdbus

Interface classes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Python-sdbus works by declaring interface classes.

Interface classes for async IO should be derived from :py:class:`DbusInterfaceCommonAsync`.

The class constructor takes ``interface_name`` keyword to determine the D-Bus interface name for all
D-Bus elements declared in the class body.

Example: ::

    from sdbus import DbusInterfaceCommonAsync


    class ExampleInterface(DbusInterfaceCommonAsync,
                           interface_name='org.example.myinterface'
                           ):
        ...

Interface class body should contain the definitions of methods, properties and
signals using decorators such as
:py:func:`dbus_method_async`, :py:func:`dbus_property_async` and
:py:func:`dbus_signal_async`.


Example: ::

    from sdbus import (DbusInterfaceCommonAsync, dbus_method_async,
                       dbus_property_async, dbus_signal_async)


    class ExampleInterface(DbusInterfaceCommonAsync,
                           interface_name='org.example.myinterface'
                           ):
        # Method that takes an integer and multiplies it by 2
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

Initiating proxy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:py:class:`DbusInterfaceCommonAsync` provides two methods for proxying remote objects.

:py:meth:`DbusInterfaceCommonAsync.new_proxy` class method bypasses the class ``__init__`` and returns proxy object.

:py:meth:`DbusInterfaceCommonAsync._proxify` should be used inside the ``__init__`` methods if your class is a proxy only.

Recommended to create proxy classes that a subclass of the interface: ::

    from sdbus import DbusInterfaceCommonAsync


    class ExampleInterface(...):
        # Some interface class
        ...

    class ExampleClient(ExampleInterface):
        def __init__(self) -> None:
            # Your client init can proxy to any object based on passed arguments.
            self._proxify('org.example.test', '/')


.. note:: Successfully initiating a proxy object does NOT guarantee that the D-Bus object exists.

Serving objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:py:meth:`DbusInterfaceCommonAsync.export_to_dbus` method
will export the object to the D-Bus. After calling it the object
becomes visible on D-Bus for other processes to call.

Example using ExampleInterface from before: ::

    from sdbus import request_default_bus_name_async


    loop = get_event_loop()

    i = ExampleInterface()

    async def start() -> None:
        # Acquire a name on the bus
        await request_default_bus_name_async('org.example.test')
        # Start serving at / path
        i.export_to_dbus('/')

    loop.run_until_complete(start())
    loop.run_forever()

Connection transparency
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The interface objects are designed to be transparent to their connection
status. This means if the object not proxied to remote the calls to decorated
methods will still work in the local scope.

This is the call to local object: ::

    i = ExampleInterface()
    
    async def test() -> None:
        print(await i.double_int(5))  # Will print 10

This is a call to remote object at ``'org.example.test'`` service name
and ``'/'`` path: ::

    i = ExampleInterface.new_proxy('org.example.test', '/')

    async def test() -> None:
        print(await i.double_int(5))  # Will print 10

Methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Methods are async function calls wrapped with :py:func:`dbus_method_async` decorator. (see the API reference for decorator parameters)

Methods have to be async function, otherwise :py:exc:`AssertionError` will be raised.

While method calls are async there is a inherit timeout timer for any method call.

To return an error to caller you need to raise exception which has a :py:exc:`.DbusFailedError` as base.
Regular exceptions will not propagate.

See :doc:`/exceptions`.

Example: ::

    from sdbus import DbusInterfaceCommonAsync, dbus_method_async


    class ExampleInterface(...):

        ...
        # Body of some class

        # Method that takes a string 
        # and returns uppercase of that string
        @dbus_method_async(
            input_signature='s',
            result_signature='s',
            result_args_names=('uppercased', )  # This is optional but
                                                # makes arguments have names in 
                                                # introspection data.
        )
        async def upper(self, str_to_up: str) -> str:
            return str_to_up.upper()

Methods behave exact same way as Python methods would: ::

    print(await example_object.upper('test'))  # prints TEST


Properties
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Properties are a single value that can be read and write.

To declare a read only property you need to decorate a regular function with
:py:func:`dbus_property_async` decorator.

Example: ::

    from sdbus import DbusInterfaceCommonAsync, dbus_property_async


    class ExampleInterface(...):

        ...
        # Body of some class

        # Read only property. No setter defined.
        @dbus_property_async('i')
        def read_only_number(self) -> int:
            return 10

To create a read/write property you need to decorate the setter function with
the :py:obj:`setter` attribute of your getter function.

Example: ::

    from sdbus import DbusInterfaceCommonAsync, dbus_property_async


    class ExampleInterface(...):

        ...
        # Body of some class

        # Read/write property. First define getter.
        @dbus_property_async('s')
        def read_write_str(self) -> str:
            return self.s

        # Now create setter. Method name does not matter.
        @read_write_str.setter  # Use the property setter method as decorator
        def read_write_str_setter(self, new_str: str) -> None:
            self.s = new_str


Properties are supposed to be lightweight. Make sure you don't block event loop with getter or setter.

Async properties do not behave the same way as :py:func:`property` decorator does.

To get the value of the property you can either directly ``await`` on property
or use :py:meth:`get_async` method. (also need to be awaited)

To set property use :py:meth:`set_async` method.

Example: ::

    ...
    # Somewhere in async function
    # Assume we have example_object of class defined above
    print(await example_object.read_write_str)  # Print the value of read_write_str

    ...
    # Set read_write_str to new value
    await example_object.read_write_str.set_async('test')


Signals
^^^^^^^^^^^^^^^^^^^^^^^^^^^

To define a D-Bus signal wrap a function with :py:func:`dbus_signal_async` decorator.

The function is only used for type hints information. It is recommended
to just put ``raise NotImplementedError`` in to the body of the function.

Example: ::

    from sdbus import DbusInterfaceCommonAsync, dbus_signal_async


    class ExampleInterface(...):

            ...
            # Body of some class
            @dbus_signal_async('s')
            def name_changed(self) -> str:
                raise NotImplementedError

To catch a signal use ``async for`` loop: ::

    async for x in example_object.name_changed:
        print(x)

.. warning:: If you are creating an asyncio task to listen on signals
   make sure to bind it to a variable and keep it referenced otherwise
   garbage collector will destroy your task.

A signal can be emitted with :py:meth:`emit <DbusSignalAsync.emit>` method.

Example::

    example_object.name_changed.emit('test')

Signals can also be caught from multiple D-Bus objects using
:py:meth:`catch_anywhere <DbusSignalAsync.catch_anywhere>` method. The async
iterator will yield the path of the object that emitted the signal and the signal data.

:py:meth:`catch_anywhere <DbusSignalAsync.catch_anywhere>` can be called from
class but in such case the service name must be provided.

Example::

    async for path, x in ExampleInterface.name_changed.catch_anywhere('org.example.test'):
        print(f"On {path} caught: {x}")

Subclass Overrides
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you define a subclass which overrides a declared D-Bus method or property
you need to use :py:func:`dbus_method_async_override` and :py:func:`dbus_property_async_override`
decorators. Overridden property can decorate a new setter.

Overridden methods should take same number and type of arguments.

Example: ::

    from sdbus import (dbus_method_async_override,
                       dbus_property_async_override)


    # Some subclass
    class SubclassInterface(...):

        ...
        @dbus_method_async_override()
        async def upper(self, str_to_up: str) -> str:
            return 'Upper: ' + str_to_up.upper()

        @dbus_property_async_override()
        def str_prop(self) -> str:
            return 'Test property' + self.s

        # Setter needs to be decorated again to override
        @str_prop.setter
        def str_prop_setter(self, new_s: str) -> None:
            self.s = new_s.upper()

Multiple interfaces
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A D-Bus object can have multiple interfaces with different methods and properties.

To implement this define multiple interface classes and do a
multiple inheritance on all interfaces the object has.

Example: ::

    from sdbus import DbusInterfaceCommonAsync


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
