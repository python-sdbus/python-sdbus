

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

from .interfaces_devices import (NetworkManagerDeviceBluetoothInterface,
                                 NetworkManagerDeviceBondInterface,
                                 NetworkManagerDeviceBridgeInterface,
                                 NetworkManagerDeviceGenericInterface,
                                 NetworkManagerDeviceInterface,
                                 NetworkManagerDeviceIPTunnelInterface,
                                 NetworkManagerDeviceMacsecInterface,
                                 NetworkManagerDeviceMacvlanInterface,
                                 NetworkManagerDeviceModemInterface,
                                 NetworkManagerDeviceOlpcMeshInterface,
                                 NetworkManagerDeviceOvsBridgeInterface,
                                 NetworkManagerDeviceOvsPortInterface,
                                 NetworkManagerDeviceStatisticsInterface,
                                 NetworkManagerDeviceTeamInterface,
                                 NetworkManagerDeviceTunInterface,
                                 NetworkManagerDeviceVethInterface,
                                 NetworkManagerDeviceVlanInterface,
                                 NetworkManagerDeviceVrfInterface,
                                 NetworkManagerDeviceVxlanInterface,
                                 NetworkManagerDeviceWifiP2PInterface,
                                 NetworkManagerDeviceWiredInterface,
                                 NetworkManagerDeviceWireGuardInterface,
                                 NetworkManagerDeviceWirelessInterface,
                                 NetworkManagerPPPInterface)
from .interfaces_other import (NetworkManagerAccessPointInterface,
                               NetworkManagerCheckpointInterface,
                               NetworkManagerConnectionActiveInterface,
                               NetworkManagerDHCP4ConfigInterface,
                               NetworkManagerDHCP6ConfigInterface,
                               NetworkManagerDnsManagerInterface,
                               NetworkManagerInterface,
                               NetworkManagerIP4ConfigInterface,
                               NetworkManagerIP6ConfigInterface,
                               NetworkManagerSecretAgentManagerInterface,
                               NetworkManagerSettingsConnectionInterface,
                               NetworkManagerSettingsInterface,
                               NetworkManagerVPNConnectionInterface,
                               NetworkManagerWifiP2PPeerInterface)

NETWORK_MANAGER_SERVICE_NAME = 'org.freedesktop.NetworkManager'


class NetworkManager(NetworkManagerInterface):
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            '/org/freedesktop/NetworkManager',
            bus)


class NetworkManagerAgentManager(NetworkManagerSecretAgentManagerInterface):
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            '/org/freedesktop/NetworkManager/AgentManager',
            bus)


class NetworkManagerDnsManager(NetworkManagerDnsManagerInterface):
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            '/org/freedesktop/NetworkManager/DnsManager',
            bus)


class NetworkManagerSettings(NetworkManagerSettingsInterface):
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            '/org/freedesktop/NetworkManager/Settings',
            bus)


