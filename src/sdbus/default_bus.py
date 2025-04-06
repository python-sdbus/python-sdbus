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

import threading
from contextvars import ContextVar, Token
from logging import getLogger
from typing import TYPE_CHECKING

from .sd_bus_internals import (
    NameAllowReplacementFlag,
    NameQueueFlag,
    NameReplaceExistingFlag,
    sd_bus_open,
)

if TYPE_CHECKING:
    from typing import Optional

    from .sd_bus_internals import SdBus

logger = getLogger(__name__)


class DefaultBusTLStorage(threading.local):
    bus: Optional[SdBus] = None


bus_tls = DefaultBusTLStorage()
bus_contextvar: ContextVar[SdBus] = ContextVar("DEFAULT_BUS")


def _get_defaul_bus_tls() -> Optional[SdBus]:
    return bus_tls.bus


def _set_default_bus_tls(new_bus: Optional[SdBus]) -> None:
    bus_tls.bus = new_bus


def get_default_bus() -> SdBus:
    """Get default bus.

    Returns context-local default bus if set or
    thread-local otherwise.

    If no default bus is set initializes a new bus using
    :py:func:`sdbus.sd_bus_open` and sets it as a thread-local
    default bus.
    """
    if (context_bus := bus_contextvar.get(None)) is not None:
        return context_bus

    if (tls_bus := _get_defaul_bus_tls()) is not None:
        return tls_bus
    else:
        new_bus = sd_bus_open()
        logger.info(
            "Created new default bus for thread %r",
            threading.current_thread(),
        )
        _set_default_bus_tls(new_bus)
        return new_bus


def set_default_bus(new_default: SdBus) -> None:
    """Set thread-local default bus.

    Should be called before creating any objects that will use
    default bus.

    Default bus can be replaced but the change will only affect
    newly created objects.
    """
    _set_default_bus_tls(new_default)


def set_context_default_bus(new_default: SdBus) -> Token[SdBus]:
    """Set context-local default bus.

    Should be called before creating any objects that will use
    default bus.

    Default bus can be replaced but the change will only affect
    newly created objects.

    Context-local default bus has higher priority over thread-local one
    but has to be explicitly set.

    :returns:
        Token that can be used to reset context bus back.
        See ``contextvars`` documentation for details.
    """
    return bus_contextvar.set(new_default)


def _prepare_request_name_flags(
        allow_replacement: bool,
        replace_existing: bool,
        queue: bool,
) -> int:
    return (
        (NameAllowReplacementFlag if allow_replacement else 0)
        +
        (NameReplaceExistingFlag if replace_existing else 0)
        +
        (NameQueueFlag if queue else 0)
    )


async def request_default_bus_name_async(
    new_name: str,
    allow_replacement: bool = False,
    replace_existing: bool = False,
    queue: bool = False,
) -> None:
    r"""Asynchronously acquire a name on the default bus.

    :param new_name:
        Name to acquire.
        Must be a valid D-Bus service name.
    :param allow_replacement:
        If name was acquired allow other D-Bus peers to take away the name.
    :param replace_existing:
        If current name owner allows, take away the name.
    :param queue:
        Queue up for name acquisition. :py:exc:`.SdBusRequestNameInQueueError`
        will be raised when successfully placed in queue. :py:meth:`Ownership
        change signal <sdbus_async.dbus_daemon.FreedesktopDbus.\
        name_owner_changed>` should be monitored get notified when the name
        was acquired.
    :raises: :ref:`name-request-exceptions` and other D-Bus exceptions.
    """
    default_bus = get_default_bus()
    await default_bus.request_name_async(
        new_name,
        _prepare_request_name_flags(
            allow_replacement,
            replace_existing,
            queue,
        )
    )


def request_default_bus_name(
    new_name: str,
    allow_replacement: bool = False,
    replace_existing: bool = False,
    queue: bool = False,
) -> None:
    r"""Acquire a name on the default bus.

    Blocks until a reply is received from D-Bus daemon.

    :param new_name:
        Name to acquire.
        Must be a valid D-Bus service name.
    :param allow_replacement:
        If name was acquired allow other D-Bus peers to take away the name.
    :param replace_existing:
        If current name owner allows, take away the name.
    :param queue:
        Queue up for name acquisition. :py:exc:`.SdBusRequestNameInQueueError`
        will be raised when successfully placed in queue. :py:meth:`Ownership
        change signal <sdbus_async.dbus_daemon.FreedesktopDbus.\
        name_owner_changed>` should be monitored get notified when the name
        was acquired.
    :raises: :ref:`name-request-exceptions` and other D-Bus exceptions.
    """
    default_bus = get_default_bus()
    default_bus.request_name(
        new_name,
        _prepare_request_name_flags(
            allow_replacement,
            replace_existing,
            queue,
        )
    )


__all__ = (
    "get_default_bus",
    "set_default_bus",
    "set_context_default_bus",
    "request_default_bus_name_async",
    "request_default_bus_name",
)
