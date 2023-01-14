# Deprecation information

## Awaiting on `request_default_bus_name`

By mistake `request_default_bus_name` was made in to async function
even though it was never documented to be one. It is now a blocking
function but returns an awaitable for backwards compatibility.

* **Since**: 0.11.0
* **Warning**: 0.11.0
* **Removed**: 1.0.0

## Importing exceptions from `sdbus` module

All exceptions have been moved to `sdbus.exceptions` to clean up imports.

* **Since**: 0.11.0
* **Warning**: Not possible?
* **Removed**: 1.0.0

## `_connect` and `new_connect` of the `DbusInterfaceCommonAsync` class

Replaced with equivalent `_proxify` and `new_proxy`.

* **Since**: 0.8.4
* **Warning**: 0.9.0
* **Removed**: 1.0.0

## `start_serving` of the `DbusInterfaceCommonAsync` class

Replaced with equivalent but sync `export_to_dbus`.

* **Since**: 0.7.6
* **Warning**: 0.7.6
* **Removed**: 1.0.0
