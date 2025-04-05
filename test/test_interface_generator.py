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
from unittest.mock import MagicMock, patch

from sdbus.__main__ import generator_main
from sdbus.interface_generator import (
    DbusSigToTyping,
    camel_case_to_snake_case,
    generate_py_file,
    interface_name_to_class,
    interfaces_from_str,
)
from sdbus.unittest import IsolatedDbusTestCase

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
      <property name="FooFoo" type="as" access="read">
        <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal"
        value="false"/>
      </property>
      <property name="BoundBy" type="as" access="read">
        <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal"
        value="const"/>
      </property>
      <property name="FooInvalidates" type="s" access="read">
        <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal"
        value="invalidates"/>
      </property>
    </interface>
    <node name="child_of_sample_object"/>
    <node name="another_child_of_sample_object"/>
</node>
"""


class TestConverter(TestCase):
    def test_camel_to_snake(self) -> None:
        with self.subTest("CamelCase"):
            self.assertEqual(
                'activate_connection',
                camel_case_to_snake_case('ActivateConnection'),
            )

        with self.subTest("Already snake case"):
            self.assertEqual(
                'activate_connection',
                camel_case_to_snake_case('activate_connection'),
            )

        with self.subTest("Upper snake case"):
            self.assertEqual(
                'activate_connection',
                camel_case_to_snake_case('ACTIVATE_CONNECTION'),
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
                'tuple[str, Any]', DbusSigToTyping.typing_complete('v')
            )

        with self.subTest('Splitter test'):
            self.assertEqual(
                ['v', 'as', '(uisa{sx})', 'h', 'a(ss)', 'a{ss}', 'ay'],
                DbusSigToTyping.split_sig('vas(uisa{sx})ha(ss)a{ss}ay')
            )

        with self.subTest('Parse struct'):
            self.assertEqual(
                DbusSigToTyping.typing_complete('(sx)'),
                'tuple[str, int]',
            )

        with self.subTest('Parse list'):
            self.assertEqual(
                DbusSigToTyping.typing_complete('a(sx)'),
                'list[tuple[str, int]]',
            )

        with self.subTest('Parse dict'):
            self.assertEqual(
                DbusSigToTyping.typing_complete('a{s(xh)}'),
                'dict[str, tuple[int, int]]',
            )

        with self.subTest('Parse signature'):
            self.assertEqual(
                DbusSigToTyping.sig_to_typing('a{s(xh)}'),
                'dict[str, tuple[int, int]]',
            )

            self.assertEqual(
                DbusSigToTyping.sig_to_typing('a{s(xh)}xs'),
                'tuple[dict[str, tuple[int, int]], int, str]',
            )

            self.assertEqual(
                DbusSigToTyping.sig_to_typing('a{s(xh)}xs'),
                'tuple[dict[str, tuple[int, int]], int, str]',
            )

            self.assertEqual(
                DbusSigToTyping.sig_to_typing('as'),
                'list[str]',
            )

            self.assertEqual(
                DbusSigToTyping.sig_to_typing(''),
                'None',
            )

    def test_parsing(self) -> None:
        if find_spec('jinja2') is None:
            raise SkipTest('Jinja2 not installed')

        interfaces_intro = interfaces_from_str(test_xml)

        with self.subTest('Test introspection details'):
            test_interface = interfaces_intro[0]

            for test_property in test_interface.properties:
                if test_property.method_name == 'BoundBy':
                    self.assertEqual(
                        test_property.emits_changed,
                        'const',
                    )
                elif test_property.method_name == 'Bar':
                    self.assertEqual(
                        test_property.emits_changed,
                        True,
                    )
                elif test_property.method_name == 'FooInvalidates':
                    self.assertEqual(
                        test_property.emits_changed,
                        'invalidates',
                    )
                elif test_property.method_name == 'FooFoo':
                    self.assertEqual(
                        test_property.emits_changed,
                        False,
                    )

        generated = generate_py_file(interfaces_intro)
        self.assertIn('flags=DbusPropertyEmitsInvalidationFlag', generated)
        self.assertIn('flags=DbusPropertyConstFlag', generated)


class TestGeneratorAgainstDbus(IsolatedDbusTestCase):
    def setUp(self) -> None:
        if find_spec('jinja2') is None:
            raise SkipTest('Jinja2 not installed')

        super().setUp()

    def test_generate_from_connection(self) -> None:
        with patch("sdbus.__main__.stdout") as stdout_mock:
            generator_main(
                [
                    "gen-from-connection",
                    "org.freedesktop.DBus",
                    "/org/freedesktop/DBus",
                ]
            )

        write_mock: MagicMock = stdout_mock.write
        write_mock.assert_called_once()

        generated_interface = write_mock.call_args.args[0]

        self.assertIn(
            "OrgFreedesktopDBusDebugStatsInterface",
            generated_interface,
        )
        self.assertIn(
            "get_connection_unix_process_id",
            generated_interface,
        )
        self.assertIn(
            "async",
            generated_interface,
        )

    def test_generate_from_connection_blocking(self) -> None:
        with patch("sdbus.__main__.stdout") as stdout_mock:
            generator_main(
                [
                    "gen-from-connection",
                    "--block",
                    "org.freedesktop.DBus",
                    "/org/freedesktop/DBus",
                ]
            )

        write_mock: MagicMock = stdout_mock.write
        write_mock.assert_called_once()

        generated_interface = write_mock.call_args.args[0]

        self.assertNotIn(
            "async",
            generated_interface,
        )
        self.assertIn(
            "dbus_property",
            generated_interface,
        )


INTERFACE_NO_MEMBERS_XML = """
<!DOCTYPE node PUBLIC "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
  "http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd">
<node name="/com/example/sample_object0">
    <interface name="com.example.SampleInterface1">
    </interface>
    <node name="child_of_sample_object"/>
    <node name="another_child_of_sample_object"/>
</node>
"""


class TestGeneratorSyntaxCompile(TestCase):
    def setUp(self) -> None:
        if find_spec('jinja2') is None:
            raise SkipTest('Jinja2 not installed')

        super().setUp()

    def test_syntax_compile_async(self) -> None:
        source_code = generate_py_file(
            interfaces_from_str(test_xml),
            do_async=True,
        )
        compile(source_code, filename="<string>", mode="exec")

    def test_syntax_compile_block(self) -> None:
        source_code = generate_py_file(
            interfaces_from_str(test_xml),
            do_async=False,
        )
        compile(source_code, filename="<string>", mode="exec")

    def test_syntax_no_members_interface(self) -> None:

        regular_interface = interfaces_from_str(test_xml)
        no_members_interface = interfaces_from_str(INTERFACE_NO_MEMBERS_XML)

        self.assertFalse(no_members_interface[0].methods)
        self.assertFalse(no_members_interface[0].properties)
        self.assertFalse(no_members_interface[0].signals)

        compile(
            generate_py_file(
                regular_interface + no_members_interface,
                do_async=True,
            ),
            filename="<string>",
            mode="exec",
        )
        compile(
            generate_py_file(
                no_members_interface + regular_interface,
                do_async=True,
            ),
            filename="<string>",
            mode="exec",
        )

        compile(
            generate_py_file(
                regular_interface + no_members_interface,
                do_async=False,
            ),
            filename="<string>",
            mode="exec",
        )
        compile(
            generate_py_file(
                no_members_interface + regular_interface,
                do_async=False,
            ),
            filename="<string>",
            mode="exec",
        )


if __name__ == "__main__":
    main()
