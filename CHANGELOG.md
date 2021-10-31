## 0.8.3

### Features:

* Added `gen-from-connection` command to module that generates interface
  classes from run-time introspection. Takes service name and one or
  more object paths as arguments. Outputs to stdout.
* Added `sd_bus_open_system_remote` call that opens a remote system bus
  through SSH.
* Added `sd_bus_open_system_machine` and `sd_bus_open_user_machine` calls
  that open a bus connection inside systemd-nspawn containers.

### Fixes:

* Typing stub will raise an exception when called in case the C module failed
  to load. This should reduce crypting erros in case the module failure.
* Interface generator now skips standard interfaces such as
  `org.freedesktop.DBus.Introspectable`

## 0.8.2

* Added limited API module.
  This has advantage of working on multiple Python versions but 5% performance penalty.
  PyPI will probably use the limited API module.
* Fixed any libsystemd errors casuing a segmentation fault.

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
