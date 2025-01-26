Asyncio API
============

Classes
++++++++++++++++++++

.. py:currentmodule:: sdbus

.. py:class:: DbusInterfaceCommonAsync(interface_name)

    D-Bus async interface class.
    D-Bus methods and properties should be defined using
    :py:func:`dbus_property_async`, :py:func:`dbus_signal_async`,
    and :py:func:`dbus_method_async` decorators.

    .. note::
        Don't forget to call ``super().__init__()`` in derived classes
        init calls as it sets up important attributes.

    :param str interface_name: Sets the D-Bus interface
        name that will be used for all properties, methods
        and signals defined in the body of the class.

    :param bool serving_enabled: If set to :py:obj:`True`
        the interface will not be served on D-Bus. Mostly used
        for interfaces that sd-bus already provides such as
        ``org.freedesktop.DBus.Peer``.

    .. py:method:: dbus_ping()
        :async:

        Pings the remote service using D-Bus.

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

        Get D-Bus introspection XML.

        It is users responsibility to parse that data.

        :return: string with introspection XML
        :rtype: str

    .. py:method:: properties_get_all_dict()
        :async:

        Get all object properties as a dictionary where keys are member
        names and values are properties values.

        Equivalent to ``GetAll`` method of the ``org.freedesktop.DBus.Properties``
        interface but the member names are automatically translated to python
        names. (internally calls it for each interface used in class definition)

        :param str on_unknown_member: If an unknown D-Bus property was encountered
            either raise an ``"error"`` (default), ``"ignore"`` the property
            or ``"reuse"`` the D-Bus name for the member.
        :return: dictionary of properties
        :rtype: dict[str, Any]

    .. py:attribute:: properties_changed
        :type: tuple[str, dict[str, tuple[str, Any]], list[str]]

        Signal when one of the objects properties changes.

        :py:func:`sdbus.utils.parse.parse_properties_changed` can be used to transform
        this signal data in to an easier to work with dictionary.

        Signal data is:

        Interface name : str
            Name of the interface where property changed

        Changed properties : dict[str, tuple[str, Any]]
            Dictionary there keys are names of properties changed and
            values are variants of new value.

        Invalidated properties : list[str]
            List of property names changed but no new value had been provided

    .. py:method:: _proxify(bus, service_name, object_path)

        Begin proxying to a remote D-Bus object.

        :param str service_name:
            Remote object D-Bus connection name.
            For example, systemd uses ``org.freedesktop.systemd1``

        :param str object_path:
            Remote object D-Bus path.
            Should be a forward slash separated path.
            Starting object is usually ``/``.
            Example: ``/org/freedesktop/systemd/unit/dbus_2eservice``

        :param SdBus bus:
            Optional D-Bus connection object.
            If not passed the default D-Bus will be used.

    .. py:classmethod:: new_proxy(bus, service_name, object_path)

        Create new proxy object and bypass ``__init__``.

        :param str service_name:
            Remote object D-Bus connection name.
            For example, systemd uses ``org.freedesktop.systemd1``

        :param str object_path:
            Remote object D-Bus path.
            Should be a forward slash separated path.
            Starting object is usually ``/``.
            Example: ``/org/freedesktop/systemd/unit/dbus_2eservice``

        :param SdBus bus:
            Optional D-Bus connection object.
            If not passed the default D-Bus will be used.

    .. py:method:: export_to_dbus(object_path, bus)

        Object will appear and become callable on D-Bus.

        Returns a handle that can either be used as a context manager
        to remove the object from D-Bus or ``.stop()`` method of the
        handle can be called to remove object from D-Bus.

        Returns a handle that can be used to remove object from D-Bus
        by either using it as a context manager or by calling ``.stop()``
        method of the handle.

        .. code-block:: python

            with dbus_object.export_to_dbus("/"):
                # dbus_object can be called from D-Bus inside this
                # with block.
                ...

            ...

            handle = dbus_object2.export_to_dbus("/")
            # dbus_object2 can be called from D-Bus between these statements
            handle.stop()

            ...

            dbus_object3.export_to_dbus("/")
            # dbus_object3 can be called from D-Bus until all references are
            # dropped.
            del dbus_object3

        If the handle is discarded the object will remain exported until
        it gets deallocated.

        *Changed in version 0.12.0:* Added a handle return.

        :param str object_path:
            Object path that it will be available at.

        :param SdBus bus:
            Optional D-Bus connection object.
            If not passed the default D-Bus will be used.

        :return: Handle to control the export.


