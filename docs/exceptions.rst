Exceptions
========================

Error name bound exceptions
+++++++++++++++++++++++++++++++

These exceptions are bound to specific dbus error names. For example, 
:py:exc:`DbusFailedError` is bound to `org.freedesktop.DBus.Error.Failed`
error name.

This means if the remote object sends an error message with this error name
the Python will receive this exception.

When raised in a method callback an error message will be sent
back to caller.

See `list of error exceptions`_.

New error bound exceptions
+++++++++++++++++++++++++++++++

If you want to create a new error bound exception you should subclass
it from :py:exc:`DbusFailedError` and provide a **unique** ``dbus_error_name``
attribute in the exception body definition.

Example: ::

    class DbusExampleError(DbusFailedError):
        dbus_error_name = 'org.example.Error'


If ``dbus_error_name`` is not unique the :py:exc:`ValueError` will be raised.

Defining an exception will automatically bind incoming error message to this
new exception.

Existing exceptions can be manually binded using :py:func:`map_exception_to_dbus_error`
function.

Python built-in exceptions
+++++++++++++++++++++++++++

All Python built-in exceptions are mapped to D-Bus errors.

The D-Bus error name is created by appending ``org.python.Error.``
to the exception name.

For example, ``AssertionError`` is bound
to ``org.python.Error.AssertionError`` name.

Functions
+++++++++

.. py:function:: map_exception_to_dbus_error(exception, dbus_error_name)

    Map exception to a D-bus error. Error name must be unique.

    :param Type[Exception] exception: Exception to bind.
    :param str dbus_error_name: D-Bus error name to bind to.


Other exceptions
+++++++++++++++++++++++++

.. py:exception:: SdBusBaseError

    Base exceptions for all exceptions defined in sdbus.

.. py:exception:: SdBusUnmappedMessageError

    Message error that is unmapped.

    The exceptions argument is a tuple of
    error name and error message. 

.. py:exception:: SdBusLibraryError

    sd-bus library returned error.

    Exception message contains line number and the error name.


.. _list of error exceptions:

Error name exception list
++++++++++++++++++++++++++++++

.. py:exception:: DbusFailedError

    Generic failure exception.

    Recommended to subclass to create a new exception.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.Failed

.. py:exception:: DbusNoMemoryError

    Remote object is out of memory.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.NoMemory

.. py:exception:: DbusServiceUnknownError

    No service with such name exists.

    Probably should only be raised by bus daemon.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.ServiceUnknown

.. py:exception:: DbusNameHasNoOwnerError

    No process owns the name you called.

    Probably should only be raised by bus daemon.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.NameHasNoOwner

.. py:exception:: DbusNoReplyError

    Timeout on reply.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.NoReply

.. py:exception:: DbusIOError

    Input/Output error.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.IOError

.. py:exception:: DbusBadAddressError

    Bad address.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.BadAddress

.. py:exception:: DbusNotSupportedError

    Something is unsupported on this platform.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.NotSupported

.. py:exception:: DbusLimitsExceededError

    Some resource was exhausted. (for example, file descriptors)

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.LimitsExceeded

.. py:exception:: DbusAccessDeniedError

    Caller does not have enough privileges.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.AccessDenied

.. py:exception:: DbusAuthFailedError

    Authentication failed.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.AuthFailed

.. py:exception:: DbusNoServerError

    Unable to connect to bus.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.NoServer

.. py:exception:: DbusTimeoutError

    Socket timeout.

    This is different from :py:exc:`DbusNoReplyError` as here the
    connection to bus timeout not the remote object not replying.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.Timeout

.. py:exception:: DbusNoNetworkError

    No network access.

    Encountered you use Dbus over TCP or SSH.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.NoNetwork

.. py:exception:: DbusAddressInUseError

    Address in use.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.AddressInUse

.. py:exception:: DbusDisconnectedError

    Disconnected from bus.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.Disconnected

.. py:exception:: DbusInvalidArgsError

    Method call args are invalid.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.InvalidArgs

.. py:exception:: DbusFileNotFoundError

    File not found.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.FileNotFound

.. py:exception:: DbusFileExistsError

    Generic failure exception.

    Recommended to subclass to create a new exception.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.FileExists

.. py:exception:: DbusUnknownMethodError

    Unknown dbus method.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.UnknownMethod

.. py:exception:: DbusUnknownObjectError

    Unknown dbus object.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.UnknownObject

.. py:exception:: DbusUnknownInterfaceError

    Unknown dbus interface.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.UnknownInterface

.. py:exception:: DbusUnknownPropertyError

    Unknown dbus property.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.UnknownProperty

.. py:exception:: DbusPropertyReadOnlyError

    Dbus property is read only.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.PropertyReadOnly

.. py:exception:: DbusUnixProcessIdUnknownError

    PID does not exists.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.UnixProcessIdUnknown

.. py:exception:: DbusInvalidSignatureError

    Invalid dbus type signature.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.InvalidSignature

.. py:exception:: DbusInvalidFileContentError

    Invalid file content.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.InvalidFileContent

.. py:exception:: DbusInconsistentMessageError

    Dbus message is malformed.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.InconsistentMessage

.. py:exception:: DbusMatchRuleNotFound

    Match rule does not exist.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.MatchRuleNotFound

.. py:exception:: DbusMatchRuleInvalidError

    Match rule is invalid.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.MatchRuleInvalid

.. py:exception:: DbusInteractiveAuthorizationRequiredError

    Requires interactive authorization.

    .. py:attribute:: dbus_error_name
        :type: str
        :value: org.freedesktop.DBus.Error.InteractiveAuthorizationRequired
