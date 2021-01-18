Asyncio API
============

Quick start
+++++++++++++++++++++

You need to define an interface class.

Classes
++++++++++++++++++++

.. py:class:: DbusInterfaceCommonAsync(interface_name)

    Dbus async interface class.
    Dbus methods and properties should be defined using
    :py:func:`dbus_property_async`, :py:func:`dbus_signal_async`,
    and :py:func:`dbus_method_async` decorators.

    :param str interface_name: Sets the dbus interface
        name that will be used for all properties, methods
        and signals defined in the body of the class.

    :param bool serving_enabled: If set to :py:obj:`True`
        the interface will not be served on dbus. Mostly used
        for interfaces that sd-bus already provides such as
        ``org.freedesktop.DBus.Peer``.

    .. py:method:: ping()
        :async:
    
        Pings the remote object using dbus.
        Usefull to test if remote object is alive.

    .. py:method:: get_machine_id()
        :async:
    
        Returns the machine UUID of the remote object.
        
        :return: machine UUID
        :rtype: str

    .. py:method:: introspect()
        :async:

        Get dbus introspection XML.
        It is users responsibility to parse that data.

        :return: string with introspection XML
        :rtype: str

    .. py:classmethod:: _connect(bus, service_name, object_path)

        Binds object to a remote dbus object. Local calls
        will be redirected to dbus.

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

    .. py:method:: new_connect(bus, service_name, object_path)

        Create new python object and bypass ``__init__``.

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

    .. py:method:: start_serving(bus, object_path)
        :async:

        Object will apear and become callable on dbus.

        :param str object_path:
            Object path that it will be available at.

        :param SdBus bus:
            Optional dbus connection object.
            If not passed the default dbus will be used.

