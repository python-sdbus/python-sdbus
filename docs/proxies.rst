Interface repository
==========================================

sdbus contains a collection of common and well known interfaces
for you to use.

Async interfaces can be found under ``sdbus.async_proxies`` and blocking
under ``sdbus.proxies``

This page document the asyncio interfaces. Blocking interfaces mirror asyncio
interface with all methods being regular ``def`` functions and no signals.

Freedesktop dbus
+++++++++++++++++++++++++++++++++

This is the dbus daemon interface. Used for querying dbus state.

.. py:class:: FreedesktopDbus

    .. py:method:: __init__([bus])

        Dbus interface object path and service name is
        predetermined.
        (at ``'org.freedesktop.DBus'``, ``'/org/freedesktop/DBus'``)

        :param SdBus bus:
            Optional dbus connection.
            If not passed the default dbus will be used.

    .. py:method:: get_connection_pid(service_name)
        :async:

        Get process ID that owns a specified name.

        :param str service_name: Service name to query.
        :return: PID of name owner
        :rtype: int
        :raises DbusNameHasNoOwnerError: Nobody owns that name

    .. py:method:: get_connection_uid(service_name)
        :async:

        Get process user ID that owns a specified name.

        :param str service_name: Service name to query.
        :return: User ID of name owner
        :rtype: int
        :raises DbusNameHasNoOwnerError: Nobody owns that name

    .. py:method:: get_id()
        :async:

        Returns machine id where bus is run. (stored in ``/etc/machine-id``)

        :return: Machine id
        :rtype: str

    .. py:method:: get_name_owner(service_name)
        :async:

        Returns unique bus name (i.e. ``':1.94'``) for given service name.

        :param str service_name: Service name to query.
        :return: Unique bus name.
        :rtype: str
        :raises DbusNameHasNoOwnerError: Nobody owns that name
    
    .. py:method:: list_activatable_names()
        :async:

        Lists all activatable services names.

        :return: List of all names.
        :rtype: List[str]

    .. py:method:: list_names()
        :async:

        List all services and connections currently
        of the bus.

        :return: List of all current names.
        :rtype: List[str]

    .. py:method:: name_has_owner(service_name)
        :async:

        Return True if someone already owns the name,
        False if nobody does.

        :param str service_name: Service name to query.
        :return: Is the name owned?
        :rtype: bool

    .. py:method:: start_service_by_name(service_name, [flags])
        :async:

        Starts a specified service.

        Flags parameter is not used currently and should be
        omited or set to 0.

        :param str service_name: Service name to start.
        :param int flags: Not used. Omit or pass 0.
        :return: 1 on success, 2 if already started.
        :rtype: int

    .. py:attribute:: features
        :type: List[str]

        List of dbus daemon features.

        Features include:

        * 'AppArmor' - Messages filtered by AppArmor on this bus.
        * 'HeaderFiltering' - Messages are filtered if they have incorrect header fields.
        * 'SELinux' - Messages filtered by SELinux on this bus.
        * 'SystemdActivation' - services activated by systemd if their .service file
            specifies a dbus name.

    .. py:attribute:: name_acquired
        :type: str

        Signal when current process acquires a bus name.

    .. py:attribute:: name_lost
        :type: str

        Signal when current process loses a bus name.

    .. py:attribute:: name_owner_changed
        :type: Tuple[str, str, str]

        Signal when some name on a bus changes owner.

        Is a tuple of:
        
        * The name that acquired or lost
        * Old owner (by unique bus name) or empty string if no one owned it
        * New owner (by unique bus name) or emptry string if no one owns it now
