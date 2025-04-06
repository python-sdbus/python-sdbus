# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2025 igo95862

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

from contextvars import copy_context
from unittest import main

from sdbus.unittest import IsolatedDbusTestCase

from sdbus import get_default_bus, sd_bus_open_user, set_context_default_bus


def return_bus_id() -> int:
    return id(get_default_bus())


def set_context_and_return_id() -> int:
    set_context_default_bus(sd_bus_open_user())
    return id(get_default_bus())


class TestDefaultBus(IsolatedDbusTestCase):
    def test_context_bus(self) -> None:
        bus_id = id(get_default_bus())

        self.assertEqual(
            bus_id,
            copy_context().run(return_bus_id),
        )

        self.assertNotEqual(
            bus_id,
            copy_context().run(set_context_and_return_id),
        )

        self.assertEqual(
            bus_id,
            id(get_default_bus()),
        )


if __name__ == "__main__":
    main()