class NetworkConnectionSettings(
        NetworkManagerSettingsConnectionInterface):
    """Setting of specific connection

    Implements :py:class:`NetworkManagerSettingsConnectionInterface`
    """

    def __init__(self, settings_path: str,
                 bus: Optional[SdBus] = None) -> None:
        """
        :param settings_path: D-Bus path to settings object. \
            Usually obtained from \
            :py:attr:`NetworkManagerDeviceInterface.active_connection`

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            settings_path,
            bus)


class NetworkDeviceGeneric(
        NetworkManagerDeviceInterface,
        NetworkManagerDeviceStatisticsInterface,
        NetworkManagerDeviceGenericInterface):
    """Generic device

    Implements :py:class:`NetworkManagerDeviceInterface`, \
    :py:class:`NetworkManagerDeviceStatisticsInterface` and \
    :py:class:`NetworkManagerDeviceGenericInterface`
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceWired(
        NetworkManagerDeviceInterface,
        NetworkManagerDeviceStatisticsInterface,
        NetworkManagerDeviceWiredInterface):
    """Ethernet device

    Implements :py:class:`NetworkManagerDeviceInterface`, \
    :py:class:`NetworkManagerDeviceStatisticsInterface` and \
    :py:class:`NetworkManagerDeviceWiredInterface`
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceWireless(
        NetworkManagerDeviceInterface,
        NetworkManagerDeviceStatisticsInterface,
        NetworkManagerDeviceWirelessInterface):
    """WiFi device

    Implements :py:class:`NetworkManagerDeviceInterface`, \
    :py:class:`NetworkManagerDeviceStatisticsInterface` and \
    :py:class:`NetworkManagerDeviceWirelessInterface`
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceBluetooth(
        NetworkManagerDeviceInterface,
        NetworkManagerDeviceStatisticsInterface,
        NetworkManagerDeviceBluetoothInterface):
    """Bluetooth device

    Implements :py:class:`NetworkManagerDeviceInterface`, \
    :py:class:`NetworkManagerDeviceStatisticsInterface` and \
    :py:class:`NetworkManagerDeviceBluetoothInterface`
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceBond(
        NetworkManagerDeviceInterface,
        NetworkManagerDeviceStatisticsInterface,
        NetworkManagerDeviceBondInterface):
    """Bond device

    Implements :py:class:`NetworkManagerDeviceInterface`, \
    :py:class:`NetworkManagerDeviceStatisticsInterface` and \
    :py:class:`NetworkManagerDeviceBondInterface`
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceBridge(
        NetworkManagerDeviceInterface,
        NetworkManagerDeviceStatisticsInterface,
        NetworkManagerDeviceBridgeInterface):
    """Bridge device

    Implements :py:class:`NetworkManagerDeviceInterface`, \
    :py:class:`NetworkManagerDeviceStatisticsInterface` and \
    :py:class:`NetworkManagerDeviceBridgeInterface`
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceIpTunnel(
        NetworkManagerDeviceInterface,
        NetworkManagerDeviceStatisticsInterface,
        NetworkManagerDeviceIPTunnelInterface):
    """Generic device

    Implements :py:class:`NetworkManagerDeviceInterface`, \
    :py:class:`NetworkManagerDeviceStatisticsInterface` and \
    :py:class:`NetworkManagerDeviceIPTunnelInterface`
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceMacsec(
        NetworkManagerDeviceInterface,
        NetworkManagerDeviceStatisticsInterface,
        NetworkManagerDeviceMacsecInterface):
    """Macsec device

    Implements :py:class:`NetworkManagerDeviceInterface`, \
    :py:class:`NetworkManagerDeviceStatisticsInterface` and \
    :py:class:`NetworkManagerDeviceMacsecInterface`
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceMacvlan(
        NetworkManagerDeviceInterface,
        NetworkManagerDeviceStatisticsInterface,
        NetworkManagerDeviceMacvlanInterface):
    """Macvlan device

    Implements :py:class:`NetworkManagerDeviceInterface`, \
    :py:class:`NetworkManagerDeviceStatisticsInterface` and \
    :py:class:`NetworkManagerDeviceMacvlanInterface`
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceModem(
        NetworkManagerDeviceInterface,
        NetworkManagerDeviceStatisticsInterface,
        NetworkManagerDeviceModemInterface):
    """Generic device

    Implements :py:class:`NetworkManagerDeviceInterface`, \
    :py:class:`NetworkManagerDeviceStatisticsInterface` and \
    :py:class:`NetworkManagerDeviceModemInterface`
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceOlpcMesh(
        NetworkManagerDeviceInterface,
        NetworkManagerDeviceStatisticsInterface,
        NetworkManagerDeviceOlpcMeshInterface):
    """OLPC wireless mesh device

    Implements :py:class:`NetworkManagerDeviceInterface`, \
    :py:class:`NetworkManagerDeviceStatisticsInterface` and \
    :py:class:`NetworkManagerDeviceOlpcMeshInterface`
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceOpenVSwitchBridge(
        NetworkManagerDeviceInterface,
        NetworkManagerDeviceStatisticsInterface,
        NetworkManagerDeviceOvsBridgeInterface):
    """Open vSwitch bridge device

    Implements :py:class:`NetworkManagerDeviceInterface`, \
    :py:class:`NetworkManagerDeviceStatisticsInterface` and \
    :py:class:`NetworkManagerDeviceOvsBridgeInterface`
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceOpenVSwitchPort(
        NetworkManagerDeviceInterface,
        NetworkManagerDeviceStatisticsInterface,
        NetworkManagerDeviceOvsPortInterface):
    """Open vSwitch port device

    Implements :py:class:`NetworkManagerDeviceInterface`, \
    :py:class:`NetworkManagerDeviceStatisticsInterface` and \
    :py:class:`NetworkManagerDeviceOvsPortInterface`
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceTeam(
        NetworkManagerDeviceInterface,
        NetworkManagerDeviceStatisticsInterface,
        NetworkManagerDeviceTeamInterface):
    """Team device (special Bond device for NetworkManager)

    Implements :py:class:`NetworkManagerDeviceInterface`, \
    :py:class:`NetworkManagerDeviceStatisticsInterface` and \
    :py:class:`NetworkManagerDeviceTeamInterface`
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceTun(
        NetworkManagerDeviceInterface,
        NetworkManagerDeviceStatisticsInterface,
        NetworkManagerDeviceTunInterface):
    """TUN device

    Implements :py:class:`NetworkManagerDeviceInterface`, \
    :py:class:`NetworkManagerDeviceStatisticsInterface` and \
    :py:class:`NetworkManagerDeviceTunInterface`
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceVeth(
        NetworkManagerDeviceInterface,
        NetworkManagerDeviceStatisticsInterface,
        NetworkManagerDeviceVethInterface):
    """Virtual Ethernet device

    Implements :py:class:`NetworkManagerDeviceInterface`, \
    :py:class:`NetworkManagerDeviceStatisticsInterface` and \
    :py:class:`NetworkManagerDeviceVethInterface`
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceVlan(
        NetworkManagerDeviceInterface,
        NetworkManagerDeviceStatisticsInterface,
        NetworkManagerDeviceVlanInterface):
    """VLAN device

    Implements :py:class:`NetworkManagerDeviceInterface`, \
    :py:class:`NetworkManagerDeviceStatisticsInterface` and \
    :py:class:`NetworkManagerDeviceVlanInterface`
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceVrf(
        NetworkManagerDeviceInterface,
        NetworkManagerDeviceStatisticsInterface,
        NetworkManagerDeviceVrfInterface):
    """VRF (virtual routing) device

    Implements :py:class:`NetworkManagerDeviceInterface`, \
    :py:class:`NetworkManagerDeviceStatisticsInterface` and \
    :py:class:`NetworkManagerDeviceVrfInterface`
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceVxlan(
        NetworkManagerDeviceInterface,
        NetworkManagerDeviceStatisticsInterface,
        NetworkManagerDeviceVxlanInterface):
    """VXLAN device

    Implements :py:class:`NetworkManagerDeviceInterface`, \
    :py:class:`NetworkManagerDeviceStatisticsInterface` and \
    :py:class:`NetworkManagerDeviceVxlanInterface`
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceWifiP2P(
        NetworkManagerDeviceInterface,
        NetworkManagerDeviceStatisticsInterface,
        NetworkManagerDeviceWifiP2PInterface):
    """Wifi Peer-to-Peer (P2P) device

    Implements :py:class:`NetworkManagerDeviceInterface`, \
    :py:class:`NetworkManagerDeviceStatisticsInterface` and \
    :py:class:`NetworkManagerDeviceWifiP2PInterface`
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDeviceWireGuard(
        NetworkManagerDeviceInterface,
        NetworkManagerDeviceStatisticsInterface,
        NetworkManagerDeviceWireGuardInterface):
    """Generic device

    Implements :py:class:`NetworkManagerDeviceInterface`, \
    :py:class:`NetworkManagerDeviceStatisticsInterface` and \
    :py:class:`NetworkManagerDeviceWireGuardInterface`
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class NetworkDevicePPP(
        NetworkManagerDeviceInterface,
        NetworkManagerDeviceStatisticsInterface,
        NetworkManagerPPPInterface):
    """PPP device

    Implements :py:class:`NetworkManagerDeviceInterface`, \
    :py:class:`NetworkManagerDeviceStatisticsInterface` and \
    :py:class:`NetworkManagerPPPInterface`
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
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path,
            bus)


class ActiveConnection(NetworkManagerConnectionActiveInterface):
    """Active connection object

    Implements :py:class:`NetworkManagerConnectionActiveInterface`
    """

    def __init__(self, connection_path: str,
                 bus: Optional[SdBus] = None) -> None:
        """

        :param connection_path: D-Bus path to connection object. \
            Obtained from \
            :py:meth:`NetworkManagerDeviceInterface.active_connection`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            connection_path,
            bus)


