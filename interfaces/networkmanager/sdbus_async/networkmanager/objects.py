

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

from typing import Optional

from sdbus.sd_bus_internals import SdBus

from .interfaces_devices import (NetworkManagerDeviceBluetoothInterfaceAsync,
                                 NetworkManagerDeviceBondInterfaceAsync,
                                 NetworkManagerDeviceBridgeInterfaceAsync,
                                 NetworkManagerDeviceGenericInterfaceAsync,
                                 NetworkManagerDeviceInterfaceAsync,
                                 NetworkManagerDeviceIPTunnelInterfaceAsync,
                                 NetworkManagerDeviceMacsecInterfaceAsync,
                                 NetworkManagerDeviceMacvlanInterfaceAsync,
                                 NetworkManagerDeviceModemInterfaceAsync,
                                 NetworkManagerDeviceOlpcMeshInterfaceAsync,
                                 NetworkManagerDeviceOvsBridgeInterfaceAsync,
                                 NetworkManagerDeviceOvsPortInterfaceAsync,
                                 NetworkManagerDeviceStatisticsInterfaceAsync,
                                 NetworkManagerDeviceTeamInterfaceAsync,
                                 NetworkManagerDeviceTunInterfaceAsync,
                                 NetworkManagerDeviceVethInterfaceAsync,
                                 NetworkManagerDeviceVlanInterfaceAsync,
                                 NetworkManagerDeviceVrfInterfaceAsync,
                                 NetworkManagerDeviceVxlanInterfaceAsync,
                                 NetworkManagerDeviceWifiP2PInterfaceAsync,
                                 NetworkManagerDeviceWiredInterfaceAsync,
                                 NetworkManagerDeviceWireGuardInterfaceAsync,
                                 NetworkManagerDeviceWirelessInterfaceAsync,
                                 NetworkManagerPPPInterfaceAsync)
from .interfaces_other import (NetworkManagerAccessPointInterfaceAsync,
                               NetworkManagerCheckpointInterfaceAsync,
                               NetworkManagerConnectionActiveInterfaceAsync,
                               NetworkManagerDHCP4ConfigInterfaceAsync,
                               NetworkManagerDHCP6ConfigInterfaceAsync,
                               NetworkManagerDnsManagerInterfaceAsync,
                               NetworkManagerInterfaceAsync,
                               NetworkManagerIP4ConfigInterfaceAsync,
                               NetworkManagerIP6ConfigInterfaceAsync,
                               NetworkManagerSecretAgentManagerInterfaceAsync,
                               NetworkManagerSettingsConnectionInterfaceAsync,
                               NetworkManagerSettingsInterfaceAsync,
                               NetworkManagerVPNConnectionInterfaceAsync,
                               NetworkManagerWifiP2PPeerInterfaceAsync)

NETWORK_MANAGER_SERVICE_NAME = 'org.freedesktop.NetworkManager'


class NetworkManager(NetworkManagerInterfaceAsync):
    """Network Manger main object

    Implements :py:class:`NetworkManagerInterface`

    Service name ``'org.freedesktop.NetworkManager'``
    and object path ``/org/freedesktop/NetworkManager`` is predetermined.
    """

    def __init__(self, bus: Optional[SdBus] = None) -> None:
        """
        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            '/org/freedesktop/NetworkManager',
            bus)


class NetworkManagerAgentManager(
        NetworkManagerSecretAgentManagerInterfaceAsync):
    """NetworkManager secrets manager

    Implements :py:class:`NetworkManagerSecretAgentManagerInterface`.

    Service name ``'org.freedesktop.NetworkManager'``
    and object path ``/org/freedesktop/NetworkManager/AgentManager``
    is predetermined.
    """

    def __init__(self, bus: Optional[SdBus] = None) -> None:
        """
        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            '/org/freedesktop/NetworkManager/AgentManager',
            bus)


