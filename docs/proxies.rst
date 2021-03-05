Interface repository
==========================================

sdbus contains a collection of common and well known interfaces
for you to use.

Async interfaces can be found under ``sdbus.async_proxies`` and blocking
under ``sdbus.proxies``

This page document the asyncio interfaces. Blocking interfaces mirror asyncio
interface with all methods being regular ``def`` functions and no signals.

.. py:currentmodule:: sdbus.async_proxies

.. toctree::
    :maxdepth: 2
    :caption: Interfaces:

    proxies/dbus
    proxies/notifications
    proxies/systemd
    proxies/network_manager
