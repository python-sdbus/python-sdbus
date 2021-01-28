General Information
===================

Glossary
+++++++++++++++++++++

* **Signature** dbus type definition. Represented by a string. See :ref:`dbus-types`.


.. _dbus-types:

Dbus types conversion
++++++++++++++++++++++++

`Dbus types reference <https://dbus.freedesktop.org/doc/dbus-specification.html#type-system>`_

.. note:: Python integers are unlimited size but dbus intergers are not.
    All integer types raise :py:exc:`OverflowError` 
    if you try to pass number outside the type size.

    Unsigned integers range is ``0 < (2**bit_size)-1``.

    Signed integers range is ``-(2**(bit_size-1)) < (2**(bit_size-1))-1``.


+-------------+----------+-----------------+--------------------------------------------------------------------+
| Name        | Dbus type| Python type     | Description                                                        |
+=============+==========+=================+====================================================================+
| Boolean     | b        | :py:obj:`bool`  | :py:obj:`True` or :py:obj:`False`                                  |
+-------------+----------+-----------------+--------------------------------------------------------------------+
| Byte        | y        | :py:obj:`int`   | Unsigned 8-bit integer.                                            |
|             |          |                 | **Note:** array of bytes (*ay*) has different type                 |
|             |          |                 | in python domain.                                                  |
+-------------+----------+-----------------+--------------------------------------------------------------------+
| Int16       | n        | :py:obj:`int`   | Signed 16-bit integer.                                             |
+-------------+----------+-----------------+--------------------------------------------------------------------+
| Uint16      | q        | :py:obj:`int`   | Unsigned 16-bit integer.                                           |
+-------------+----------+-----------------+--------------------------------------------------------------------+
| Int32       | i        | :py:obj:`int`   | Signed 32-bit integer.                                             |
+-------------+----------+-----------------+--------------------------------------------------------------------+
| Uint32      | u        | :py:obj:`int`   | Unsigned 32-bit integer.                                           |
+-------------+----------+-----------------+--------------------------------------------------------------------+
| Int64       | x        | :py:obj:`int`   | Signed 64-bit integer.                                             |
+-------------+----------+-----------------+--------------------------------------------------------------------+
| Uint64      | t        | :py:obj:`int`   | Unsigned 64-bit integer.                                           |
+-------------+----------+-----------------+--------------------------------------------------------------------+
| Double      | d        | :py:obj:`float` | Float point number                                                 |
+-------------+----------+-----------------+--------------------------------------------------------------------+
| Unix FD     | h        | :py:obj:`int`   | File descriptor                                                    | 
+-------------+----------+-----------------+--------------------------------------------------------------------+
| String      | s        | :py:obj:`str`   | String                                                             |
+-------------+----------+-----------------+--------------------------------------------------------------------+
| Object      | o        | :py:obj:`str`   | Syntactically correct dbus object path                             |
| Path        |          |                 |                                                                    |
+-------------+----------+-----------------+--------------------------------------------------------------------+
| Signature   | g        | :py:obj:`str`   | Dbus type signature                                                |
+-------------+----------+-----------------+--------------------------------------------------------------------+
| Array       | a        | :py:obj:`list`  | List of some single type.                                          |
|             |          |                 |                                                                    |
|             |          |                 | Example: ``as`` array of strings                                   |
+-------------+----------+-----------------+--------------------------------------------------------------------+
| Byte Array  | ay       | :py:obj:`bytes` | Array of bytes. Not a unique type in dbus but a different type in  |
|             |          |                 | Python. Accepts both :py:obj:`bytes` and :py:obj:`bytearray`.      |
|             |          |                 | Used for binary data.                                              |
+-------------+----------+-----------------+--------------------------------------------------------------------+
| Struct      | ()       | :py:obj:`tuple` | Tuple.                                                             |
|             |          |                 |                                                                    |
|             |          |                 | Example: ``(isax)`` tuple of int, string and array of int.         |
+-------------+----------+-----------------+--------------------------------------------------------------------+
| Dictionary  | a{}      | :py:obj:`dict`  | Dictionary with key type and value type.                           |
|             |          |                 |                                                                    |
|             |          |                 | **Note:** Dictionary is always a part of array.                    |
|             |          |                 | I.E. ``a{si}`` is the dict with string keys and integer values.    |
|             |          |                 | ``{si}`` is NOT a valid signature.                                 |
+-------------+----------+-----------------+--------------------------------------------------------------------+
| Variant     | v        | :py:obj:`tuple` | Unknown type that can be any signle type.                          |
|             |          |                 | In Python represented by a tuple of                                |
|             |          |                 | a signature string and a single type.                              |
|             |          |                 |                                                                    |
|             |          |                 | Example: ``("s", "test")`` variant of a single string              |
+-------------+----------+-----------------+--------------------------------------------------------------------+

.. _blocking-vs-async:

Blocking vs Async
+++++++++++++++++++++

py_sd_bus supports both blocking and async IO.

Regular python functions are always blocking.

Asyncio is a part of python standard library that allows non-blocking io.

`Asyncio documentation <https://docs.python.org/3/library/asyncio.html>`_ 

Generally blocking IO should only be used for simple scripts and programms that interact
with existing dbus objects.

Blocking:
^^^^^^^^^^^^^^^^^^^^^
* Blocking is easier to initiate (no event loop)
* Properties behaive exactly as Python properties do. (i.e. can asing with '=' operator)
* Only allows one request at a time.
* No dbus signals.
* Cannot serve objects, only interact with existing object on dbus.

:doc:`/sync_api`

Asyncio:
^^^^^^^^^^^^^^^^^^^^^^^^
* Calls need to be ``await`` ed.
* Multiple requests at the same time.
* Serve object on dbus for other programms.
* Dbus Signals.

:doc:`/asyncio_api`

Name conversions
+++++++++++++++++++++

Dbus uses CamelCase for method names.

Python uses snake_case.

When decorating a method name will be automatically translated from snake_case
to CamelCase. Example: ``close_notification`` -> ``CloseNotification``

However, all decorators have a parametre to force Dbus name to a specific value.
See API documentation for a particular decorator.


Default bus
++++++++++++++++++++++++++

Most object methods that take a bus as a parametre
will use a default bus connection if a bus object is
not explicitly passed.

Session bus is default bus when running as a user and
system bus otherwise.

:py:func:`request_default_bus_name_async` can be used to acquire
a service name on default bus.

Use :py:func`sd_bus_open_user` and :py:func`sd_bus_open_system` to
acquire a specific bus connection.


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`