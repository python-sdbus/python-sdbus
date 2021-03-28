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

from enum import IntEnum, IntFlag


class AccessPointCapabilities(IntFlag):
    """Wi-Fi Access point capabilities

    Flags:

    * NONE
    * PRIVACY
    * WPS
    * WPS_BUTTON
    * WPS_PIN
    """
    NONE = 0x0
    PRIVACY = 0x1
    WPS = 0x2
    WPS_BUTTON = 0x4
    WPS_PIN = 0x8


class WpaSecurityFlags(IntFlag):
    """WPA (WiFi protected Access) encryption and authentication types

    Flags:

    * NONE
    * P2P_WEP40
    * P2P_WEP104
    * P2P_TKIP
    * P2P_CCMP
    * BROADCAST_WEP40
    * BROADCAST_WEP104
    * BROADCAST_TKIP
    * BROADCAST_CCMP
    * AUTH_PSK
    * AUTH_802_1X
    * AUTH_SAE
    * AUTH_OWE
    * AUTH_OWE_TM
    * AUTH_EAP_SUITE_B
    """
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
    """Operation mode of WiFi access point

    * UNKNOWN
    * ADHOC
    * INFRASTRUCTURE
    * AP
    * MESH
    """
    UNKNOWN = 0
    ADHOC = 1
    INFRASTRUCTURE = 2
    AP = 3
    MESH = 4


class SecretAgentCapabilities(IntFlag):
    """Secret agent capabilities

    Flags:

    * NONE
    * VPN_HINTS
    """
    NONE = 0x0
    VPN_HINTS = 0x1


class ConnectionState(IntEnum):
    """State of the connection

    * UNKNOWN
    * ACTIVATING
    * ACTIVATED
    * DEACTIVATING
    * DEACTIVATED
    """
    UNKNOWN = 0
    ACTIVATING = 1
    ACTIVATED = 2
    DEACTIVATING = 3
    DEACTIVATED = 4


class ConnectionStateFlags(IntFlag):
    """State of connection flags

    Flags:

    * NONE
    * IS_MASTER
    * IS_SLAVE
    * LAYER2_READY
    * IP4_READY
    * IP6_READY
    * MASTER_HAS_SLAVES
    * LIFE_TIME_BOUND_TO_PROFILE_VISIBILITY
    * EXTERNAL
    """
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
    """Connection state change reason

    * UNKNOWN
    * NONE
    * USER_DISCONNECTED
    * DEVICE_DISCONNECTED
    * SERVICE_STOPPED
    * IP_CONFIG_INVALID
    * CONNECT_TIMEOUT
    * SERVICE_START_TIMEOUT
    * SERVICE_START_FAILED
    * NO_SECRETS
    * LOGIN_FAILED
    * CONNECTION_REMOVED
    * DEPENDENCY_FAILED
    * DEVICE_REALIZE_FAILED
    * DEVICE_REMOVED
    """
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


class BluetoothCapabilities(IntFlag):
    """Bluetooth Capabilities

    Flags:

    * NONE
    * DIAL_UP
    * NETWORK_ACCESS_POINT
    """
    NONE = 0x0
    DIAL_UP = 0x1
    NETWORK_ACCESS_POINT = 0x2


class IpTunnelMode(IntEnum):
    """Mode of IP tunnel

    * UNKNOWN
    * IP_IP
    * GRE
    * SIT
    * ISATAP
    * VTI
    * IP6_IP6
    * IP_IP6
    * IP6_GRE
    * VTI6
    * GRE_TAP
    * IP6_GRE_TAP
    """
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


class ModemCapabilities(IntFlag):
    """Modem capabilities flags

    Flags:

    * NONE
    * ANALOG_WIRE
    * CDMA
    * GSM
    * LTE
    """
    NONE = 0x0
    ANALOG_WIRE = 0x1
    CDMA = 0x2
    GSM = 0x4
    LTE = 0x8


class WirelessCapabilities(IntFlag):
    """Wireless device capabilities flags

    Flags:

    * NONE
    * CIPHER_WEP40
    * CIPHER_WEP104
    * CIPHER_TKIP
    * CIPHER_CCMP
    * WPA
    * WPA2
    * AP
    * ADHOC
    * FREQ_VALID
    * FREQ_2GHZ
    * FREQ_5GHZ
    * MESH
    * IBSS_WPA2
    """
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


class DeviceCapabilities(IntFlag):
    """Device Capabilities

    Flags:

    * NONE
    * SUPPORTED
    * CARRIER_DETECTABLE
    * IS_SOFTWARE
    * CAN_SRIOV
    """
    NONE = 0x0
    SUPPORTED = 0x1
    CARRIER_DETECTABLE = 0x2
    IS_SOFTWARE = 0x4
    CAN_SRIOV = 0x8