class NetworkManagerDnsManager(NetworkManagerDnsManagerInterfaceAsync):
    """NetworkManager DNS manager

    Implements :py:class:`NetworkManagerDnsManagerInterface`.

    Service name ``'org.freedesktop.NetworkManager'``
    and object path ``/org/freedesktop/NetworkManager/DnsManager``
    is predetermined.
    """

    def __init__(self, bus: Optional[SdBus] = None) -> None:
        """
        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            '/org/freedesktop/NetworkManager/DnsManager',
            bus)


class NetworkManagerSettings(NetworkManagerSettingsInterfaceAsync):
    """NetworkManager settings

    Implements :py:class:`NetworkManagerSettingsInterface`.

    Service name ``'org.freedesktop.NetworkManager'``
    and object path ``/org/freedesktop/NetworkManager/DnsManager``
    is predetermined.
    """

    def __init__(self, bus: Optional[SdBus] = None) -> None:
        """
        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            '/org/freedesktop/NetworkManager/Settings',
            bus)


class NetworkConnectionSettings(
        NetworkManagerSettingsConnectionInterfaceAsync):
    """Setting of specific connection

    Implements :py:class:`NetworkManagerSettingsConnectionInterface`
    """

    def __init__(self, settings_path: str,
                 bus: Optional[SdBus] = None) -> None:
        """
        :param settings_path: D-Bus path to settings object. \
            Usually obtained from \
            :py:attr:`NetworkManagerDeviceInterfaceAsync.active_connection`

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            settings_path,
            bus)


class NetworkDeviceGeneric(
        NetworkManagerDeviceInterfaceAsync,
        NetworkManagerDeviceStatisticsInterfaceAsync,
        NetworkManagerDeviceGenericInterfaceAsync):
    """Generic device

    Implements :py:class:`NetworkManagerDeviceInterfaceAsync`, \
    :py:class:`NetworkManagerDeviceStatisticsInterfaceAsync` and \
    :py:class:`NetworkManagerDeviceGenericInterfaceAsync`
    """

    def __init__(self, device_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param device_path: D-Bus path to device object. \
            Obtained from \
            :py:meth:`NetworkManagerInterface.get_devices` or \
            :py:meth:`NetworkManagerInterface.get_device_by_ip_iface`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceWired(
        NetworkManagerDeviceInterfaceAsync,
        NetworkManagerDeviceStatisticsInterfaceAsync,
        NetworkManagerDeviceWiredInterfaceAsync):
    """Ethernet device

    Implements :py:class:`NetworkManagerDeviceInterfaceAsync`, \
    :py:class:`NetworkManagerDeviceStatisticsInterfaceAsync` and \
    :py:class:`NetworkManagerDeviceWiredInterfaceAsync`
    """

    def __init__(self, device_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param device_path: D-Bus path to device object. \
            Obtained from \
            :py:meth:`NetworkManagerInterface.get_devices` or \
            :py:meth:`NetworkManagerInterface.get_device_by_ip_iface`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceWireless(
        NetworkManagerDeviceInterfaceAsync,
        NetworkManagerDeviceStatisticsInterfaceAsync,
        NetworkManagerDeviceWirelessInterfaceAsync):
    """WiFi device

    Implements :py:class:`NetworkManagerDeviceInterfaceAsync`, \
    :py:class:`NetworkManagerDeviceStatisticsInterfaceAsync` and \
    :py:class:`NetworkManagerDeviceWirelessInterfaceAsync`
    """

    def __init__(self, device_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param device_path: D-Bus path to device object. \
            Obtained from \
            :py:meth:`NetworkManagerInterface.get_devices` or \
            :py:meth:`NetworkManagerInterface.get_device_by_ip_iface`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceBluetooth(
        NetworkManagerDeviceInterfaceAsync,
        NetworkManagerDeviceStatisticsInterfaceAsync,
        NetworkManagerDeviceBluetoothInterfaceAsync):
    """Bluetooth device

    Implements :py:class:`NetworkManagerDeviceInterfaceAsync`, \
    :py:class:`NetworkManagerDeviceStatisticsInterfaceAsync` and \
    :py:class:`NetworkManagerDeviceBluetoothInterfaceAsync`
    """

    def __init__(self, device_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param device_path: D-Bus path to device object. \
            Obtained from \
            :py:meth:`NetworkManagerInterface.get_devices` or \
            :py:meth:`NetworkManagerInterface.get_device_by_ip_iface`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceBond(
        NetworkManagerDeviceInterfaceAsync,
        NetworkManagerDeviceStatisticsInterfaceAsync,
        NetworkManagerDeviceBondInterfaceAsync):
    """Bond device

    Implements :py:class:`NetworkManagerDeviceInterfaceAsync`, \
    :py:class:`NetworkManagerDeviceStatisticsInterfaceAsync` and \
    :py:class:`NetworkManagerDeviceBondInterfaceAsync`
    """

    def __init__(self, device_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param device_path: D-Bus path to device object. \
            Obtained from \
            :py:meth:`NetworkManagerInterface.get_devices` or \
            :py:meth:`NetworkManagerInterface.get_device_by_ip_iface`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceBridge(
        NetworkManagerDeviceInterfaceAsync,
        NetworkManagerDeviceStatisticsInterfaceAsync,
        NetworkManagerDeviceBridgeInterfaceAsync):
    """Bridge device

    Implements :py:class:`NetworkManagerDeviceInterfaceAsync`, \
    :py:class:`NetworkManagerDeviceStatisticsInterfaceAsync` and \
    :py:class:`NetworkManagerDeviceBridgeInterfaceAsync`
    """

    def __init__(self, device_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param device_path: D-Bus path to device object. \
            Obtained from \
            :py:meth:`NetworkManagerInterface.get_devices` or \
            :py:meth:`NetworkManagerInterface.get_device_by_ip_iface`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceIpTunnel(
        NetworkManagerDeviceInterfaceAsync,
        NetworkManagerDeviceStatisticsInterfaceAsync,
        NetworkManagerDeviceIPTunnelInterfaceAsync):
    """Generic device

    Implements :py:class:`NetworkManagerDeviceInterfaceAsync`, \
    :py:class:`NetworkManagerDeviceStatisticsInterfaceAsync` and \
    :py:class:`NetworkManagerDeviceIPTunnelInterfaceAsync`
    """

    def __init__(self, device_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param device_path: D-Bus path to device object. \
            Obtained from \
            :py:meth:`NetworkManagerInterface.get_devices` or \
            :py:meth:`NetworkManagerInterface.get_device_by_ip_iface`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceMacsec(
        NetworkManagerDeviceInterfaceAsync,
        NetworkManagerDeviceStatisticsInterfaceAsync,
        NetworkManagerDeviceMacsecInterfaceAsync):
    """Macsec device

    Implements :py:class:`NetworkManagerDeviceInterfaceAsync`, \
    :py:class:`NetworkManagerDeviceStatisticsInterfaceAsync` and \
    :py:class:`NetworkManagerDeviceMacsecInterfaceAsync`
    """

    def __init__(self, device_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param device_path: D-Bus path to device object. \
            Obtained from \
            :py:meth:`NetworkManagerInterface.get_devices` or \
            :py:meth:`NetworkManagerInterface.get_device_by_ip_iface`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceMacvlan(
        NetworkManagerDeviceInterfaceAsync,
        NetworkManagerDeviceStatisticsInterfaceAsync,
        NetworkManagerDeviceMacvlanInterfaceAsync):
    """Macvlan device

    Implements :py:class:`NetworkManagerDeviceInterfaceAsync`, \
    :py:class:`NetworkManagerDeviceStatisticsInterfaceAsync` and \
    :py:class:`NetworkManagerDeviceMacvlanInterfaceAsync`
    """

    def __init__(self, device_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param device_path: D-Bus path to device object. \
            Obtained from \
            :py:meth:`NetworkManagerInterface.get_devices` or \
            :py:meth:`NetworkManagerInterface.get_device_by_ip_iface`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceModem(
        NetworkManagerDeviceInterfaceAsync,
        NetworkManagerDeviceStatisticsInterfaceAsync,
        NetworkManagerDeviceModemInterfaceAsync):
    """Generic device

    Implements :py:class:`NetworkManagerDeviceInterfaceAsync`, \
    :py:class:`NetworkManagerDeviceStatisticsInterfaceAsync` and \
    :py:class:`NetworkManagerDeviceModemInterfaceAsync`
    """

    def __init__(self, device_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param device_path: D-Bus path to device object. \
            Obtained from \
            :py:meth:`NetworkManagerInterface.get_devices` or \
            :py:meth:`NetworkManagerInterface.get_device_by_ip_iface`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceOlpcMesh(
        NetworkManagerDeviceInterfaceAsync,
        NetworkManagerDeviceStatisticsInterfaceAsync,
        NetworkManagerDeviceOlpcMeshInterfaceAsync):
    """OLPC wireless mesh device

    Implements :py:class:`NetworkManagerDeviceInterfaceAsync`, \
    :py:class:`NetworkManagerDeviceStatisticsInterfaceAsync` and \
    :py:class:`NetworkManagerDeviceOlpcMeshInterfaceAsync`
    """

    def __init__(self, device_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param device_path: D-Bus path to device object. \
            Obtained from \
            :py:meth:`NetworkManagerInterface.get_devices` or \
            :py:meth:`NetworkManagerInterface.get_device_by_ip_iface`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceOpenVSwitchBridge(
        NetworkManagerDeviceInterfaceAsync,
        NetworkManagerDeviceStatisticsInterfaceAsync,
        NetworkManagerDeviceOvsBridgeInterfaceAsync):
    """Open vSwitch bridge device

    Implements :py:class:`NetworkManagerDeviceInterfaceAsync`, \
    :py:class:`NetworkManagerDeviceStatisticsInterfaceAsync` and \
    :py:class:`NetworkManagerDeviceOvsBridgeInterfaceAsync`
    """

    def __init__(self, device_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param device_path: D-Bus path to device object. \
            Obtained from \
            :py:meth:`NetworkManagerInterface.get_devices` or \
            :py:meth:`NetworkManagerInterface.get_device_by_ip_iface`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceOpenVSwitchPort(
        NetworkManagerDeviceInterfaceAsync,
        NetworkManagerDeviceStatisticsInterfaceAsync,
        NetworkManagerDeviceOvsPortInterfaceAsync):
    """Open vSwitch port device

    Implements :py:class:`NetworkManagerDeviceInterfaceAsync`, \
    :py:class:`NetworkManagerDeviceStatisticsInterfaceAsync` and \
    :py:class:`NetworkManagerDeviceOvsPortInterfaceAsync`
    """

    def __init__(self, device_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param device_path: D-Bus path to device object. \
            Obtained from \
            :py:meth:`NetworkManagerInterface.get_devices` or \
            :py:meth:`NetworkManagerInterface.get_device_by_ip_iface`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceTeam(
        NetworkManagerDeviceInterfaceAsync,
        NetworkManagerDeviceStatisticsInterfaceAsync,
        NetworkManagerDeviceTeamInterfaceAsync):
    """Team device (special Bond device for NetworkManager)

    Implements :py:class:`NetworkManagerDeviceInterfaceAsync`, \
    :py:class:`NetworkManagerDeviceStatisticsInterfaceAsync` and \
    :py:class:`NetworkManagerDeviceTeamInterfaceAsync`
    """

    def __init__(self, device_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param device_path: D-Bus path to device object. \
            Obtained from \
            :py:meth:`NetworkManagerInterface.get_devices` or \
            :py:meth:`NetworkManagerInterface.get_device_by_ip_iface`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceTun(
        NetworkManagerDeviceInterfaceAsync,
        NetworkManagerDeviceStatisticsInterfaceAsync,
        NetworkManagerDeviceTunInterfaceAsync):
    """TUN device

    Implements :py:class:`NetworkManagerDeviceInterfaceAsync`, \
    :py:class:`NetworkManagerDeviceStatisticsInterfaceAsync` and \
    :py:class:`NetworkManagerDeviceTunInterfaceAsync`
    """

    def __init__(self, device_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param device_path: D-Bus path to device object. \
            Obtained from \
            :py:meth:`NetworkManagerInterface.get_devices` or \
            :py:meth:`NetworkManagerInterface.get_device_by_ip_iface`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceVeth(
        NetworkManagerDeviceInterfaceAsync,
        NetworkManagerDeviceStatisticsInterfaceAsync,
        NetworkManagerDeviceVethInterfaceAsync):
    """Virtual Ethernet device

    Implements :py:class:`NetworkManagerDeviceInterfaceAsync`, \
    :py:class:`NetworkManagerDeviceStatisticsInterfaceAsync` and \
    :py:class:`NetworkManagerDeviceVethInterfaceAsync`
    """

    def __init__(self, device_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param device_path: D-Bus path to device object. \
            Obtained from \
            :py:meth:`NetworkManagerInterface.get_devices` or \
            :py:meth:`NetworkManagerInterface.get_device_by_ip_iface`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceVlan(
        NetworkManagerDeviceInterfaceAsync,
        NetworkManagerDeviceStatisticsInterfaceAsync,
        NetworkManagerDeviceVlanInterfaceAsync):
    """VLAN device

    Implements :py:class:`NetworkManagerDeviceInterfaceAsync`, \
    :py:class:`NetworkManagerDeviceStatisticsInterfaceAsync` and \
    :py:class:`NetworkManagerDeviceVlanInterfaceAsync`
    """

    def __init__(self, device_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param device_path: D-Bus path to device object. \
            Obtained from \
            :py:meth:`NetworkManagerInterface.get_devices` or \
            :py:meth:`NetworkManagerInterface.get_device_by_ip_iface`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceVrf(
        NetworkManagerDeviceInterfaceAsync,
        NetworkManagerDeviceStatisticsInterfaceAsync,
        NetworkManagerDeviceVrfInterfaceAsync):
    """VRF (virtual routing) device

    Implements :py:class:`NetworkManagerDeviceInterfaceAsync`, \
    :py:class:`NetworkManagerDeviceStatisticsInterfaceAsync` and \
    :py:class:`NetworkManagerDeviceVrfInterfaceAsync`
    """

    def __init__(self, device_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param device_path: D-Bus path to device object. \
            Obtained from \
            :py:meth:`NetworkManagerInterface.get_devices` or \
            :py:meth:`NetworkManagerInterface.get_device_by_ip_iface`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceVxlan(
        NetworkManagerDeviceInterfaceAsync,
        NetworkManagerDeviceStatisticsInterfaceAsync,
        NetworkManagerDeviceVxlanInterfaceAsync):
    """VXLAN device

    Implements :py:class:`NetworkManagerDeviceInterfaceAsync`, \
    :py:class:`NetworkManagerDeviceStatisticsInterfaceAsync` and \
    :py:class:`NetworkManagerDeviceVxlanInterfaceAsync`
    """

    def __init__(self, device_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param device_path: D-Bus path to device object. \
            Obtained from \
            :py:meth:`NetworkManagerInterface.get_devices` or \
            :py:meth:`NetworkManagerInterface.get_device_by_ip_iface`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceWifiP2P(
        NetworkManagerDeviceInterfaceAsync,
        NetworkManagerDeviceStatisticsInterfaceAsync,
        NetworkManagerDeviceWifiP2PInterfaceAsync):
    """Wifi Peer-to-Peer (P2P) device

    Implements :py:class:`NetworkManagerDeviceInterfaceAsync`, \
    :py:class:`NetworkManagerDeviceStatisticsInterfaceAsync` and \
    :py:class:`NetworkManagerDeviceWifiP2PInterfaceAsync`
    """

    def __init__(self, device_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param device_path: D-Bus path to device object. \
            Obtained from \
            :py:meth:`NetworkManagerInterface.get_devices` or \
            :py:meth:`NetworkManagerInterface.get_device_by_ip_iface`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceWireGuard(
        NetworkManagerDeviceInterfaceAsync,
        NetworkManagerDeviceStatisticsInterfaceAsync,
        NetworkManagerDeviceWireGuardInterfaceAsync):
    """Generic device

    Implements :py:class:`NetworkManagerDeviceInterfaceAsync`, \
    :py:class:`NetworkManagerDeviceStatisticsInterfaceAsync` and \
    :py:class:`NetworkManagerDeviceWireGuardInterfaceAsync`
    """

    def __init__(self, device_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param device_path: D-Bus path to device object. \
            Obtained from \
            :py:meth:`NetworkManagerInterface.get_devices` or \
            :py:meth:`NetworkManagerInterface.get_device_by_ip_iface`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDevicePPP(
        NetworkManagerDeviceInterfaceAsync,
        NetworkManagerDeviceStatisticsInterfaceAsync,
        NetworkManagerPPPInterfaceAsync):
    """PPP device

    Implements :py:class:`NetworkManagerDeviceInterfaceAsync`, \
    :py:class:`NetworkManagerDeviceStatisticsInterfaceAsync` and \
    :py:class:`NetworkManagerPPPInterfaceAsync`
    """

    def __init__(self, device_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param device_path: D-Bus path to device object. \
            Obtained from \
            :py:meth:`NetworkManagerInterface.get_devices` or \
            :py:meth:`NetworkManagerInterface.get_device_by_ip_iface`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class ActiveConnection(NetworkManagerConnectionActiveInterfaceAsync):
    """Active connection object

    Implements :py:class:`NetworkManagerConnectionActiveInterface`
    """

    def __init__(self, connection_path: str,
                 bus: Optional[SdBus] = None) -> None:
        """

        :param connection_path: D-Bus path to connection object. \
            Obtained from \
            :py:meth:`NetworkManagerDeviceInterfaceAsync.active_connection`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            connection_path,
            bus)


