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

from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple, Union
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import fromstring as etree_from_str
from xml.etree.ElementTree import parse as etree_from_file


def _camel_case_to_snake_case_generator(camel: str) -> Iterator[str]:
    i = iter(camel)

    # First character is directly converted to low
    try:
        first_char = next(i)
    except StopIteration:
        raise ValueError('Name too short')

    yield first_char.lower()

    # Yield every character
    # if upper is encountered
    # yield _ and lower
    while True:
        try:
            c = next(i)
        except StopIteration:
            return

        if c.isupper():
            yield '_'
            yield c.lower()
        else:
            yield c


def camel_case_to_snake_case(camel: str) -> str:
    return ''.join(_camel_case_to_snake_case_generator(camel))


def _iterface_name_to_class_generator(interface_name: str) -> Iterator[str]:
    i = iter(interface_name)

    try:
        first_char = next(i)
    except StopIteration:
        raise ValueError('Interface name too short')

    yield first_char.upper()

    up_next_char = False

    for _ in range(120):
        try:
            c = next(i)
        except StopIteration:
            return

        if c == '.':
            up_next_char = True
        else:
            if up_next_char:
                yield c.upper()
            else:
                yield c

            up_next_char = False


def interface_name_to_class(interface_name: str) -> str:
    return ''.join(_iterface_name_to_class_generator(interface_name))


def parse_str_bool(annotation_value: str) -> bool:
    if annotation_value == 'true':
        return True
    elif annotation_value == 'false':
        return False
    else:
        raise ValueError(f"Unknown bool value: {annotation_value}")


class DbusSigToTyping:

    _DBUS_BASIC_SIG_TO_TYPING = {
        'y': 'int',
        'b': 'bool',
        'n': 'int',
        'q': 'int',
        'i': 'int',
        'u': 'int',
        'x': 'int',
        't': 'int',
        'd': 'float',
        's': 'str',
        'o': 'str',
        'g': 'str',
        'h': 'int',
    }

    @classmethod
    def typing_basic(cls, char: str) -> str:
        return cls._DBUS_BASIC_SIG_TO_TYPING[char]

    @staticmethod
    def typing_into_tuple(typing_iter: Iterable[str]) -> str:
        return f"Tuple[{', '.join(typing_iter)}]"

    @staticmethod
    def slice_container(dbus_sig_iter: Iterator[str], peek_str: str) -> str:
        accumulator: List[str] = [peek_str]
        round_braces_count = 0
        curly_braces_count = 0

        if peek_str == '(':
            round_braces_count += 1

        if peek_str == '{':
            curly_braces_count += 1

        while True:
            try:
                char = next(dbus_sig_iter)
            except StopIteration:
                break

            if char == ')':
                round_braces_count -= 1

            if char == '}':
                curly_braces_count -= 1

            if char == '(':
                round_braces_count += 1

            if char == '{':
                curly_braces_count += 1

            accumulator.append(char)

            if char == 'a':

                continue

            if round_braces_count == 0 and curly_braces_count == 0:
                break

        return ''.join(accumulator)

    @classmethod
    def split_sig(cls, sig: str) -> List[str]:
        completes: List[str] = []

        sig_iter = iter(sig)

        while True:
            try:
                next_char = next(sig_iter)
            except StopIteration:
                break

            if next_char == '(':
                next_complete = cls.slice_container(sig_iter, '(')
            elif next_char == 'a':
                next_complete = cls.slice_container(sig_iter, 'a')
            else:
                next_complete = next_char

            completes.append(next_complete)

        return completes

    @classmethod
    def typing_complete(cls, complete_sig: str) -> str:

        if complete_sig == 'v':
            return cls.typing_into_tuple(('str', 'Any'))
        elif complete_sig == 'ay':
            return 'bytes'
        elif complete_sig.startswith('a{'):
            if complete_sig[-1] != '}':
                raise ValueError(f"Malformed dict {complete_sig}")

            dict_key_sig = complete_sig[2]
            dict_key_typing = cls.typing_basic(dict_key_sig)

            dict_value_sig = complete_sig[3:-1]
            dict_value_typing = cls.typing_complete(dict_value_sig)

            return f"Dict[{dict_key_typing}, {dict_value_typing}]"

        elif complete_sig.startswith('a'):
            array_completes = cls.split_sig(complete_sig[1:])

            if len(array_completes) != 1:
                raise ValueError("Array does not have only "
                                 "one complete type: {array_completes}")

            array_single_complete = array_completes[0]

            return f"List[{cls.typing_complete(array_single_complete)}]"
        elif complete_sig.startswith('('):
            if complete_sig[-1] != ')':
                raise ValueError(f"Malformed struct {complete_sig}")

            struct_completes = cls.split_sig(complete_sig[1:-1])
            struct_typing = (cls.typing_complete(x) for x in struct_completes)

            return cls.typing_into_tuple(struct_typing)
        else:
            return cls.typing_basic(complete_sig)

    @classmethod
    def result_typing(cls, result_args: List[str]) -> str:
        result_len = len(result_args)

        if result_len == 0:
            return 'None'
        elif result_len == 1:
            return cls.typing_complete(result_args[0])
        else:
            return cls.typing_into_tuple(
                (cls.typing_complete(x) for x in result_args)
            )

    @classmethod
    def sig_to_typing(cls, signature: str) -> str:
        return cls.result_typing(cls.split_sig(signature))


