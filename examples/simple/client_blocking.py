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

from sdbus import DbusInterfaceCommon, dbus_method, dbus_property

# The interface has to be redefined using the blocking base class
# and decorators.


class ExampleInterfaceBlocking(
    DbusInterfaceCommon, interface_name="org.example.interface"
):
    @dbus_method(
        input_signature="s",
        result_signature="s",
    )
    def upper(self, string: str) -> str:
        return string.upper()

    @dbus_property(
        property_signature="s",
    )
    def hello_world(self) -> str:
        return "Hello, World!"


def main() -> None:
    # Create a new proxied object
    example_object = ExampleInterfaceBlocking(
        service_name="org.example.test",
        object_path="/",
    )

    # Call upper
    s = "test string"
    s_after = example_object.upper(s)

    print("Initial string: ", s)
    print("After call: ", s_after)

    # Get property
    print("Remote property: ", example_object.hello_world)


if __name__ == "__main__":
    main()
