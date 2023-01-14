# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2023 igo95862

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
from .sd_bus_internals import (
    SdBusBaseError,
    SdBusLibraryError,
    SdBusRequestNameAlreadyOwnerError,
    SdBusRequestNameError,
    SdBusRequestNameExistsError,
    SdBusRequestNameInQueueError,
    SdBusUnmappedMessageError,
    map_exception_to_dbus_error,
)

__all__ = (
    'DbusAccessDeniedError',
    'DbusAddressInUseError',
    'DbusAuthFailedError',
    'DbusBadAddressError',
    'DbusDisconnectedError',
    'DbusFailedError',
    'DbusFileExistsError',
    'DbusFileNotFoundError',
    'DbusInconsistentMessageError',
    'DbusInteractiveAuthorizationRequiredError',
    'DbusInvalidArgsError',
    'DbusInvalidFileContentError',
    'DbusInvalidSignatureError',
    'DbusIOError',
    'DbusLimitsExceededError',
    'DbusMatchRuleInvalidError',
    'DbusMatchRuleNotFound',
    'DbusNameHasNoOwnerError',
    'DbusNoMemoryError',
    'DbusNoNetworkError',
    'DbusNoReplyError',
    'DbusNoServerError',
    'DbusNotSupportedError',
    'DbusPropertyReadOnlyError',
    'DbusServiceUnknownError',
    'DbusTimeoutError',
    'DbusUnixProcessIdUnknownError',
    'DbusUnknownInterfaceError',
    'DbusUnknownMethodError',
    'DbusUnknownObjectError',
    'DbusUnknownPropertyError',
    'map_exception_to_dbus_error',

    'SdBusBaseError',
    'SdBusLibraryError',
    'SdBusRequestNameAlreadyOwnerError',
    'SdBusRequestNameError',
    'SdBusRequestNameExistsError',
    'SdBusRequestNameInQueueError',
    'SdBusUnmappedMessageError',
)