class DbusMemberAbstract:

    def __init__(self, element: Element):
        self.method_name = element.attrib['name']
        self.python_name = camel_case_to_snake_case(self.method_name)

        self.is_deprecated = False
        self.is_unpriveledged = False

        self.iter_sub_elements(element)

    def _flags_iter(self) -> Iterator[str]:
        if self.is_deprecated:
            yield 'DbusDeprecatedFlag'

        if self.is_unpriveledged:
            yield 'DbusUnprivilegedFlag'

    @property
    def flags_str(self) -> str:
        return ' | '.join(self._flags_iter())

    def _parse_arg(self, arg: Element) -> None:
        raise NotImplementedError('Member does not have arguments')

    def _parse_annotation_data(self,
                               annotation_name: str,
                               annotation_value: str) -> None:

        if annotation_name == 'org.freedesktop.DBus.Deprecated':
            self.is_deprecated = parse_str_bool(annotation_value)
        elif annotation_name == 'org.freedesktop.systemd1.Privileged':
            self.is_unpriveledged = parse_str_bool(annotation_value)
        else:
            ...

    def _parse_annotation(self, annotation: Element) -> None:
        if annotation.tag != 'annotation':
            raise ValueError('Uknown element of member: ', annotation.tag)

        annotation_name = annotation.attrib['name']
        annotation_value = annotation.attrib['value']

        self._parse_annotation_data(annotation_name, annotation_value)

    def iter_sub_elements(self, element: Element) -> None:
        for sub_element in element:
            tag = sub_element.tag
            if tag == 'annotation':
                self._parse_annotation(sub_element)
            elif tag == 'arg':
                self._parse_arg(sub_element)
            else:
                raise ValueError(
                    'Uknown member annotation tag: ', tag)


class DbusArgsIntrospection:
    def __init__(self, element: Element):
        if element.tag != 'arg':
            raise ValueError(f"Expected arg tag, got {element.tag}")

        try:
            self.name: Optional[str] = element.attrib['name']
        except KeyError:
            self.name = None

        self.dbus_type = element.attrib['type']

        direction = element.attrib.get('direction')
        if direction == 'in':
            self.is_input: Optional[bool] = True
        elif direction == 'out':
            self.is_input = False
        elif direction is None:
            self.is_input = None
        else:
            raise ValueError(f'Unknown arg direction {direction}')

    @property
    def typing(self) -> str:
        return DbusSigToTyping.typing_complete(self.dbus_type)

    def __repr__(self) -> str:
        return (f"Dbus Arg: {self.name}, "
                f"type: {self.dbus_type}, "
                f"is input: {self.is_input}")


