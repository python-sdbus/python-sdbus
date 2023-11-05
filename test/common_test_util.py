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

from unittest import SkipTest, main


def mem_test() -> None:
    while True:
        try:
            main()
        except SystemExit:
            ...


def mem_test_single(test_class: type, test_name: str) -> None:
    while True:
        t = test_class()
        t.setUp()
        getattr(t, test_name)()


def skip_if_no_asserts() -> None:
    try:
        assert False
    except AssertionError:
        return

    raise SkipTest("Assertions are not enabled")


def skip_if_no_name_validations() -> None:
    skip_if_no_asserts()

    from sdbus.sd_bus_internals import is_interface_name_valid

    try:
        is_interface_name_valid("org.test")
    except NotImplementedError:
        raise SkipTest("Validation functions not available")
