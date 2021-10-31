Asyncio API
============

Classes
++++++++++++++++++++

.. py:currentmodule:: sdbus

.. py:class:: DbusInterfaceCommonAsync(interface_name)

    Dbus async interface class.
    Dbus methods and properties should be defined using
    :py:func:`dbus_property_async`, :py:func:`dbus_signal_async`,
    and :py:func:`dbus_method_async` decorators.

    .. note::
        Don't forget to call ``super().__init__()`` in derived classes
        init calls as it sets up important attributes.

    :param str interface_name: Sets the dbus interface
        name that will be used for all properties, methods
        and signals defined in the body of the class.

    :param bool serving_enabled: If set to :py:obj:`True`
        the interface will not be served on dbus. Mostly used
        for interfaces that sd-bus already provides such as
        ``org.freedesktop.DBus.Peer``.

    .. py:method:: dbus_ping()
        :async:

        Pings the remote service using dbus.

        Useful to test if connection or remote service is alive.

        .. warning:: This method is ignores the particular object path
                     meaning it can NOT be used to test if object exist.

    .. py:method:: dbus_machine_id()
        :async:

        Returns the machine UUID of D-Bus the object is connected to.

        :return: machine UUID
        :rtype: str

    .. py:method:: dbus_introspect()
        :async:

        Get dbus introspection XML.

        It is users responsibility to parse that data.

        :return: string with introspection XML
        :rtype: str

    .. py:attribute:: properties_changed
        :type: Tuple[str, Dict[str, Tuple[str, Any]], List[str]]

        Signal when one of the objects properties changes.

        Signal data is:

        Interface name : str
            Name of the interface where property changed

        Changed properties : Dict[str, Tuple[str, Any]]
            Dictionary there keys are names of properties changed and
            values are variants of new value.

        Invalidated properties : List[str]
            List of property names changed but no new value had been provided

    .. py:method:: _proxify(bus, service_name, object_path)

        Begin proxying to a remote dbus object.

        :param str service_name:
            Remote object dbus connection name. 
            For example, systemd uses ``org.freedesktop.systemd1``

        :param str object_path:
            Remote object dbus path.
            Should be a forward slash separated path.
            Starting object is usually ``/``.
            Example: ``/org/freedesktop/systemd/unit/dbus_2eservice``

        :param SdBus bus:
            Optional dbus connection object.
            If not passed the default dbus will be used.

    .. py:classmethod:: new_proxy(bus, service_name, object_path)

        Create new proxy object and bypass ``__init__``.

        :param str service_name:
            Remote object dbus connection name. 
            For example, systemd uses ``org.freedesktop.systemd1``

        :param str object_path:
            Remote object dbus path.
            Should be a forward slash separated path.
            Starting object is usually ``/``.
            Example: ``/org/freedesktop/systemd/unit/dbus_2eservice``

        :param SdBus bus:
            Optional dbus connection object.
            If not passed the default dbus will be used.

    .. py:method:: export_to_dbus(bus, object_path)

        Object will appear and become callable on dbus.

        :param str object_path:
            Object path that it will be available at.

        :param SdBus bus:
            Optional dbus connection object.
            If not passed the default dbus will be used.


.. py:class:: DbusObjectManagerInterfaceAsync(interface_name)

    This class is almost identical to :py:class:`DbusInterfaceCommonAsync`
    but implements `ObjectManager <https://dbus.freedesktop.org/doc/dbus-specification.html#standard-interfaces-objectmanager>`_
    interface.

    .. py:method:: get_managed_objects()
        :async:

        Get the objects this object manager in managing.

        :return:
            Triple nested dictionary that contains all the objects
            paths with their properties values.

            Dict[ObjectPath, Dict[InterfaceName, Dict[PropertyName, PropertyValue]]]

        :rtype: Dict[str, Dict[str, Dict[str, Any]]]

    .. py:attribute:: interfaces_added
        :type: Tuple[str, Dict[str, Dict[str, Any]]]

        Signal when a new object is added or and existing object
        gains a new interface.

        Signal data is:

        Object path : str
            Path to object that was added or modified.

        Object interfaces and properties : Dict[str, Dict[str, Any]]]
            Dict[InterfaceName, Dict[PropertyName, PropertyValue]]

    .. py:attribute:: interfaces_removed
        :type: Tuple[str, List[str]]

        Signal when existing object or and interface of
        existing object is removed.

        Signal data is:

        Object path : str
            Path to object that was removed or modified.

        Interfaces list : List[str]
            Interfaces names that were removed.


Decorators
++++++++++++++++++++++++

.. py:decorator:: dbus_method_async([input_signature, [result_signature, [flags, [result_args_names, [input_args_names, [method_name]]]]]])

    Define a method.

    Underlying function must be a coroutine function.

    :param str input_signature: dbus input signature.
        Defaults to "" meaning method takes no arguments.
        Required if you intend to connect to a remote object.

    :param str result_signature: dbus result signature.
        Defaults to "" meaning method returns empty reply on success.
        Required if you intend to serve the object.

    :param int flags: modifies behavior.
        No effect on remote connections.
        Defaults to 0 meaning no special behavior.

        See :ref:`dbus-flags` .

    :param Sequence[str] result_args_names: sequence of result
        argument names.

        These names will show up in introspection data but otherwise
        have no effect.

        Sequence can be list, tuple, etc...
        Number of elements in the sequence should match
        the number of result arguments otherwise :py:exc:`SdBusLibraryError`
        will be raised.

        Defaults to result arguments being nameless.

    :param Sequence[str] input_args_names: sequence of input
        argument names.

        These names will show up in introspection data but otherwise
        have no effect.

        Sequence can be list, tuple, etc...
        Number of elements in the sequence should match
        the number of result arguments otherwise :py:exc:`RuntimeError`
        will be raised.

        If ``result_args_names`` has been passed when Python function
        argument names will be used otherwise input arguments 
        will be nameless

    :param str method_name: Force specific dbus method name 
        instead of being based on Python function name.

    Example: ::

        from sdbus import DbusInterfaceCommonAsync, dbus_method_async


        class ExampleInterface(DbusInterfaceCommonAsync,
                               interface_name='org.example.test'
                               ):

            # Method that takes a string 
            # and returns uppercase of that string
            @dbus_method_async(
                input_signature='s',
                result_signature='s',
                result_args_names=('uppercased', )  # This is optional but
                                                    # makes arguments have names in 
                                                    # instrospection data.
            )
            async def upper(self, str_to_up: str) -> str:
                return str_to_up.upper()



