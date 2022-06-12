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

from unittest import SkipTest, main

from sdbus.sd_bus_internals import (
    SdBus,
    is_interface_name_valid,
    is_member_name_valid,
    is_object_path_valid,
    is_service_name_valid,
)
from sdbus.unittest import IsolatedDbusTestCase


class TestDbusTypes(IsolatedDbusTestCase):
    def test_init_bus(self) -> None:
        not_connected_bus = SdBus()
        self.assertIsNone(not_connected_bus.address)

        self.assertIsNotNone(self.bus.address)

    def test_validation_funcs(self) -> None:
        try:
            self.assertTrue(
                is_interface_name_valid('org.example.test')
            )

            self.assertFalse(
                is_interface_name_valid('Not very valid 😀')
            )

            self.assertTrue(
                is_service_name_valid('org.example.test')
            )

            self.assertFalse(
                is_service_name_valid('Not very valid 😀')
            )

            self.assertTrue(
                is_member_name_valid('GetSomething')
            )

            self.assertFalse(
                is_member_name_valid('no.dots.in.member.names')
            )

            self.assertTrue(
                is_object_path_valid('/test')
            )

            self.assertFalse(
                is_object_path_valid('no.dots.in.object.paths')
            )
        except NotImplementedError:
            raise SkipTest(
                (
                    "Validation funcs not implemented. "
                    "Probably too old libsystemd. (< 246)"
                )
            )


if __name__ == "__main__":
    main()
