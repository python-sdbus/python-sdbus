Blocking API
============

Classes
+++++++++++++++

.. py:currentmodule:: sdbus

.. py:class:: DbusInterfaceCommon(interface_name)

    D-Bus interface class.
    D-Bus methods and properties should be defined using
    :py:func:`dbus_property` and :py:func:`dbus_method` decorators.

    :param str interface_name: Sets the D-Bus interface
        name that will be used for all properties and methods
        defined in the body of the class

    .. py:method:: __init__(service_name, object_path, [bus])

        Init will create a proxy to a remote object

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

    .. py:method:: dbus_ping()

        Pings the remote service using D-Bus.

        Useful to test if connection or remote service is alive.

        .. warning:: This method is ignores the particular object path
                     meaning it can NOT be used to test if object exist.

    .. py:method:: dbus_machine_id()

        Returns the machine UUID of D-Bus the object is connected to.

        :return: machine UUID
        :rtype: str

    .. py:method:: dbus_introspect()

        Get D-Bus introspection XML.

        It is users responsibility to parse that data.

        :return: string with introspection XML
        :rtype: str

    .. py:method:: properties_get_all_dict()

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

    Example: ::

        from sdbus import (DbusInterfaceCommon,
                           dbus_method, dbus_property)


        class ExampleInterface(DbusInterfaceCommon,
                               interface_name='org.example.my'
                               ):

            # Method that takes an integer and does not return anything
            @dbus_method('u')
            def close_notification(self, an_int: int) -> None:
                raise NotImplementedError

            # Method that does not take any arguments and returns a list of str
            @dbus_method()
            def get_capabilities(self) -> list[str]:
                raise NotImplementedError

            # Method that takes a dict of {str: str} and returns an int
            @dbus_method('a{ss}')
            def count_entries(self, a_dict: dict[str, str]) -> int:
                raise NotImplementedError

            # Read only property of int
            @dbus_property()
            def test_int(self) -> int:
                raise NotImplementedError

            # Read/Write property of str
            @dbus_property('s')
            def test_string(self) -> str:
                raise NotImplementedError


.. py:class:: DbusObjectManagerInterface(interface_name)

    This class is almost identical to :py:class:`DbusInterfaceCommon`
    but implements `ObjectManager <https://dbus.freedesktop.org/doc/dbus-specification.html#standard-interfaces-objectmanager>`_
    interface.

    .. py:method:: get_managed_objects()

        Get the objects this object manager in managing.

        :return:
            Triple nested dictionary that contains all the objects
            paths with their properties values.

            dict[ObjectPath, dict[InterfaceName, dict[PropertyName, PropertyValue]]]

        :rtype: dict[str, dict[str, dict[str, Any]]]

Decorators
+++++++++++++++

.. py:decorator:: dbus_method([input_signature, [flags, [method_name]]])

    Define D-Bus method

    Decorated function becomes linked to D-Bus method.
    Always use round brackets () even when not passing any arguments.

    :param str input_signature: D-Bus input signature.
        Defaults to "" meaning method takes no arguments.
        Required if method takes any arguments.

    :param int flags: modifies behavior.
        No effect on remote connections.
        Defaults to 0 meaning no special behavior.

        See :ref:`dbus-flags` .

    :param str method_name: Explicitly define remote method name.
        Usually not required as remote method name will be constructed
        based on original method name.

    Defining methods example: ::

        from sdbus import DbusInterfaceCommon, dbus_method


        class ExampleInterface(DbusInterfaceCommon,
                               interface_name='org.example.my'
                               ):

            # Method that takes an integer and does not return anything
            @dbus_method('u')
            def close_notification(self, an_int: int) -> None:
                raise NotImplementedError

            # Method that does not take any arguments and returns a list of str
            @dbus_method()
            def get_capabilities(self) -> list[str]:
                raise NotImplementedError

            # Method that takes a dict of {str: str} and returns an int
            @dbus_method('a{ss}')
            def count_entries(self, a_dict: dict[str, str]) -> int:
                raise NotImplementedError

    Calling methods example::

        # Initialize the object
        d = ExampleInterface(
            service_name='org.example.test',
            object_path='/',
        )

        d.close_notification(1234)

        l = d.get_capabilities()

        d.count_entries({'a': 'asdasdasd', 'b': 'hgterghead213d'})


.. py:decorator:: dbus_property([property_signature, [flags, [property_name]]])

    Define D-Bus property

    Property works just like @property decorator would.
    Always use round brackets () even when not passing any arguments.

    Read only property can be indicated by passing empty D-Bus signature "".

    Trying to assign a read only property will raise :py:exc:`AttributeError`

    :param str property_signature: D-Bus property signature.
        Empty signature "" indicates read-only property.
        Defaults to empty signature "".
        Required only for writable properties.

    :param int flags: modifies behavior.
        No effect on remote connections.
        Defaults to 0 meaning no special behavior.

        See :ref:`dbus-flags` .

    :param str property_name: Explicitly define remote property name.
        Usually not required as remote property name will be constructed
        based on original method name.

    Defining properties example: ::

        from sdbus import DbusInterfaceCommon, dbus_property


        class ExampleInterface(DbusInterfaceCommon,
                               interface_name='org.example.myproperty'
                               ):

            # Property of int
            @dbus_property('i')
            def test_int(self) -> int:
                raise NotImplementedError

            # Property of str
            @dbus_property('s')
            def test_string(self) -> str:
                raise NotImplementedError

    Properties usage example::

        # Initialize the object
        d = ExampleInterface(
            service_name='org.example.test',
            object_path='/',
        )

        # Print the int
        print(d.test_int)

        # Assign new string
        d.test_string = 'some_string'

        # Print it
        print(d.test_string)


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
