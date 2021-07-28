## 0.8.1

* Fixed unmapped errors not being raised properly.

## 0.8.0

* Added binary packages to PyPI. No more issues with libsystem versions.
* **BREAKING** Moved proxies from `sdbus.proxies`, `sdbus.async_proxies`
    to `sdbus_async` and `sdbus_block`.
* Added `org.freedesktop.DBus.ObjectManager` interface and a base interface with it.
* Added `org.freedesktop.DBus.Properties` interface to base interface.
* Added [autodoc extension](https://python-sdbus.readthedocs.io/en/latest/autodoc.html).
* Added [interface code generator](https://python-sdbus.readthedocs.io/en/latest/code_generator.html).
* Added `request_default_bus_name` to request name on default
    bus in blocking order.
* Added `SdBus.request_name` to requests name in blocking
    order. Usefull to initialize the daemons.
* Fixed any initialized dbus objects never being deleted
    even if there were no more references to them.
