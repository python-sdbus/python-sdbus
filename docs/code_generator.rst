Interface code generator
========================

Python-sdbus is able to generate the interfaces code from
the dbus introspection XML. Currently only async interfaces
code can be generated and only from XML files. (such as found
under ``/usr/share/dbus-1/interfaces/`` folder)

Running code generator requires
`Jinja2 <https://jinja2docs.readthedocs.io/en/stable/>`_
to be installed.

.. warning:: Do NOT send the generator result to ``exec()`` function.
    Interface code MUST be inspected before running.

To run generator execute the ``sdbus`` module with ``gen-from-file``
first argument and file paths to introspection XML files:

.. code-block:: shell

    python -m sdbus gen-from-file /usr/share/dbus-1/interfaces/org.gnome.Shell.Screenshot.xml

The generated interface code will be printed in to stdout. You
can use shell redirection ``>`` to save it in to file.

Multiple interface files can be passed which generates a file
containing multiple interfaces.
