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
from typing import Any, Dict, Literal, NamedTuple, Optional, Tuple, Union


class NotificationsHelper:

    def create_hints(
        self,
        use_action_icons: Optional[bool] = None,
        category: Optional[str] = None,
        desktop_entry_name: Optional[str] = None,
        image_data_tuple: Optional[
            Tuple[int, int, int, bool, int, int, Union[bytes, bytearray]]
        ] = None,
        image_path: Optional[Union[str, Path]] = None,
        is_resident: Optional[bool] = None,
        sound_file_path: Optional[Union[str, Path]] = None,
        sound_name: Optional[str] = None,
        suppress_sound: Optional[bool] = None,
        is_transient: Optional[bool] = None,
        xy_pos: Optional[Tuple[int, int]] = None,
        urgency: Optional[int] = None,
    ) -> Dict[str, Tuple[str, Any]]:

        hints_dict: Dict[str, Tuple[str, Any]] = {}

        # action-icons
        if use_action_icons is not None:
            hints_dict['action-icons'] = ('b', use_action_icons)

        # category
        if category is not None:
            hints_dict['category'] = ('s', category)

        # desktop-entry
        if desktop_entry_name is not None:
            hints_dict['desktop-entry'] = ('s', desktop_entry_name)

        # image-data
        if image_data_tuple is not None:
            hints_dict['image-data'] = ('iiibiiay', image_data_tuple)

        # image-path
        if image_path is not None:
            hints_dict['image-path'] = (
                's',
                image_path
                if isinstance(image_path, str)
                else str(image_path))

        # resident
        if is_resident is not None:
            hints_dict['resident'] = ('b', is_resident)

        # sound-file
        if sound_file_path is not None:
            hints_dict['sound-file'] = (
                's',
                sound_file_path
                if isinstance(sound_file_path, str)
                else str(sound_file_path))

        # sound-name
        if sound_name is not None:
            hints_dict['sound-name'] = (
                's', sound_name
            )

        # suppress-sound
        if suppress_sound is not None:
            hints_dict['suppress-sound'] = ('b', suppress_sound)

        # is_transient
        if is_transient is not None:
            hints_dict['is_transient'] = ('b', is_transient)

        # x
        # y
        if xy_pos is not None:
            hints_dict['x'] = ('i', xy_pos[0])
            hints_dict['y'] = ('i', xy_pos[1])

        return hints_dict


class SystemdUnitListTuple(NamedTuple):
    primary_name: str
    description: str
    load_state: str
    active_state: str
    sub_state: str
    followed_unit: str
    unit_path: str
    job_id: int
    job_type: str
    job_path: str


SystemdUnitStartModes = Literal[
    'replace', 'fail', 'isolate',
    'ignore-dependencies', 'ignore-requirements'
]

SystemdUnitStopModes = Literal[
    'replace', 'fail',
    'ignore-dependencies', 'ignore-requirements'
]

SystemdActiveState = Literal[
    'active', 'reloading', 'failed',
    'activating', 'deactivating'
]
