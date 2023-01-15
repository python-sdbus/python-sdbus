Welcome to Python-sdbus documentation!
=======================================================

Python-sdbus is the python dbus library that aim to use the modern features of python

* `Asyncio <https://docs.python.org/3/library/asyncio.html>`_
* `Type hints <https://docs.python.org/3/library/typing.html>`_
* `Based on fast sd-bus <https://www.freedesktop.org/software/systemd/man/sd-bus.html>`_
* Unified client/server interface classes. Write interface class once.
* Dbus methods can have keyword and default arguments.

D-Bus
-----------

D-Bus is the inter-process communication standard commonly used on Linux desktop.

This documentation expects you to be familiar with dbus concepts and conventions.

If you are unfamiliar with D-Bus you might want to read following pages:

`Wikipedia page <https://en.wikipedia.org/wiki/D-Bus>`_

`Lennart Poettering post about dbus <https://web.archive.org/web/20200522193008/http://0pointer.net/blog/the-new-sd-bus-api-of-systemd.html>`_

`Dbus specification by freedesktop <https://dbus.freedesktop.org/doc/dbus-specification.html>`_

`Install D-Feet D-Bus debugger and observe services and objects on your dbus <https://wiki.gnome.org/Apps/DFeet>`_


.. toctree::
    :maxdepth: 3
    :caption: Contents:

    general
    common_api
    sync_quick
    sync_api
    asyncio_quick
    asyncio_api
    exceptions
    utils
    examples
    proxies
    code_generator
    autodoc
    unittest
    api_index


Indices and tables
==================

* :ref:`genindex`
* :doc:`/api_index`
* :ref:`search`
