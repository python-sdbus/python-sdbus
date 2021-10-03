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

from asyncio import Future, Queue
from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

DbusBasicTypes = Union[str, int, bytes, float, Any]
DbusStructType = Tuple[DbusBasicTypes, ...]
DbusDictType = Dict[DbusBasicTypes, DbusBasicTypes]
DbusVariantType = Tuple[str, DbusStructType]
DbusListType = List[DbusBasicTypes]
DbusCompleteTypes = Union[DbusBasicTypes, DbusStructType,
                          DbusDictType, DbusVariantType, DbusListType]

__STUB_ERROR = (
    'Typing stub. You should never see this '
    'error unless the actual module failed to load. '
    'Check your installation.'
)


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
        raise NotImplementedError(__STUB_ERROR)

    def add_property(
        self,
        property_name: str,
        property_signature: str,
        get_function: Callable[[SdBusMessage], Any],
        set_function: Optional[Callable[[SdBusMessage], None]],
        flags: int, /
    ) -> None:
        raise NotImplementedError(__STUB_ERROR)

    def add_signal(
        self,
        signal_name: str,
        signal_signature: str,
        signal_args_names: Sequence[str],
        flags: int, /
    ) -> None:
        raise NotImplementedError(__STUB_ERROR)


class SdBusMessage:
    def append_data(self, signature: str, *args: DbusCompleteTypes) -> None:
        raise NotImplementedError(__STUB_ERROR)

    def open_container(self, container_type: str,
                       container_signature: str, /) -> None:
        raise NotImplementedError(__STUB_ERROR)

    def close_container(self) -> None:
        raise NotImplementedError(__STUB_ERROR)

    def enter_container(self, container_type: str,
                        container_signature: str, /) -> None:
        raise NotImplementedError(__STUB_ERROR)

    def exit_container(self) -> None:
        raise NotImplementedError(__STUB_ERROR)

    def dump(self) -> None:
        raise NotImplementedError(__STUB_ERROR)

    def seal(self) -> None:
        raise NotImplementedError(__STUB_ERROR)

    def get_contents(self
                     ) -> Tuple[DbusCompleteTypes, ...]:
        raise NotImplementedError(__STUB_ERROR)

    def get_member(self) -> str:
        raise NotImplementedError(__STUB_ERROR)

    def create_reply(self) -> SdBusMessage:
        raise NotImplementedError(__STUB_ERROR)

    def create_error_reply(
            self,
            error_name: str,
            error_message: str, /) -> SdBusMessage:
        raise NotImplementedError(__STUB_ERROR)

    def send(self) -> None:
        raise NotImplementedError(__STUB_ERROR)

    expect_reply: bool = False


class SdBus:
    def call(self, message: SdBusMessage, /) -> SdBusMessage:
        raise NotImplementedError(__STUB_ERROR)

    def call_async(
            self, message: SdBusMessage,
            /) -> Future[SdBusMessage]:
        raise NotImplementedError(__STUB_ERROR)

    def drive(self) -> None:
        raise NotImplementedError(__STUB_ERROR)

    def get_fd(self) -> int:
        raise NotImplementedError(__STUB_ERROR)

    def new_method_call_message(
            self,
            destination_name: str, object_path: str,
            interface_name: str, member_name: str,
            /) -> SdBusMessage:
        raise NotImplementedError(__STUB_ERROR)

    def new_property_get_message(
            self,
            destination_service_name: str, object_path: str,
            interface_name: str, member_name: str,
            /) -> SdBusMessage:
        raise NotImplementedError(__STUB_ERROR)

    def new_property_set_message(
            self,
            destination_service_name: str, object_path: str,
            interface_name: str, member_name: str,
            /) -> SdBusMessage:
        raise NotImplementedError(__STUB_ERROR)

    def new_signal_message(
            self,
            object_path: str,
            interface_name: str,
            member_name: str,
            /) -> SdBusMessage:
        raise NotImplementedError(__STUB_ERROR)

    def add_interface(self, new_interface: SdBusInterface,
                      object_path: str, interface_name: str, /) -> None:
        raise NotImplementedError(__STUB_ERROR)

    def get_signal_queue_async(
        self,
        destination_name: str, object_path: str,
        interface_name: str, member_name: str,
        /
    ) -> Future[Queue[SdBusMessage]]:
        raise NotImplementedError(__STUB_ERROR)

    def request_name_async(self, name: str, flags: int, /) -> Future[None]:
        raise NotImplementedError(__STUB_ERROR)

    def request_name(self, name: str, flags: int, /) -> None:
        raise NotImplementedError(__STUB_ERROR)

    def add_object_manager(self, path: str, /) -> SdBusSlot:
        raise NotImplementedError(__STUB_ERROR)

    def emit_object_added(self, path: str, /) -> None:
        raise NotImplementedError(__STUB_ERROR)


def sd_bus_open() -> SdBus:
    raise NotImplementedError(__STUB_ERROR)


def sd_bus_open_user() -> SdBus:
    raise NotImplementedError(__STUB_ERROR)


def sd_bus_open_system() -> SdBus:
    raise NotImplementedError(__STUB_ERROR)


def sd_bus_open_system_remote(host: str, /) -> SdBus:
    raise NotImplementedError(__STUB_ERROR)


def sd_bus_open_user_machine(machine: str, /) -> SdBus:
    raise NotImplementedError(__STUB_ERROR)


def sd_bus_open_system_machine(machine: str, /) -> SdBus:
    raise NotImplementedError(__STUB_ERROR)


def encode_object_path(prefix: str, external: str) -> str:
    raise NotImplementedError(__STUB_ERROR)


def decode_object_path(prefix: str, full_path: str) -> str:
    raise NotImplementedError(__STUB_ERROR)


def add_exception_mapping(exc: Exception, /) -> None:
    ...  # We want to be able to generate docs without module


class SdBusBaseError(Exception):
    ...


class SdBusUnmappedMessageError(SdBusBaseError):
    ...


class SdBusLibraryError(SdBusBaseError):
    ...


DBUS_ERROR_TO_EXCEPTION: Dict[str, Exception] = {}

EXCEPTION_TO_DBUS_ERROR: Dict[Exception, str] = {}

DbusDeprecatedFlag: int = 0
DbusHiddenFlag: int = 0
DbusUnprivilegedFlag: int = 0
DbusNoReplyFlag: int = 0
DbusPropertyConstFlag: int = 0
DbusPropertyEmitsChangeFlag: int = 0
DbusPropertyEmitsInvalidationFlag: int = 0
DbusPropertyExplicitFlag: int = 0
DbusSensitiveFlag: int = 0
