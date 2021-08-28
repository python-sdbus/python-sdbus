Interface code generator
========================

Python-sdbus is able to generate the interfaces code from
the D-Bus introspection XML. (either from a file or live object on D-Bus)
Currently only async interfaces code can be generated.

Running code generator requires
`Jinja2 <https://jinja2docs.readthedocs.io/en/stable/>`_
to be installed.

.. warning:: Do NOT send the generator result to ``exec()`` function.
    Interface code MUST be inspected before running.

Generating from XML files
-------------------------

To run generator on files (such as found under ``/usr/share/dbus-1/interfaces/`` folder)
execute the ``sdbus`` module with ``gen-from-file`` first argument
and file paths to introspection XML files:

.. code-block:: shell

    python -m sdbus gen-from-file /usr/share/dbus-1/interfaces/org.gnome.Shell.Screenshot.xml

The generated interface code will be printed in to stdout. You
can use shell redirection ``>`` to save it in to file.

Multiple interface files can be passed which generates a file
containing multiple interfaces.

Generating from run-time introspection
--------------------------------------

To run generator on some service on the D-Bus execute
the ``sdbus`` module with ``gen-from-connection`` first argument,
the service connection name as second and one or more object paths:

.. code-block:: shell

    python -m sdbus gen-from-connection org.freedesktop.systemd1 /org/freedesktop/systemd1

The generated interface code will be printed in to stdout. You
can use shell redirection ``>`` to save it in to file.

Multiple object paths can be passed which generates a file
containing all interfaces encountered in the objects.

Pass ``--system`` option to use system bus instead of session bus.
