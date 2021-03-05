Systemd
=====================================

Systemd interfaces and objects.

Systemd Manager
+++++++++++++++++++++++++++++++++++++

Systemd state manager.

This interface is not finished and only has a limited subset of methods and properties.

.. py:class:: SystemdManager

    .. py:method:: __init__([bus])

        Dbus interface object path and service name is
        predetermined.
        (at ``'org.freedesktop.systemd1'``,
        ``'/org/freedesktop/systemd1'``)

        :param SdBus bus:
            Optional dbus connection.
            If not passed the default dbus will be used.

    .. py:method:: list_units()
        :async:

        Lists units.

        This function is not recommended as the output is hard to use.
        See :py:meth:`SystemdManager.list_units_named` .

        :returns: List of unit data.
        :rtype: List[Tuple[str, str, str, str, str, str, str, int, str, str]]
        
    .. py:method:: list_units_named()

        Async iterator over unit data in named tuples.

        Named tuple has following definition: ::

            class SystemdUnitListTuple(NamedTuple):
                primary_name: str
                description: str
                load_state: str
                active_state: str
                sub_state: str
                followed_unit: str
                unit_path: str
                job_id: int
                job_type: str
                job_path: str

        :returns: Async iterator over unit data.
        :rtype: SystemdUnitListTuple

    .. py:method:: subscribe()

        Enables signals.

        :rtype: None

    .. py:method:: unsubscribe()

        Disables signals.

        :rtype: None

    .. py:attribute:: version
        :type: str

        Systemd version.

    .. py:attribute:: unit_new
        :type: Tuple[str, str]

        Signal when new systemd unit loads in to memory.
        Data is unit name and dbus path. 

        This signal **only works** after :py:meth:`SystemdManager.subscribe` had been called.

    .. py:attribute:: unit_removed
        :type: Tuple[str, str]

        Signal when new systemd unit removed from memory.
        Data is unit name and dbus path.

        This signal **only works** after :py:meth:`SystemdManager.subscribe` had been called.

Systemd Unit
+++++++++++++++++++++++++++++++++++++

Systemd unit.

This interface is not finished and only has a limited subset of methods and properties.

.. py:class:: SystemdUnit

    .. py:method:: __init__(unit_name, [bus])

        Create object representing systemd unit.
        Unit name should be passed in full.

        Example: ``'dbus.service'`` is dbus daemon service.

        :param str unit_name: Systemd unit name. 
        :param SdBus bus:
            Optional dbus connection.
            If not passed the default dbus will be used.

    .. py:method:: freeze()
        :async:

        Freeze unit. See systemd documentation.

    .. py:method:: thaw()
        :async:

        Thaw unit. See systemd documentation.

    .. py:method:: kill(kill_who, signal)
        :async:

        Send a signal to a processes of a unit.

        :param str kill_who: Who to send signal.
            Possible values:

            * ``'main'`` - main process of the unit
            * ``'control'`` - control process
            * ``'all'`` - all processes

        :param int signal: Signal to use.

    .. py:method:: start(mode)

        Start unit.

        :param str mode: Start mode of the unit.
            One of:

            * ``'replace'``
            * ``'fail'``
            * ``'isolate'``
            * ``'ignore-dependencies'``
            * ``'ignore-requirements'``
    
    .. py:method:: restart(mode)

        Restart unit.

        :param str mode: See :py:meth:`SystemdUnit.start`

    .. py:method:: stop(mode)

        Stop unit.

        :param str mode: See :py:meth:`SystemdUnit.start` except `'isolate'`.

    .. py:method:: reload(mode)

        Reload unit. Only works if unit is already running.

        :param str mode: See :py:meth:`SystemdUnit.start`

    .. py:method:: reload_or_restart(mode)

        Restart or reload unit.

        :param str mode: See :py:meth:`SystemdUnit.start`

    .. py:method:: reload_or_try_restart(mode)

        Restart or reload unit.

        :param str mode: See :py:meth:`SystemdUnit.start`

    .. py:method:: try_restart(mode)

        Try restart unit.

        :param str mode: See :py:meth:`SystemdUnit.start`

    .. py:method:: reset_failed(mode)

        Reset 'failed' status
    
    .. py:method:: set_properties(is_runtime, properties)

        Sets the unit properties.

        Can either be at runtime or permanent.

        :param bool is_runtime: Runtime or permanent.

    .. py:attribute:: active_state
        :type: str

        Current state of the unit:

        One of:

        * ``'active'``
        * ``'reloading'``
        * ``'inactive'``
        * ``'failed'``
        * ``'activating'``
        * ``'deactivating'``

    .. py:attribute:: sub_state
        :type: str

        Unit type specific state.

        For example, service unit can be ``'running'``.
