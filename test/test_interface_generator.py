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

from importlib.util import find_spec
from unittest import SkipTest, TestCase, main

from sdbus.interface_generator import (
    DbusSigToTyping,
    camel_case_to_snake_case,
    generate_async_py_file,
    interface_name_to_class,
    interfaces_from_str,
)

test_xml = """
<!DOCTYPE node PUBLIC "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
  "http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd">
<node name="/com/example/sample_object0">
    <interface name="com.example.SampleInterface0">
      <method name="Frobate">
        <arg name="foo" type="i" direction="in"/>
        <arg name="bar" type="s" direction="out"/>
        <arg name="baz" type="a{us}" direction="out"/>
        <annotation name="org.freedesktop.DBus.Deprecated" value="true"/>
        <annotation name="org.freedesktop.systemd1.Privileged" value="true"/>
      </method>
      <method name="Bazify">
        <arg name="bar" type="(iiu)" direction="in"/>
        <arg name="bar" type="v" direction="out"/>
      </method>
      <method name="Mogrify">
        <arg name="bar" type="(iiav)" direction="in"/>
      </method>
      <signal name="Changed">
        <arg name="new_value" type="b"/>
      </signal>
      <property name="Bar" type="y" access="readwrite"/>
    </interface>
    <node name="child_of_sample_object"/>
    <node name="another_child_of_sample_object"/>
</node>
"""


class TestConverter(TestCase):
    def test_camel_to_snake(self) -> None:
        self.assertEqual(
            'activate_connection',
            camel_case_to_snake_case('ActivateConnection'),
        )

    def test_interface_name_to_class(self) -> None:
        self.assertEqual(
            'ComExampleSampleInterface0',
            interface_name_to_class('com.example.SampleInterface0'),
        )

    def test_signature_to_typing(self) -> None:
        with self.subTest('Parse basic'):
            self.assertEqual(
                'str', DbusSigToTyping.typing_basic('s')
            )

            self.assertRaises(
                KeyError, DbusSigToTyping.typing_basic, 'v')

        with self.subTest('Parse variant'):
            self.assertEqual(
                'Tuple[str, Any]', DbusSigToTyping.typing_complete('v')
            )

        with self.subTest('Splitter test'):
            self.assertEqual(
                ['v', 'as', '(uisa{sx})', 'h', 'a(ss)', 'a{ss}', 'ay'],
                DbusSigToTyping.split_sig('vas(uisa{sx})ha(ss)a{ss}ay')
            )

        with self.subTest('Parse struct'):
            self.assertEqual(
                DbusSigToTyping.typing_complete('(sx)'),
                'Tuple[str, int]',
            )

        with self.subTest('Parse list'):
            self.assertEqual(
                DbusSigToTyping.typing_complete('a(sx)'),
                'List[Tuple[str, int]]',
            )

        with self.subTest('Parse dict'):
            self.assertEqual(
                DbusSigToTyping.typing_complete('a{s(xh)}'),
                'Dict[str, Tuple[int, int]]',
            )

        with self.subTest('Parse signature'):
            self.assertEqual(
                DbusSigToTyping.sig_to_typing('a{s(xh)}'),
                'Dict[str, Tuple[int, int]]',
            )

            self.assertEqual(
                DbusSigToTyping.sig_to_typing('a{s(xh)}xs'),
                'Tuple[Dict[str, Tuple[int, int]], int, str]',
            )

            self.assertEqual(
                DbusSigToTyping.sig_to_typing('a{s(xh)}xs'),
                'Tuple[Dict[str, Tuple[int, int]], int, str]',
            )

            self.assertEqual(
                DbusSigToTyping.sig_to_typing('as'),
                'List[str]',
            )

            self.assertEqual(
                DbusSigToTyping.sig_to_typing(''),
                'None',
            )

    def test_parsing(self) -> None:
        if find_spec('jinja2') is None:
            raise SkipTest('Jinja2 not installed')

        print(generate_async_py_file(interfaces_from_str(test_xml)))


if __name__ == "__main__":
    main()