class ActiveVPNConnection(
        ActiveConnection,
        NetworkManagerVPNConnectionInterfaceAsync):
    """Active VPN connection object

    Implements :py:class:`NetworkManagerConnectionActiveInterface`
    and :py:class:`NetworkManagerVPNConnectionInterface`
    """
    ...


class IPv4Config(NetworkManagerIP4ConfigInterfaceAsync):
    """IPv4 configuration interface

    Implements :py:class:`NetworkManagerIP4ConfigInterface`
    """

    def __init__(self, ip4_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param ip4_path: D-Bus path to IPv4 config object. \
            Obtained from \
            :py:attr:`NetworkManagerDeviceInterfaceAsync.ip4_config`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            ip4_path,
            bus)


class IPv6Config(NetworkManagerIP6ConfigInterfaceAsync):
    """IPv6 configuration interface

    Implements :py:class:`NetworkManagerIP6ConfigInterface`
    """

    def __init__(self, ip6_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param ip6_path: D-Bus path to IPv6 config object. \
            Obtained from \
            :py:attr:`NetworkManagerDeviceInterfaceAsync.ip4_config`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            ip6_path,
            bus)


class DHCPv4Config(NetworkManagerDHCP4ConfigInterfaceAsync):
    """DHCPv4 configuration interface

    Implements :py:class:`NetworkManagerDHCP4ConfigInterface`
    """

    def __init__(self, dhcp4_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param dhcp4_path: D-Bus path to DHCPv4 config object. \
            Obtained from \
            :py:attr:`NetworkManagerDeviceInterfaceAsync.dhcp4_config`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            dhcp4_path,
            bus)


