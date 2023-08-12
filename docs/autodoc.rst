Autodoc extensions
==================

Python-sdbus has an extension for Sphinx autodoc that can
document D-Bus interfaces.

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
    does not work on the D-Bus elements.

Writing docstrings
-------------------

The D-Bus methods should be documented same way as the regular function
would. See `Sphinx documentation on possible fields \
<https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#info-field-lists>`_

Example docstring for a D-Bus method:

.. code-block:: python

    @dbus_method_async('s', method_name='GetConnectionUnixProcessID')
    async def get_connection_pid(self, service_name: str) -> int:
        """Get process ID that owns a specified name.

        :param service_name: Service name to query.
        :return: PID of name owner
        :raises DbusNameHasNoOwnerError: Nobody owns that name
        """
        raise NotImplementedError

D-Bus properties and signals will be annotated with type taken from the
stub function.

.. code-block:: python

    @dbus_property_async('as')
    def features(self) -> List[str]:
        """List of D-Bus daemon features.

        Features include:

        * 'AppArmor' - Messages filtered by AppArmor on this bus.
        * 'HeaderFiltering' - Messages are filtered if they have incorrect \
                              header fields.
        * 'SELinux' - Messages filtered by SELinux on this bus.
        * 'SystemdActivation' - services activated by systemd if their \
                               .service file specifies a D-Bus name.
        """
        raise NotImplementedError

No parameters are supported at the moment for properties and signals.
