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

from typing import TYPE_CHECKING

from .sd_bus_internals import (
    SdBusBaseError,
    add_exception_mapping,
    map_exception_to_dbus_error,
)

if TYPE_CHECKING:
    from typing import Any, Dict, Tuple


class DbusErrorMeta(type):

    def __new__(
        cls,
        name: str,
        bases: Tuple[type, ...],
        namespace: Dict[str, Any],
    ) -> DbusErrorMeta:

        dbus_error_name = namespace.get('dbus_error_name')

        if dbus_error_name is None:
            raise TypeError('D-Bus error name not passed')

        new_cls = super().__new__(cls, name, bases, namespace)
        assert issubclass(new_cls, Exception), (
            f"New class {new_cls} is not an Exception but {bases}."
        )

        add_exception_mapping(new_cls)

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


map_exception_to_dbus_error(AssertionError,
                            "org.python.Error.AssertionError")
map_exception_to_dbus_error(AttributeError,
                            "org.python.Error.AttributeError")
map_exception_to_dbus_error(BufferError,
                            "org.python.Error.BufferError")
map_exception_to_dbus_error(EOFError,
                            "org.python.Error.EOFError")
map_exception_to_dbus_error(ImportError,
                            "org.python.Error.ImportError")
map_exception_to_dbus_error(ModuleNotFoundError,
                            "org.python.Error.ModuleNotFoundError")
map_exception_to_dbus_error(LookupError,
                            "org.python.Error.LookupError")
map_exception_to_dbus_error(IndexError,
                            "org.python.Error.IndexError")
map_exception_to_dbus_error(KeyError,
                            "org.python.Error.KeyError")
map_exception_to_dbus_error(NameError,
                            "org.python.Error.NameError")
map_exception_to_dbus_error(NotImplementedError,
                            "org.python.Error.NotImplementedError")
map_exception_to_dbus_error(OSError,
                            "org.python.Error.OSError")
map_exception_to_dbus_error(RecursionError,
                            "org.python.Error.RecursionError")
map_exception_to_dbus_error(ReferenceError,
                            "org.python.Error.ReferenceError")
map_exception_to_dbus_error(RuntimeError,
                            "org.python.Error.RuntimeError")
map_exception_to_dbus_error(SyntaxError,
                            "org.python.Error.SyntaxError")
map_exception_to_dbus_error(IndentationError,
                            "org.python.Error.IndentationError")
map_exception_to_dbus_error(TabError,
                            "org.python.Error.TabError")
map_exception_to_dbus_error(SystemError,
                            "org.python.Error.SystemError")
map_exception_to_dbus_error(TypeError,
                            "org.python.Error.TypeError")
map_exception_to_dbus_error(UnboundLocalError,
                            "org.python.Error.UnboundLocalError")
map_exception_to_dbus_error(UnicodeError,
                            "org.python.Error.UnicodeError")
map_exception_to_dbus_error(UnicodeEncodeError,
                            "org.python.Error.UnicodeEncodeError")
map_exception_to_dbus_error(UnicodeDecodeError,
                            "org.python.Error.UnicodeDecodeError")
map_exception_to_dbus_error(UnicodeTranslateError,
                            "org.python.Error.UnicodeTranslateError")
map_exception_to_dbus_error(ValueError,
                            "org.python.Error.ValueError")
map_exception_to_dbus_error(EnvironmentError,
                            "org.python.Error.EnvironmentError")
map_exception_to_dbus_error(IOError,
                            "org.python.Error.IOError")
map_exception_to_dbus_error(BlockingIOError,
                            "org.python.Error.BlockingIOError")
map_exception_to_dbus_error(ChildProcessError,
                            "org.python.Error.ChildProcessError")
map_exception_to_dbus_error(ConnectionError,
                            "org.python.Error.ConnectionError")
map_exception_to_dbus_error(BrokenPipeError,
                            "org.python.Error.BrokenPipeError")
map_exception_to_dbus_error(ConnectionAbortedError,
                            "org.python.Error.ConnectionAbortedError")
map_exception_to_dbus_error(ConnectionRefusedError,
                            "org.python.Error.ConnectionRefusedError")
map_exception_to_dbus_error(ConnectionResetError,
                            "org.python.Error.ConnectionResetError")
map_exception_to_dbus_error(FileExistsError,
                            "org.python.Error.FileExistsError")
map_exception_to_dbus_error(FileNotFoundError,
                            "org.python.Error.FileNotFoundError")
map_exception_to_dbus_error(InterruptedError,
                            "org.python.Error.InterruptedError")
map_exception_to_dbus_error(IsADirectoryError,
                            "org.python.Error.IsADirectoryError")
map_exception_to_dbus_error(NotADirectoryError,
                            "org.python.Error.NotADirectoryError")
map_exception_to_dbus_error(PermissionError,
                            "org.python.Error.PermissionError")
map_exception_to_dbus_error(ProcessLookupError,
                            "org.python.Error.ProcessLookupError")
map_exception_to_dbus_error(TimeoutError,
                            "org.python.Error.TimeoutError")
map_exception_to_dbus_error(ArithmeticError,
                            "org.python.Error.ArithmeticError")
map_exception_to_dbus_error(FloatingPointError,
                            "org.python.Error.FloatingPointError")
map_exception_to_dbus_error(OverflowError,
                            "org.python.Error.OverflowError")
map_exception_to_dbus_error(ZeroDivisionError,
                            "org.python.Error.ZeroDivisionError")
