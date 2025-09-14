## 0.14.1

### Features

* Added `sdbus.utils.inspect.inspect_dbus_bus` function. Returns a bus object
  used by a proxy or exported local object.

### Fixes

* Fix object manager's `InterfacesRemoved` signal being emitted without having
  interface names. (reported and fixed by @arkq)
* Fixed interface ordering for signals and methods that return interface information
  like `InterfacesAdded` or `GetManagedObjects`. (reported and fixed by @arkq)
* Fixed exported methods callbacks sometimes getting garbage collected before
  reply could be sent. (reported by @arkq)
* Fixed several documentation URLs linking outdated repository. (reported and fixed by @rmelotte)

## 0.14.0

### Minimum requirements raised

* Python 3.9 or higher.

For binary PyPI wheel:

* glibc 2.28 or higher. (Debian 10+, Ubuntu 18.10+, CentOS/RHEL 8+)
* pip 20.3 or higher.
* Added 32 bit ARM (`armv7l`) architecture wheel.

### Default bus changes

Previously the default bus always used the context-local variables
to store the reference to the current default bus. As it turned out
the context tends to be changed a lot which resulted in new buses being
opened multiple times. (reported by @wes8ty)

To avoid this the default bus was changed to be thread-local.
`set_default_bus` will now set the thread-local default bus.
A new function `set_context_default_bus` was added to set the context-local
bus. The `get_default_bus` will return the context-local bus if set or
thread-local otherwise. If no default bus has been set a new thread-local
bus will be initialized and set.

### Code generator

* Code generator will now add manual D-Bus member name override where
  automatic snake_case to CamelCase does not result in the original member name.
  This applies to when member renaming options were used. (reported by @nicomuns)
* Generated code will now use Python 3.9 built-in collections type hints.
  (`typing.List[str]` -> `list[str]`)
* Fixed blocking generated code adding unexpected `result_args_names` keyword.
  (reported by @christophehenry)

### Features

* All `sdbus.utils.parse` functions can now accept the blocking interfaces.
  (requested by @christophehenry)
* Added boolean `use_interface_subsets` option to `sdbus.utils.parse` functions.
  When enabled the subset of interfaces will be considered a valid match.
  (requested by @christophehenry)

### Fixes

* Fixed exceptions mapped by `map_exception_to_dbus_error` not being translated
  from Python to D-Bus errors. This means the Python built-in exceptions will
  now be properly returned as D-Bus errors when raised in exported object callback.
  The built-in exceptions translating as added back in version 0.10.0 but probably
  never worked correctly. (reported by @arkq)
* Fixed not being able to export interfaces with no implemented D-Bus members.
  This also means `export_to_dbus` will only access D-Bus related attributes
  avoiding triggering unrelated `@property` methods.
* Renamed certain internal classes from `Binded` to `Bound` and
  from `DbusSomething` to `DbusMember`. (reported by @souliane,
  implemented by @dragomirecky)

## 0.13.0

### Code generator improvements

* Added interface and member renaming CLI options. `--select-interface`, `--select-method`,
  `--select-property` and `--select-signal` will select a particular interface or member and
  `--set-name` will set the selected interface or member Python name.
* Fix generated D-Bus properties not using emits changed flag by default.
* Fix generated D-Bus methods not using unprivileged flag by default. (reported by @damienklotz77)
* Generated methods and signals will now have result argument names set which will be shown
  in the introspection. (requested by @colazzo)

### New `sdbus.utils.inspect` submodule

Contains inspection utilities.

Current only provides the `inspect_dbus_path` function which will return
the D-Bus path of either proxy or exported object. (requested by )

### New `sdbus.utils.parse` submodule

The existing `parse_properties_changed`, `parse_interfaces_added`, `parse_interfaces_removed` and
`parse_get_managed_objects` have been moved from from `sdbus.utils` to `sdbus.utils.parse`.

For backwards compatibility `sdbus.utils` re-exports those functions but no new exports will be
added to it.

### Fixes

