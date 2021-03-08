
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

from typing import Any, Dict, List, Tuple, Optional
from enum import IntFlag, IntEnum

from sdbus import (DbusInterfaceCommonAsync, dbus_method_async,
                   dbus_property_async, dbus_signal_async)

from ..sd_bus_internals import SdBus

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
        """Identifies an agent.

        Only one agent in each user session may use same identifier.
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
    """Connection state change reason"""
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

# region Bluetooth device


class BluetoothCapabilities(IntFlag):
    """Bluetooth Capabilities"""
    NONE = 0x0
    DIAL_UP = 0x1
    NETWORK_ACCESS_POINT = 0x2


class NetworkManagerDeviceBluetoothInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Bluetooth',
):
    """Bluetooth device interface"""

    @dbus_property_async(
        property_signature='s',
    )
    def name(self) -> str:
        """Name of Bluetooth device"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def bt_capabilities(self) -> int:
        """Bluetooth device capabilities

        See :py:class:`BluetoothCapabilities`
        """
        raise NotImplementedError

# endregion Bluetooth device


class NetworkManagerDeviceBondInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Bond',
):
    """Bond device interface"""

    @dbus_property_async(
        property_signature='ao',
    )
    def slaves(self) -> List[str]:
        """List of paths of enslaved devices"""
        raise NotImplementedError


class NetworkManagerDeviceBridgeInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Bridge',
):
    """Bridge device interface"""

    @dbus_property_async(
        property_signature='ao',
    )
    def slaves(self) -> List[str]:
        """List of paths of enslaved devices"""
        raise NotImplementedError


class NetworkManagerDeviceGenericInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Generic',
):
    """Generic device interface"""

    @dbus_property_async(
        property_signature='s',
    )
    def type_description(self) -> str:
        """Description of the interface type"""
        raise NotImplementedError


class IpTunnelMode(IntEnum):
    """Mode of IP tunnel"""
    UNKNOWN = 0
    IP_IP = 1
    GRE = 2
    SIT = 3
    ISATAP = 4
    VTI = 5
    IP6_IP6 = 6
    IP_IP6 = 7
    IP6_GRE = 8
    VTI6 = 9
    GRE_TAP = 10
    IP6_GRE_TAP = 11


class NetworkManagerDeviceIPTunnelInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.IPTunnel',
):
    """IP tunnel device interface"""

    @dbus_property_async(
        property_signature='u',
    )
    def mode(self) -> int:
        """Tunnel mode

        See :py:class:`IpTunnelMode`
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def parent(self) -> str:
        """Object path of parent device"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def local(self) -> str:
        """Local endpoint"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def remote(self) -> str:
        """Remote endpoint"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='y',
    )
    def ttl(self) -> int:
        """Time to Live (TTL)

        0 is special value meaning the packets inherit TTL value.
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='y',
    )
    def tos(self) -> int:
        """Type of service (IPv4) or traffic class (IPv6)"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def path_mtu_discovery(self) -> bool:
        """Whether path MTU discovery is enabled on this tunnel"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def input_key(self) -> str:
        """Key used for incoming packets"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def output_key(self) -> str:
        """Key used for outgoing packets"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='y',
    )
    def encapsulation_limit(self) -> int:
        """How many levels of enapsulation are permitted

        Only IPv6 tunnels
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def flow_label(self) -> int:
        """Flow label assigned to tunnel packets

        Only IPv6 tunnels
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def flags(self) -> int:
        """Tunnel flags

        Missing upstream documentation
        """
        raise NotImplementedError


class NetworkManagerDeviceLowpanInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Lowpan',
):
    """6LoWPAN device interface"""

    @dbus_property_async(
        property_signature='o',
    )
    def parent(self) -> str:
        """Path to parent device"""
        raise NotImplementedError


class NetworkManagerDeviceMacsecInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Macsec',
):
    """MacSec device interface"""

    @dbus_property_async(
        property_signature='o',
    )
    def parent(self) -> str:
        """Path to parent device"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='t',
    )
    def sci(self) -> int:
        """Secure Channel Identifier"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='y',
    )
    def icv_length(self) -> int:
        """Length of Integrity Check Value"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='t',
    )
    def cipher_suite(self) -> int:
        """Set of cryptographic algorithms in use

        Not documented upstream.
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def window(self) -> int:
        """Size of replay window. (in number of packets)"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='y',
    )
    def encoding_sa(self) -> int:
        """Security Association in use"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def validation(self) -> str:
        """Validation mode for incoming packets

        * strict
        * check
        * disabled
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def encrypt(self) -> bool:
        """Whether encryption of transmitted frames is enabled"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def protect(self) -> bool:
        """Whether protection of transmitted frames is enabled"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def include_sci(self) -> bool:
        """Whether SCI is always included in transmitted SecTAG"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
        property_name='Es',
    )
    def end_station_enabled(self) -> bool:
        """Whether End Station bit is enabled in SecTAG"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
        property_name='Scb',
    )
    def scb_enabled(self) -> bool:
        """Whether Single Copy Broadcast is enabled in SecTAG"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def replay_protect(self) -> bool:
        """Whether replay protection is enabled"""
        raise NotImplementedError


class NetworkManagerDeviceMacvlanInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Macvlan',
):
    """MACVLAN device interface"""

    @dbus_property_async(
        property_signature='o',
    )
    def parent(self) -> str:
        """Path to parent device"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def mode(self) -> str:
        """MacVlan mode

        One of:
        * private
        * vepa
        * bridge
        * passthru
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def no_promisc(self) -> bool:
        """Whether this device is blocked from promiscuous mode"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def tap(self) -> bool:
        """Whether the device is macvtap"""
        raise NotImplementedError


class ModemCapabilities(IntFlag):
    """Modem capabilities flags"""
    NONE = 0x0
    ANALOG_WIRE = 0x1
    CDMA = 0x2
    GSM = 0x4
    LTE = 0x8


class NetworkManagerDeviceModemInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Modem',
):
    """Modem device interface"""

    @dbus_property_async(
        property_signature='u',
    )
    def modem_capabilities(self) -> int:
        """Modem radio technology

        Switching the radio technology might require
        firmware reboot.

        See :py:class:`ModemCapabilities`
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def current_capabilities(self) -> int:
        """Current supported radio technologies without firmware reload"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def device_id(self) -> str:
        """Unique modem identifier"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def operator_code(self) -> str:
        """Mobile country codes (MCC) + mobile network codes (MNC)

        Blank if disconnected or not a 3GPP modem.
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def apn(self) -> str:
        """Access point name modem is connected to.

        Blank if disconnected.
        """
        raise NotImplementedError


class NetworkManagerDeviceOlpcMeshInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.OlpcMesh',
):
    """OLPC Wireless Mesh device interface"""

    @dbus_property_async(
        property_signature='o',
    )
    def companion(self) -> str:
        """Path to companion device"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def active_channel(self) -> int:
        """Currently active channel"""
        raise NotImplementedError


class NetworkManagerDeviceOvsBridgeInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.OvsBridge',
):
    """Open vSwitch device interface"""

    @dbus_property_async(
        property_signature='ao',
    )
    def slaves(self) -> List[str]:
        """List of paths to slave devices"""
        raise NotImplementedError


class NetworkManagerDeviceOvsPortInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.OvsPort',
):
    """Open vSwitch port device interface"""

    @dbus_property_async(
        property_signature='ao',
    )
    def slaves(self) -> List[str]:
        """List of paths to slave devices"""
        raise NotImplementedError


class NetworkManagerDeviceStatisticsInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Statistics',
):
    """Device statistics interface"""

    @dbus_property_async(
        property_signature='u',
    )
    def refresh_rate_ms(self) -> int:
        """Refreshed rate of properties of this interface in milliseconds."""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='t',
    )
    def tx_bytes(self) -> int:
        """Number of transmitted bytes"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='t',
    )
    def rx_bytes(self) -> int:
        """Number of received bytes"""
        raise NotImplementedError


class NetworkManagerDeviceTeamInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Team',
):
    """Teaming device

    Aggregates multiple devices to a single one.

    Seems to be Network Manager specific type bond device.
    """
    @dbus_property_async(
        property_signature='ao',
    )
    def slaves(self) -> List[str]:
        """List of paths to slave devices"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def config(self) -> str:
        """JSON config of the device"""
        raise NotImplementedError


class NetworkManagerDeviceTunInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Tun',
):
    """Userspace tunneling device interface"""

    @dbus_property_async(
        property_signature='x',
    )
    def owner(self) -> int:
        """User ID (UID) of the device owner"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='x',
    )
    def group(self) -> int:
        """Group ID (GID) of the device owner"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def mode(self) -> str:
        """Tunnel mode

        Either tun or tap
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def no_pi(self) -> bool:
        """If true no protocol info is prepended to packets"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def vnet_hdr(self) -> bool:
        """If true tunnel packets include virtio network header"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def multi_queue(self) -> bool:
        """If true callers can connect multiple times"""
        raise NotImplementedError


class NetworkManagerDeviceVethInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Veth',
):
    """Virtual Ethernet device interface"""

    @dbus_property_async(
        property_signature='o',
    )
    def peer(self) -> str:
        """Path to peer device"""
        raise NotImplementedError


class NetworkManagerDeviceVlanInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Vlan',
):
    """Virtual LAN device interface"""

    @dbus_property_async(
        property_signature='o',
    )
    def parent(self) -> str:
        """Path to parent device"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def vlan_id(self) -> int:
        """VLAN ID of this interface"""
        raise NotImplementedError


class NetworkManagerDeviceVrfInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Vrf',
):
    """Virtual routing and forwarding device interface"""

    @dbus_property_async(
        property_signature='u',
    )
    def table(self) -> int:
        """Routing table ID of this device"""
        raise NotImplementedError


class NetworkManagerDeviceVxlanInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Vxlan',
):
    """Virtual Extensible LAN device interface"""

    @dbus_property_async(
        property_signature='o',
    )
    def parent(self) -> str:
        """Path to parent device"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
        property_name='Id'
    )
    def vxlan_id(self) -> int:
        """VXLAN Network Identifier (VNI)"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def group(self) -> str:
        """Multicast IP group used to communicate (v4 or v6)"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def local(self) -> str:
        """Local IP address used to communicate"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='y',
    )
    def tos(self) -> int:
        """TOS field of IP packets"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='y',
    )
    def ttl(self) -> int:
        """TTL of IP packets"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def learning(self) -> bool:
        """If true VXLAN dynamically learns the remote IP address"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def ageing(self) -> int:
        """Interval in seconds at which kernel purges stale cached addresses"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def limit(self) -> int:
        """Maximum number of entries in forwarding table"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='q',
    )
    def dst_port(self) -> int:
        """Destination port for outgoing packets"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='q',
    )
    def src_port_min(self) -> int:
        """Lowest source port for outgoing packets"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='q',
    )
    def src_port_max(self) -> int:
        """Highest source port for outgoing packets"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
        property_name='Proxy'
    )
    def arp_proxy(self) -> bool:
        """If true ARP proxying is enabled"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
        property_name='Rsc'
    )
    def route_short_circuit(self) -> bool:
        """If true route short circuiting is enabled"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def l2miss(self) -> bool:
        """If true emit netlink notification on L2 switch misses"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def l3miss(self) -> bool:
        """If true emit netlink notification on L3 switch misses"""
        raise NotImplementedError