class DeviceState(IntEnum):
    """Device State

    * UNKNOWN
    * UNMANAGED
    * UNAVAILABLE
    * DISCONNECTED
    * PREPARE
    * CONFIG
    * NEED_AUTH
    * IP_CONFIG
    * IP_CHECK
    * SECONDARIES
    * ACTIVATED
    * DEACTIVATING
    * FAILED
    """
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
    """Device State reason

    * NONE
    * UNKNOWN
    * NOW_MANAGED
    * NOW_UNMANAGED
    * CONFIG_FAILED
    * IP_CONFIG_UNAVAILABLE
    * IP_CONFIG_EXPIRED
    * NO_SECRETS
    * SUPPLICANT_DISCONNECT
    * SUPPLICANT_CONFIG_FAILED
    * SUPPLICANT_FAILED
    * SUPPLICANT_TIMEOUT
    * PPP_START_FAILED
    * PPP_DISCONNECT
    * PPP_FAILED
    * DHCP_START_FAILED
    * DHCP_ERROR
    * DHCP_FAILED
    * SHARED_START_FAILED
    * SHARED_FAILED
    * AUTOIP_START_FAILED
    * AUTOIP_ERROR
    * AUTOIP_FAILED
    * MODEM_BUSY
    * MODEM_NO_DIAL_TONE
    * MODEM_NO_CARRIER
    * MODEM_DIAL_TIMEOUT
    * MODEM_DIAL_FAILED
    * MODEM_INIT_FAILED
    * GSM_APN_FAILED
    * GSM_REGISTRATION_NOT_SEARCHING
    * GSM_REGISTRATION_DENIED
    * GSM_REGISTRATION_TIMEOUT
    * GSM_REGISTRATION_FAILED
    * GSM_PIN_CHECK_FAILED
    * FIRMWARE_MISSING
    * REMOVED
    * SLEEPING
    * CONNECTION_REMOVED
    * USER_REQUESTED
    * CARRIER
    * CONNECTION_ASSUMED
    * SUPPLICANT_AVAILABLE
    * MODEM_NOT_FOUND
    * BT_FAILED
    * GSM_SIM_NOT_INSERTED
    * GSM_SIM_PIN_REQUIRED
    * GSM_SIM_PUK_REQUIRED
    * GSM_SIM_WRONG
    * INFINIBAND_MODE
    * DEPENDENCY_FAILED
    * BR2684_FAILED
    * MODEM_MANAGER_UNAVAILABLE
    * SSID_NOT_FOUND
    * SECONDARY_CONNECTION_FAILED
    * DCB_FCOE_FAILED
    * TEAMD_CONTROL_FAILED
    * MODEM_FAILED
    * MODEM_AVAILABLE
    * SIM_PIN_INCORRECT
    * NEW_ACTIVATION
    * PARENT_CHANGED
    * PARENT_MANAGED_CHANGED
    * OVSDB_FAILED
    * IP_ADDRESS_DUPLICATE
    * IP_METHOD_UNSUPPORTED
    * SRIOV_CONFIGURATION_FAILED
    * PEER_NOT_FOUND
    """
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
    """Device Type

    * UNKNOWN
    * ETHERNET
    * WIFI
    * UNUSED1
    * UNUSED2
    * BLUETOOTH
    * OLPC_MESH
    * WIMAX
    * MODEM
    * INFINIBAND
    * BOND
    * VLAN
    * ADSL
    * BRIDGE
    * GENERIC
    * TEAM
    * TUN
    * IP_TUNNEL
    * MACVLAN
    * VXLAN
    * VETH
    * MACSEC
    * DUMMY
    * PPP
    * OVS_INTERFACE
    * OVS_PORT
    * OVS_BRIDGE
    * WPAN
    * SIXLOWPAN
    * WIREGUARD
    * WIFI_P2P
    * VRF
    """
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
    """Device Metered state

    * UNKNOWN
    * YES
    * NO
    * GUESS_YES
    * GUESS_NO
    """
    UNKNOWN = 0
    YES = 1
    NO = 2
    GUESS_YES = 3
    GUESS_NO = 4


class ConnectivityState(IntEnum):
    """Connectivity state

    * UNKNOWN
    * NONE
    * PORTAL
    * LIMITED
    * FULL
    """
    UNKNOWN = 0
    NONE = 1
    PORTAL = 2
    LIMITED = 3
    FULL = 4


class DeviceInterfaceFlags(IntFlag):
    """Device network interface flags

    Flags:

    * NONE
    * UP
    * LOWER_UP
    * CARRIER
    """
    NONE = 0x0
    UP = 0x1
    LOWER_UP = 0x2
    CARRIER = 0x10000


class ConnectionFlags(IntFlag):
    """Connection flags

    Flags

    * NONE
    * UNSAVED
    * GENERATED
    * VOLATILE
    * EXTERNAL
    """
    NONE = 0x0
    UNSAVED = 0x1
    GENERATED = 0x2
    VOLATILE = 0x4
    EXTERNAL = 0x8


class VpnState(IntEnum):
    """VPN State

    * UNKNOWN
    * INIT
    * SHUTDOWN
    * STARTING
    * STARTED
    * STOPPING
    * STOPPED
    """
    UNKNOWN = 0
    INIT = 1
    SHUTDOWN = 2
    STARTING = 3
    STARTED = 4
    STOPPING = 5
    STOPPED = 6


class VpnFailure(IntEnum):
    """VPN Failure

    * LOGIN_FAILURE
    * CONNECT_FAILED
    * BAD_IP_CONFIG
    """
    LOGIN_FAILURE = 0
    CONNECT_FAILED = 1
    BAD_IP_CONFIG = 3


class NetworkManagerConnectivityState(IntEnum):
    """NetworkManager connectivity state enum

    * UNKNOWN
    * NONE
    * PORTAL
    * LIMITED
    * FULL
    """
    UNKNOWN = 0
    NONE = 1
    PORTAL = 2
    LIMITED = 3
    FULL = 4


class NetworkManagerState(IntEnum):
    """NetworkManager state enum

    * UNKNOWN
    * ASLEEP
    * DISCONNECTED
    * DISCONNECTING
    * CONNECTING
    * CONNECTED_LOCAL
    * CONNECTED_SITE
    * GLOBAL
    """
    UNKNOWN = 0
    ASLEEP = 10
    DISCONNECTED = 20
    DISCONNECTING = 30
    CONNECTING = 40
    CONNECTED_LOCAL = 50
    CONNECTED_SITE = 60
    GLOBAL = 70
