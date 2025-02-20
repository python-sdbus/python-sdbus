Utilities
=========

Parsing utilities
+++++++++++++++++

Parse unweildy D-Bus structures in to Python native objects and names.
Available under ``sdbus.utils.parse`` subpackage.

.. py:currentmodule:: sdbus.utils.parse

.. py:function:: parse_properties_changed(interface, properties_changed_data, on_unknown_member='error')

    Parse data from :py:meth:`properties_changed <sdbus.DbusInterfaceCommonAsync.properties_changed>` signal.

    Member names will be translated to python defined names.
    Invalidated properties will have a value of None.

    :param DbusInterfaceBaseAsync interface: Takes either D-Bus interface or interface class.
    :param Tuple properties_changed_data: Tuple caught from signal.
    :param str on_unknown_member: If an unknown D-Bus property was encountered
            either raise an ``"error"`` (default), ``"ignore"`` the property
            or ``"reuse"`` the D-Bus name for the member.
    :rtype: dict[str, Any]
    :returns: Dictionary of changed properties with keys translated to python
            names. Invalidated properties will have value of None.

.. py:function:: parse_interfaces_added(interfaces, interfaces_added_data, on_unknown_interface='error', on_unknown_member='error')

    Parse data from :py:meth:`interfaces_added <sdbus.DbusObjectManagerInterfaceAsync.interfaces_added>` signal.

    Takes an iterable of D-Bus interface classes (or a single class) and the signal data.
    Returns the path of new object, the class of the added object (if it matched one of passed interface classes)
    and the dictionary of python named properties and their values.

    :param Iterable[DbusInterfaceBaseAsync] interfaces: Possible interfaces that were added.
        Can accept classes with multiple interfaces defined.
    :param Tuple interfaces_added_data: Tuple caught from signal.
    :param str on_unknown_interface: If an unknown D-Bus interface was encountered
            either raise an ``"error"`` (default) or return ``"none"`` instead
            of interface class.
    :param str on_unknown_member: If an unknown D-Bus property was encountered
            either raise an ``"error"`` (default), ``"ignore"`` the property
            or ``"reuse"`` the D-Bus name for the member.
    :rtype: tuple[str, Optional[type[DbusInterfaceBaseAsync]], dict[str, Any]]
    :returns: Path of new added object, object's class (or ``None``) and dictionary
            of python translated members and their values.

.. py:function:: parse_interfaces_removed(interfaces, interfaces_removed_data, on_unknown_interface='error')

    Parse data from :py:meth:`interfaces_added <sdbus.DbusObjectManagerInterfaceAsync.interfaces_removed>` signal.

    Takes an iterable of D-Bus interface classes (or a single class) and the signal data.
    Returns the path of removed object and the class of the added object.
    (if it matched one of passed interface classes)

    :param Iterable[DbusInterfaceBaseAsync] interfaces: Possible interfaces that were removed.
        Can accept classes with multiple interfaces defined.
    :param Tuple interfaces_added_data: Tuple caught from signal.
    :param str on_unknown_member: If an unknown D-Bus interface was encountered
            either raise an ``"error"`` (default) or return ``"none"`` instead
            of interface class.
    :rtype: tuple[str, Optional[type[DbusInterfaceBaseAsync]]]
    :returns: Path of removed object and object's class (or ``None``).

.. py:function:: parse_get_managed_objects(interfaces, managed_objects_data, on_unknown_interface='error', on_unknown_member='error')

    Parse data from :py:meth:`get_managed_objects <sdbus.DbusObjectManagerInterfaceAsync.get_managed_objects>` call.

    Takes an iterable of D-Bus interface classes (or a single class) and the method returned data.
    Returns a dictionary where keys a paths of the managed objects and value is a tuple of class of the object
    and dictionary of its python named properties and their values.

    :param Union[DbusInterfaceBase, Iterable[DbusInterfaceBase], DbusInterfaceBaseAsync, Iterable[DbusInterfaceBaseAsync]] interfaces: Possible interfaces of the managed objects.
        Can accept classes with multiple interfaces defined.
    :param Dict managed_objects_data: Data returned by ``get_managed_objects`` call.
    :param str on_unknown_interface: If an unknown D-Bus interface was encountered
            either raise an ``"error"`` (default) or return ``"none"`` instead
            of interface class.
    :param str on_unknown_member: If an unknown D-Bus property was encountered
            either raise an ``"error"`` (default), ``"ignore"`` the property
            or ``"reuse"`` the D-Bus name for the member.
    :rtype: dict[str, tuple[Optional[type[DbusInterfaceBaseAsync], dict[str, Any]]]]
    :returns: Dictionary where keys are paths and values are tuples of managed objects classes and their properties data.

    *New in version 0.12.0.*

Inspect utilities
+++++++++++++++++

Inspect D-Bus objects and retrieve their D-Bus related attributes
such as D-Bus object paths and etc...
Available under ``sdbus.utils.inspect`` subpackage.

.. py:currentmodule:: sdbus.utils.inspect

.. py:function:: inspect_dbus_path(obj, bus=None)

    Returns the D-Bus path of an object.

    If called on a D-Bus proxy returns path of the proxied object.

    If called on a local D-Bus object returns the exported D-Bus path.
    If object is not exported raises ``LookupError``.

    If called on an object that is unrelated to D-Bus raises ``TypeError``.

    The object's path is inspected in the context of the given bus and if the
    object is attached to a different bus the ``LookupError`` will be raised.
    If the bus argument is not given or is ``None`` the default bus will be
    checked against.

    :param object obj: Object to inspect.
    :param SdBus bus:
        Bus to inspect against.
        If not given or ``None`` the default bus will be used.
    :rtype: str
    :returns: D-Bus path of the object.

    *New in version 0.13.0.*
