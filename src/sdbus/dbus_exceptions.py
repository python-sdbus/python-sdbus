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

from typing import Any, Dict, Tuple, cast

from .sd_bus_internals import SdBusBaseError, add_exception_mapping


class DbusErrorMeta(type):

    def __new__(cls, name: str,
                bases: Tuple[type, ...],
                namespace: Dict[str, Any],
                ) -> DbusErrorMeta:

        dbus_error_name = namespace.get('dbus_error_name')

        if dbus_error_name is None:
            raise TypeError('Dbus error name not passed')

        new_cls = super().__new__(cls, name, bases, namespace)

        add_exception_mapping(cast(Exception, new_cls))

        return new_cls


class DbusFailedError(SdBusBaseError, metaclass=DbusErrorMeta):
    dbus_error_name: str = 'org.freedesktop.DBus.Error.Failed'


class DbusNoMemoryError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.NoMemory'


class DbusServiceUnknownError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.ServiceUnknown'


class DbusNameHasNoOwnerError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.NameHasNoOwner'


class DbusNoReplyError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.NoReply'


class DbusIOError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.IOError'


class DbusBadAddressError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.BadAddress'


class DbusNotSupportedError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.NotSupported'


class DbusLimitsExceededError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.LimitsExceeded'


class DbusAccessDeniedError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.AccessDenied'


class DbusAuthFailedError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.AuthFailed'


class DbusNoServerError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.NoServer'


class DbusTimeoutError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.Timeout'


class DbusNoNetworkError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.NoNetwork'


class DbusAddressInUseError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.AddressInUse'


class DbusDisconnectedError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.Disconnected'


class DbusInvalidArgsError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'


class DbusFileNotFoundError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.FileNotFound'


class DbusFileExistsError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.FileExists'


class DbusUnknownMethodError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.UnknownMethod'


class DbusUnknownObjectError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.UnknownObject'


class DbusUnknownInterfaceError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.UnknownInterface'


class DbusUnknownPropertyError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.UnknownProperty'


class DbusPropertyReadOnlyError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.PropertyReadOnly'


class DbusUnixProcessIdUnknownError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.UnixProcessIdUnknown'


class DbusInvalidSignatureError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.InvalidSignature'


class DbusInvalidFileContentError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.InvalidFileContent'


class DbusInconsistentMessageError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.InconsistentMessage'


class DbusMatchRuleNotFound(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.MatchRuleNotFound'


class DbusMatchRuleInvalidError(DbusFailedError):
    dbus_error_name = 'org.freedesktop.DBus.Error.MatchRuleInvalid'


class DbusInteractiveAuthorizationRequiredError(DbusFailedError):
    dbus_error_name = ('org.freedesktop.DBus.Error'
                       '.InteractiveAuthorizationRequired')