class NetworkManagerDeviceWifiP2PInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.WifiP2P',
):
    """Wi-Fi Peet to Peer device interface"""

    @dbus_method_async(
        input_signature='a{sv}',
    )
    async def start_find(
        self,
        options: Dict[str, Tuple[str, Any]],
    ) -> None:
        """Start find operation for Wi-Fi P2P peers

        Options supported:

        * ``timeout`` of type "i" which is a number of seconds \
                    for search timeout between 1-600. Default 300.
        """
        raise NotImplementedError

    @dbus_method_async(
    )
    async def stop_find(
        self,
    ) -> None:
        """Stop find operation"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ao',
    )
    def peers(self) -> List[str]:
        """List of peer objects paths visible to this Wi-Fi device"""
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='o',
    )
    def peer_added(self) -> str:
        """Signal when peer has been added with the new peer object path"""
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='o',
    )
    def peer_removed(self) -> str:
        """Signal when peer has been lost with the lost peer object path"""
        raise NotImplementedError


class NetworkManagerDeviceWiredInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Wired',
):
    """Wired Ethernet device interface"""

    @dbus_property_async(
        property_signature='s',
    )
    def perm_hw_address(self) -> str:
        """Permanent hardware address"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def speed(self) -> int:
        """Design speed of the device in megabits/second"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='as',
    )
    def s390_subchannels(self) -> List[str]:
        """Array of IBM Z Architecture S/390 subchannels"""
        raise NotImplementedError


class NetworkManagerDeviceWireGuardInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.WireGuard',
):
    """WireGuard device interface"""

    @dbus_property_async(
        property_signature='ay',
    )
    def public_key(self) -> bytes:
        """Public key of the device"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='q',
    )
    def listen_port(self) -> int:
        """UDP listening port for incoming connections"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def fw_mark(self) -> int:
        """Optional packet marker to set routing policy"""
        raise NotImplementedError


class WirelessCapabilities(IntFlag):
    """Wireless device capabilities flags"""
    NONE = 0x0
    CIPHER_WEP40 = 0x1
    CIPHER_WEP104 = 0x2
    CIPHER_TKIP = 0x4
    CIPHER_CCMP = 0x8
    WPA = 0x10
    WPA2 = 0x20
    AP = 0x40
    ADHOC = 0x80
    FREQ_VALID = 0x100
    FREQ_2GHZ = 0x200
    FREQ_5GHZ = 0x400
    MESH = 0x800
    IBSS_WPA2 = 0x2000


class NetworkManagerDeviceWirelessInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device.Wireless',
):
    """Wi-Fi device interface"""

    @dbus_method_async(
        result_signature='ao',
    )
    async def get_all_access_points(
        self,
    ) -> List[str]:
        """Return the list of paths to all access points visible

        Includes the hidden ones without SSID.
        """
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sv}',
    )
    async def request_scan(
        self,
        options: Dict[str, Tuple[str, Any]],
    ) -> None:
        """Request to scan for Wi-Fi access points

        Options:

        * ``ssids`` of type 'ayy' (List[bytes])
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def perm_hw_address(self) -> str:
        """Permanent hardware address"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def mode(self) -> int:
        """Operating mode of the device

        See :py:class:`WiFiOperationMode`
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def bitrate(self) -> int:
        """Bit rate currently used in kilobits/second"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ao',
    )
    def access_points(self) -> List[str]:
        """List of paths of access point currently visible"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def active_access_point(self) -> str:
        """Path to currently used access point"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def wireless_capabilities(self) -> int:
        """List of wireless device capabilities

        See :py:class:`WirelessCapabilities`
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='x',
    )
    def last_scan(self) -> int:
        """Time in CLOCK_BOOTTIME milliseconds since last scan

        Value -1 means never scanned.
        """
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='o',
    )
    def access_point_added(self) -> str:
        """Signal when new point is added with the path"""
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='o',
    )
    def access_point_removed(self) -> str:
        """Signal when a point was removed with the path"""
        raise NotImplementedError


class DeviceCapabilities(IntFlag):
    """Device Capabilities"""
    NONE = 0x0
    SUPPORTED = 0x1
    CARRIER_DETECTABLE = 0x2
    IS_SOFTWARE = 0x4
    CAN_SRIOV = 0x8


class DeviceState(IntEnum):
    """Device State"""
    UNKNOWN = 0
    UNMANAGED = 10
    UNAVAILABLE = 20
    DISCONNECTED = 30
    PREPARE = 40
    CONFIG = 50
    NEED_AUTH = 60
    IP_CONFIG = 70
    IP_CHECK = 80
    SECONDARIES = 90
    ACTIVATED = 100
    DEACTIVATING = 110
    FAILED = 120


class DeviceStateReason(IntEnum):
    """Device State reason"""
    NONE = 0
    UNKNOWN = 1
    NOW_MANAGED = 2
    NOW_UNMANAGED = 3
    CONFIG_FAILED = 4
    IP_CONFIG_UNAVAILABLE = 5
    IP_CONFIG_EXPIRED = 6
    NO_SECRETS = 7
    SUPPLICANT_DISCONNECT = 8
    SUPPLICANT_CONFIG_FAILED = 9
    SUPPLICANT_FAILED = 10
    SUPPLICANT_TIMEOUT = 11
    PPP_START_FAILED = 12
    PPP_DISCONNECT = 13
    PPP_FAILED = 14
    DHCP_START_FAILED = 15
    DHCP_ERROR = 16
    DHCP_FAILED = 17
    SHARED_START_FAILED = 18
    SHARED_FAILED = 19
    AUTOIP_START_FAILED = 20
    AUTOIP_ERROR = 21
    AUTOIP_FAILED = 22
    MODEM_BUSY = 23
    MODEM_NO_DIAL_TONE = 24
    MODEM_NO_CARRIER = 25
    MODEM_DIAL_TIMEOUT = 26
    MODEM_DIAL_FAILED = 27
    MODEM_INIT_FAILED = 28
    GSM_APN_FAILED = 29
    GSM_REGISTRATION_NOT_SEARCHING = 30
    GSM_REGISTRATION_DENIED = 31
    GSM_REGISTRATION_TIMEOUT = 32
    GSM_REGISTRATION_FAILED = 33
    GSM_PIN_CHECK_FAILED = 34
    FIRMWARE_MISSING = 35
    REMOVED = 36
    SLEEPING = 37
    CONNECTION_REMOVED = 38
    USER_REQUESTED = 39
    CARRIER = 40
    CONNECTION_ASSUMED = 41
    SUPPLICANT_AVAILABLE = 42
    MODEM_NOT_FOUND = 43
    BT_FAILED = 44
    GSM_SIM_NOT_INSERTED = 45
    GSM_SIM_PIN_REQUIRED = 46
    GSM_SIM_PUK_REQUIRED = 47
    GSM_SIM_WRONG = 48
    INFINIBAND_MODE = 49
    DEPENDENCY_FAILED = 50
    BR2684_FAILED = 51
    MODEM_MANAGER_UNAVAILABLE = 52
    SSID_NOT_FOUND = 53
    SECONDARY_CONNECTION_FAILED = 54
    DCB_FCOE_FAILED = 55
    TEAMD_CONTROL_FAILED = 56
    MODEM_FAILED = 57
    MODEM_AVAILABLE = 58
    SIM_PIN_INCORRECT = 59
    NEW_ACTIVATION = 60
    PARENT_CHANGED = 61
    PARENT_MANAGED_CHANGED = 62
    OVSDB_FAILED = 63
    IP_ADDRESS_DUPLICATE = 64
    IP_METHOD_UNSUPPORTED = 65
    SRIOV_CONFIGURATION_FAILED = 66
    PEER_NOT_FOUND = 67


