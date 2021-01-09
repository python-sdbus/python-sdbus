# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2020  igo95862

# This file is part of py_sd_bus

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

from asyncio import Future, Queue
from typing import (Any, Callable, Coroutine, Dict, List, Optional, Sequence,
                    Tuple, Union)

DbusBasicTypes = Union[str, int, bytes, float, Any]
DbusStructType = Tuple[DbusBasicTypes, ...]
DbusDictType = Dict[DbusBasicTypes, DbusBasicTypes]
DbusVariantType = Tuple[str, DbusStructType]
DbusListType = List[DbusBasicTypes]
DbusCompleteTypes = Union[DbusBasicTypes, DbusStructType,
                          DbusDictType, DbusVariantType, DbusListType]


class SdBusSlot:
    """Holds reference to SdBus slot"""
    ...


class SdBusInterface:

    def add_method(
        self,
        member_name: str,
        signature: str, input_args_names: Sequence[str],
        result_signature: str, result_args_names: Sequence[str],
        flags: int,
        callback: Callable[[SdBusMessage], Coroutine[Any, Any, None]], /
    ) -> None:
        ...

    def add_property(
        self,
        property_name: str,
        property_signature: str,
        get_function: Callable[[], Any],
        set_function: Optional[Callable[[Any], None]],
        flags: int, /
    ) -> None:
        ...

    def add_signal(
        self,
        signal_name: str,
        signal_signature: str,
        signal_args_names: Sequence[str],
        flags: int, /
    ) -> None:
        ...


class SdBusMessage:
    def append_data(self, signature: str, *args: DbusCompleteTypes) -> None:
        ...

    def open_container(self, container_type: str,
                       container_signature: str, /) -> None:
        ...

    def close_container(self) -> None:
        ...

    def enter_container(self, container_type: str,
                        container_signature: str, /) -> None:
        ...

    def exit_container(self) -> None:
        ...

    def dump(self) -> None:
        ...

    def seal(self) -> None:
        ...

    def get_contents(self
                     ) -> Tuple[DbusCompleteTypes, ...]:
        ...

    def get_member(self) -> str:
        ...

    def create_reply(self) -> SdBusMessage:
        ...

    def send(self) -> None:
        ...


class SdBus:
    def call(self, message: SdBusMessage, /) -> SdBusMessage:
        ...

    def call_async(
            self, message: SdBusMessage,
            /) -> Future[SdBusMessage]:
        ...

    def drive(self) -> None:
        ...

    def get_fd(self) -> int:
        ...

    def new_method_call_message(
            self,
            destination_name: str, object_path: str,
            interface_name: str, member_name: str,
            /) -> SdBusMessage:
        ...

    def new_property_get_message(
            self,
            destination_service_name: str, object_path: str,
            interface_name: str, member_name: str,
            /) -> SdBusMessage:
        ...

    def new_property_set_message(
            self,
            destination_service_name: str, object_path: str,
            interface_name: str, member_name: str,
            /) -> SdBusMessage:
        ...

    def new_signal_message(
            self,
            object_path: str,
            interface_name: str,
            member_name: str,
            /) -> SdBusMessage:
        ...

    def add_interface(self, new_interface: SdBusInterface,
                      object_path: str, interface_name: str, /) -> None:
        ...

    def get_signal_queue_async(
        self,
        destination_name: str, object_path: str,
        interface_name: str, member_name: str,
        /
    ) -> Future[Queue[SdBusMessage]]:
        ...

    def request_name_async(self, name: str, flags: int, /) -> Future[None]:
        ...


def sd_bus_open() -> SdBus:
    ...


def sd_bus_open_user() -> SdBus:
    ...


def sd_bus_open_system() -> SdBus:
    ...


def encode_object_path(prefix: str, external: str) -> str:
    ...


def decode_object_path(prefix: str, full_path: str) -> str:
    ...


class DbusBaseError(Exception):
    ...


class DbusFailedError(DbusBaseError):
    ...


class DbusNoMemoryError(DbusBaseError):
    ...


class DbusServiceUnknownError(DbusBaseError):
    ...


class DbusNameHasNoOwnerError(DbusBaseError):
    ...


class DbusNoReplyError(DbusBaseError):
    ...


class DbusIOError(DbusBaseError):
    ...


class DbusBadAddressError(DbusBaseError):
    ...


class DbusNotSupportedError(DbusBaseError):
    ...


class DbusLimitsExceededError(DbusBaseError):
    ...


class DbusAccessDeniedError(DbusBaseError):
    ...


class DbusAuthFailedError(DbusBaseError):
    ...


class DbusNoServerError(DbusBaseError):
    ...


class DbusTimeoutError(DbusBaseError):
    ...


class DbusNoNetworkError(DbusBaseError):
    ...


class DbusAddressInUseError(DbusBaseError):
    ...


class DbusDisconnectedError(DbusBaseError):
    ...


class DbusInvalidArgsError(DbusBaseError):
    ...


class DbusFileExistsError(DbusBaseError):
    ...


class DbusUnknownMethodError(DbusBaseError):
    ...


class DbusUnknownObjectError(DbusBaseError):
    ...


class DbusUnknownInterfaceError(DbusBaseError):
    ...


class DbusUnknownPropertyError(DbusBaseError):
    ...


class DbusPropertyReadOnlyError(DbusBaseError):
    ...


class DbusUnixProcessIdUnknownError(DbusBaseError):
    ...


class DbusInvalidSignatureError(DbusBaseError):
    ...


class DbusInconsistentMessageError(DbusBaseError):
    ...


class DbusMatchRuleNotFound(DbusBaseError):
    ...


class DbusMatchRuleInvalidError(DbusBaseError):
    ...


class DbusInteractiveAuthorizationRequiredError(DbusBaseError):
    ...
