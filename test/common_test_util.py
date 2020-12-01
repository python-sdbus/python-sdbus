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

from asyncio.subprocess import DEVNULL, create_subprocess_exec
from os import kill, environ
from pathlib import Path
from signal import SIGKILL
from tempfile import TemporaryDirectory
from unittest import IsolatedAsyncioTestCase, main

dbus_config = '''
<!DOCTYPE busconfig PUBLIC
 "-//freedesktop//DTD D-Bus Bus Configuration 1.0//EN"
 "http://www.freedesktop.org/standards/dbus/1.0/busconfig.dtd">
<busconfig>

  <!-- Our well-known bus type, do not change this -->
  <type>session</type>


  <!-- Write a pid file -->
  <pidfile>{pidfile_path}</pidfile>

  <!-- Only allow socket-credentials-based authentication -->
  <auth>EXTERNAL</auth>

  <!-- Only listen on a local socket. (abstract=/path/to/socket
       means use abstract namespace, don't really create filesystem
       file; only Linux supports this. Use path=/whatever on other
       systems.) -->
  <listen>unix:path={socket_path}</listen>

  <policy context="default">
    <!-- Allow everything to be sent -->
    <allow send_destination="*" eavesdrop="true"/>
    <!-- Allow everything to be received -->
    <allow eavesdrop="true"/>
    <!-- Allow anyone to own anything -->
    <allow own="*"/>
  </policy>

</busconfig>
'''


class TempDbusTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.temp_dir_path = Path(self.temp_dir.name)

        self.dbus_socket_path = self.temp_dir_path / 'test_dbus.socket'
        self.pid_path = self.temp_dir_path / 'dbus.pid'

        self.dbus_config_file = self.temp_dir_path / 'dbus.config'

        with open(self.dbus_config_file, mode='x') as conf_file:
            conf_file.write(dbus_config.format(
                socket_path=self.dbus_socket_path,
                pidfile_path=self.pid_path))

        self.dbus_process = await create_subprocess_exec(
            '/usr/bin/dbus-daemon',
            f'--config-file={self.dbus_config_file}',
            '--fork',
            stdin=DEVNULL,
        )
        await self.dbus_process.wait()
        environ[
            'DBUS_SESSION_BUS_ADDRESS'] = f"unix:path={self.dbus_socket_path}"

    async def asyncTearDown(self) -> None:
        with open(self.pid_path) as pid_file:
            dbus_pid = int(pid_file.read())

        kill(dbus_pid, SIGKILL)
        self.temp_dir.cleanup()


def mem_test() -> None:
    while True:
        try:
            main()
        except SystemExit:
            ...
