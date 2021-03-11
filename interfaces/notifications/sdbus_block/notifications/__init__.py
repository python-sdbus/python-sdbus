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
from typing import Any, Dict, List, Optional, Tuple, Union

from sdbus import DbusInterfaceCommon, dbus_method
from sdbus.sd_bus_internals import SdBus


class FreedesktopNotifications(
        DbusInterfaceCommon,
        interface_name='org.freedesktop.Notifications'):

    def __init__(self, bus: Optional[SdBus] = None) -> None:
        """
        Dbus interface object path and service name is
        predetermined.
        (at ``'org.freedesktop.Notifications'``,
        ``'/org/freedesktop/Notifications'``)

        :param SdBus bus:
            Optional dbus connection. \
            If not passed the default dbus will be used.
        """
        super().__init__(
            'org.freedesktop.Notifications',
            '/org/freedesktop/Notifications',
            bus,
        )

    @dbus_method('u')
    def close_notification(self, notif_id: int) -> None:
        """Close notification by id.

        :param int notif_id: Notification id to close.
        """
        raise NotImplementedError

    @dbus_method()
    def get_capabilities(self) -> List[str]:
        """Returns notification daemon capabilities.

        List of capabilities:

        * "action-icons" - Supports using icons instead of text for \
            displaying actions.
        * "actions" - The server will provide the specified actions to the \
            user.
        * "body" - Supports body text.
        * "body-hyperlinks" - The server supports hyperlinks in \
            the notifications.
        * "body-images" - The server supports images in the notifications.
        * "body-markup" - Supports markup in the body text.
        * "icon-multi" - The server will render an animation of all \
            the frames in a given image array.
        * "icon-static" - Supports display of exactly 1 frame of any \
            given image array.
        * "persistence" - The server supports persistence of notifications.
        * "sound" - The server supports sounds on notifications.

        :returns: List of capabilities
        :rtype: List[str]
        """
        raise NotImplementedError

    @dbus_method()
    def get_server_information(self) -> Tuple[str, str, str, str]:
        """Returns notification server information.

        :returns: Tuple of server name, server vendor, version, notifications \
            specification version
        :rtype: Tuple[str, str, str, str]
        """
        raise NotImplementedError

    @dbus_method('susssasa{sv}i')
    def notify(
            self,
            app_name: str = '',
            replaces_id: int = 0,
            app_icon: str = '',
            summary: str = '',
            body: str = '',
            actions: List[str] = [],
            hints: Dict[str, Tuple[str, Any]] = {},
            expire_timeout: int = -1, ) -> int:
        """Create new notification.

        Only ``summary`` argument is required.

        :param str app_name: Application that sent notification. Optional.
        :param int replaces_id: Optional notification id to replace.
        :param str app_icon: Optional application icon name.
        :param str summary: Summary of notification.
        :param str body: Optional body of notification.
        :param List[str] actions: Optional list of actions presented to user. \
            List index becomes action id.
        :param Dict[str,Tuple[str,Any]] hints: Extra options such as sounds \
            that can be passed. See :py:meth:`create_hints`.
        :param int expire_timeout: Optional notification expiration timeout \
            in milliseconds. -1 means dependent on server setting, \
            0 is never expire.
        :returns: New notification id.
        :rtype: int
        """

        raise NotImplementedError

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
        """Create hints dictionary for :py:meth:`notify`.

        All parameters are optional.

        :param bool use_action_icons: When set, a server that has the \
            "action-icons" capability will attempt to interpret any action \
            identifier as a named icon.
        :param str category: The type of notification. (what types there are?)
        :param str desktop_entry_name: This specifies the name of the \
            desktop filename representing the calling program. \
            An example would be "rhythmbox" from "rhythmbox.desktop".
        :param Tuple[int,int,int,bool,int,int,Union[bytes,bytearray]] \
            image_data_tuple: This is a raw data image format which \
            describes the width, height, rowstride, has alpha, \
            bits per sample, channels and image data respectively.
        :param Union[str,Path] image_path: Path to notification image. \
            (alternative to desktop_entry_name)
        :param bool is_resident: When set the server will not automatically \
            remove the notification when an action has been invoked.
        :param Union[str,Path] sound_file_path: The path to a sound file \
            to play when the notification pops up.
        :param str sound_name: A themeable named sound to play. Similar to \
            icon-name, only for sounds. \
            An example would be "message-new-instant".
        :param bool suppress_sound: Causes the server to suppress playing \
            any sounds when this notification is displayed.
        :param bool is_transient: When set the server will treat \
            the notification as transient and by-pass the server's \
            persistence capability.
        :param Tuple[int,int] xy_pos: Specifies the X and Y location on the \
            screen that the notification should point to.
        :param int urgency: The urgency level. 0 low, 1 normal, 2 critical.
        """

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
