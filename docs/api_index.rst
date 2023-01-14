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

:py:exc:`exceptions.DbusAccessDeniedError`

:py:exc:`exceptions.DbusAccessDeniedError`

:py:exc:`exceptions.DbusAddressInUseError`

:py:exc:`exceptions.DbusAuthFailedError`

:py:exc:`exceptions.DbusBadAddressError`

:py:exc:`exceptions.DbusDisconnectedError`

:py:exc:`exceptions.DbusFailedError`

:py:exc:`exceptions.DbusFileExistsError`

:py:exc:`exceptions.DbusFileNotFoundError`

:py:exc:`exceptions.DbusInconsistentMessageError`

:py:exc:`exceptions.DbusInteractiveAuthorizationRequiredError`

:py:exc:`exceptions.DbusInvalidArgsError`

:py:exc:`exceptions.DbusInvalidFileContentError`

:py:exc:`exceptions.DbusInvalidSignatureError`

:py:exc:`exceptions.DbusIOError`

:py:exc:`exceptions.DbusLimitsExceededError`

:py:exc:`exceptions.DbusMatchRuleInvalidError`

:py:exc:`exceptions.DbusMatchRuleNotFound`

:py:exc:`exceptions.DbusNameHasNoOwnerError`

:py:exc:`exceptions.DbusNoMemoryError`

:py:exc:`exceptions.DbusNoNetworkError`

:py:exc:`exceptions.DbusNoReplyError`

:py:exc:`exceptions.DbusNoServerError`

:py:exc:`exceptions.DbusNotSupportedError`

:py:exc:`exceptions.DbusPropertyReadOnlyError`

:py:exc:`exceptions.DbusServiceUnknownError`

:py:exc:`exceptions.DbusTimeoutError`

:py:exc:`exceptions.DbusUnixProcessIdUnknownError`

:py:exc:`exceptions.DbusUnknownInterfaceError`

:py:exc:`exceptions.DbusUnknownMethodError`

:py:exc:`exceptions.DbusUnknownObjectError`

:py:exc:`exceptions.DbusUnknownPropertyError`

:py:exc:`exceptions.SdBusBaseError`

:py:exc:`exceptions.SdBusLibraryError`

:py:exc:`exceptions.SdBusUnmappedMessageError`

:py:func:`exceptions.map_exception_to_dbus_error`

:py:exc:`exceptions.SdBusRequestNameError`

:py:exc:`exceptions.SdBusRequestNameInQueueError`

:py:exc:`exceptions.SdBusRequestNameExistsError`

:py:exc:`exceptions.SdBusRequestNameAlreadyOwnerError`