class DeviceType(IntEnum):
    """Device Type"""
    UNKNOWN = 0
    ETHERNET = 1
    WIFI = 2
    UNUSED1 = 3
    UNUSED2 = 4
    BLUETOOTH = 5
    OLPC_MESH = 6
    WIMAX = 7
    MODEM = 8
    INFINIBAND = 9
    BOND = 10
    VLAN = 11
    ADSL = 12
    BRIDGE = 13
    GENERIC = 14
    TEAM = 15
    TUN = 16
    IP_TUNNEL = 17
    MACVLAN = 18
    VXLAN = 19
    VETH = 20
    MACSEC = 21
    DUMMY = 22
    PPP = 23
    OVS_INTERFACE = 24
    OVS_PORT = 25
    OVS_BRIDGE = 26
    WPAN = 27
    SIXLOWPAN = 28
    WIREGUARD = 29
    WIFI_P2P = 30
    VRF = 31


class DeviceMetered(IntEnum):
    """Device Metered state"""
    UNKNOWN = 0
    YES = 1
    NO = 2
    GUESS_YES = 3
    GUESS_NO = 4


class ConnectivityState(IntEnum):
    """Connectivity state"""
    UNKNOWN = 0
    NONE = 1
    PORTAL = 2
    LIMITED = 3
    FULL = 4


class DeviceInterfaceFlags(IntFlag):
    """Device network interface flags"""
    NONE = 0x0
    UP = 0x1
    LOWER_UP = 0x2
    CARRIER = 0x10000


class NetworkManagerDeviceInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Device',
):
    """Device interface with common functionality"""

    @dbus_method_async(
        input_signature='a{sa{sv}}tu',
    )
    async def reapply(
        self,
        connection: Dict[str, Dict[str, Tuple[str, Any]]],
        version_id: int,
        flags: int = 0,
    ) -> None:
        """Attempt to update the device configuration without deactivating

        :param connection: Optional connection settings to be reapplied
        :param version_id: Current version id of applied connection.
        :param flags: currently there are no flags so it should be zero
        """
        raise NotImplementedError

    @dbus_method_async(
        input_signature='u',
        result_signature='a{sa{sv}}t',
    )
    async def get_applied_connection(
        self,
        flags: int = 0,
    ) -> Tuple[Dict[str, Dict[str, Tuple[str, Any]]], int]:
        """Get the currently applied connection on the device

        :param flags: Currently there are no flags so this should be zero
        :returns: Tuple of dictionary of connection settings \
                 and an int version id.
        """
        raise NotImplementedError

    @dbus_method_async(
    )
    async def disconnect(
        self,
    ) -> None:
        """Disconnect device and prevent from automatically activating"""
        raise NotImplementedError

    @dbus_method_async(
    )
    async def delete(
        self,
    ) -> None:
        """Deletes the software device.

        Raises an exception if the device is a hardware device.
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def udi(self) -> str:
        """Not stable device identifier

        Should not be used for tracking connection.
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def path(self) -> str:
        """Device path as exposed by Udev"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def interface(self) -> str:
        """Name of device control interface (???)"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def ip_interface(self) -> str:
        """Name of device data interface (???)"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def driver(self) -> str:
        """Driver handling device"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def driver_version(self) -> str:
        """Driver version"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def firmware_version(self) -> str:
        """Firmware version of the device"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def capabilities(self) -> int:
        """Capabilities of the device

        See :py:class:`DeviceCapabilities`
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def state(self) -> int:
        """Device state.

        See :py:class:`DeviceState`
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='(uu)',
    )
    def state_reason(self) -> Tuple[int, int]:
        """Current state and the reason.

        See :py:class:`DeviceState` and :py:class:`DeviceStateReason`
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def active_connection(self) -> str:
        """Path of active connection object"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def ip4_config(self) -> str:
        """Path of Ip4Config object

        Only valid when device is in ACTIVATED state.
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def dhcp4_config(self) -> str:
        """Path of Dhcp4 object

        Only valid when device is in ACTIVATED state.
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def ip6_config(self) -> str:
        """Path to Ip6Config object

        Only valid when device is in ACTIVATED state.
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def dhcp6_config(self) -> str:
        """Path to Dhcp6 object

        Only valid when device is in ACTIVATED state.
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def managed(self) -> bool:
        """Whether or not this device is manager by NetworkManager

        This setting can be written.
        The value is not persistent on NetworkManager restarts.
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def autoconnect(self) -> bool:
        """If true device is allowed to auto connect

        Can be written.
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def firmware_missing(self) -> bool:
        """If true means the device is missing firmware"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def nm_plugin_missing(self) -> bool:
        """If true means the plugin for NetworkManager is missing"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def device_type(self) -> int:
        """Device type

        See :py:class:`DeviceType`
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ao',
    )
    def available_connections(self) -> List[str]:
        """List of object paths to connections available"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def physical_port_id(self) -> str:
        """Physical network port of the device"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def mtu(self) -> int:
        """Maximum Transmission Unit"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def metered(self) -> int:
        """Whether the traffic is subject to limitations

        See :py:class:`DeviceMetered`
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='aa{sv}',
    )
    def lldp_neighbors(self) -> List[Dict[str, Tuple[str, Any]]]:
        """List of LLDP neighbors

        Each element is the dictionary of LLDP TLV names \
        to variants values.
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def real(self) -> bool:
        """Whether this device is exists

        If it does not yet exist it can be automatically created \
        if one of the available connections becomes activated.
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def ip4_connectivity(self) -> int:
        """IPv4 connectivity state

        See :py:class:`ConnectivityState`
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def ip6_connectivity(self) -> int:
        """IPv6 connectivity state

        See :py:class:`ConnectivityState`
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def interface_flags(self) -> int:
        """Interface flags

        See :py:class:`DeviceInterfaceFlags`
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def hw_address(self) -> str:
        """Hardware address"""
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='uuu',
    )
    def state_changed(self) -> Tuple[int, int, int]:
        """Signal when device state has changed

        Tuple of new state, old state and reason for new state.

        See :py:class:`DeviceState` and :py:class:`DeviceStateReason`
        """
        raise NotImplementedError


