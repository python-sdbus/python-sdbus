
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

from typing import Any, Dict, List, Tuple
from enum import IntFlag, IntEnum

from sdbus import (DbusInterfaceCommonAsync, dbus_method_async,
                   dbus_property_async, dbus_signal_async)

# region Interfaces

# region Access Point


class AccessPointCapabilities(IntFlag):
    """Wi-Fi Access point capabilities

    .. autoattribute:: NONE
    .. autoattribute:: PRIVACY
    .. autoattribute:: WPS
    .. autoattribute:: WPS_BUTTON
    .. autoattribute:: WPS_PIN
    """
    NONE = 0x0
    PRIVACY = 0x1
    WPS = 0x2
    WPS_BUTTON = 0x4
    WPS_PIN = 0x8


class WpaSecurityFlags(IntFlag):
    """WPA (WiFi protected Access) encryption and authentication types"""
    NONE = 0x0
    P2P_WEP40 = 0x1
    P2P_WEP104 = 0x2
    P2P_TKIP = 0x4
    P2P_CCMP = 0x8
    BROADCAST_WEP40 = 0x10
    BROADCAST_WEP104 = 0x20
    BROADCAST_TKIP = 0x40
    BROADCAST_CCMP = 0x80
    AUTH_PSK = 0x100
    AUTH_802_1X = 0x200
    AUTH_SAE = 0x400
    AUTH_OWE = 0x800
    AUTH_OWE_TM = 0x1000
    AUTH_EAP_SUITE_B = 0x2000


class WiFiOperationMode(IntEnum):
    """Operation mode of WiFi access point"""
    UNKNOWN = 0
    ADHOC = 1
    INFRASTRUCTURE = 2
    AP = 3
    MESH = 4


class NetworkManagerAccessPointInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.AccessPoint',
):
    """Interface representing Wi-Fi access point"""

    @dbus_property_async(
        property_signature='u',
    )
    def flags(self) -> int:
        """Flags describing capabilities of the point

        See :py:class:`AccessPointCapabilities`
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def wpa_flags(self) -> int:
        """Flags WPA authentication and encryption

        See :py:class:`WpaSecurityFlags`
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def rsn_flags(self) -> int:
        """Flags describing RSN (Robust Secure Network) capabilities

        See :py:class:`WpaSecurityFlags`
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ay',
    )
    def ssid(self) -> bytes:
        """SSID of the access point. (name)"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def frequency(self) -> int:
        """Frequency in MHz"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def hw_address(self) -> str:
        """Hardware address (BSSID)"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def mode(self) -> int:
        """Mode of operation of access point

        See :py:class:`WiFiOperationMode`
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def max_bitrate(self) -> int:
        """Maximum bit rate of this access point. (in kilobits/second)"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='y',
    )
    def strength(self) -> int:
        """Current signal quality in % percent"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='i',
    )
    def last_seen(self) -> int:
        """Timestamp in CLOCK_BOOTTIME seconds since last seen in scan

        Value of -1 means that the point was never found in scans.
        """
        raise NotImplementedError


# endregion Access Point

# region Secret Agent

class SecretAgentCapabilities(IntFlag):
    """Secret agent capabilities"""
    NONE = 0x0
    VPN_HINTS = 0x1


class NetworkManagerSecretAgentManagerInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.AgentManager',
):
    """Secret Agent Manager"""

    @dbus_method_async(
        input_signature='s',
    )
    async def register(
        self,
        identifier: str,
    ) -> None:
        """Indentifies an agent.

        Only one agent in each user session may use same indentifier.
        """
        raise NotImplementedError

    @dbus_method_async(
        input_signature='su',
    )
    async def register_with_capabilities(
        self,
        identifier: str,
        capabilities: int,
    ) -> None:
        """Same as register() but with agent capabilities

        See :py:class:`SecretAgentCapabilities`
        """
        raise NotImplementedError

    @dbus_method_async(
    )
    async def unregister(
        self,
    ) -> None:
        """Notify NetworkManager that secret agent is no longer active"""
        raise NotImplementedError

# endregion Secret Agent


class NetworkManagerCheckpointInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Checkpoint',
):
    """Network Manager configuration snapshot interface"""

    @dbus_property_async(
        property_signature='ao',
    )
    def devices(self) -> List[str]:
        """List of devices which are part of this checkpoint"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='x',
    )
    def created(self) -> int:
        """Snapohot creation time in CLOCK_BOOTTIME milliseconds"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def rollback_timeout(self) -> int:
        """Automatic tollback timeout in seconds or zero"""
        raise NotImplementedError

# region Connection State


class ConnectionState(IntEnum):
    """State of the connection"""
    UNKNOWN = 0
    ACTIVATING = 1
    ACTIVATED = 2
    DEACTIVATING = 3
    DEACTIVATED = 4


class ConnectionStateFlags(IntFlag):
    """State of connection flags"""
    NONE = 0x0
    IS_MASTER = 0x1
    IS_SLAVE = 0x2
    LAYER2_READY = 0x4
    IP4_READY = 0x8
    IP6_READY = 0x10
    MASTER_HAS_SLAVES = 0x20
    LIFE_TIME_BOUND_TO_PROFILE_VISIBILITY = 0x40
    EXTERNAL = 0x80


class ConnectionStateReason(IntEnum):
    UNKNOWN = 0
    NONE = 1
    USER_DISCONNECTED = 2
    DEVICE_DISCONNECTED = 3
    SERVICE_STOPPED = 4
    IP_CONFIG_INVALID = 5
    CONNECT_TIMEOUT = 6
    SERVICE_START_TIMEOUT = 7
    SERVICE_START_FAILED = 8
    NO_SECRETS = 9
    LOGIN_FAILED = 10
    CONNECTION_REMOVED = 11
    DEPENDENCY_FAILED = 12
    DEVICE_REALIZE_FAILED = 13
    DEVICE_REMOVED = 14


class NetworkManagerConnectionActiveInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Connection.Active',
):
    """Represents an attempt to connect to network"""

    @dbus_property_async(
        property_signature='o',
    )
    def connection(self) -> str:
        """Path of connection object"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def specific_object(self) -> str:
        """Specific object associated with active connection"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def id(self) -> str:
        """Connection id"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def uuid(self) -> str:
        """Connection UUID"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
        property_name="Type"
    )
    def connection_type(self) -> str:
        """Connection type"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ao',
    )
    def devices(self) -> List[str]:
        """Array of devices object paths which are part of connection"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def state(self) -> int:
        """Connection state

        See :py:class:`ConnectionState`
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def state_flags(self) -> int:
        """Connection state flags

        See :py:class:`ConnectionStateFlags`
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def default(self) -> bool:
        """Whether or not this connection owns default IPv4 route"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def ip4_config(self) -> str:
        """Object path to Ip4Config object

        Only valid if connection state is ACTIVATED
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def dhcp4_config(self) -> str:
        """Object path to Dhcp4Config object

        Only valid if connection state is ACTIVATED
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def default6(self) -> bool:
        """Whether or not this connection owns default IPv6 route"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def ip6_config(self) -> str:
        """Object path to Ip4Config object

        Only valid if connection state is ACTIVATED
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def dhcp6_config(self) -> str:
        """Object path to Dhcp6Config object

        Only valid if connection state is ACTIVATED
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def vpn(self) -> bool:
        """Whether this connection is a VPN"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def master(self) -> str:
        """Path to master device if this connection is a slave"""
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='uu',
    )
    def state_changed(self) -> Tuple[int, int]:
        """Signal of the new state and the reason

        See :py:class:`ConnectionState` and :py:class:`ConnectionStateReason`
        """
        raise NotImplementedError

# endregion Connection State