.. py:decorator:: dbus_property_async(property_signature, [flags, [property_name]])

    Declare a dbus property.

    The underlying function has to be a regular ``def`` function.

    The property will be read-only or read/write based on if setter was
    declared.

    .. warning:: Properties are supposed 
        to be lightweight to get or set. 
        Make sure property getter or setter
        does not perform heavy IO or computation
        as that will block other methods or properties.

    :param str property_signature: Property dbus signature.
        Has to be a single type or container.

    :param int flags: modifies behavior.
        No effect on remote connections.
        Defaults to 0 meaning no special behavior.

        See :ref:`dbus-flags` .

    :param str property_name: Force specific property name
        instead of constructing it based on Python function name.

    Properties have following methods:

    .. py:decoratormethod:: setter(set_function)

        Defines the setter function.
        This makes the property read/write instead of read-only.

        See example on how to use. 

    .. py:method:: get_async()
        :async:

        Get the property value.

        The property can also be directly ``await`` ed 
        instead of calling this method.

    .. py:method:: set_async(new_value)
        :async:

        Set property value.


    Example: ::

        from sdbus import DbusInterfaceCommonAsync, dbus_property_async


        class ExampleInterface(DbusInterfaceCommonAsync,
                               interface_name='org.example.test'
                               ):

            def __init__(self) -> None:
                # This is just a generic init
                self.i = 12345
                self.s = 'test'

            # Read only property. No setter defined.
            @dbus_property_async('i')
            def read_only_number(self) -> int:
                return self.i

            # Read/write property. First define getter.
            @dbus_property_async('s')
            def read_write_str(self) -> str:
                return self.s

            # Now create setter. Method name does not matter.
            @read_write_str.setter  # Use the property setter method as decorator
            def read_write_str_setter(self, new_str: str) -> None:
                self.s = new_str

.. py:decorator:: dbus_signal_async([signal_signature, [signal_args_names, [flags, [signal_name]]]])

    Defines a dbus signal.

    Underlying function return type hint is used for signal type hints.

    :param str signal_signature: signal dbus signature.
        Defaults to empty signal.

    :param Sequence[str] signal_args_names: sequence of signal argument names.

        These names will show up in introspection data but otherwise
        have no effect.

        Sequence can be list, tuple, etc...
        Number of elements in the sequence should match
        the number of result arguments otherwise :py:exc:`RuntimeError`
        will be raised.

        Defaults to result arguments being nameless.

    :param int flags: modifies behavior.
        No effect on remote connections.
        Defaults to 0 meaning no special behavior.

        See :ref:`dbus-flags` .

    :param str signal_name: Forces specific signal name instead
        of being based on Python function name.

    Signals have following methods:

    .. py:method:: __aiter__()

        Signal can be used as an async generator for loop:
        ``async for x in something.some_signal:``

        This is main way to await for new events.

        Both remote and local objects operate the same way.

    .. py:method:: emit(args)

        Emit a new signal with *args* data.

    Example: ::

        from sdbus import DbusInterfaceCommonAsync, dbus_signal_async


        class ExampleInterface(DbusInterfaceCommonAsync,
                               interface_name='org.example.signal'
                               ):

            @dbus_signal_async('s')
            def name_changed(self) -> str:
                raise NotImplementedError

.. py:decorator:: dbus_method_async_override()

    Override the method.

    Method name should match the super class method name that you
    want to override.

    New method should take same arguments.

    You **must** add round brackets to decorator.

    Example: ::

        from sdbus import (DbusInterfaceCommonAsync, dbus_method_async
                           dbus_method_async_override)


        class ExampleInterface(DbusInterfaceCommonAsync,
                               interface_name='org.example.test'
                               ):

            # Original call
            @dbus_method_async('s', 's')
            async def upper(self, str_to_up: str) -> str:
                return str_to_up.upper()


        class ExampleOverride(ExampleInterface):

            @dbus_method_async_override()
            async def upper(self, str_to_up: str) -> str:
                return 'Upper: ' + str_to_up.upper()


.. py:decorator:: dbus_property_async_override()

    Override property.

    You **must** add round brackets to decorator.

    Example: ::

        from sdbus import (DbusInterfaceCommonAsync, dbus_property_async
                           dbus_property_async_override)


        class ExampleInterface(DbusInterfaceCommonAsync,
                               interface_name='org.example.test'
                               ):

            def __init__(self) -> None:
                self.s = 'aaaaaaaaa'

            # Original property
            @dbus_property_async('s')
            def str_prop(self) -> str:
                return self.s

            @str_prop.setter
            def str_prop_setter(self, new_s: str) -> None:
                self.s = new_s


        class ExampleOverride(ExampleInterface):

            @dbus_property_async_override()
            def str_prop(self) -> str:
                return 'Test property' + self.s

            # Setter needs to be decorated again to override
            @str_prop.setter
            def str_prop_setter(self, new_s: str) -> None:
                self.s = new_s.upper()