class DHCPv6Config(NetworkManagerDHCP6ConfigInterfaceAsync):
    """DHCPv6 configuration interface

    Implements :py:class:`NetworkManagerDHCP6ConfigInterface`
    """

    def __init__(self, dhcpv6_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param dhcpv6_path: D-Bus path to DHCPv6 config object. \
            Obtained from \
            :py:attr:`NetworkManagerDeviceInterfaceAsync.dhcp6_config`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            dhcpv6_path,
            bus)


class AccessPoint(NetworkManagerAccessPointInterfaceAsync):
    """Access Point (WiFi point) object

    Implements :py:class:`NetworkManagerAccessPointInterface`
    """

    def __init__(self, point_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param point_path: D-Bus path to access point object. \
            Obtained from \
            :py:attr:`NetworkManagerDeviceWirelessInterfaceAsync.access_points`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            point_path,
            bus)


class WiFiP2PPeer(NetworkManagerWifiP2PPeerInterfaceAsync):
    """WiFi peer object

    Implements :py:class:`NetworkManagerWifiP2PPeerInterface`
    """

    def __init__(self, peer_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param peer_path: D-Bus path to access point object. \
            Obtained from \
            :py:attr:`NetworkManagerDeviceWifiP2PInterfaceAsync.peers`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            peer_path,
            bus)


class ConfigCheckpoint(NetworkManagerCheckpointInterfaceAsync):
    """Configuration checkpoint interface

    Implements :py:class:`NetworkManagerCheckpointInterface`
    """

    def __init__(self, checkpoint_path: str,
                 bus: Optional[SdBus] = None) -> None:
        """

        :param checkpoint_path: D-Bus path to access point object. \
            Obtained from \
            :py:attr:`NetworkManagerDeviceWifiP2PInterfaceAsync.checkpoint_create`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__()
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            checkpoint_path,
            bus)
