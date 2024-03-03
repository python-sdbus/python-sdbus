# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2022 igo95862

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

from asyncio import Event, TimeoutError, wait_for
from os import environ, kill
from pathlib import Path
from signal import SIGTERM
from subprocess import DEVNULL
from subprocess import run as subprocess_run
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING
from unittest import IsolatedAsyncioTestCase
from weakref import ref as weak_ref

from .dbus_common_funcs import set_default_bus
from .dbus_proxy_async_signal import (
    DbusSignalAsyncLocalBind,
    DbusSignalAsyncProxyBind,
)
from .sd_bus_internals import SdBusMessage, sd_bus_open_user

if TYPE_CHECKING:
    from typing import (
        Any,
        AsyncContextManager,
        ClassVar,
        List,
        Optional,
        TypeVar,
        Union,
    )

    from .dbus_proxy_async_signal import (
        DbusSignalAsync,
        DbusSignalAsyncBaseBind,
    )
    from .sd_bus_internals import SdBus, SdBusSlot

    T = TypeVar('T')


dbus_config = '''
<busconfig>
  <type>session</type>
  <pidfile>{pidfile_path}</pidfile>
  <auth>EXTERNAL</auth>
  <listen>unix:path={socket_path}</listen>
  <policy context="default">
    <allow send_destination="*" eavesdrop="true"/>
    <allow eavesdrop="true"/>
    <allow own="*"/>
  </policy>
</busconfig>
'''


class DbusSignalRecorderBase:
    def __init__(
        self,
        timeout: Union[int, float],
    ):
        self._timeout = timeout
        self._captured_data: List[Any] = []
        self._ready_event = Event()
        self._callback_method = self._callback

    async def start(self) -> None:
        raise NotImplementedError

    async def stop(self) -> None:
        raise NotImplementedError

    async def __aenter__(self) -> DbusSignalRecorderBase:
        raise NotImplementedError

    async def __aexit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any,
    ) -> None:
        if exc_type is not None:
            return

        try:
            await wait_for(self._ready_event.wait(), timeout=self._timeout)
        except TimeoutError:
            raise AssertionError("D-Bus signal not captured.") from None

    def _callback(self, data: Any) -> None:
        if isinstance(data, SdBusMessage):
            data = data.get_contents()

        self._captured_data.append(data)
        self._ready_event.set()

    @property
    def output(self) -> List[Any]:
        return self._captured_data.copy()


class DbusSignalRecorderRemote(DbusSignalRecorderBase):
    def __init__(
        self,
        timeout: Union[int, float],
        bus: SdBus,
        remote_signal: DbusSignalAsyncProxyBind[Any],
    ):
        super().__init__(timeout)
        self._bus = bus
        self._match_slot: Optional[SdBusSlot] = None
        self._remote_signal = remote_signal

    async def __aenter__(self) -> DbusSignalRecorderBase:
        self._match_slot = await self._remote_signal._register_match_slot(
            self._bus,
            self._callback_method,
        )

        return self

    async def __aexit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any,
    ) -> None:
        try:
            await super().__aexit__(exc_type, exc_value, traceback)
        finally:
            if self._match_slot is not None:
                self._match_slot.close()


class DbusSignalRecorderLocal(DbusSignalRecorderBase):
    def __init__(
        self,
        timeout: Union[int, float],
        local_signal: DbusSignalAsyncLocalBind[Any],
    ):
        super().__init__(timeout)
        self._local_signal_ref: weak_ref[DbusSignalAsync[Any]] = (
            weak_ref(local_signal.dbus_signal)
        )

    async def __aenter__(self) -> DbusSignalRecorderBase:
        local_signal = self._local_signal_ref()

        if local_signal is None:
            raise RuntimeError

        local_signal.local_callbacks.add(self._callback_method)
        return self


class IsolatedDbusTestCase(IsolatedAsyncioTestCase):
    dbus_executable_name: ClassVar[str] = 'dbus-daemon'

    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.temp_dir_path = Path(self.temp_dir.name)

        self.dbus_socket_path = self.temp_dir_path / 'test_dbus.socket'
        self.pid_path = self.temp_dir_path / 'dbus.pid'

        self.dbus_config_file = self.temp_dir_path / 'dbus.config'

        with open(self.dbus_config_file, mode='x') as conf_file:
            conf_file.write(dbus_config.format(
                socket_path=self.dbus_socket_path,
                pidfile_path=self.pid_path))

        subprocess_run(
            args=(
                self.dbus_executable_name,
                '--config-file', self.dbus_config_file,
                '--fork',
            ),
            stdin=DEVNULL,
            check=True,
        )

        self.old_session_bus_address = environ.get('DBUS_SESSION_BUS_ADDRESS')
        environ[
            'DBUS_SESSION_BUS_ADDRESS'] = f"unix:path={self.dbus_socket_path}"

        self.bus = sd_bus_open_user()
        set_default_bus(self.bus)

    async def asyncSetUp(self) -> None:
        set_default_bus(self.bus)

    def tearDown(self) -> None:
        with open(self.pid_path) as pid_file:
            dbus_pid = int(pid_file.read())

        kill(dbus_pid, SIGTERM)
        self.temp_dir.cleanup()
        environ.pop('DBUS_SESSION_BUS_ADDRESS')
        if self.old_session_bus_address is not None:
            environ['DBUS_SESSION_BUS_ADDRESS'] = self.old_session_bus_address

    def assertDbusSignalEmits(
        self,
        signal: DbusSignalAsyncBaseBind[Any],
        timeout: Union[int, float] = 1,
    ) -> AsyncContextManager[DbusSignalRecorderBase]:

        if isinstance(signal, DbusSignalAsyncLocalBind):
            return DbusSignalRecorderLocal(timeout, signal)
        elif isinstance(signal, DbusSignalAsyncProxyBind):
            return DbusSignalRecorderRemote(timeout, self.bus, signal)
        else:
            raise TypeError("Unknown or unsupported signal class.")
