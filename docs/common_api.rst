Common API
=======================

These calls are shared between async and blocking API.

.. py:currentmodule:: sdbus

Dbus connections calls
++++++++++++++++++++++++++++++++++

.. py:function:: request_default_bus_name_async(new_name)
    :async:

    Acquire a name on the default bus async.

    :param str new_name: the name to acquire.
        Must be a valid dbus service name.

.. py:function:: request_default_bus_name(new_name)

    Acquire a name on the default bus.

    :param str new_name: the name to acquire.
        Must be a valid dbus service name.

.. py:function:: set_default_bus(new_default)

    Sets default bus.

    Should be called before you create any objects that might use
    default bus.

    Default bus can be replaced but the change will only affect
    newly created objects.

    :param SdBus new_default: The bus object to set default to.

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

.. py:function:: sd_bus_open_system_remote(host)

    Opens a new system bus connection on a remote host
    through SSH. Host can be prefixed with ``username@`` and
    followed by ``:port`` and ``/machine_name`` as in
    ``systemd-nspawn`` container name.

    :param str host: Host name to connect.
    :return: Remote system bus
    :rtype: SdBus

.. py:function:: sd_bus_open_system_machine(machine)

    Opens a new system bus connection in a systemd-nspawn
    container. Machine name can be prefixed with ``username@``.
    Special machine name ``.host`` indicates local system.

    :param str machine: Machine (container) name.
    :return: Remote system bus
    :rtype: SdBus

.. py:function:: sd_bus_open_user_machine(machine)

    Opens a new user session bus connection in a systemd-nspawn
    container. Opens root user bus session or can be
    prefixed with ``username@`` for a specific user.

    :param str machine: Machine (container) name.
    :return: Remote system bus
    :rtype: SdBus

Helper functions
++++++++++++++++++++++++++++++++++

.. py:function:: encode_object_path(prefix, external)

    Encode that arbitrary string as a valid object path prefixed
    with prefix.

    :param str prefix: Prefix path. Must be a valid object path.
    :param str external: Arbitrary string to identify object.
    :return: valid object path
    :rtype: str

    Example on how systemd encodes unit names on dbus: ::

        from sdbus import encode_object_path


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

    Example decoding systemd unit name: ::

        from sdbus import decode_object_path


        s = decode_object_path(
            '/org/freedesktop/systemd1/unit',
            '/org/freedesktop/systemd1/unit/dbus_2eservice'
        )
        print(s)
        # Prints: dbus.service


.. _dbus-flags:

Flags
+++++++++++++++++++++++++++++++++++

Flags are :py:obj:`int` values that should be ORed to combine.

Example, :py:obj:`DbusDeprecatedFlag` plus :py:obj:`DbusHiddenFlag`: ``DbusDeprecatedFlag | DbusHiddenFlag``

.. py:data:: DbusDeprecatedFlag
    :type: int

    Mark this method or property as deprecated in introspection data.

.. py:data:: DbusHiddenFlag
    :type: int

    Method or property will not show up in introspection data.

.. py:data:: DbusUnprivilegedFlag
    :type: int

    Mark this method or property as unprivileged. This means anyone can
    call it. Only works for system bus as user session bus is fully
    trusted by default.

.. py:data:: DbusNoReplyFlag
    :type: int

    This method does not have a reply message. It instantly returns
    and does not have any errors.

.. py:data:: DbusPropertyConstFlag
    :type: int

    Mark that this property does not change during object life time.

.. py:data:: DbusPropertyEmitsChangeFlag
    :type: int

    This property emits signal when it changes.

.. py:data:: DbusPropertyEmitsInvalidationFlag
    :type: int

    This property emits signal when it invalidates. (means the value changed
    but does not include new value in the signal)

.. py:data:: DbusPropertyExplicitFlag
    :type: int

    This property is too heavy to calculate so its not included in GetAll method
    call.

.. py:data:: DbusSensitiveFlag
    :type: int

    Data in messages in sensitive and will be scrubbed from memory after message
    is red.
