Unit testing
============

Python-sdbus provides several utilities to enable unit testing.

.. py:currentmodule:: sdbus.unittest

.. py:class:: IsolatedDbusTestCase

    Extension of `unittest.IsolatedAsyncioTestCase
    <https://docs.python.org/3/library/unittest.html#unittest.IsolatedAsyncioTestCase>`__
    from standard library.

    Creates an isolated instance of session D-Bus. The D-Bus will be closed
    and cleaned up after tests are finished.

    Requires ``dbus-daemon`` executable be installed.

    Example::

        from sdbus import DbusInterfaceCommonAsync, dbus_method_async
        from sdbus.unittest import IsolatedDbusTestCase

        class TestInterface(DbusInterfaceCommonAsync,
                            interface_name='org.test.test',
                            ):

            @dbus_method_async("s", "s")
            async def upper(self, string: str) -> str:
                """Uppercase the input"""
                return string.upper()

        def initialize_object() -> tuple[TestInterface, TestInterface]:
            test_object = TestInterface()
            test_object.export_to_dbus('/')

            test_object_connection = TestInterface.new_proxy(
            "org.example.test", '/')

            return test_object, test_object_connection


        class TestProxy(IsolatedDbusTestCase):
            async def asyncSetUp(self) -> None:
                await super().asyncSetUp()
                await self.bus.request_name_async("org.example.test", 0)

            async def test_method_kwargs(self) -> None:
                test_object, test_object_connection = initialize_object()

                self.assertEqual(
                    'TEST',
                    await test_object_connection.upper('test'),
                )

    .. py:attribute:: bus
        :type: SdBus

        Bus instance connected to isolated D-Bus environment.

        It is also set as a default bus.

    .. py:method:: assertDbusSignalEmits(signal, timeout=1)

      Assert that a given signal was emitted at least once within the
      given timeout.

      :param signal: D-Bus signal object. Can be a signal from either local or proxy object.
      :param Union[int, float] timeout: Maximum wait time until first captured signal.

      Should be used as an async context manager. The context manager exits as soon
      as first signal is captured.

      The object returned by context manager has following attributes:

      .. py:attribute:: output
        :type: list[Any]

        List of captured data.

      Example::

        async with self.assertDbusSignalEmits(test_object.test_signal) as signal_record:
            test_object.test_signal.emit("test")

        self.assertEqual(["test"], signal_record.output)

      *New in version 0.12.0.*



