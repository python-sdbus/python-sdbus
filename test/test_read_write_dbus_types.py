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

from typing import Dict, List
from unittest import main

from sdbus.sd_bus_internals import SdBus, SdBusMessage

from sdbus import SdBusLibraryError

from .common_test_util import TempDbusTest


def create_message(bus: SdBus) -> SdBusMessage:
    return bus.new_method_call_message(
        'org.freedesktop.systemd1',
        '/org/freedesktop/systemd1',
        'org.freedesktop.systemd1.Manager',
        'GetUnit')


class TestDbusTypes(TempDbusTest):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    def test_unsigned(self) -> None:
        message = create_message(self.bus)

        int_t_max = 2**64
        unsigned_integers = ((2**8)-1, (2**16)-1, (2**32)-1, int_t_max-1)
        message.append_data("yqut", *unsigned_integers)
        # Test overflows
        self.assertRaises(
            OverflowError, message.append_data, "y", 2**8)

        self.assertRaises(
            OverflowError, message.append_data, "q", 2**16)

        self.assertRaises(
            OverflowError, message.append_data, "u", 2**32)

        self.assertRaises(
            OverflowError, message.append_data, "t", 2**64)

        self.assertRaises(
            OverflowError, message.append_data, "y", -1)
        self.assertRaises(
            OverflowError, message.append_data, "q", -1)
        self.assertRaises(
            OverflowError, message.append_data, "u", -1)
        self.assertRaises(
            OverflowError, message.append_data, "t", -1)

        message.seal()
        return_integers = message.get_contents()
        self.assertEqual(unsigned_integers, return_integers)

    def test_signed(self) -> None:
        message = create_message(self.bus)

        int_n_max = (2**(16-1))-1
        int_i_max = (2**(32-1))-1
        int_x_max = (2**(64-1))-1
        signed_integers_positive = (int_n_max, int_i_max, int_x_max)
        message.append_data("nix", *signed_integers_positive)

        self.assertRaises(
            OverflowError, message.append_data, "n", int_n_max + 1)

        self.assertRaises(
            OverflowError, message.append_data, "i", int_i_max + 1)

        self.assertRaises(
            OverflowError, message.append_data, "x", int_x_max + 1)

        int_n_min = -(2**(16-1))
        int_i_min = -(2**(32-1))
        int_x_min = -(2**(64-1))
        signed_integers_negative = (int_n_min, int_i_min, int_x_min)
        message.append_data("n", int_n_min)
        self.assertRaises(
            OverflowError, message.append_data, "n", int_n_min - 1)

        message.append_data("i", int_i_min)
        self.assertRaises(
            OverflowError, message.append_data, "i", int_i_min - 1)

        message.append_data("x", int_x_min)
        self.assertRaises(
            OverflowError, message.append_data, "x", int_x_min - 1)

        message.seal()
        return_integers = message.get_contents()
        self.assertEqual(signed_integers_positive +
                         signed_integers_negative, return_integers)

    def test_strings(self) -> None:
        message = create_message(self.bus)

        test_string = "test"
        test_path = "/test/object"
        test_signature = "say(xsai)o"

        message.append_data("sog", test_string, test_path, test_signature)

        message.seal()
        self.assertEqual(message.get_contents(),
                         (test_string, test_path, test_signature))

    def test_double(self) -> None:
        message = create_message(self.bus)

        test_double = 1.0
        message.append_data("d", test_double)

        message.seal()
        self.assertEqual(message.get_contents(), test_double)

    def test_bool(self) -> None:
        message = create_message(self.bus)

        test_booleans = (True, False, False, True, 1 == 1)

        message.append_data("bbbbb", *test_booleans)

        self.assertRaises(TypeError, message.append_data, 'b', 'asdasad')

        message.seal()
        self.assertEqual(message.get_contents(), test_booleans)

    def test_array(self) -> None:
        message = create_message(self.bus)

        test_string_array = ["Ttest", "serawer", "asdadcxzc"]
        message.append_data("as", test_string_array)

        test_bytes_array = b"asdasrddjkmlh\ngnmflkdtgh\0oer27852y4785823"
        message.append_data("ay", test_bytes_array)

        test_int_list = [1234, 123123, 764523]
        message.append_data("ai", test_int_list)

        message.append_data("ax", [])

        self.assertRaises(TypeError, message.append_data,
                          "a", test_int_list)

        message.seal()

        self.assertEqual(
            message.get_contents(),
            (test_string_array, test_bytes_array, test_int_list, []))

    def test_empty_array(self) -> None:
        message = create_message(self.bus)

        test_array: List[str] = []
        message.append_data("as", test_array)

        message.seal()

        self.assertEqual(
            message.get_contents(),
            test_array)

    def test_array_compound(self) -> None:
        message = create_message(self.bus)

        test_string_array = ["Ttest", "serawer", "asdadcxzc"]
        test_bytes_array = b"asdasrddjkmlh\ngnmflkdtgh\0oer27852y4785823"
        test_int_list = [1234, 123123, 764523]

        message.append_data(
            "asayai", test_string_array, test_bytes_array, test_int_list)

        message.seal()

        self.assertEqual(message.get_contents(),
                         (test_string_array, test_bytes_array, test_int_list))

    def test_nested_array(self) -> None:
        message = create_message(self.bus)

        test_string_array_one = ["Ttest", "serawer", "asdadcxzc"]
        test_string_array_two = ["asdaf", "seragdsfrgdswer", "sdfsdgg"]

        message.append_data(
            "aas", [test_string_array_one, test_string_array_two])

        message.seal()

        self.assertEqual(message.get_contents(),
                         [test_string_array_one, test_string_array_two])

    def test_struct(self) -> None:
        message = create_message(self.bus)

        struct_data = (123123, "test")
        message.append_data("(xs)", struct_data)

        message.seal()

        self.assertEqual(message.get_contents(), struct_data)

    def test_dict(self) -> None:
        message = create_message(self.bus)

        test_dict = {'test': 'a', 'asdaefd': 'cvbcfg'}
        message.append_data("a{ss}", test_dict)

        self.assertRaises(
            TypeError, message.append_data, "{ss}", test_dict)

        message.seal()
        self.assertEqual(message.get_contents(), test_dict)

    def test_empty_dict(self) -> None:
        message = create_message(self.bus)

        test_dict: Dict[str, str] = {}
        message.append_data("a{ss}", test_dict)

        message.seal()
        self.assertEqual(message.get_contents(), test_dict)

    def test_dict_nested_array(self) -> None:
        message = create_message(self.bus)

        test_array_one = [12, 1234234, 5, 2345, 24, 5623, 46, 2546, 68798]
        test_array_two = [124, 5, 356, 3, 57, 35,
                          67, 356, 2, 647, 36, 5784, 8, 809]
        test_dict = {'test': test_array_one, 'asdaefd': test_array_two}
        message.append_data("a{sax}", test_dict)

        message.seal()

        self.assertEqual(message.get_contents(), test_dict)

    def test_variant(self) -> None:
        message = create_message(self.bus)

        test_signature = "x"
        test_int = 1241354

        message.append_data("v", (test_signature, test_int))

        message.seal()

        self.assertEqual(message.get_contents(),
                         (test_signature, test_int))

    def test_array_of_variant(self) -> None:
        message = create_message(self.bus)

        test_signature_one = "(ssx)"
        test_str_1 = 'asdasdasd'
        test_str_2 = 'asdasdaddasdasdzc'
        test_int = 1241354

        test_signature_two = "ai"
        test_array = [12, 1234234, 5, 2345, 24, 5623, 46, 2546, 68798]

        message.append_data(
            "av",
            [
                (test_signature_one, (test_str_1, test_str_2, test_int)),
                (test_signature_two, test_array)
            ]
        )

        message.seal()

        self.assertEqual(
            message.get_contents(),
            [
                (test_signature_one, (test_str_1, test_str_2, test_int)),
                (test_signature_two, test_array)
            ]
        )

    def test_array_of_dict(self) -> None:
        message = create_message(self.bus)

        test_data = [
            {'asdasd': 'asdasd'},
            {'asdasdsg': 'asdasfdaf'},
            {},
        ]

        message.append_data("aa{ss}", test_data)
        message.seal()

        self.assertEqual(
            message.get_contents(),
            test_data)

    def test_array_of_struct(self) -> None:
        message = create_message(self.bus)

        test_data = [
            ('asdasd', 34636),
            ('asdasdads', -5425),
        ]

        message.append_data("a(si)", test_data)
        message.seal()

        self.assertEqual(
            message.get_contents(),
            test_data)

    def test_dict_of_struct(self) -> None:
        message = create_message(self.bus)

        test_dict = {
            1: ('asdasd', 'xcvghtrh'),
            2: ('rjhtyjdg', 'gbdtsret'),
            3: ('gvsgdthgdeth', 'gsgderfgd'),
        }

        message.append_data("a{n(ss)}", test_dict)
        message.seal()

        self.assertEqual(
            message.get_contents(),
            test_dict)

    def test_struct_with_dict(self) -> None:
        message = create_message(self.bus)

        test_struct = (
            'asdasdag',
            {
                'asdasd': 25,
                'dfasf': 63
            },
            542524,
            True
        )

        message.append_data("(sa{sq}ib)", test_struct)
        message.seal()

        self.assertEqual(
            message.get_contents(),
            test_struct
        )

    def test_dict_of_array(self) -> None:
        message = create_message(self.bus)

        test_dict = {
            '/': [341, 134, 764, 8986],
            '/test': [-245, -245, -1, 25],
        }

        message.append_data("a{oai}", test_dict)
        message.seal()

        self.assertEqual(
            message.get_contents(),
            test_dict
        )

    def test_array_of_array(self) -> None:
        message = create_message(self.bus)

        test_array = [
            ['asda', 'afgrfyhgdr', 'adffgvfdrfg'],
            ['afhryfjh', 'sgffgddrhg'],
            []
        ]
        message.append_data("aas", test_array)
        message.seal()

        self.assertEqual(
            message.get_contents(),
            test_array
        )

    def test_sealed_message_append(self) -> None:
        message = create_message(self.bus)

        message.append_data('s', 'test')
        message.seal()
        self.assertRaises(SdBusLibraryError,
                          message.append_data, 's', 'error')


if __name__ == "__main__":
    main()