class DbusMethodInrospection(DbusMemberAbstract):
    def __init__(self, element: Element):
        if element.tag != 'method':
            raise ValueError(f"Expected method tag, got {element.tag}")

        self.is_no_reply = False

        self.input_args: List[DbusArgsIntrospection] = []
        self.result_args: List[DbusArgsIntrospection] = []

        super().__init__(element)

    def _flags_iter(self) -> Iterator[str]:
        if self.is_no_reply:
            yield 'DbusNoReplyFlag'

        yield from super()._flags_iter()

    def _parse_arg(self, arg: Element) -> None:
        new_arg = DbusArgsIntrospection(arg)
        if new_arg.is_input or new_arg.is_input is None:
            self.input_args.append(new_arg)
        elif not new_arg.is_input:
            self.result_args.append(new_arg)
        else:
            raise ValueError('Malformed arg direction')

    @property
    def dbus_input_signature(self) -> str:
        return ''.join(
            (x.dbus_type for x in self.input_args)
        )

    @property
    def dbus_result_signature(self) -> str:
        return ''.join(
            (x.dbus_type if not x.is_input else ''
             for x in self.result_args)
        )

    @property
    def args_names_and_typing(self) -> List[Tuple[str, str]]:
        arg_names: List[Tuple[str, str]] = []

        for i, input_arg in enumerate(self.input_args):
            if input_arg.name is not None:
                input_arg_name = camel_case_to_snake_case(input_arg.name)
            else:
                input_arg_name = f"arg_{i}"

            arg_names.append((input_arg_name, input_arg.typing))

        return arg_names

    @property
    def result_typing(self) -> str:
        return DbusSigToTyping.result_typing(
            [x.dbus_type for x in self.result_args])

    def __repr__(self) -> str:
        return (f"Dbus Method: {self.method_name}, "
                f"args: {self.args_names_and_typing}, "
                f"result: {self.dbus_result_signature}")


class DbusPropertyIntrospection(DbusMemberAbstract):
    _EMITS_CHANGED_MAP: Dict[str, Optional[str]] = {
        'true': 'DbusPropertyEmitsChangeFlag',
        'false': None,
        'invalidates': 'DbusPropertyEmitsInvalidationFlag',
        'const': 'DbusPropertyConstFlag',
    }

    def __init__(self, element: Element):
        if element.tag != 'property':
            raise ValueError(f"Expected property tag, got {element.tag}")

        self.dbus_signature = element.attrib['type']

        self.emits_changed: Optional[str] = None
        self.is_explicit = False

        access_type = element.attrib['access']
        if access_type == 'readwrite':
            self.is_read_only = False
        elif access_type == 'read':
            self.is_read_only = True
        else:
            raise ValueError(f"Unknown property access {self.is_read_only}")

        super().__init__(element)

    def _flags_iter(self) -> Iterator[str]:
        if self.emits_changed is not None:
            yield self.emits_changed

        yield from super()._flags_iter()

    def _parse_annotation_data(self,
                               annotation_name: str,
                               annotation_value: str) -> None:

        if annotation_name == ('org.freedesktop.DBus.Property'
                               '.EmitsChangedSignal'):
            if annotation_value not in self._EMITS_CHANGED_MAP:
                raise ValueError('Unknown EmitsChanged value',
                                 annotation_value)

            self.emits_changed = self._EMITS_CHANGED_MAP[annotation_value]
        elif annotation_name == 'org.freedesktop.systemd1.Explicit':
            self.is_explicit = parse_str_bool(annotation_value)

        super()._parse_annotation_data(annotation_name, annotation_value)

    @property
    def typing(self) -> str:
        return DbusSigToTyping.typing_complete(self.dbus_signature)


class DbusSignalIntrospection(DbusMemberAbstract):
    def __init__(self, element: Element):
        if element.tag != 'signal':
            raise ValueError(f"Expected signal tag, got {element.tag}")

        self.args: List[DbusArgsIntrospection] = []
        super().__init__(element)

    def _parse_arg(self, arg: Element) -> None:
        new_arg = DbusArgsIntrospection(arg)

        if new_arg.is_input:
            raise ValueError('Signal argument cannot be in', new_arg)

        self.args.append(new_arg)

    @property
    def dbus_signature(self) -> str:
        return ''.join((x.dbus_type for x in self.args))

    @property
    def typing(self) -> str:
        return DbusSigToTyping.result_typing(
            [x.dbus_type for x in self.args])


