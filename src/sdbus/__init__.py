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

from .dbus_common import (
    get_default_bus,
    request_default_bus_name,
    request_default_bus_name_async,
    set_default_bus,
)
from .dbus_exceptions import (
    DbusAccessDeniedError,
    DbusAddressInUseError,
    DbusAuthFailedError,
    DbusBadAddressError,
    DbusDisconnectedError,
    DbusFailedError,
    DbusFileExistsError,
    DbusFileNotFoundError,
    DbusInconsistentMessageError,
    DbusInteractiveAuthorizationRequiredError,
    DbusInvalidArgsError,
    DbusInvalidFileContentError,
    DbusInvalidSignatureError,
    DbusIOError,
    DbusLimitsExceededError,
    DbusMatchRuleInvalidError,
    DbusMatchRuleNotFound,
    DbusNameHasNoOwnerError,
    DbusNoMemoryError,
    DbusNoNetworkError,
    DbusNoReplyError,
    DbusNoServerError,
    DbusNotSupportedError,
    DbusPropertyReadOnlyError,
    DbusServiceUnknownError,
    DbusTimeoutError,
    DbusUnixProcessIdUnknownError,
    DbusUnknownInterfaceError,
    DbusUnknownMethodError,
    DbusUnknownObjectError,
    DbusUnknownPropertyError,
)
from .dbus_proxy_async import (
    DbusInterfaceCommonAsync,
    DbusObjectManagerInterfaceAsync,
    dbus_method_async,
    dbus_method_async_override,
    dbus_property_async,
    dbus_property_async_override,
    dbus_signal_async,
)
from .dbus_proxy_sync import (
    DbusInterfaceCommon,
    DbusObjectManagerInterface,
    dbus_method,
    dbus_property,
)
from .sd_bus_internals import (
    DbusDeprecatedFlag,
    DbusHiddenFlag,
    DbusNoReplyFlag,
    DbusPropertyConstFlag,
    DbusPropertyEmitsChangeFlag,
    DbusPropertyEmitsInvalidationFlag,
    DbusPropertyExplicitFlag,
    DbusSensitiveFlag,
    DbusUnprivilegedFlag,
    SdBusBaseError,
    SdBusLibraryError,
    SdBusUnmappedMessageError,
    decode_object_path,
    encode_object_path,
    sd_bus_open,
    sd_bus_open_system,
    sd_bus_open_user,
)

__all__ = [
    'get_default_bus', 'request_default_bus_name',
    'request_default_bus_name_async', 'set_default_bus',

    'DbusAccessDeniedError', 'DbusAddressInUseError',
    'DbusAuthFailedError', 'DbusBadAddressError',
    'DbusDisconnectedError', 'DbusFailedError',
    'DbusFileExistsError', 'DbusFileNotFoundError',
    'DbusInconsistentMessageError',
    'DbusInteractiveAuthorizationRequiredError',
    'DbusInvalidArgsError',
    'DbusInvalidFileContentError',
    'DbusInvalidSignatureError', 'DbusIOError',
    'DbusLimitsExceededError',
    'DbusMatchRuleInvalidError', 'DbusMatchRuleNotFound',
    'DbusNameHasNoOwnerError', 'DbusNoMemoryError',
    'DbusNoNetworkError', 'DbusNoReplyError',
    'DbusNoServerError', 'DbusNotSupportedError',
    'DbusPropertyReadOnlyError',
    'DbusServiceUnknownError', 'DbusTimeoutError',
    'DbusUnixProcessIdUnknownError',
    'DbusUnknownInterfaceError',
    'DbusUnknownMethodError', 'DbusUnknownObjectError',
    'DbusUnknownPropertyError',

    'DbusObjectManagerInterfaceAsync',
    'DbusInterfaceCommonAsync', 'dbus_method_async',
    'dbus_method_async_override', 'dbus_property_async',
    'dbus_property_async_override', 'dbus_signal_async',

    'DbusInterfaceCommon',
    'DbusObjectManagerInterface',
    'dbus_method',
    'dbus_property',

    'DbusDeprecatedFlag', 'DbusHiddenFlag',
    'DbusNoReplyFlag', 'DbusPropertyConstFlag',
    'DbusPropertyEmitsChangeFlag',
    'DbusPropertyEmitsInvalidationFlag',
    'DbusPropertyExplicitFlag', 'DbusSensitiveFlag',
    'DbusUnprivilegedFlag', 'SdBusBaseError',
    'SdBusLibraryError', 'SdBusUnmappedMessageError',
    'decode_object_path', 'encode_object_path',
    'sd_bus_open', 'sd_bus_open_system',
    'sd_bus_open_user'
]
