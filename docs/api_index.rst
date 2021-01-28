API Index
============================

.. py:module:: sdbus

Common:
++++++++++++++++++++++++++

:py:func:`get_default_bus`

:py:func:`request_default_bus_name_async`

:py:func:`set_default_bus`

:py:func:`decode_object_path`

:py:func:`encode_object_path`

:py:func:`sd_bus_open_system`

:py:func:`sd_bus_open_user`

:py:obj:`DbusDeprecatedFlag`

:py:obj:`DbusHiddenFlag`

:py:obj:`DbusNoReplyFlag`

:py:obj:`DbusPropertyConstFlag`

:py:obj:`DbusPropertyEmitsChangeFlag`

:py:obj:`DbusPropertyEmitsInvalidationFlag`

:py:obj:`DbusPropertyExplicitFlag`

:py:obj:`DbusSensitiveFlag`

:py:obj:`DbusUnprivilegedFlag`

Asyncio:
++++++++++++++++++++++++++

:py:class:`DbusInterfaceCommonAsync`

:py:func:`dbus_method_async`

:py:func:`dbus_method_async_override`

:py:func:`dbus_property_async`

:py:func:`dbus_property_async_override`

:py:func:`dbus_signal_async`

Blocking:
++++++++++++++++++++++++++

:py:class:`DbusInterfaceCommon`

:py:func:`dbus_method`

:py:func:`dbus_property`

Exceptions:
++++++++++++++++++++++++++

:py:exc:`DbusAccessDeniedError`

:py:exc:`DbusAddressInUseError`

:py:exc:`DbusAuthFailedError`

:py:exc:`DbusBadAddressError`

:py:exc:`DbusDisconnectedError`

:py:exc:`DbusFailedError`

:py:exc:`DbusFileExistsError`

:py:exc:`DbusFileNotFoundError`

:py:exc:`DbusInconsistentMessageError`

:py:exc:`DbusInteractiveAuthorizationRequiredError`

:py:exc:`DbusInvalidArgsError`

:py:exc:`DbusInvalidFileContentError`

:py:exc:`DbusInvalidSignatureError`

:py:exc:`DbusIOError`

:py:exc:`DbusLimitsExceededError`

:py:exc:`DbusMatchRuleInvalidError`

:py:exc:`DbusMatchRuleNotFound`

:py:exc:`DbusNameHasNoOwnerError`

:py:exc:`DbusNoMemoryError`

:py:exc:`DbusNoNetworkError`

:py:exc:`DbusNoReplyError`

:py:exc:`DbusNoServerError`

:py:exc:`DbusNotSupportedError`

:py:exc:`DbusPropertyReadOnlyError`

:py:exc:`DbusServiceUnknownError`

:py:exc:`DbusTimeoutError`

:py:exc:`DbusUnixProcessIdUnknownError`

:py:exc:`DbusUnknownInterfaceError`

:py:exc:`DbusUnknownMethodError`

:py:exc:`DbusUnknownObjectError`

:py:exc:`DbusUnknownPropertyError`

:py:exc:`SdBusBaseError`

:py:exc:`SdBusLibraryError`

:py:exc:`SdBusUnmappedMessageError`