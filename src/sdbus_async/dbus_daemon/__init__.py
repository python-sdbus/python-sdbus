# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2020, 2021 igo95862

# This file is part of python-sdbus

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
from __future__ import annotations

from typing import List, Optional, Tuple

from sdbus.sd_bus_internals import SdBus

from sdbus import (
    DbusInterfaceCommonAsync,
    dbus_method_async,
    dbus_property_async,
    dbus_signal_async,
)


class FreedesktopDbus(DbusInterfaceCommonAsync,
                      interface_name='org.freedesktop.DBus'):
    """D-Bus daemon."""

    def __init__(self, bus: Optional[SdBus] = None):
        """This is the dbus daemon interface. Used for querying dbus state.

        Dbus interface object path and service name is
        predetermined.
        (at ``'org.freedesktop.DBus'``, ``'/org/freedesktop/DBus'``)

        :param bus:
            Optional dbus connection.
            If not passed the default dbus will be used.
        """
        super().__init__()
        self._connect(
            'org.freedesktop.DBus',
            '/org/freedesktop/DBus',
            bus,
        )

    @dbus_method_async('s', method_name='GetConnectionUnixProcessID')
    async def get_connection_pid(self, service_name: str) -> int:
        """Get process ID that owns a specified name.

        :param service_name: Service name to query.
        :return: PID of name owner
        :raises DbusNameHasNoOwnerError: Nobody owns that name
        """
        raise NotImplementedError

    @dbus_method_async('s', method_name='GetConnectionUnixUser')
    async def get_connection_uid(self, service_name: str) -> int:
        """Get process user ID that owns a specified name.

        :param service_name: Service name to query.
        :return: User ID of name owner
        :raises DbusNameHasNoOwnerError: Nobody owns that name
        """
        raise NotImplementedError

    @dbus_method_async()
    async def get_id(self) -> str:
        """Returns machine id where bus is run. (stored in ``/etc/machine-id``)

        :return: Machine id
        """
        raise NotImplementedError

    @dbus_method_async('s')
    async def get_name_owner(self, service_name: str) -> str:
        """Returns unique bus name (i.e. ``':1.94'``) for given service name.

        :param service_name: Service name to query.
        :return: Unique bus name.
        :raises DbusNameHasNoOwnerError: Nobody owns that name
        """
        raise NotImplementedError

    @dbus_method_async()
    async def list_activatable_names(self) -> List[str]:
        """Lists all activatable services names.

        :return: List of all names.
        """
        raise NotImplementedError

    @dbus_method_async()
    async def list_names(self) -> List[str]:
        """List all services and connections currently of the bus.

        :return: List of all current names.
        """
        raise NotImplementedError

    @dbus_method_async('s')
    async def name_has_owner(self, service_name: str) -> bool:
        """
        Return True if someone already owns the name,
        False if nobody does.

        :param service_name: Service name to query.
        :return: Is the name owned?
        """
        raise NotImplementedError

    @dbus_method_async('su')
    async def start_service_by_name(
            self,
            service_name: str,
            flags: int = 0) -> int:
        """Starts a specified service.

        Flags parameter is not used currently and should be
        omitted or set to 0.

        :param service_name: Service name to start.
        :param flags: Not used. Omit or pass 0.
        :return: 1 on success, 2 if already started.
        """
        raise NotImplementedError

    @dbus_property_async('as')
    def features(self) -> List[str]:
        """List of dbus daemon features.

        Features include:

        * 'AppArmor' - Messages filtered by AppArmor on this bus.
        * 'HeaderFiltering' - Messages are filtered if they have incorrect \
                              header fields.
        * 'SELinux' - Messages filtered by SELinux on this bus.
        * 'SystemdActivation' - services activated by systemd if their \
                               .service file specifies a dbus name.
        """
        raise NotImplementedError

    @dbus_property_async('as')
    def interfaces(self) -> List[str]:
        """Extra dbus daemon interfaces"""
        raise NotImplementedError

    @dbus_signal_async()
    def name_acquired(self) -> str:
        """Signal when current process acquires a bus name."""
        raise NotImplementedError

    @dbus_signal_async()
    def name_lost(self) -> str:
        """Signal when current process loses a bus name."""
        raise NotImplementedError

    @dbus_signal_async()
    def name_owner_changed(self) -> Tuple[str, str, str]:
        """Signal when some name on a bus changes owner.

        Is a tuple of:

        * The name that acquired or lost
        * Old owner (by unique bus name) or empty string if no one owned it
        * New owner (by unique bus name) or empty string if no one owns it now
        """
        raise NotImplementedError
