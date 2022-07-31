## 0.10.1

### Features:

* Added `catch_anywhere` method to dbus signals.
  Creates an async iterator which yields object path that emitted
  signal and signal data. Can be called from class but requires explicit
  service name in that case.
* Added `properties_get_all_dict()` method to `DbusInterfaceCommonAsync` and
  `DbusInterfaceCommon` classes. Retrieves all D-Bus object properties as
  a dictionary where keys are member names translated to Python names and
  values are property values.

## 0.10.0

### Features:

* **Mapped all built-in Python exceptions to D-Bus errors.**
* **Default bus connection now uses context/thread-local storage.** This is potentially
  breaking in code that used bus in a different threads or contexts.
* Added `map_exception_to_dbus_error` which lets mapping of any exception to D-Bus
  error name.
* D-Bus interfaces and member names are now verified before exporting to D-Bus.
  A helpful error message will be returned if verification fails.
* Added ability to export and track objects with ObjectManager.
* Added `sdbus.unittest.IsolatedDbusTestCase` which is a test case that
  runs on a separated D-Bus instance. Requires `dbus-daemon` command be installed.
* Allow replacing the default bus. Changing default bus will not have effect on
  existing objects which will continue to use the old bus.

### Fixes:

* Fixed non-mapped errors in methods called from D-Bus not returning generic
  error.
* Fixed errors in properties always returning Access Denied instead of specific
  or generic D-Bus errors.
* Fixed `str` and `int` subclasses not being accepted on fast API.
* Fixes trying to process a disconnected bus and causing high CPU usage.
* Marked autodoc extension safe for parallel reading and writing.

## 0.9.0

* **pkg-config is now required** when building from source.
* **Added support for Alpine Linux** and any other distros using elogind instead of systemd.
* Improved PropertiesChanged signal emissions for python objects.
* Fixed python D-Bus methods that return single struct.

## 0.8.5

* Fixed missing header file from the source package.

## 0.8.4

* Deprecated `DbusInterfaceCommonAsync._connect` and `DbusInterfaceCommonAsync.new_connect` in favor
  of `DbusInterfaceCommonAsync._proxify` and `DbusInterfaceCommonAsync.new_proxy` respectively.

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
  to load. This should reduce crypting errors in case the module failure.
* Interface generator now skips standard interfaces such as
  `org.freedesktop.DBus.Introspectable`

## 0.8.2

* Added limited API module.
  This has advantage of working on multiple Python versions but 5% performance penalty.
  PyPI will probably use the limited API module.
* Fixed any libsystemd errors causing a segmentation fault.

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
    order. Useful to initialize the daemons.
* Fixed any initialized dbus objects never being deleted
    even if there were no more references to them.
