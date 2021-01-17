Blocking
========


Decorators
++++++++++

.. py:decorator:: dbus_method([input_signature, [flags, [method_name]]])
    
    Define dbus method

    Decorated function becomes linked to dbus method.
    Always use round brackets () even when not passing any arguments.

    :param str input_signature: dbus input signature.
        Defaults to "" meaning method takes no arguments.
        Required if method takes any arguments.
    :param str method_name: Explicitly define remote method name.
        Usually not required as remote method name will be constructed
        based on original method name.

    Example::

        class NotificationsInterface(DbusInterfaceCommon,
                                     interface_name='org.example.my'
                                    ):

            # Method that takes an integer and does not return anything
            @dbus_method('u')
            def close_notification(self, an_int: int) -> None:
                raise NotImplementedError

            # Method that does not take any arguments and returns a list of str
            @dbus_method()
            def get_capabilities(self) -> List[str]:
                raise NotImplementedError

            # Method that takes a dict of {str: str} and returns an int
            @dbus_method('a{ss}')
            def count_entries(self, a_dict: Dict[str, str]) -> int:
                raise NotImplementedError

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
