Asyncio advanced topics
+++++++++++++++++++++++++

.. py:currentmodule:: sdbus

Signals without data
^^^^^^^^^^^^^^^^^^^^

D-Bus allows signals to not carry any data. Such signals have the
type signature of ``""``. (empty string)

To emit such signals the :py:meth:`emit <sdbus.emit>` must
be explicitly called with ``None``.

Example of an empty signal::

    from asyncio import new_event_loop
    from sdbus import DbusInterfaceCommonAsync, dbus_signal_async


    class ExampleInterface(
        DbusInterfaceCommonAsync,
        interface_name="org.example.signal"
    ):

        @dbus_signal_async("")
        def name_invalidated(self) -> None:
            raise NotImplementedError


    test_object = ExampleInterface()


    async def emit_empty_signal() -> None:
        test_object.export_to_dbus("/")

        test_object.name_invalidated.emit(None)


    loop = new_event_loop()
    loop.run_until_complete(emit_empty_signal())

