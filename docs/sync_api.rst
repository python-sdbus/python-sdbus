Blocking API
============

Classes
+++++++++++++++

.. py:currentmodule:: sdbus

.. py:class:: DbusInterfaceCommon(interface_name)

    Dbus interface class.
    Dbus methods and properties should be defined using
    :py:func:`dbus_property` and :py:func:`dbus_method` decorators.

    :param str interface_name: Sets the dbus interface
        name that will be used for all properties and methods
        defined in the body of the class

    .. py:method:: __init__(service_name, object_path, [bus])

        Init will bind to a remote object

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

    .. py:method:: dbus_ping()
    
        Pings the remote object using dbus.

        Useful to test if remote object is alive.

    .. py:method:: dbus_machine_id()
    
        Returns the machine UUID of the remote object.

        :return: machine UUID
        :rtype: str

    .. py:method:: dbus_introspect()

        Get dbus introspection XML.

        It is users responsibility to parse that data.

        :return: string with introspection XML
        :rtype: str

    Example::

        class ExampleInterface(DbusInterfaceCommon,
                               interface_name='org.example.my'
                               ):

            # Method that takes an integer and does not return anything
            @dbus_method('u')
            def close_notification(self, an_int: int) -> None:
                raise NotImplementedError

            # Method that does not take any arguments and returns a list of str
            @dbus_method()
            def get_capabilities(self) -> List[str]:
                raise NotImplementedError

            # Method that takes a dict of {str: str} and returns an int
            @dbus_method('a{ss}')
            def count_entries(self, a_dict: Dict[str, str]) -> int:
                raise NotImplementedError

            # Read only property of int
            @dbus_property()
            def test_int(self) -> int:
                raise NotImplementedError

            # Read/Write property of str
            @dbus_property('s')
            def test_string(self) -> str:
                raise NotImplementedError


Decorators
+++++++++++++++

.. py:decorator:: dbus_method([input_signature, [flags, [method_name]]])
    
    Define dbus method

    Decorated function becomes linked to dbus method.
    Always use round brackets () even when not passing any arguments.

    :param str input_signature: dbus input signature.
        Defaults to "" meaning method takes no arguments.
        Required if method takes any arguments.

    :param int flags: modifies behaivor.
        No effect on remote connections.
        Defaults to 0 meaning no special behavior.

        See :ref:`dbus-flags` .

    :param str method_name: Explicitly define remote method name.
        Usually not required as remote method name will be constructed
        based on original method name.

    Defining methods example::

        class ExampleInterface(DbusInterfaceCommon,
                               interface_name='org.example.my'
                               ):

            # Method that takes an integer and does not return anything
            @dbus_method('u')
            def close_notification(self, an_int: int) -> None:
                raise NotImplementedError

            # Method that does not take any arguments and returns a list of str
            @dbus_method()
            def get_capabilities(self) -> List[str]:
                raise NotImplementedError

            # Method that takes a dict of {str: str} and returns an int
            @dbus_method('a{ss}')
            def count_entries(self, a_dict: Dict[str, str]) -> int:
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

    Define dbus property

    Property works just like @property decorator would.
    Always use round brackets () even when not passing any arguments.

    Read only property can be indicated by passing empty dbus signature "".

    Trying to assign a read only property will raise :py:exc:`AttributeError`

    :param str property_signature: dbus property signature.
        Empty signature "" indicates read-only property.
        Defaults to empty signature "".
        Required only for writable properties.
    
    :param int flags: modifies behaivor.
        No effect on remote connections.
        Defaults to 0 meaning no special behavior.

        See :ref:`dbus-flags` .

    :param str property_name: Explicitly define remote property name.
        Usually not required as remote property name will be constructed
        based on original method name.

    Defining properties example::

        class ExampleInterface(DbusInterfaceCommon,
                               interface_name='org.example.myproperty'
                               ):

            # Read only property of int
            @dbus_property()
            def test_int(self) -> int:
                raise NotImplementedError

            # Read/Write property of str
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
