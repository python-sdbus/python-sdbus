Common API
=======================

These calls are shared between async and blocking API.

.. py:function:: request_default_bus_name_async(new_name)
    :async:

    Acquire a name on the default bus.

    :param str new_name: the name to acquire.
        Must be a valid dbus service name.
