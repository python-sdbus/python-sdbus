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

from os import environ, kill
from pathlib import Path
from signal import SIGTERM
from subprocess import DEVNULL
from subprocess import run as subprocess_run
from tempfile import TemporaryDirectory
from typing import ClassVar
from unittest import IsolatedAsyncioTestCase

from sdbus import sd_bus_open_user, set_default_bus

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