class DbusInterfaceIntrospection:
    def __init__(self, element: Element):
        if element.tag != 'interface':
            raise ValueError(f"Expected interface tag, got {element.tag}")

        self.interface_name = element.attrib['name']
        self.python_name = interface_name_to_class(
            self.interface_name) + 'Interface'

        self.is_deprecated = False
        self.c_name: Optional[str] = None

        self.methods: List[DbusMethodInrospection] = []
        self.properties: List[DbusPropertyIntrospection] = []
        self.signals: List[DbusSignalIntrospection] = []
        for dbus_member in element:
            if dbus_member.tag == 'method':
                self.methods.append(DbusMethodInrospection(dbus_member))
            elif dbus_member.tag == 'property':
                self.properties.append(DbusPropertyIntrospection(dbus_member))
            elif dbus_member.tag == 'signal':
                self.signals.append(DbusSignalIntrospection(dbus_member))
            elif dbus_member.tag == 'annotation':
                annotation_name = dbus_member.attrib['name']
                annotation_value = dbus_member.attrib['value']

                if annotation_name == 'org.freedesktop.DBus.Deprecated':
                    self.is_deprecated = parse_str_bool(annotation_value)
                elif annotation_name == 'org.freedesktop.DBus.GLib.CSymbol':
                    self.c_name = annotation_value
                else:
                    ...
            else:
                raise ValueError(f'Unknown dbus member {dbus_member}')

    def generate_interface_class(self) -> str:
        from jinja2 import Environment as JinjaEnv

        env = JinjaEnv(trim_blocks=True)
        template = env.from_string(async_interface_template_txt)

        return template.render(interface=self)


async_import_header_txt = """
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from sdbus import (DbusDeprecatedFlag, DbusInterfaceCommonAsync,
                   DbusNoReplyFlag, DbusPropertyConstFlag,
                   DbusPropertyEmitsChangeFlag,
                   DbusPropertyEmitsInvalidationFlag, DbusPropertyExplicitFlag,
                   DbusUnprivilegedFlag, dbus_method_async,
                   dbus_property_async, dbus_signal_async)
"""

async_interface_template_txt = """

class {{ interface.python_name }}(
    DbusInterfaceCommonAsync,
    interface_name='{{ interface.interface_name }}',
):
{% for method in interface.methods %}

    @dbus_method_async(
{% if method.dbus_input_signature %}
        input_signature='{{ method.dbus_input_signature }}',
{% endif %}
{% if method.dbus_result_signature %}
        result_signature='{{ method.dbus_result_signature }}',
{% endif %}
{% if method.flags_str %}
        flags={{ method.flags_str }},
{% endif %}
    )
    async def {{ method.python_name }}(
        self,
{% for arg_name, arg_type in method.args_names_and_typing %}
        {{ arg_name }}: {{ arg_type }},
{% endfor %}
    ) -> {{ method.result_typing }}:
        raise NotImplementedError
{% endfor %}
{% for a_property in interface.properties %}

    @dbus_property_async(
{% if a_property.dbus_signature %}
        property_signature='{{ a_property.dbus_signature }}',
{% endif %}
{% if a_property.flags_str %}
        flags={{ a_property.flags_str }},
{% endif %}
    )
    def {{ a_property.python_name }}(self) -> {{ a_property.typing }}:
        raise NotImplementedError
{% endfor %}
{% for signal in interface.signals %}

    @dbus_signal_async(
{% if signal.dbus_signature %}
        signal_signature='{{ signal.dbus_signature }}',
{% endif %}
{% if signal.flags_str %}
        flags={{ signal.flags_str }},
{% endif %}
    )
    def {{ signal.python_name }}(self) -> {{ signal.typing }}:
        raise NotImplementedError
{% endfor %}

"""


def xml_to_interfaces_introspection(
        root: Element) -> List[DbusInterfaceIntrospection]:

    list_of_interface_introspection: List[DbusInterfaceIntrospection] = []

    if root.tag != 'node':
        raise ValueError(f"Expected node tag got {root.tag}")

    for interface in root:
        if interface.tag == 'node':
            continue

        list_of_interface_introspection.append(
            DbusInterfaceIntrospection(interface))

    return list_of_interface_introspection


def interfaces_from_file(filename_or_path: Union[str, Path]
                         ) -> List[DbusInterfaceIntrospection]:

    etree = etree_from_file(filename_or_path)

    return xml_to_interfaces_introspection(etree.getroot())


def interfaces_from_str(xml_str: str) -> List[DbusInterfaceIntrospection]:

    etree = etree_from_str(xml_str)

    return xml_to_interfaces_introspection(etree)


def generate_async_py_file(
        interfaces: List[DbusInterfaceIntrospection],
        include_import_header: bool = True) -> str:

    interfaces_definitions = '\n'.join(
        (x.generate_interface_class() for x in interfaces))

    if include_import_header:
        return async_import_header_txt + interfaces_definitions
    else:
        return interfaces_definitions
