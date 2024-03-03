Utilities
=========

Parsing utilities
+++++++++++++++++

.. py:currentmodule:: sdbus.utils

.. py:function:: parse_properties_changed(interface, properties_changed_data, on_unknown_member='error')

    Parse data from :py:meth:`properties_changed <sdbus.DbusInterfaceCommonAsync.properties_changed>` signal.

    Member names will be translated to python defined names.
    Invalidated properties will have a value of None.

    :param DbusInterfaceBaseAsync interface: Takes either D-Bus interface or interface class.
    :param Tuple properties_changed_data: Tuple caught from signal.
    :param str on_unknown_member: If an unknown D-Bus property was encountered
            either raise an ``"error"`` (default), ``"ignore"`` the property
            or ``"reuse"`` the D-Bus name for the member.
    :rtype: Dict[str, Any]
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
    :rtype: Tuple[str, Optional[Type[DbusInterfaceBaseAsync]], Dict[str, Any]]
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
    :rtype: Tuple[str, Optional[Type[DbusInterfaceBaseAsync]]]
    :returns: Path of removed object and object's class (or ``None``).