* Fix bus timeouts not being processed on time. (requested by @ofacklam)

## 0.12.0

No changes since 0.12.RC1.

## 0.12.RC1

This version significantly reworked the internal undocumented classes
and functions. If you used the undocumented API you would probably need
to adjust your code. Type checker like `mypy` can be very useful for this.

### Features:

* `@setter_private` can now be used in overrides.
* Added `assertDbusSignalEmits` method to `IsolatedDbusTestCase`.
  Can be used to assert that a D-Bus signal was emitted
  inside the `async with` block.
* Added `sdbus.utils.parse_get_managed_objects` function. Can be
  used to parse the ObjectManager's `get_managed_objects` method
  data to classes and Python attribute names.
* Added a handle that is returned by `export_to_dbus` and `export_with_manager`
  methods. This handle can be used to explicitly control when object is accessible
  from D-Bus. (requested by @dragomirecky)

### Fixes:

* Fixed async D-Bus properties not having a proper generic typing. (reported by @ValdezFOmar)
* Fixed build not working when systemd has a minor version suffix.
* Fixed being unable to name arguments in D-Bus introspection when
  method has no return arguments. (reported by @colazzo)
* Fixed serving D-Bus methods that return a single struct. (reported by @colazzo)
* Fixed sending extremely large D-Bus messages getting stuck. (reported by @colazzo)

## 0.11.1

### Features:

* Improved interface generator handling of multiple uppercase letters
  sequences. For example, `ACTIVATE_CONNECTION` would before be converted
  to `a_c_t_i_v_a_t_e__c_o_n_n_e_c_t_i_o_n` and after to `activate_connection`.
  (reported by @bhattarabi)
* Improved python formatting generated by interface code generator.
* Added option `--block` to generate blocking interface code.
  (requested by @zhanglongqi and @MathisMARION)

### Fixes:

* Fixed docstrings still being present even if python was configured with
  `--without-doc-strings`.
* Fixed interface generator crashing when a rare write-only property is
  encountered. (reported by @gotthardp)
* Fixed async interfaces iterating over all members during initialization.
  (reported by @gotthardp)
* Fixed `TypeError: Dbus type '\x00' is unknown` being raised when trying to read
  from a message more than one time. (reported by @IB1387 and @asmello)
* Fixed missing class body when generating code for interface without members.

## 0.11.0

### Features:

* Added support for `None` signals without data.
* Added boolean flags for the name request functions
  which can be used to specify replacements or queueing.
* Added `sdbus.utils.parse_properties_changed` helper function.
  Parses signal data to python member names and values.
* Added `sdbus.utils.parse_interfaces_added` helper function.
  Parses signal data to path, python class and python member names
  and values.
* Added `sdbus.utils.parse_interfaces_removed` helper function.
  Parses signal data to path and python class.
* Added `setter_private` decorator to async properties. Private
  setter can only be called locally but to D-Bus property will
  appear as read only.
* Added new exceptions for when D-Bus name requests fail.
  * `SdBusRequestNameExistsError`: Someone already owns name.
  * `SdBusRequestNameAlreadyOwnerError`: Caller already owns name.
  * `SdBusRequestNameInQueueError`: Name request queued up.

### Deprecations:

* Moved all exceptions to `sdbus.exceptions` module.
  For backwards compatibility old exceptions will be
  available from the root module until the version `1.0.0`.

### Fixes:

* Fixed autodoc adding `dbus_method` to dbus methods names
* Fix async D-Bus name requests not raising appropriate exceptions.
* Fixed `request_default_bus_name` being an async function.
  For backwards compatibility it returns an awaitable that raises a warning.

## 0.10.2

### Features:

* Added `on_unknown_member` option to the `properties_get_all_dict`
  method. Specifies the action on what to do with unknown property.
  (`"error"` (default), `"ignore"`, `"reuse"`)

### Fixes:

* Fixed autodoc regressions introduced in `0.10.1`.
  Properties and signals headers have been redesigned.
* Fixed PropertiesChanged signal emitting only the newest object
  path.

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
