
Freedesktop Notifications
===================================

Desktop notifications. 

``FreedesktopNotifications`` class automatically connects.

``NotificationsInterface`` is the interface definition class if you want
to implement your own notification daemon.

See `notification specifications <https://specifications.freedesktop.org/notification-spec/latest/ar01s09.html>`_
for more details.

.. py:class:: FreedesktopNotifications

    .. py:method:: __init__([bus])

        Dbus interface object path and service name is
        predetermined.
        (at ``'org.freedesktop.Notifications'``,
        ``'/org/freedesktop/Notifications'``)

        :param SdBus bus:
            Optional dbus connection.
            If not passed the default dbus will be used.

    .. py:method:: close_notification(notif_id)
        :async:

        Close notification by id.

        :param int notif_id: Notification id to close.

    .. py:method:: get_capabilities()
        :async:

        Returns notification daemon capabilities.

        List of capabilities:

        * "action-icons" - Supports using icons instead of text for displaying actions.
        * "actions" - The server will provide the specified actions to the user.
        * "body" - Supports body text.
        * "body-hyperlinks" - The server supports hyperlinks in the notifications.
        * "body-images" - The server supports images in the notifications.
        * "body-markup" - Supports markup in the body text.
        * "icon-multi" - The server will render an animation of all the frames in a given image array.
        * "icon-static" - Supports display of exactly 1 frame of any given image array.
        * "persistence" - The server supports persistence of notifications.
        * "sound" - The server supports sounds on notifications.

        :returns: List of capabilities
        :rtype: List[str]

    .. py:method:: get_server_information()
        :async:

        Returns notification server information.

        :returns: Tuple of server name, server vendor, version, notifications specification version
        :rtype: Tuple[str, str, str, str]

    .. py:method:: notify([app_name, [replaces_id, [app_icon, [summary, [body, [actions, [hints, [expire_timeout]]]]]]]])
        :async:

        Create new notification.

        Only ``summary`` argument is required.

        :param str app_name: Application that sent notification. Optional.
        :param int replaces_id: Optional notification id to replace.
        :param str app_icon: Optional application icon name.
        :param str summary: Summary of notification.
        :param str body: Optional body of notification.
        :param List[str] actions: Optional list of actions presented to user. List index becomes action id.
        :param Dict[str,Tuple[str,Any]] hints: Extra options such as sounds that can be passed. See :py:meth:`create_hints`.
        :param int expire_timeout: Optional notification expiration timeout in milliseconds. -1 means dependent on server setting, 0 is never expire.
        :returns: New notification id.
        :rtype: int

    .. py:method:: create_hints()

        Create hints dictionary for :py:meth:`notify`.

        All parameters are optional.

        :param bool use_action_icons: When set, a server that has the "action-icons" capability will attempt to interpret any action identifier as a named icon.
        :param str category: The type of notification. (what types there are?)
        :param str desktop_entry_name: This specifies the name of the desktop filename representing the calling program. An example would be "rhythmbox" from "rhythmbox.desktop".
        :param Tuple[int,int,int,bool,int,int,Union[bytes,bytearray]] image_data_tuple: This is a raw data image format which describes the width, height, rowstride, has alpha, bits per sample, channels and image data respectively.
        :param Union[str,Path] image_path: Path to notification image. (alternative to desktop_entry_name)
        :param bool is_resident: When set the server will not automatically remove the notification when an action has been invoked.
        :param Union[str,Path] sound_file_path: The path to a sound file to play when the notification pops up.
        :param str sound_name: A themeable named sound to play. Similar to icon-name, only for sounds. An example would be "message-new-instant".
        :param bool suppress_sound: Causes the server to suppress playing any sounds when this notification is displayed.
        :param bool is_transient: When set the server will treat the notification as transient and by-pass the server's persistence capability.
        :param Tuple[int,int] xy_pos: Specifies the X and Y location on the screen that the notification should point to.
        :param int urgency: The urgency level. (what urgency levels there are?)

    .. py:attribute:: action_invoked
        :type: Tuple[int, int]

        Signal when user invokes one of the actions specified.

        First element of tuple is notification id.

        Second element is the index of the action invoked. Matches the index of passed list of actions.

    .. py:attribute:: notification_closed
        :type: Tuple[int, int]

        Signal when notification is closed.

        First element of the tuple is notification id.

        Second element is the reason which can be:

        * 1 - notification expired
        * 2 - notification was dismissed by user
        * 3 - notification was closed by call to :py:meth:`close_notification`
        * 4 - undefined/reserved reasons.
