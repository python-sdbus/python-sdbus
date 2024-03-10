# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2020-2022 igo95862

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

from inspect import getfullargspec
from typing import TYPE_CHECKING

from .dbus_common_funcs import (
    _is_property_flags_correct,
    _method_name_converter,
    get_default_bus,
)
from .sd_bus_internals import is_interface_name_valid, is_member_name_valid

if TYPE_CHECKING:
    from types import FunctionType
    from typing import (
        Any,
        Callable,
        Dict,
        List,
        Optional,
        Sequence,
        Tuple,
        Type,
        TypeVar,
    )

    T = TypeVar('T')
    SelfMeta = TypeVar('SelfMeta', bound="DbusInterfaceMetaCommon")

    from .sd_bus_internals import SdBus, SdBusInterface


class DbusSomethingCommon:
    interface_name: str
    serving_enabled: bool


class DbusSomethingAsync(DbusSomethingCommon):
    ...


class DbusSomethingSync(DbusSomethingCommon):
    ...


class DbusInterfaceMetaCommon(type):
    def __new__(cls: Type[SelfMeta], name: str,
                bases: Tuple[type, ...],
                namespace: Dict[str, Any],
                interface_name: Optional[str] = None,
                serving_enabled: bool = True,
                ) -> SelfMeta:
        if interface_name is not None:
            try:
                assert is_interface_name_valid(interface_name), (
                    f"Invalid interface name: \"{interface_name}\"; "
                    'Interface names must be composed of 2 or more elements '
                    'separated by a dot \'.\' character. All elements must '
                    'contain at least one character, consist of ASCII '
                    'characters, first character must not be digit and '
                    'length must not exceed 255 characters.'
                )
            except NotImplementedError:
                ...

        for attr_name, attr in namespace.items():
            if not isinstance(attr, DbusSomethingCommon):
                continue

            # TODO: Fix async metaclass copying all methods
            if hasattr(attr, "interface_name"):
                continue

            if interface_name is None:
                raise TypeError(
                    f"Defined D-Bus element {attr_name!r} without "
                    f"interface name in the class {name!r}."
                )

            attr.interface_name = interface_name
            attr.serving_enabled = serving_enabled

        new_cls = super().__new__(cls, name, bases, namespace)

        return new_cls


MEMBER_NAME_REQUIREMENTS = (
    'Member name must only contain ASCII characters, '
    'cannot start with digit, '
    'must not contain dot \'.\' and be between 1 '
    'and 255 characters in length.'
)


class DbusMethodCommon(DbusSomethingCommon):

    def __init__(
            self,
            original_method: FunctionType,
            method_name: Optional[str],
            input_signature: str,
            input_args_names: Optional[Sequence[str]],
            result_signature: str,
            result_args_names: Optional[Sequence[str]],
            flags: int):

        assert not isinstance(input_args_names, str), (
            "Passed a string as input args"
            " names. Did you forget to put"
            " it in to a tuple ('string', ) ?")

        if method_name is None:
            method_name = ''.join(
                _method_name_converter(original_method.__name__))

        try:
            assert is_member_name_valid(method_name), (
                f"Invalid method name: \"{method_name}\"; "
                f"{MEMBER_NAME_REQUIREMENTS}"
            )
        except NotImplementedError:
            ...

        super().__init__()
        self.original_method = original_method
        self.args_spec = getfullargspec(original_method)
        self.args_names = self.args_spec.args[1:]  # 1: because of self
        self.num_of_args = len(self.args_names)
        self.args_defaults = (
            self.args_spec.defaults
            if self.args_spec.defaults is not None
            else ())
        self.default_args_start_at = self.num_of_args - len(self.args_defaults)

        self.method_name = method_name
        self.input_signature = input_signature
        self.input_args_names: Sequence[str] = ()
        if input_args_names is not None:
            assert not any(' ' in x for x in input_args_names), (
                "Can't have spaces in argument input names"
                f"Args: {input_args_names}")

            self.input_args_names = input_args_names
        elif result_args_names is not None:
            self.input_args_names = self.args_names

        self.result_signature = result_signature
        self.result_args_names: Sequence[str] = ()
        if result_args_names is not None:
            assert not any(' ' in x for x in result_args_names), (
                "Can't have spaces in argument result names."
                f"Args: {result_args_names}")

            self.result_args_names = result_args_names

        self.flags = flags

        self.__doc__ = original_method.__doc__

    def _rebuild_args(
            self,
            function: FunctionType,
            *args: Any,
            **kwargs: Dict[str, Any]) -> List[Any]:
        # 3 types of arguments
        # *args - should be passed directly
        # **kwargs - should be put in a proper order
        # defaults - should be retrieved and put in proper order

        # Strategy:
        # Iterate over arg names
        # Use:
        # 1. Arg
        # 2. Kwarg
        # 3. Default

        # a, b, c, d, e
        #       ^ defaults start here
        # 5 - 3 = [2]
        # ^ total args
        #     ^ number of default args
        # First arg that supports default is
        # (total args - number of default args)
        passed_args_iter = iter(args)
        default_args_iter = iter(self.args_defaults)

        new_args_list: List[Any] = []

        for i, a_name in enumerate(self.args_spec.args[1:]):
            try:
                next_arg = next(passed_args_iter)
            except StopIteration:
                next_arg = None

            if i >= self.default_args_start_at:
                next_default_arg = next(default_args_iter)
            else:
                next_default_arg = None

            next_kwarg = kwargs.get(a_name)

            if next_arg is not None:
                new_args_list.append(next_arg)
            elif next_kwarg is not None:
                new_args_list.append(next_kwarg)
            elif next_default_arg is not None:
                new_args_list.append(next_default_arg)
            else:
                raise TypeError('Could not flatten the args')

        return new_args_list


