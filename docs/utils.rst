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
    :returns: Dictionary of changed properties with keys translated to python
            names. Invalidated properties will have value of None.