.. py:class:: DbusObjectManagerInterfaceAsync(interface_name)

    This class is almost identical to :py:class:`DbusInterfaceCommonAsync`
    but implements `ObjectManager <https://dbus.freedesktop.org/doc/dbus-specification.html#standard-interfaces-objectmanager>`_
    interface.

    Example of serving objects with ObjectManager::

        my_object_manager = DbusObjectManagerInterfaceAsync()
        my_object_manager.export_to_dbus('/object/manager')

        managed_object = DbusInterfaceCommonAsync()
        my_object_manager.export_with_manager('/object/manager/example')

    .. py:method:: get_managed_objects()
        :async:

        Get the objects this object manager in managing.

        :py:func:`sdbus.utils.parse.parse_get_managed_objects` can be used
        to make returned data easier to work with.

        :return:
            Triple nested dictionary that contains all the objects
            paths with their properties values.

            dict[ObjectPath, dict[InterfaceName, dict[PropertyName, PropertyValue]]]

        :rtype: dict[str, dict[str, dict[str, Any]]]

    .. py:attribute:: interfaces_added
        :type: tuple[str, dict[str, dict[str, Any]]]

        Signal when a new object is added or and existing object
        gains a new interface.

        :py:func:`sdbus.utils.parse.parse_interfaces_added` can be used
        to make signal data easier to work with.

        Signal data is:

        Object path : str
            Path to object that was added or modified.

        Object interfaces and properties : dict[str, dict[str, Any]]]
            dict[InterfaceName, dict[PropertyName, PropertyValue]]

    .. py:attribute:: interfaces_removed
        :type: tuple[str, list[str]]

        Signal when existing object or and interface of
        existing object is removed.

        :py:func:`sdbus.utils.parse.parse_interfaces_removed` can be used
        to make signal data easier to work with.

        Signal data is:

        Object path : str
            Path to object that was removed or modified.

        Interfaces list : list[str]
            Interfaces names that were removed.

    .. py:method:: export_with_manager(object_path, object_to_export, bus)

        Export object to D-Bus and emit a signal that it was added.

        ObjectManager must be exported first.

        Path should be a subpath of where ObjectManager was exported.
        Example, if ObjectManager exported to ``/object/manager``, the managed
        object can be exported at ``/object/manager/test``.

        ObjectManager will keep the reference to the object.

        Returns a handle that can be used to remove object from D-Bus and
        drop reference to it by either using it as a context manager or
        by calling ``.stop()`` method of the handle. Signal will be emitted
        once the object is stopped being exported.

        .. code-block:: python

            manager = DbusObjectManagerInterfaceAsync()
            manager.export_to_dbus('/object/manager')

            with manager.export_with_manager("/object/manager/example", dbus_object):
                # dbus_object can be called from D-Bus inside this
                # with block.
                ...

            # Removed signal will be emitted once the with block exits

            ...

            handle = manager.export_with_manager("/object/manager/example", dbus_object2)
            # dbus_object2 can be called from D-Bus between these statements
            handle.stop()
            # Removed signal will be emitted once the .stop() method is called

        If the handle is discarded the object will remain exported until
        it gets removed from manager with :py:meth:`remove_managed_object` and
        the object gets deallocated.

        *Changed in version 0.12.0:* Added a handle return.

        :param str object_path:
            Object path that it will be available at.

        :param DbusInterfaceCommonAsync object_to_export:
            Object to export to D-Bus.

        :param SdBus bus:
            Optional D-Bus connection object.
            If not passed the default D-Bus will be used.

        :raises RuntimeError: ObjectManager was not exported.
        :return: Handle to control the export.

    .. py:method:: remove_managed_object(managed_object)

        Emit signal that object was removed.

        Releases reference to the object.

        .. caution::
            The object will still be accessible over D-Bus until
            all references to it will be removed.

        :param DbusInterfaceCommonAsync managed_object:
            Object to remove from ObjectManager.

        :raises RuntimeError: ObjectManager was not exported.
        :raises KeyError: Passed object is not managed by ObjectManager.