class ActiveVPNConnection(
        ActiveConnection,
        NetworkManagerVPNConnectionInterface):
    """Active VPN connection object

    Implements :py:class:`NetworkManagerConnectionActiveInterface`
    and :py:class:`NetworkManagerVPNConnectionInterface`
    """
    ...


class IPv4Config(NetworkManagerIP4ConfigInterface):
    """IPv4 configuration interface

    Implements :py:class:`NetworkManagerIP4ConfigInterface`
    """

    def __init__(self, ip4_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param ip4_path: D-Bus path to IPv4 config object. \
            Obtained from \
            :py:attr:`NetworkManagerDeviceInterface.ip4_config`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            ip4_path,
            bus)


class IPv6Config(NetworkManagerIP6ConfigInterface):
    """IPv6 configuration interface

    Implements :py:class:`NetworkManagerIP6ConfigInterface`
    """

    def __init__(self, ip6_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param ip6_path: D-Bus path to IPv6 config object. \
            Obtained from \
            :py:attr:`NetworkManagerDeviceInterface.ip4_config`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            ip6_path,
            bus)


class DHCPv4Config(NetworkManagerDHCP4ConfigInterface):
    """DHCPv4 configuration interface

    Implements :py:class:`NetworkManagerDHCP4ConfigInterface`
    """

    def __init__(self, dhcp4_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param dhcp4_path: D-Bus path to DHCPv4 config object. \
            Obtained from \
            :py:attr:`NetworkManagerDeviceInterface.dhcp4_config`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            dhcp4_path,
            bus)


