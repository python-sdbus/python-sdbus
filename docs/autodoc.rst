Autodoc extensions
==================

Python-sdbus has an extension for Sphinx autodoc that can
document dbus interfaces.

To use it include ``"sdbus.autodoc"`` extension in your
``conf.py`` file.

.. code-block:: python

    extensions = ['sdbus.autodoc']

The extension can document interface class bodies. For example,
`python-sdbus-networkmanager <https://github.com/igo95862/python-sdbus-networkmanager>`_
uses it to document the classes.

.. code-block:: rst

    .. autoclass:: sdbus_async.networkmanager.NetworkManagerDeviceBluetoothInterfaceAsync
        :members:

.. warning:: Autodoc extension is early in development and
    has multiple issues. For example, the inheritance ``:inherited-members:``
    does not work on the dbus elements.
