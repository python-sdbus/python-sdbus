Interfaces repository
==========================================

python-sdbus includes two namespace packages
``sdbus_async`` and ``sdbus_block`` which are used for
proxies.

For example, D-Bus daemon interface (which comes by default)
can be found under
``sdbus_async.dbus_daemon`` for async binds and
``sdbus_block.dbus_daemon`` for blocking binds.

Known proxies
-------------

.. toctree::
  :hidden:

  proxies/dbus

This list contains the known python-sdbus interface
collections:

* :doc:`proxies/dbus`. Built-in.
* `Notifications <https://github.com/igo95862/python-sdbus-notifications>`_.
* `NetworkManager <https://github.com/igo95862/python-sdbus-networkmanager>`_.