class DHCPv6Config(NetworkManagerDHCP6ConfigInterface):
    """DHCPv6 configuration interface

    Implements :py:class:`NetworkManagerDHCP6ConfigInterface`
    """

    def __init__(self, dhcpv6_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param dhcpv6_path: D-Bus path to DHCPv6 config object. \
            Obtained from \
            :py:attr:`NetworkManagerDeviceInterface.dhcp6_config`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            dhcpv6_path,
            bus)


class AccessPoint(NetworkManagerAccessPointInterface):
    """Access Point (WiFi point) object

    Implements :py:class:`NetworkManagerAccessPointInterface`
    """

    def __init__(self, point_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param point_path: D-Bus path to access point object. \
            Obtained from \
            :py:attr:`NetworkManagerDeviceWirelessInterface.access_points`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            point_path,
            bus)


class WiFiP2PPeer(NetworkManagerWifiP2PPeerInterface):
    """WiFi peer object

    Implements :py:class:`NetworkManagerWifiP2PPeerInterface`
    """

    def __init__(self, peer_path: str, bus: Optional[SdBus] = None) -> None:
        """

        :param peer_path: D-Bus path to access point object. \
            Obtained from \
            :py:attr:`NetworkManagerDeviceWifiP2PInterface.peers`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            peer_path,
            bus)


class ConfigCheckpoint(NetworkManagerCheckpointInterface):
    """Configuration checkpoint interface

    Implements :py:class:`NetworkManagerCheckpointInterface`
    """

    def __init__(self, checkpoint_path: str,
                 bus: Optional[SdBus] = None) -> None:
        """

        :param checkpoint_path: D-Bus path to access point object. \
            Obtained from \
            :py:attr:`NetworkManagerDeviceWifiP2PInterface.checkpoint_create`.

        :param bus: You probably want to set default bus to system bus \
            or pass system bus directly.
        """
        super().__init__(
            NETWORK_MANAGER_SERVICE_NAME,
            checkpoint_path,
            bus)
