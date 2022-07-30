# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2020-2022 igo95862

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

from contextvars import ContextVar, copy_context
from inspect import iscoroutinefunction
from types import FunctionType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
    Sequence,
    Type,
    TypeVar,
    cast,
)
from weakref import ref as weak_ref

from .dbus_common_elements import (
    DbusBindedAsync,
    DbusMethodCommon,
    DbusOverload,
    DbusSomethingAsync,
)
from .dbus_exceptions import DbusFailedError
from .sd_bus_internals import DbusNoReplyFlag, SdBusMessage

CURRENT_MESSAGE: ContextVar[SdBusMessage] = ContextVar('CURRENT_MESSAGE')


def get_current_message() -> SdBusMessage:
    return CURRENT_MESSAGE.get()


T_input = TypeVar('T_input')
T = TypeVar('T')


if TYPE_CHECKING:
    from .dbus_proxy_async_interface_base import DbusInterfaceBaseAsync


class DbusMethodAsync(DbusMethodCommon, DbusSomethingAsync):
    def __get__(self,
                obj: DbusInterfaceBaseAsync,
                obj_class: Optional[Type[DbusInterfaceBaseAsync]] = None,
                ) -> Callable[..., Any]:
        return DbusMethodAsyncBinded(self, obj)


class DbusMethodAsyncBinded(DbusBindedAsync):
    def __init__(self,
                 dbus_method: DbusMethodAsync,
                 interface: DbusInterfaceBaseAsync):
        self.dbus_method = dbus_method
        self.interface_ref = (
            weak_ref(interface)
            if interface is not None
            else None
        )

        self.__doc__ = dbus_method.__doc__

    async def _call_dbus_async(self, *args: Any) -> Any:
        assert self.interface_ref is not None
        interface = self.interface_ref()
        assert interface is not None

        assert interface._attached_bus is not None
        assert interface._remote_service_name is not None
        assert interface._remote_object_path is not None
        assert self.dbus_method.interface_name is not None
        new_call_message = interface._attached_bus. \
            new_method_call_message(
                interface._remote_service_name,
                interface._remote_object_path,
                self.dbus_method.interface_name,
                self.dbus_method.method_name,
            )

        if args:
            new_call_message.append_data(
                self.dbus_method.input_signature, *args)

        if self.dbus_method.flags & DbusNoReplyFlag:
            new_call_message.expect_reply = False
            new_call_message.send()
            return

        reply_message = await interface._attached_bus.call_async(
            new_call_message)
        return reply_message.get_contents()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        assert self.interface_ref is not None
        interface = self.interface_ref()
        assert interface is not None

        if interface._is_binded:

            if len(args) == self.dbus_method.num_of_args:
                assert not kwargs, (
                    "Passed more arguments than method supports"
                    f"Extra args: {kwargs}")
                rebuilt_args: Sequence[Any] = args
            else:
                rebuilt_args = self.dbus_method._rebuild_args(
                    self.dbus_method.original_method,
                    *args,
                    **kwargs)

            return self._call_dbus_async(*rebuilt_args)
        else:
            return self.dbus_method.original_method(
                interface, *args, **kwargs)

    async def _call_method_from_dbus(
            self,
            request_message: SdBusMessage,
            interface: DbusInterfaceBaseAsync) -> Any:
        request_data = request_message.get_contents()

        local_method = self.dbus_method.original_method.__get__(
            interface, None)

        CURRENT_MESSAGE.set(request_message)

        if isinstance(request_data, tuple):
            return await local_method(*request_data)
        elif request_data is None:
            return await local_method()
        else:
            return await local_method(request_data)

    async def _call_from_dbus(
            self,
            request_message: SdBusMessage) -> None:
        assert self.interface_ref is not None
        interface = self.interface_ref()
        assert interface is not None

        call_context = copy_context()

        try:
            reply_data = await call_context.run(
                self._call_method_from_dbus,
                request_message,
                interface,
            )
        except DbusFailedError as e:
            if not request_message.expect_reply:
                return

            error_message = request_message.create_error_reply(
                e.dbus_error_name,
                str(e.args[0]) if e.args else "",
            )
            error_message.send()
            return
        except Exception:
            error_message = request_message.create_error_reply(
                DbusFailedError.dbus_error_name,
                "",
            )
            error_message.send()
            return

        if not request_message.expect_reply:
            return

        reply_message = request_message.create_reply()

        if isinstance(reply_data, tuple):
            try:
                reply_message.append_data(
                    self.dbus_method.result_signature, *reply_data)
            except TypeError:
                # In case of single struct result type
                # We can't figure out if return is multiple values
                # or a tuple
                reply_message.append_data(
                    self.dbus_method.result_signature, reply_data)
        elif reply_data is not None:
            reply_message.append_data(
                self.dbus_method.result_signature, reply_data)

        reply_message.send()


def dbus_method_async(
    input_signature: str = "",
    result_signature: str = "",
    flags: int = 0,
    result_args_names: Sequence[str] = (),
    input_args_names: Sequence[str] = (),
    method_name: Optional[str] = None,
) -> Callable[[T_input], T_input]:

    assert not isinstance(input_signature, FunctionType), (
        "Passed function to decorator directly. "
        "Did you forget () round brackets?"
    )

    def dbus_method_decorator(original_method: T_input) -> T_input:
        assert isinstance(original_method, FunctionType)
        assert iscoroutinefunction(original_method), (
            "Expected coroutine function. ",
            "Maybe you forgot 'async' keyword?",
        )
        new_wrapper = DbusMethodAsync(
            original_method=original_method,
            method_name=method_name,
            input_signature=input_signature,
            result_signature=result_signature,
            result_args_names=result_args_names,
            input_args_names=input_args_names,
            flags=flags,
        )

        return cast(T_input, new_wrapper)

    return dbus_method_decorator


def dbus_method_async_override() -> Callable[[T], T]:

    def new_decorator(
            new_function: T) -> T:
        return cast(T, DbusOverload(new_function))

    return new_decorator