class DbusPropertyCommon(DbusSomethingCommon):
    def __init__(self,
                 property_name: Optional[str],
                 property_signature: str,
                 flags: int,
                 original_method: FunctionType):
        if property_name is None:
            property_name = ''.join(
                _method_name_converter(original_method.__name__))

        try:
            assert is_member_name_valid(property_name), (
                f"Invalid property name: \"{property_name}\"; "
                f"{MEMBER_NAME_REQUIREMENTS}"
            )
        except NotImplementedError:
            ...

        assert _is_property_flags_correct(flags), (
            'Incorrect number of Property flags. '
            'Only one of DbusPropertyConstFlag, DbusPropertyEmitsChangeFlag, '
            'DbusPropertyEmitsInvalidationFlag or DbusPropertyExplicitFlag '
            'is allowed.'
        )

        super().__init__()
        self.property_name: str = property_name
        self.property_signature = property_signature
        self.flags = flags


class DbusSignalCommon(DbusSomethingCommon):
    def __init__(self,
                 signal_name: Optional[str],
                 signal_signature: str,
                 args_names: Sequence[str],
                 flags: int,
                 original_method: FunctionType):
        if signal_name is None:
            signal_name = ''.join(
                _method_name_converter(original_method.__name__))

        try:
            assert is_member_name_valid(signal_name), (
                f"Invalid signal name: \"{signal_name}\"; "
                f"{MEMBER_NAME_REQUIREMENTS}"
            )
        except NotImplementedError:
            ...

        super().__init__()
        self.signal_name = signal_name
        self.signal_signature = signal_signature
        self.args_names = args_names
        self.flags = flags

        self.__doc__ = original_method.__doc__
        self.__annotations__ = original_method.__annotations__


class DbusBindedAsync:
    ...


class DbusBindedSync:
    ...


class DbusMethodOverride:
    def __init__(self, override_method: T):
        self.override_method = override_method


class DbusPropertyOverride:
    def __init__(self, getter_override: T):
        self.getter_override = getter_override
        self.setter_override: Optional[Callable[[Any, T], None]] = None
        self.is_setter_public = True

    def setter(self, new_setter: Optional[Callable[[Any, T], None]]) -> None:
        self.setter_override = new_setter

    def setter_private(
        self,
        new_setter: Optional[Callable[[Any, T], None]],
    ) -> None:
        self.setter_override = new_setter
        self.is_setter_public = False


class DbusRemoteObjectMeta:
    def __init__(
        self,
        service_name: str,
        object_path: str,
        bus: Optional[SdBus] = None,
    ):
        self.service_name = service_name
        self.object_path = object_path
        self.attached_bus = (
            bus if bus is not None
            else get_default_bus()
        )


class DbusLocalObjectMeta:
    def __init__(self) -> None:
        self.activated_interfaces: List[SdBusInterface] = []
        self.serving_object_path: Optional[str] = None
        self.attached_bus: Optional[SdBus] = None


class DbusClassMeta:
    def __init__(
        self,
        interface_name: str,
        serving_enabled: bool,
    ) -> None:
        self.interface_name = interface_name
        self.serving_enabled = serving_enabled
        self.dbus_member_to_python_attr: Dict[str, str] = {}
        self.python_attr_to_dbus_member: Dict[str, str] = {}