class OrgFreedesktopNetworkManagerDeviceAdslInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Adsl',
):

    @dbus_property_async(
        property_signature='b',
    )
    def carrier(self) -> bool:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceBluetoothInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Bluetooth',
):

    @dbus_property_async(
        property_signature='s',
    )
    def hw_address(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def name(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def bt_capabilities(self) -> int:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceBondInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Bond',
):

    @dbus_property_async(
        property_signature='s',
    )
    def hw_address(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def carrier(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ao',
    )
    def slaves(self) -> List[str]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceBridgeInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Bridge',
):

    @dbus_property_async(
        property_signature='s',
    )
    def hw_address(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def carrier(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ao',
    )
    def slaves(self) -> List[str]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceDummyInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Dummy',
):

    @dbus_property_async(
        property_signature='s',
    )
    def hw_address(self) -> str:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceGenericInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Generic',
):

    @dbus_property_async(
        property_signature='s',
    )
    def hw_address(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def type_description(self) -> str:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceInfinibandInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Infiniband',
):

    @dbus_property_async(
        property_signature='s',
    )
    def hw_address(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def carrier(self) -> bool:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceIPTunnelInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.IPTunnel',
):

    @dbus_property_async(
        property_signature='u',
    )
    def mode(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def parent(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def local(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def remote(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='y',
    )
    def ttl(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='y',
    )
    def tos(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def path_mtu_discovery(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def input_key(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def output_key(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='y',
    )
    def encapsulation_limit(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def flow_label(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def flags(self) -> int:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceLowpanInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Lowpan',
):

    @dbus_property_async(
        property_signature='s',
    )
    def hw_address(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def parent(self) -> str:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceMacsecInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Macsec',
):

    @dbus_property_async(
        property_signature='o',
    )
    def parent(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='t',
    )
    def sci(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='y',
    )
    def icv_length(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='t',
    )
    def cipher_suite(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def window(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='y',
    )
    def encoding_sa(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def validation(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def encrypt(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def protect(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def include_sci(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def es(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def scb(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def replay_protect(self) -> bool:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceMacvlanInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Macvlan',
):

    @dbus_property_async(
        property_signature='o',
    )
    def parent(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def mode(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def no_promisc(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def tap(self) -> bool:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceModemInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Modem',
):

    @dbus_property_async(
        property_signature='u',
    )
    def modem_capabilities(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def current_capabilities(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def device_id(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def operator_code(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def apn(self) -> str:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceOlpcMeshInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.OlpcMesh',
):

    @dbus_property_async(
        property_signature='s',
    )
    def hw_address(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def companion(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def active_channel(self) -> int:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceOvsBridgeInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.OvsBridge',
):

    @dbus_property_async(
        property_signature='ao',
    )
    def slaves(self) -> List[str]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceOvsInterfaceInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.OvsInterface',
):

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceOvsPortInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.OvsPort',
):

    @dbus_property_async(
        property_signature='ao',
    )
    def slaves(self) -> List[str]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDevicePppInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Ppp',
):

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceStatisticsInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Statistics',
):

    @dbus_property_async(
        property_signature='u',
    )
    def refresh_rate_ms(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='t',
    )
    def tx_bytes(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='t',
    )
    def rx_bytes(self) -> int:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceTeamInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Team',
):

    @dbus_property_async(
        property_signature='s',
    )
    def hw_address(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def carrier(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ao',
    )
    def slaves(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def config(self) -> str:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceTunInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Tun',
):

    @dbus_property_async(
        property_signature='x',
    )
    def owner(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='x',
    )
    def group(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def mode(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def no_pi(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def vnet_hdr(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def multi_queue(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def hw_address(self) -> str:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceVethInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Veth',
):

    @dbus_property_async(
        property_signature='o',
    )
    def peer(self) -> str:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceVlanInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Vlan',
):

    @dbus_property_async(
        property_signature='s',
    )
    def hw_address(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def carrier(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def parent(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def vlan_id(self) -> int:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceVrfInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Vrf',
):

    @dbus_property_async(
        property_signature='u',
    )
    def table(self) -> int:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceVxlanInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Vxlan',
):

    @dbus_property_async(
        property_signature='o',
    )
    def parent(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def hw_address(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def id(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def group(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def local(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='y',
    )
    def tos(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='y',
    )
    def ttl(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def learning(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def ageing(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def limit(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='q',
    )
    def dst_port(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='q',
    )
    def src_port_min(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='q',
    )
    def src_port_max(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def proxy(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def rsc(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def l2miss(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def l3miss(self) -> bool:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceWifiP2PInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.WifiP2P',
):

    @dbus_method_async(
        input_signature='a{sv}',
    )
    async def start_find(
        self,
        options: Dict[str, Tuple[str, Any]],
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
    )
    async def stop_find(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def hw_address(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ao',
    )
    def peers(self) -> List[str]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='o',
    )
    def peer_added(self) -> str:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='o',
    )
    def peer_removed(self) -> str:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceWiMaxInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.WiMax',
):

    @dbus_method_async(
        result_signature='ao',
    )
    async def get_nsp_list(
        self,
    ) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ao',
    )
    def nsps(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def hw_address(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def center_frequency(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='i',
    )
    def rssi(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='i',
    )
    def cinr(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='i',
    )
    def tx_power(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def bsid(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def active_nsp(self) -> str:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='o',
    )
    def nsp_added(self) -> str:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='o',
    )
    def nsp_removed(self) -> str:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceWiredInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Wired',
):

    @dbus_property_async(
        property_signature='s',
    )
    def hw_address(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def perm_hw_address(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def speed(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='as',
    )
    def s390_subchannels(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def carrier(self) -> bool:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceWireGuardInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.WireGuard',
):

    @dbus_property_async(
        property_signature='ay',
    )
    def public_key(self) -> bytes:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='q',
    )
    def listen_port(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def fw_mark(self) -> int:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceWirelessInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Wireless',
):

    @dbus_method_async(
        result_signature='ao',
    )
    async def get_access_points(
        self,
    ) -> List[str]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature='ao',
    )
    async def get_all_access_points(
        self,
    ) -> List[str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sv}',
    )
    async def request_scan(
        self,
        options: Dict[str, Tuple[str, Any]],
    ) -> None:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def hw_address(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def perm_hw_address(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def mode(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def bitrate(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ao',
    )
    def access_points(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def active_access_point(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def wireless_capabilities(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='x',
    )
    def last_scan(self) -> int:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='o',
    )
    def access_point_added(self) -> str:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='o',
    )
    def access_point_removed(self) -> str:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceWpanInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Wpan',
):

    @dbus_property_async(
        property_signature='s',
    )
    def hw_address(self) -> str:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDeviceInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device',
):

    @dbus_method_async(
        input_signature='a{sa{sv}}tu',
    )
    async def reapply(
        self,
        connection: Dict[str, Dict[str, Tuple[str, Any]]],
        version_id: int,
        flags: int,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='u',
        result_signature='a{sa{sv}}t',
    )
    async def get_applied_connection(
        self,
        flags: int,
    ) -> Tuple[Dict[str, Dict[str, Tuple[str, Any]]], int]:
        raise NotImplementedError

    @dbus_method_async(
    )
    async def disconnect(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
    )
    async def delete(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def udi(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def path(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def interface(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def ip_interface(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def driver(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def driver_version(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def firmware_version(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def capabilities(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def ip4_address(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def state(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='(uu)',
    )
    def state_reason(self) -> Tuple[int, int]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def active_connection(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def ip4_config(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def dhcp4_config(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def ip6_config(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def dhcp6_config(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def managed(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def autoconnect(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def firmware_missing(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def nm_plugin_missing(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def device_type(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ao',
    )
    def available_connections(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def physical_port_id(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def mtu(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def metered(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='aa{sv}',
    )
    def lldp_neighbors(self) -> List[Dict[str, Tuple[str, Any]]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def real(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def ip4_connectivity(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def ip6_connectivity(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def interface_flags(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def hw_address(self) -> str:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='uuu',
    )
    def state_changed(self) -> Tuple[int, int, int]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDHCP4ConfigInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.DHCP4Config',
):

    @dbus_property_async(
        property_signature='a{sv}',
    )
    def options(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDHCP6ConfigInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.DHCP6Config',
):

    @dbus_property_async(
        property_signature='a{sv}',
    )
    def options(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerDnsManagerInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.DnsManager',
):

    @dbus_property_async(
        property_signature='s',
    )
    def mode(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def rc_manager(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='aa{sv}',
    )
    def configuration(self) -> List[Dict[str, Tuple[str, Any]]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerIP4ConfigInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.IP4Config',
):

    @dbus_property_async(
        property_signature='aau',
    )
    def addresses(self) -> List[List[int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='aa{sv}',
    )
    def address_data(self) -> List[Dict[str, Tuple[str, Any]]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def gateway(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='aau',
    )
    def routes(self) -> List[List[int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='aa{sv}',
    )
    def route_data(self) -> List[Dict[str, Tuple[str, Any]]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='au',
    )
    def nameservers(self) -> List[int]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='aa{sv}',
    )
    def nameserver_data(self) -> List[Dict[str, Tuple[str, Any]]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='as',
    )
    def domains(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='as',
    )
    def searches(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='as',
    )
    def dns_options(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='i',
    )
    def dns_priority(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='au',
    )
    def wins_servers(self) -> List[int]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='as',
    )
    def wins_server_data(self) -> List[str]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerIP6ConfigInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.IP6Config',
):

    @dbus_property_async(
        property_signature='a(ayuay)',
    )
    def addresses(self) -> List[Tuple[bytes, int, bytes]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='aa{sv}',
    )
    def address_data(self) -> List[Dict[str, Tuple[str, Any]]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def gateway(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='a(ayuayu)',
    )
    def routes(self) -> List[Tuple[bytes, int, bytes, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='aa{sv}',
    )
    def route_data(self) -> List[Dict[str, Tuple[str, Any]]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='aay',
    )
    def nameservers(self) -> List[bytes]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='as',
    )
    def domains(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='as',
    )
    def searches(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='as',
    )
    def dns_options(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='i',
    )
    def dns_priority(self) -> int:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerPPPInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.PPP',
):

    @dbus_method_async(
        result_signature='ss',
    )
    async def need_secrets(
        self,
    ) -> Tuple[str, str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sv}',
    )
    async def set_ip4_config(
        self,
        config: Dict[str, Tuple[str, Any]],
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sv}',
    )
    async def set_ip6_config(
        self,
        config: Dict[str, Tuple[str, Any]],
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='u',
    )
    async def set_state(
        self,
        state: int,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='i',
    )
    async def set_ifindex(
        self,
        ifindex: int,
    ) -> None:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerSecretAgentInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.SecretAgent',
):

    @dbus_method_async(
        input_signature='a{sa{sv}}osasu',
        result_signature='a{sa{sv}}',
    )
    async def get_secrets(
        self,
        connection: Dict[str, Dict[str, Tuple[str, Any]]],
        connection_path: str,
        setting_name: str,
        hints: List[str],
        flags: int,
    ) -> Dict[str, Dict[str, Tuple[str, Any]]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='os',
    )
    async def cancel_get_secrets(
        self,
        connection_path: str,
        setting_name: str,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sa{sv}}o',
    )
    async def save_secrets(
        self,
        connection: Dict[str, Dict[str, Tuple[str, Any]]],
        connection_path: str,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sa{sv}}o',
    )
    async def delete_secrets(
        self,
        connection: Dict[str, Dict[str, Tuple[str, Any]]],
        connection_path: str,
    ) -> None:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerSettingsConnectionInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Settings.Connection',
):

    @dbus_method_async(
        input_signature='a{sa{sv}}',
    )
    async def update(
        self,
        properties: Dict[str, Dict[str, Tuple[str, Any]]],
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sa{sv}}',
    )
    async def update_unsaved(
        self,
        properties: Dict[str, Dict[str, Tuple[str, Any]]],
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
    )
    async def delete(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_signature='a{sa{sv}}',
    )
    async def get_settings(
        self,
    ) -> Dict[str, Dict[str, Tuple[str, Any]]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='s',
        result_signature='a{sa{sv}}',
    )
    async def get_secrets(
        self,
        setting_name: str,
    ) -> Dict[str, Dict[str, Tuple[str, Any]]]:
        raise NotImplementedError

    @dbus_method_async(
    )
    async def clear_secrets(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
    )
    async def save(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sa{sv}}ua{sv}',
        result_signature='a{sv}',
    )
    async def update2(
        self,
        settings: Dict[str, Dict[str, Tuple[str, Any]]],
        flags: int,
        args: Dict[str, Tuple[str, Any]],
    ) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def unsaved(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def flags(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def filename(self) -> str:
        raise NotImplementedError

    @dbus_signal_async(
    )
    def updated(self) -> None:
        raise NotImplementedError

    @dbus_signal_async(
    )
    def removed(self) -> None:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerSettingsInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Settings',
):

    @dbus_method_async(
        result_signature='ao',
    )
    async def list_connections(
        self,
    ) -> List[str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='s',
        result_signature='o',
    )
    async def get_connection_by_uuid(
        self,
        uuid: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sa{sv}}',
        result_signature='o',
    )
    async def add_connection(
        self,
        connection: Dict[str, Dict[str, Tuple[str, Any]]],
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sa{sv}}',
        result_signature='o',
    )
    async def add_connection_unsaved(
        self,
        connection: Dict[str, Dict[str, Tuple[str, Any]]],
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sa{sv}}ua{sv}',
        result_signature='oa{sv}',
    )
    async def add_connection2(
        self,
        settings: Dict[str, Dict[str, Tuple[str, Any]]],
        flags: int,
        args: Dict[str, Tuple[str, Any]],
    ) -> Tuple[str, Dict[str, Tuple[str, Any]]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='as',
        result_signature='bas',
    )
    async def load_connections(
        self,
        filenames: List[str],
    ) -> Tuple[bool, List[str]]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature='b',
    )
    async def reload_connections(
        self,
    ) -> bool:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='s',
    )
    async def save_hostname(
        self,
        hostname: str,
    ) -> None:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ao',
    )
    def connections(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def hostname(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def can_modify(self) -> bool:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='o',
    )
    def new_connection(self) -> str:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='o',
    )
    def connection_removed(self) -> str:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerVPNConnectionInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.VPN.Connection',
):

    @dbus_property_async(
        property_signature='u',
    )
    def vpn_state(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def banner(self) -> str:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='uu',
    )
    def vpn_state_changed(self) -> Tuple[int, int]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerVPNPluginInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.VPN.Plugin',
):

    @dbus_method_async(
        input_signature='a{sa{sv}}',
    )
    async def connect(
        self,
        connection: Dict[str, Dict[str, Tuple[str, Any]]],
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sa{sv}}a{sv}',
    )
    async def connect_interactive(
        self,
        connection: Dict[str, Dict[str, Tuple[str, Any]]],
        details: Dict[str, Tuple[str, Any]],
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sa{sv}}',
        result_signature='s',
    )
    async def need_secrets(
        self,
        settings: Dict[str, Dict[str, Tuple[str, Any]]],
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
    )
    async def disconnect(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sv}',
    )
    async def set_config(
        self,
        config: Dict[str, Tuple[str, Any]],
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sv}',
    )
    async def set_ip4_config(
        self,
        config: Dict[str, Tuple[str, Any]],
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sv}',
    )
    async def set_ip6_config(
        self,
        config: Dict[str, Tuple[str, Any]],
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='s',
    )
    async def set_failure(
        self,
        reason: str,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sa{sv}}',
    )
    async def new_secrets(
        self,
        connection: Dict[str, Dict[str, Tuple[str, Any]]],
    ) -> None:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def state(self) -> int:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='u',
    )
    def state_changed(self) -> int:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='sas',
    )
    def secrets_required(self) -> Tuple[str, List[str]]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def config(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def ip4_config(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def ip6_config(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='s',
    )
    def login_banner(self) -> str:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='u',
    )
    def failure(self) -> int:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerWifiP2PPeerInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.WifiP2PPeer',
):

    @dbus_property_async(
        property_signature='s',
    )
    def name(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def flags(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def manufacturer(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def model(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def model_number(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def serial(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ay',
    )
    def wfd_i_es(self) -> bytes:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def hw_address(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='y',
    )
    def strength(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='i',
    )
    def last_seen(self) -> int:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerWiMaxNspInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.WiMax.Nsp',
):

    @dbus_property_async(
        property_signature='s',
    )
    def name(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def signal_quality(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def network_type(self) -> int:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError


class OrgFreedesktopNetworkManagerInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager',
):

    @dbus_method_async(
        input_signature='u',
    )
    async def reload(
        self,
        flags: int,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_signature='ao',
    )
    async def get_devices(
        self,
    ) -> List[str]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature='ao',
    )
    async def get_all_devices(
        self,
    ) -> List[str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='s',
        result_signature='o',
    )
    async def get_device_by_ip_iface(
        self,
        iface: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='ooo',
        result_signature='o',
    )
    async def activate_connection(
        self,
        connection: str,
        device: str,
        specific_object: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sa{sv}}oo',
        result_signature='oo',
    )
    async def add_and_activate_connection(
        self,
        connection: Dict[str, Dict[str, Tuple[str, Any]]],
        device: str,
        specific_object: str,
    ) -> Tuple[str, str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sa{sv}}ooa{sv}',
        result_signature='ooa{sv}',
    )
    async def add_and_activate_connection2(
        self,
        connection: Dict[str, Dict[str, Tuple[str, Any]]],
        device: str,
        specific_object: str,
        options: Dict[str, Tuple[str, Any]],
    ) -> Tuple[str, str, Dict[str, Tuple[str, Any]]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='o',
    )
    async def deactivate_connection(
        self,
        active_connection: str,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='b',
    )
    async def sleep(
        self,
        sleep: bool,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='b',
    )
    async def enable(
        self,
        enable: bool,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_signature='a{ss}',
    )
    async def get_permissions(
        self,
    ) -> Dict[str, str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='ss',
    )
    async def set_logging(
        self,
        level: str,
        domains: str,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_signature='ss',
    )
    async def get_logging(
        self,
    ) -> Tuple[str, str]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature='u',
    )
    async def check_connectivity(
        self,
    ) -> int:
        raise NotImplementedError

    @dbus_method_async(
        result_signature='u',
        method_name='State',
    )
    async def get_state(
        self,
    ) -> int:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='aouu',
        result_signature='o',
    )
    async def checkpoint_create(
        self,
        devices: List[str],
        rollback_timeout: int,
        flags: int,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='o',
    )
    async def checkpoint_destroy(
        self,
        checkpoint: str,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='o',
        result_signature='a{su}',
    )
    async def checkpoint_rollback(
        self,
        checkpoint: str,
    ) -> Dict[str, int]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature='ou',
    )
    async def checkpoint_adjust_rollback_timeout(
        self,
        checkpoint: str,
        add_timeout: int,
    ) -> None:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ao',
    )
    def devices(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ao',
    )
    def all_devices(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ao',
    )
    def checkpoints(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def networking_enabled(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def wireless_enabled(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def wireless_hardware_enabled(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def wwan_enabled(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def wwan_hardware_enabled(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def wimax_enabled(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def wimax_hardware_enabled(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ao',
    )
    def active_connections(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def primary_connection(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def primary_connection_type(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def metered(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def activating_connection(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def startup(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def version(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='au',
    )
    def capabilities(self) -> List[int]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def state(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def connectivity(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def connectivity_check_available(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def connectivity_check_enabled(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def connectivity_check_uri(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='a{sv}',
    )
    def global_dns_configuration(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError

    @dbus_signal_async(
    )
    def check_permissions(self) -> None:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='u',
    )
    def state_changed(self) -> int:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def properties_changed(self) -> Dict[str, Tuple[str, Any]]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='o',
    )
    def device_added(self) -> str:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='o',
    )
    def device_removed(self) -> str:
        raise NotImplementedError
# endregion Interfaces
