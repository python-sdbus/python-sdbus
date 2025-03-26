# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2020-2023 igo95862

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
from typing import TYPE_CHECKING, cast, overload
from weakref import ref as weak_ref

from .dbus_common_elements import (
    DbusBoundAsync,
    DbusMemberAsync,
    DbusMethodCommon,
    DbusMethodOverride,
    DbusRemoteObjectMeta,
)
from .dbus_exceptions import DbusFailedError
from .sd_bus_internals import EXCEPTION_TO_DBUS_ERROR, DbusNoReplyFlag

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from typing import Any, Optional, TypeVar, Union

    from .dbus_proxy_async_interface_base import DbusInterfaceBaseAsync
    from .sd_bus_internals import SdBusMessage

    T = TypeVar('T')
else:
    T = None

CURRENT_MESSAGE: ContextVar[SdBusMessage] = ContextVar('CURRENT_MESSAGE')


def get_current_message() -> SdBusMessage:
    return CURRENT_MESSAGE.get()


class DbusMethodAsync(DbusMethodCommon, DbusMemberAsync):

    @overload
    def __get__(
        self,
        obj: None,
        obj_class: type[DbusInterfaceBaseAsync],
    ) -> DbusMethodAsync:
        ...

    @overload
    def __get__(
        self,
        obj: DbusInterfaceBaseAsync,
        obj_class: type[DbusInterfaceBaseAsync],
    ) -> Callable[..., Any]:
        ...

    def __get__(
        self,
        obj: Optional[DbusInterfaceBaseAsync],
        obj_class: Optional[type[DbusInterfaceBaseAsync]] = None,
    ) -> Union[Callable[..., Any], DbusMethodAsync]:
        if obj is not None:
            dbus_meta = obj._dbus
            if isinstance(dbus_meta, DbusRemoteObjectMeta):
                return DbusProxyMethodAsync(self, dbus_meta)
            else:
                return DbusLocalMethodAsync(self, obj)
        else:
            return self


class DbusBoundMethodAsyncBase(DbusBoundAsync):

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class DbusProxyMethodAsync(DbusBoundMethodAsyncBase):
    def __init__(
        self,
        dbus_method: DbusMethodAsync,
        proxy_meta: DbusRemoteObjectMeta,
    ):
        self.dbus_method = dbus_method
        self.proxy_meta = proxy_meta

        self.__doc__ = dbus_method.__doc__

    async def _dbus_async_call(self, call_message: SdBusMessage) -> Any:
        bus = self.proxy_meta.attached_bus
        reply_message = await bus.call_async(call_message)
        return reply_message.get_contents()

    @staticmethod
    async def _no_reply() -> None:
        return None

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        bus = self.proxy_meta.attached_bus
        dbus_method = self.dbus_method

        new_call_message = bus.new_method_call_message(
            self.proxy_meta.service_name,
            self.proxy_meta.object_path,
            dbus_method.interface_name,
            dbus_method.method_name,
        )

        if len(args) == dbus_method.num_of_args:
            assert not kwargs, (
                "Passed more arguments than method supports"
                f"Extra args: {kwargs}")
            rebuilt_args: Sequence[Any] = args
        else:
            rebuilt_args = dbus_method._rebuild_args(
                dbus_method.original_method,
                *args,
                **kwargs)

        if rebuilt_args:
            new_call_message.append_data(
                dbus_method.input_signature, *rebuilt_args)

        if dbus_method.flags & DbusNoReplyFlag:
            new_call_message.expect_reply = False
            new_call_message.send()
            return self._no_reply()

        return self._dbus_async_call(new_call_message)


class DbusLocalMethodAsync(DbusBoundMethodAsyncBase):
    def __init__(
        self,
        dbus_method: DbusMethodAsync,
        local_object: DbusInterfaceBaseAsync,
    ):
        self.dbus_method = dbus_method
        self.local_object_ref = weak_ref(local_object)

        self.__doc__ = dbus_method.__doc__

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        local_object = self.local_object_ref()
        if local_object is None:
            raise RuntimeError("Local object no longer exists!")

        return self.dbus_method.original_method(local_object, *args, **kwargs)

    async def _dbus_reply_call_method(
        self,
        request_message: SdBusMessage,
        local_object: DbusInterfaceBaseAsync,
    ) -> Any:

        local_method = self.dbus_method.original_method.__get__(
            local_object, None)

        CURRENT_MESSAGE.set(request_message)

        return await local_method(*request_message.parse_to_tuple())

    async def _dbus_reply_call(
        self,
        request_message: SdBusMessage
    ) -> None:
        local_object = self.local_object_ref()
        if local_object is None:
            raise RuntimeError("Local object no longer exists!")

        call_context = copy_context()

        try:
            reply_data = await call_context.run(
                self._dbus_reply_call_method,
                request_message,
                local_object,
            )
        except Exception as e:
            if not request_message.expect_reply:
                return

            dbus_error = EXCEPTION_TO_DBUS_ERROR.get(type(e))
            if dbus_error is None:
                dbus_error = DbusFailedError.dbus_error_name

            error_message = request_message.create_error_reply(
                dbus_error,
                str(e.args[0]) if e.args else "",
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
    result_args_names: Optional[Sequence[str]] = None,
    input_args_names: Optional[Sequence[str]] = None,
    method_name: Optional[str] = None,
) -> Callable[[T], T]:

    assert not isinstance(input_signature, FunctionType), (
        "Passed function to decorator directly. "
        "Did you forget () round brackets?"
    )

    def dbus_method_decorator(original_method: T) -> T:
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

        return cast(T, new_wrapper)

    return dbus_method_decorator


def dbus_method_async_override() -> Callable[[T], T]:

    def new_decorator(
            new_function: T) -> T:
        return cast(T, DbusMethodOverride(new_function))

    return new_decorator
