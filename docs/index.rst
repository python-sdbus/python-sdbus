Welcome to py_sd_bus documentation!
=======================================================

py_sd_bus is the python dbus library that aim to use the modern features of python

* `Asyncio <https://docs.python.org/3/library/asyncio.html>`_
* `Typing <https://docs.python.org/3/library/typing.html>`_
* `Based on fast sd-bus <https://www.freedesktop.org/software/systemd/man/sd-bus.html>`_


.. toctree::
    :maxdepth: 2
    :caption: Contents:

Dbus
-----------

Dbus is the inter-process communication standard commonly used on Linux desktop.

If you are unfamiliar with Dbus you might want to read following pages:

`Wikipedia page <https://en.wikipedia.org/wiki/D-Bus>`_

`Lennart Poettering post about dbus <https://web.archive.org/web/20200522193008/http://0pointer.net/blog/the-new-sd-bus-api-of-systemd.html>`_

`Dbus specification by freedesktop <https://dbus.freedesktop.org/doc/dbus-specification.html>`_


Blocking vs Async
------------------

py_sd_bus supports both blocking and async IO.

Regular python functions are always blocking.

Asyncio is a part of python standard library that allows non-blocking io.

`Asyncio documentation <https://docs.python.org/3/library/asyncio.html>`_ 

Generally blocking IO should only be used for simple scripts and programms that interact
with existing dbus objects.

Blocking:
++++++++++++++++
* Blocking is easier to initiate (no event loop)
* Properties behaive exactly as Python properties do. (i.e. can asing with '=' operator)
* Only allows one request at a time.
* No dbus signals.
* Cannot serve objects, only interact with existing object on dbus.

Asyncio:
++++++++++++++++
* Calls need to be ``await`` ed.
* Multiple requests at the same time.
* Serve object on dbus for other programms.
* Dbus Signals.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`