class NetworkManagerDHCP4ConfigInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.DHCP4Config',
):
    """DHCPv4 configuration"""

    @dbus_property_async(
        property_signature='a{sv}',
    )
    def options(self) -> Dict[str, Tuple[str, Any]]:
        """Options and configurations returned by DHCPv4 server"""
        raise NotImplementedError


class NetworkManagerDHCP6ConfigInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.DHCP6Config',
):
    """DHCPv6 configuration"""

    @dbus_property_async(
        property_signature='a{sv}',
    )
    def options(self) -> Dict[str, Tuple[str, Any]]:
        """Options and configurations returned by DHCPv4 server"""
        raise NotImplementedError


class NetworkManagerDnsManagerInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.DnsManager',
):
    """DNS configuration state"""

    @dbus_property_async(
        property_signature='s',
    )
    def mode(self) -> str:
        """Current DNS processing mode"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def rc_manager(self) -> str:
        """Current resolv.conf management mode"""
        raise NotImplementedError


class NetworkManagerIP4ConfigInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.IP4Config',
):
    """IPv4 configuration state"""

    @dbus_property_async(
        property_signature='aa{sv}',
    )
    def address_data(self) -> List[Dict[str, Tuple[str, Any]]]:
        """Array of IP address data objects

        Each dictionary includes ``'address'`` item with IP address string \
        and ``'prefix'`` with an int of prefix. Some addresses may include \
        additional attributes.
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def gateway(self) -> str:
        """Gateway in use"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='aa{sv}',
    )
    def route_data(self) -> List[Dict[str, Tuple[str, Any]]]:
        """Array of route data objects

        Each dictionary includes 'dest' (IP address string), 'prefix' (int).
        Some routes may include 'next-hop', 'metric' and additional attributes.
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='aa{sv}',
    )
    def nameserver_data(self) -> List[Dict[str, Tuple[str, Any]]]:
        """List of nameserver objects

        Currently, each dictionary only has the 'address' value. \
        (string of IP address)
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='as',
    )
    def domains(self) -> List[str]:
        """List of domains this address belongs to."""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='as',
    )
    def searches(self) -> List[str]:
        """List of DNS searches"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='as',
    )
    def dns_options(self) -> List[str]:
        """List of dns options"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='i',
    )
    def dns_priority(self) -> int:
        """Relative priority of DNS servers"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='as',
    )
    def wins_server_data(self) -> List[str]:
        """Windows Internet Name Service servers"""
        raise NotImplementedError


class NetworkManagerIP6ConfigInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.IP6Config',
):
    """IPv6 configuration"""

    @dbus_property_async(
        property_signature='aa{sv}',
    )
    def address_data(self) -> List[Dict[str, Tuple[str, Any]]]:
        """Array of IP address data objects

        Each dictionary includes ``'address'`` item with IP address string \
        and ``'prefix'`` with an int of prefix. Some addresses may include \
        additional attributes.
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def gateway(self) -> str:
        """Gateway in use"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='aa{sv}',
    )
    def route_data(self) -> List[Dict[str, Tuple[str, Any]]]:
        """Array of route data objects

        Each dictionary includes 'dest' (IP address string), 'prefix' (int).
        Some routes may include 'next-hop', 'metric' and additional attributes.
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='aay',
    )
    def nameservers(self) -> List[bytes]:
        """Nameservers in use"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='as',
    )
    def domains(self) -> List[str]:
        """List of domains this address belongs to."""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='as',
    )
    def searches(self) -> List[str]:
        """List of DNS searches"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='as',
    )
    def dns_options(self) -> List[str]:
        """List of dns options"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='i',
    )
    def dns_priority(self) -> int:
        """Relative priority of DNS servers"""
        raise NotImplementedError


class NetworkManagerPPPInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.PPP',
):
    """Helper interface for PPP plugin"""

    @dbus_method_async(
        result_signature='ss',
    )
    async def need_secrets(
        self,
    ) -> Tuple[str, str]:
        """Need secrets?

        Returns the tuple of username and password
        """
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sv}',
    )
    async def set_ip4_config(
        self,
        config: Dict[str, Tuple[str, Any]],
    ) -> None:
        """Set IPv4 configuration"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sv}',
    )
    async def set_ip6_config(
        self,
        config: Dict[str, Tuple[str, Any]],
    ) -> None:
        """Set IPv6 configuration"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='u',
    )
    async def set_state(
        self,
        state: int,
    ) -> None:
        """Set connection state.

        Not documented upstream.
        """
        raise NotImplementedError

    @dbus_method_async(
        input_signature='i',
    )
    async def set_ifindex(
        self,
        ifindex: int,
    ) -> None:
        """Set input device index

        Not documented upstream.
        """
        raise NotImplementedError


class NetworkManagerSecretAgentInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.SecretAgent',
):
    """D-Bus interface that stores secrets such as Wi-Fi passwords"""

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
        """Retrieve stored secrets"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='os',
    )
    async def cancel_get_secrets(
        self,
        connection_path: str,
        setting_name: str,
    ) -> None:
        """Cancel pending get_secrets request"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sa{sv}}o',
    )
    async def save_secrets(
        self,
        connection: Dict[str, Dict[str, Tuple[str, Any]]],
        connection_path: str,
    ) -> None:
        """Save given secrets"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sa{sv}}o',
    )
    async def delete_secrets(
        self,
        connection: Dict[str, Dict[str, Tuple[str, Any]]],
        connection_path: str,
    ) -> None:
        """Delete secrets"""
        raise NotImplementedError


class ConnectionFlags(IntFlag):
    """Connection flags"""
    NONE = 0x0
    UNSAVED = 0x1
    GENERATED = 0x2
    VOLATILE = 0x4
    EXTERNAL = 0x8


class NetworkManagerSettingsConnectionInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Settings.Connection',
):
    """Represents a single network connection"""

    @dbus_method_async(
        input_signature='a{sa{sv}}',
    )
    async def update(
        self,
        properties: Dict[str, Dict[str, Tuple[str, Any]]],
    ) -> None:
        """Update connection settings.

        Replaces all previous settings and properties.
        """
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sa{sv}}',
    )
    async def update_unsaved(
        self,
        properties: Dict[str, Dict[str, Tuple[str, Any]]],
    ) -> None:
        """Update connection settings but do not save to disk"""
        raise NotImplementedError

    @dbus_method_async(
    )
    async def delete(
        self,
    ) -> None:
        """Delete connection"""
        raise NotImplementedError

    @dbus_method_async(
        result_signature='a{sa{sv}}',
    )
    async def get_settings(
        self,
    ) -> Dict[str, Dict[str, Tuple[str, Any]]]:
        """Get connection settings"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='s',
        result_signature='a{sa{sv}}',
    )
    async def get_secrets(
        self,
        setting_name: str,
    ) -> Dict[str, Dict[str, Tuple[str, Any]]]:
        """Get connection secrets"""
        raise NotImplementedError

    @dbus_method_async(
    )
    async def clear_secrets(
        self,
    ) -> None:
        """Clear connection secrets"""
        raise NotImplementedError

    @dbus_method_async(
    )
    async def save(
        self,
    ) -> None:
        """Save connection settings to storage"""
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
        """Update connection settings"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def unsaved(self) -> bool:
        """If true some settings are not saved to disk"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def flags(self) -> int:
        """Connection flags

        See :py:class:`ConnectionFlags`
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def filename(self) -> str:
        """File that stores connection settings"""
        raise NotImplementedError

    @dbus_signal_async(
    )
    def updated(self) -> None:
        """Signal when connection updated"""
        raise NotImplementedError

    @dbus_signal_async(
    )
    def removed(self) -> None:
        """Signal when connection is removed"""
        raise NotImplementedError


class NetworkManagerSettingsInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.Settings',
):
    """Global NetworkManager settings"""

    @dbus_method_async(
        result_signature='ao',
    )
    async def list_connections(
        self,
    ) -> List[str]:
        """List of connection object paths"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='s',
        result_signature='o',
    )
    async def get_connection_by_uuid(
        self,
        uuid: str,
    ) -> str:
        """Get connection path by UUID"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sa{sv}}',
        result_signature='o',
    )
    async def add_connection(
        self,
        connection: Dict[str, Dict[str, Tuple[str, Any]]],
    ) -> str:
        """Add connection and save to disk"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sa{sv}}',
        result_signature='o',
    )
    async def add_connection_unsaved(
        self,
        connection: Dict[str, Dict[str, Tuple[str, Any]]],
    ) -> str:
        """Add connection and do not save"""
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
        """Add connection. Flags indicate whether to save or not"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='as',
        result_signature='bas',
    )
    async def load_connections(
        self,
        filenames: List[str],
    ) -> Tuple[bool, List[str]]:
        """Load connections from filenames

        :returns: Tuple of success and list of failed connection filenames.
        """
        raise NotImplementedError

    @dbus_method_async(
        result_signature='b',
    )
    async def reload_connections(
        self,
    ) -> bool:
        """Reload all connection from disk"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='s',
    )
    async def save_hostname(
        self,
        hostname: str,
    ) -> None:
        """Save hostname to persistent configuration

        If blank hostname is cleared.
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ao',
    )
    def connections(self) -> List[str]:
        """List of paths to connection objects"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def hostname(self) -> str:
        """Current hostname"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def can_modify(self) -> bool:
        """If true adding and modifying connections is supported"""
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='o',
    )
    def new_connection(self) -> str:
        """Signal when new connection has been added with the path"""
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='o',
    )
    def connection_removed(self) -> str:
        """Signal when connection was removed with the path"""
        raise NotImplementedError


class VpnState(IntEnum):
    """VPN State"""
    UNKNOWN = 0
    INIT = 1
    SHUTDOWN = 2
    STARTING = 3
    STARTED = 4
    STOPPING = 5
    STOPPED = 6


class VpnFailure(IntEnum):
    """VPN Failure"""
    LOGIN_FAILURE = 0
    CONNECT_FAILED = 1
    BAD_IP_CONFIG = 3


class NetworkManagerVPNConnectionInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.VPN.Connection',
):
    """VPN connection interface"""

    @dbus_property_async(
        property_signature='u',
    )
    def vpn_state(self) -> int:
        """VPN connection state

        See :py:class:`ConnectionState`
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def banner(self) -> str:
        """Banner string of VPN connection"""
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='uu',
    )
    def vpn_state_changed(self) -> Tuple[int, int]:
        """Signal when VPN state changed

        Tuple of new state and reason.
        See :py:class:`ConnectionState` and :py:class:`ConnectionStateReason`
        """
        raise NotImplementedError


class NetworkManagerVPNPluginInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.VPN.Plugin',
):
    """Interface provided by VPN plugins"""

    @dbus_method_async(
        input_signature='a{sa{sv}}',
    )
    async def connect(
        self,
        connection: Dict[str, Dict[str, Tuple[str, Any]]],
    ) -> None:
        """Connect to described connection

        Interactive secrets requests not allowed.
        """
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sa{sv}}a{sv}',
    )
    async def connect_interactive(
        self,
        connection: Dict[str, Dict[str, Tuple[str, Any]]],
        details: Dict[str, Tuple[str, Any]],
    ) -> None:
        """Connect to described connection

        Interactive secrets requests allowed.
        (emits secrets_required signal)
        """
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sa{sv}}',
        result_signature='s',
    )
    async def need_secrets(
        self,
        settings: Dict[str, Dict[str, Tuple[str, Any]]],
    ) -> str:
        """Asks plugin if connection will require secrets

        :return: Setting name that requires secrets
        """
        raise NotImplementedError

    @dbus_method_async(
    )
    async def disconnect(
        self,
    ) -> None:
        """Disconnect from VPN"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sv}',
    )
    async def set_config(
        self,
        config: Dict[str, Tuple[str, Any]],
    ) -> None:
        """Set generic connection details"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sv}',
    )
    async def set_ip4_config(
        self,
        config: Dict[str, Tuple[str, Any]],
    ) -> None:
        """Set IPv4 settings"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sv}',
    )
    async def set_ip6_config(
        self,
        config: Dict[str, Tuple[str, Any]],
    ) -> None:
        """Set IPv6 settings"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='s',
    )
    async def set_failure(
        self,
        reason: str,
    ) -> None:
        """Set the plugin failure reason"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='a{sa{sv}}',
    )
    async def new_secrets(
        self,
        connection: Dict[str, Dict[str, Tuple[str, Any]]],
    ) -> None:
        """Called in response to secrets_required signal"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def state(self) -> int:
        """VPN state

        See :py:class:`VpnState`
        """
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='u',
    )
    def state_changed(self) -> int:
        """Signal when VPN state changed with new VPN state.

        See :py:class:`VpnState`
        """
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='sas',
    )
    def secrets_required(self) -> Tuple[str, List[str]]:
        """Signal when secrest are required during ongoing connection"""
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def config(self) -> Dict[str, Tuple[str, Any]]:
        """Signal when plugin obtained generic configuration"""
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def ip4_config(self) -> Dict[str, Tuple[str, Any]]:
        """Signal when plugin obtained IPv4 configuration"""
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='a{sv}',
    )
    def ip6_config(self) -> Dict[str, Tuple[str, Any]]:
        """Signal when plugin obtained IPv6 configuration"""
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='s',
    )
    def login_banner(self) -> str:
        """Signal when plugin receives login banner from VPN service"""
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature='u',
    )
    def failure(self) -> int:
        """Signal when VPN failure occurs

        See :py:class:`VpnFailure`
        """
        raise NotImplementedError


class NetworkManagerWifiP2PPeerInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager.WifiP2PPeer',
):
    """Interface of a peer in Wi-Fi P2P connection"""

    @dbus_property_async(
        property_signature='s',
    )
    def name(self) -> str:
        """Device name"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def flags(self) -> int:
        """Flags describing capabilities of the point

        See :py:class:`AccessPointCapabilities`
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def manufacturer(self) -> str:
        """Manufacturer of the Wi-Fi P2P peer."""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def model(self) -> str:
        """Peer model"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def model_number(self) -> str:
        """Peer model number"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def serial(self) -> str:
        """Peer serial"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ay',
    )
    def wfd_i_es(self) -> bytes:
        """Wi-Fi Display Information Elements of the peer"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='y',
    )
    def strength(self) -> int:
        """Current signal quality of the peer, in percent."""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='i',
    )
    def last_seen(self) -> int:
        """Timestamp in CLOCK_BOOTTIME seconds since last seen in scan

        Value of -1 means that the point was never found in scans.
        """
        raise NotImplementedError


class NetworkManagerConnectivityState(IntEnum):
    """NetworkManager connectivity state enum"""
    UNKNOWN = 0
    NONE = 1
    PORTAL = 2
    LIMITED = 3
    FULL = 4


class NetworkManagerState(IntEnum):
    """NetworkManager state enum"""
    UNKNOWN = 0
    ASLEEP = 10
    DISCONNECTED = 20
    DISCONNECTING = 30
    CONNECTING = 40
    CONNECTED_LOCAL = 50
    CONNECTED_SITE = 60
    GLOBAL = 70


class NetworkManagerInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.freedesktop.NetworkManager',
):
    """Main network manager interface"""

    @dbus_method_async(
        input_signature='u',
    )
    async def reload(
        self,
        flags: int = 0x0,
    ) -> None:
        """Reload NetworkManager configuration

        Flags control what to reload:

        * 0x0 everything
        * 0x1 NetworkManager.conf
        * 0x2 DNS configuration
        * 0x4 Restart DNS plugin

        :param flags: Reload what?
        """
        raise NotImplementedError

    @dbus_method_async(
        result_signature='ao',
    )
    async def get_devices(
        self,
    ) -> List[str]:
        """Get list of device object paths known"""
        raise NotImplementedError

    @dbus_method_async(
        result_signature='ao',
    )
    async def get_all_devices(
        self,
    ) -> List[str]:
        """Get list of device object paths with placeholders"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='s',
        result_signature='o',
    )
    async def get_device_by_ip_iface(
        self,
        iface: str,
    ) -> str:
        """Get device object path by interface name"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='ooo',
        result_signature='o',
    )
    async def activate_connection(
        self,
        connection: str = '/',
        device: str = '/',
        specific_object: str = '/',
    ) -> str:
        """Activate the connection.

        :return: Activated connection object path.
        """
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
        """Add a new connection and activate"""
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
        """Add a new connection and activate"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='o',
    )
    async def deactivate_connection(
        self,
        active_connection: str,
    ) -> None:
        """Deactivate connection by given path"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='b',
    )
    async def sleep(
        self,
        sleep: bool,
    ) -> None:
        """Intended for system suspend/resume tracking not user"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='b',
    )
    async def enable(
        self,
        enable: bool,
    ) -> None:
        """Disables all networking when set to false"""
        raise NotImplementedError

    @dbus_method_async(
        result_signature='a{ss}',
    )
    async def get_permissions(
        self,
    ) -> Dict[str, str]:
        """Returns the permissions of caller"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='ss',
    )
    async def set_logging(
        self,
        level: str,
        domains: str,
    ) -> None:
        """Set logging verbosity and which operations are logged"""
        raise NotImplementedError

    @dbus_method_async(
        result_signature='ss',
    )
    async def get_logging(
        self,
    ) -> Tuple[str, str]:
        """Get current logging settings"""
        raise NotImplementedError

    @dbus_method_async(
        result_signature='u',
    )
    async def check_connectivity(
        self,
    ) -> int:
        """Get current connectivity state

        See  :py:class:`NetworkManagerConnectivityState`
        """
        raise NotImplementedError

    @dbus_method_async(
        result_signature='u',
        method_name='State',
    )
    async def get_state(
        self,
    ) -> int:
        """Get current NetworkManager state

        See :py:class:`NetworkManagerState`
        """
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
        """Create configuration checkpoint for given devices

        :return: New checkpoint object path
        """
        raise NotImplementedError

    @dbus_method_async(
        input_signature='o',
    )
    async def checkpoint_destroy(
        self,
        checkpoint: str,
    ) -> None:
        """Destroy given checkpoint"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='o',
        result_signature='a{su}',
    )
    async def checkpoint_rollback(
        self,
        checkpoint: str,
    ) -> Dict[str, int]:
        """Use given checkpoint to rollback configuration"""
        raise NotImplementedError

    @dbus_method_async(
        input_signature='ou',
    )
    async def checkpoint_adjust_rollback_timeout(
        self,
        checkpoint: str,
        add_timeout: int,
    ) -> None:
        """Adjust checkpoint rollback timeout"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ao',
    )
    def devices(self) -> List[str]:
        """List of all current devices"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ao',
    )
    def all_devices(self) -> List[str]:
        """List of all current and un-realized devices"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ao',
    )
    def checkpoints(self) -> List[str]:
        """List of all checkpoint objects"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def networking_enabled(self) -> bool:
        """Whether networking enabled or not"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def wireless_enabled(self) -> bool:
        """Whether wireless enabled or not"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def wireless_hardware_enabled(self) -> bool:
        """Whether wireless hardware enabled with RF kill switch"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def wwan_enabled(self) -> bool:
        """Whether mobile broadband devices enabled"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def wwan_hardware_enabled(self) -> bool:
        """Whether mobile hardware devices enabled with RF kill switch"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def wimax_enabled(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature='ao',
    )
    def active_connections(self) -> List[str]:
        """List of active connection paths"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def primary_connection(self) -> str:
        """Object path for primary connection"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def primary_connection_type(self) -> str:
        """Primary connection type"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def metered(self) -> int:
        """Primary connection metered status

        See :py:class:`DeviceMetered`
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='o',
    )
    def activating_connection(self) -> str:
        """Primary connection activating connection"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='b',
    )
    def startup(self) -> bool:
        """Whether NetworkManager is still activating"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def version(self) -> str:
        """NetworkManager version"""
        raise NotImplementedError

    @dbus_property_async(
        property_signature='au',
    )
    def capabilities(self) -> List[int]:
        """NetworkManager capabilities

        * 1 Team devices
        * 2 OpenVSwitch
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def state(self) -> int:
        """Overall state of NetworkManager

        See :py:class:`NetworkManagerState`
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='u',
    )
    def connectivity(self) -> int:
        """Overall state of connectivity

        See :py:class:`NetworkManagerConnectivityState`
        """
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
        """Whether the connectivity checking is enabled

        Can be written.
        """
        raise NotImplementedError

    @dbus_property_async(
        property_signature='s',
    )
    def connectivity_check_uri(self) -> str:
        """URI that network manager will hit to check internet connection"""
        raise NotImplementedError

    @dbus_property_async('a{sv}')
    def global_dns_configuration(self) -> Dict[str, Tuple[str, Any]]:
        """Global DNS connection settings"""
        raise NotImplementedError

    @dbus_signal_async()
    def check_permissions(self) -> None:
        """System authorization changed"""
        raise NotImplementedError

    @dbus_signal_async('u')
    def state_changed(self) -> int:
        """NetworkManager state changed

        See :py:class:`NetworkManagerState`
        """
        raise NotImplementedError

    @dbus_signal_async('o')
    def device_added(self) -> str:
        """Signal when new device has been added with path"""
        raise NotImplementedError

    @dbus_signal_async('o')
    def device_removed(self) -> str:
        """Signal when device had been removed with path"""
        raise NotImplementedError
# endregion Interfaces


# region Helper objects

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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            '/org/freedesktop/NetworkManager')


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            '/org/freedesktop/NetworkManager/AgentManager')


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            '/org/freedesktop/NetworkManager/DnsManager')


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            '/org/freedesktop/NetworkManager/Settings')


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            settings_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,

            device_path)


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
        self._connect(

            NETWORK_MANAGER_SERVICE_NAME,
            device_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            device_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            connection_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            ip4_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            ip6_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            dhcp4_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            dhcpv6_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            point_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            peer_path)


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
        self._connect(
            NETWORK_MANAGER_SERVICE_NAME,
            checkpoint_path)

# endregion Helper objects
