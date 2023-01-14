# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2023 igo95862

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

from unittest import main

from sdbus.exceptions import (
    SdBusRequestNameAlreadyOwnerError,
    SdBusRequestNameError,
    SdBusRequestNameExistsError,
    SdBusRequestNameInQueueError,
)
from sdbus.unittest import IsolatedDbusTestCase


class TestRequestName(IsolatedDbusTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    def test_request_name_exception_tree(self) -> None:
        # Test that SdBusRequestNameError is super class
        # of other request name exceptions
        self.assertTrue(
            issubclass(
                SdBusRequestNameAlreadyOwnerError,
                SdBusRequestNameError,
            )
        )
        self.assertTrue(
            issubclass(
                SdBusRequestNameExistsError,
                SdBusRequestNameError,
            )
        )
        self.assertTrue(
            issubclass(
                SdBusRequestNameInQueueError,
                SdBusRequestNameError,
            )
        )
        # Test the opposite
        self.assertFalse(
            issubclass(
                SdBusRequestNameAlreadyOwnerError,
                SdBusRequestNameExistsError,
            )
        )
        self.assertFalse(
            issubclass(
                SdBusRequestNameInQueueError,
                SdBusRequestNameExistsError,
            )
        )
        self.assertFalse(
            issubclass(
                SdBusRequestNameInQueueError,
                SdBusRequestNameAlreadyOwnerError,
            )
        )


if __name__ == '__main__':
    main()
