Common API
=======================

These calls are shared between async and blocking API.

Dbus connections calls
++++++++++++++++++++++++++++++++++

.. py:function:: request_default_bus_name_async(new_name)
    :async:

    Acquire a name on the default bus.

    :param str new_name: the name to acquire.
        Must be a valid dbus service name.

.. py:function:: set_default_bus(new_default)

    Sets default bus.

    Should be called before you create any objects that might use
    default bus.

    :param SdBus new_default: The bus object to set default to.
    :raises RuntimeError: if default bus is already set.

.. py:function:: get_default_bus(new_default)

    Gets default bus.

    :return: default bus
    :rtype: SdBus

.. py:function:: sd_bus_open_user()

    Opens a new user session bus connection.

    :return: session bus
    :rtype: SdBus

.. py:function:: sd_bus_open_system()

    Opens a new system bus connection.

    :return: system bus
    :rtype: SdBus

Helper functions
++++++++++++++++++++++++++++++++++

.. py:function:: encode_object_path(prefix, external)

    Encode that abitrary string as a valid object path prefixed
    with prefix.

    :param str prefix: Prefix path. Must be a valid object path.
    :param str external: Arbitrary string to identify object.
    :return: valid object path
    :rtype: str

    Example on how systemd encodes unit names on dbus ::

        # System uses /org/freedesktop/systemd1/unit as prefix of all units
        # dbus.service is a name of dbus unit but dot . is not a valid object path
        s = encode_object_path('/org/freedesktop/systemd1/unit', 'dbus.service')
        print(s)
        # Prints: /org/freedesktop/systemd1/unit/dbus_2eservice

.. py:function:: decode_object_path(prefix, full_path)

    Decode object name that was encoded with
    :py:func:`encode_object_path`.

    :param str prefix: Prefix path. Must be a valid object path.
    :param str full_path: Full path to be decoded.
    :return: Arbitrary name
    :rtype: str

    Example decoding systemd unit name ::

        s = encode_object_path(
            '/org/freedesktop/systemd1/unit',
            '/org/freedesktop/systemd1/unit/dbus_2eservice'
        )
        print(s)
        # Prints: dbus.service