Decorators
++++++++++++++++++++++++

.. py:decorator:: dbus_method_async([input_signature, [result_signature, [flags, [result_args_names, [input_args_names, [method_name]]]]]])

    Define a method.

    Underlying function must be a coroutine function.

    :param str input_signature: D-Bus input signature.
        Defaults to "" meaning method takes no arguments.
        Required if you intend to connect to a remote object.

    :param str result_signature: D-Bus result signature.
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

    :param str method_name: Force specific D-Bus method name
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
                                                    # introspection data.
            )
            async def upper(self, str_to_up: str) -> str:
                return str_to_up.upper()



.. py:decorator:: dbus_property_async(property_signature, [flags, [property_name]])

    Declare a D-Bus property.

    The underlying function has to be a regular ``def`` function.

    The property will be read-only or read/write based on if setter was
    declared.

    .. warning:: Properties are supposed 
        to be lightweight to get or set. 
        Make sure property getter or setter
        does not perform heavy IO or computation
        as that will block other methods or properties.

    :param str property_signature: Property D-Bus signature.
        Has to be a single type or container.

    :param int flags: modifies behavior.
        No effect on remote connections.
        Defaults to 0 meaning no special behavior.

        See :ref:`dbus-flags` .

    :param str property_name: Force specific property name
        instead of constructing it based on Python function name.

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

    .. py:class:: DbusPropertyAsync

        Properties have following methods:

        .. py:decoratormethod:: setter(set_function)

            Defines the setter function.
            This makes the property read/write instead of read-only.

            See example on how to use.

        .. py:decoratormethod:: setter_private(set_function)

            Defines the private setter function.
            The setter can be called locally but property
            will be read-only from D-Bus.

            Calling the setter locally will emit
            :py:attr:`properties_changed <DbusInterfaceCommonAsync.properties_changed>`
            signal to D-Bus.

            *Changed in version 0.12.0:* can now be used in overrides.

        .. py:method:: get_async()
            :async:

            Get the property value.

            The property can also be directly ``await`` ed
            instead of calling this method.

        .. py:method:: set_async(new_value)
            :async:

            Set property value.




.. py:decorator:: dbus_signal_async([signal_signature, [signal_args_names, [flags, [signal_name]]]])

    Defines a D-Bus signal.

    Underlying function return type hint is used for signal type hints.

    :param str signal_signature: signal D-Bus signature.
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

    Example::

        from sdbus import DbusInterfaceCommonAsync, dbus_signal_async


        class ExampleInterface(DbusInterfaceCommonAsync,
                               interface_name='org.example.signal'
                               ):

            @dbus_signal_async('s')
            def name_changed(self) -> str:
                raise NotImplementedError

    .. py:class:: DbusSignalAsync

        Signals have following methods:

        .. py:method:: catch()

            Catch D-Bus signals using the async generator for loop:
            ``async for x in something.some_signal.catch():``

            This is main way to await for new events.

            Both remote and local objects operate the same way.

            Signal objects can also be async iterated directly:
            ``async for x in something.some_signal``

        .. py:method:: catch_anywhere(service_name, bus)

            Catch signal independent of path.
            Yields tuple of path of the object that emitted signal and signal data.

            ``async for path, data in something.some_signal.catch_anywhere():``

            This method can be called from both an proxy object and class.
            However, it cannot be called on local objects and will raise
            ``NotImplementedError``.

            :param str service_name:
                Service name of which signals belong to.
                Required if called from class. When called from proxy object
                the service name of the proxy will be used.

            :param str bus:
                Optional D-Bus connection object.
                If not passed when called from proxy the bus connected
                to proxy will be used or when called from class default
                bus will be used.

        .. py:method:: emit(args)

            Emit a new signal with *args* data.



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
