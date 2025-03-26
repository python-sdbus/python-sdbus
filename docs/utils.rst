Utilities
=========

Parsing utilities
+++++++++++++++++

Parse unweildy D-Bus structures in to Python native objects and names.
Available under ``sdbus.utils.parse`` subpackage.

.. automodule:: sdbus.utils.parse
    :members:

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
