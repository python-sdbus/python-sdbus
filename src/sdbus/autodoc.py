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

from typing import Any

from sphinx.application import Sphinx
from sphinx.ext.autodoc import AttributeDocumenter, MethodDocumenter

from .dbus_proxy_async import (
    DbusInterfaceCommonAsync,
    DbusMethodAsync,
    DbusPropertyAsync,
    DbusSignal,
)


class DbusMethodDocumenter(MethodDocumenter):

    objtype = 'DbusMethodAsync'
    directivetype = 'method'
    priority = 100 + MethodDocumenter.priority

    @classmethod
    def can_document_member(cls, member: Any, *args: Any) -> bool:
        return isinstance(member, DbusMethodAsync)

    def import_object(self, raiseerror: bool = False) -> bool:
        self.objpath.append('original_method')
        ret = super().import_object(raiseerror)
        self.objpath.pop()
        return ret

    def add_content(self,
                    *args: Any, **kwargs: Any,
                    ) -> None:

        source_name = self.get_sourcename()
        self.add_line('', source_name)
        self.add_line('**D-Bus Method**', source_name)
        self.add_line('', source_name)

        super().add_content(*args, **kwargs)


class DbusPropertyDocumenter(AttributeDocumenter):

    objtype = 'DbusPropertyAsync'
    directivetype = 'attribute'
    priority = 100 + AttributeDocumenter.priority

    @classmethod
    def can_document_member(cls, member: Any, *args: Any) -> bool:
        return isinstance(member, DbusPropertyAsync)

    def update_annotations(self,
                           parent: DbusInterfaceCommonAsync) -> None:

        property_annotation = \
            self.object.property_getter.__annotations__['return']

        parent.__annotations__[self.object_name] = property_annotation

    def add_content(self,
                    *args: Any, **kwargs: Any,
                    ) -> None:

        source_name = self.get_sourcename()
        self.add_line('', source_name)
        self.add_line('**D-Bus property**', source_name)
        self.add_line('', source_name)

        super().add_content(*args, **kwargs)


class DbusSignalDocumenter(AttributeDocumenter):

    objtype = 'DbusSignal'
    directivetype = 'attribute'
    priority = 100 + AttributeDocumenter.priority

    @classmethod
    def can_document_member(cls, member: Any, *args: Any) -> bool:
        return isinstance(member, DbusSignal)

    def update_annotations(self,
                           parent: DbusInterfaceCommonAsync) -> None:

        signal_annotation = \
            self.object.original_function.__annotations__['return']

        parent.__annotations__[self.object_name] = signal_annotation

    def add_content(self,
                    *args: Any, **kwargs: Any,
                    ) -> None:

        source_name = self.get_sourcename()
        self.add_line('', source_name)
        self.add_line('**D-Bus signal**', source_name)
        self.add_line('', source_name)

        super().add_content(*args, **kwargs)


def setup(app: Sphinx) -> None:
    app.setup_extension('sphinx.ext.autodoc')
    app.add_autodocumenter(DbusMethodDocumenter)
    app.add_autodocumenter(DbusPropertyDocumenter)
    app.add_autodocumenter(DbusSignalDocumenter)
