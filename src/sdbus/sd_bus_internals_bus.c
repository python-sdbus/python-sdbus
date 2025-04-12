// SPDX-License-Identifier: LGPL-2.1-or-later
/*
    Copyright (C) 2020, 2021 igo95862

    This file is part of python-sdbus

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
*/
#include <errno.h>
#include <poll.h>
#include <sys/timerfd.h>
#include <time.h>
#include "sd_bus_internals.h"

static void SdBus_dealloc(SdBusObject* self) {
        if (NULL != self->loop && NULL != self->bus_fd) {
                Py_XDECREF(PyObject_CallMethodObjArgs(self->loop, remove_reader_str, self->bus_fd, NULL));
                Py_XDECREF(PyObject_CallMethodObjArgs(self->loop, remove_writer_str, self->bus_fd, NULL));
        }
        if (NULL != self->timer_fd) {
                Py_XDECREF(PyObject_CallMethodObjArgs(self->loop, remove_reader_str, self->timer_fd, NULL));
                Py_DECREF(self->timer_fd);
                close(self->timer_fd_int);
        }
        sd_bus_unref(self->sd_bus_ref);
        Py_XDECREF(self->bus_fd);
        Py_XDECREF(self->loop);

        SD_BUS_DEALLOC_TAIL;
}

static int SdBus_init(SdBusObject* self, PyObject* Py_UNUSED(args), PyObject* Py_UNUSED(kwds)) {
        CALL_SD_BUS_CHECK_RETURN_NEG1(sd_bus_new(&(self->sd_bus_ref)));
        return 0;
}

#ifndef Py_LIMITED_API
static SdBusMessageObject* SdBus_new_method_call_message(SdBusObject* self, PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(4);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(0, PyUnicode_Check);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(1, PyUnicode_Check);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(2, PyUnicode_Check);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(3, PyUnicode_Check);

        const char* destination_bus_name = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]);
        const char* object_path = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[1]);
        const char* interface_name = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[2]);
        const char* member_name = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[3]);
#else
static SdBusMessageObject* SdBus_new_method_call_message(SdBusObject* self, PyObject* args) {
        const char* destination_bus_name = NULL;
        const char* object_path = NULL;
        const char* interface_name = NULL;
        const char* member_name = NULL;
        CALL_PYTHON_BOOL_CHECK(PyArg_ParseTuple(args, "ssss", &destination_bus_name, &object_path, &interface_name, &member_name, NULL));
#endif
        SdBusMessageObject* new_message_object CLEANUP_SD_BUS_MESSAGE =
            (SdBusMessageObject*)CALL_PYTHON_AND_CHECK(SD_BUS_PY_CLASS_DUNDER_NEW(SdBusMessage_class));

        CALL_SD_BUS_AND_CHECK(
            sd_bus_message_new_method_call(self->sd_bus_ref, &new_message_object->message_ref, destination_bus_name, object_path, interface_name, member_name));

        Py_INCREF(new_message_object);
        return new_message_object;
}

#ifndef Py_LIMITED_API
static SdBusMessageObject* SdBus_new_property_get_message(SdBusObject* self, PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(4);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(0, PyUnicode_Check);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(1, PyUnicode_Check);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(2, PyUnicode_Check);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(3, PyUnicode_Check);

        const char* destination_service_name = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]);
        const char* object_path = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[1]);
        const char* interface_name = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[2]);
        const char* property_name = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[3]);
#else
static SdBusMessageObject* SdBus_new_property_get_message(SdBusObject* self, PyObject* args) {
        const char* destination_service_name = NULL;
        const char* object_path = NULL;
        const char* interface_name = NULL;
        const char* property_name = NULL;
        CALL_PYTHON_BOOL_CHECK(PyArg_ParseTuple(args, "ssss", &destination_service_name, &object_path, &interface_name, &property_name, NULL));
#endif
        SdBusMessageObject* new_message_object CLEANUP_SD_BUS_MESSAGE =
            (SdBusMessageObject*)CALL_PYTHON_AND_CHECK(SD_BUS_PY_CLASS_DUNDER_NEW(SdBusMessage_class));
        CALL_SD_BUS_AND_CHECK(sd_bus_message_new_method_call(self->sd_bus_ref, &new_message_object->message_ref, destination_service_name, object_path,
                                                             "org.freedesktop.DBus.Properties", "Get"));

        // Add property_name
        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(new_message_object->message_ref, 's', interface_name));
        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(new_message_object->message_ref, 's', property_name));

        Py_INCREF(new_message_object);
        return new_message_object;
}

#ifndef Py_LIMITED_API
static SdBusMessageObject* SdBus_new_property_set_message(SdBusObject* self, PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(4);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(0, PyUnicode_Check);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(1, PyUnicode_Check);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(2, PyUnicode_Check);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(3, PyUnicode_Check);

        const char* destination_service_name = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]);
        const char* object_path = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[1]);
        const char* interface_name = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[2]);
        const char* property_name = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[3]);
#else
static SdBusMessageObject* SdBus_new_property_set_message(SdBusObject* self, PyObject* args) {
        const char* destination_service_name = NULL;
        const char* object_path = NULL;
        const char* interface_name = NULL;
        const char* property_name = NULL;
        CALL_PYTHON_BOOL_CHECK(PyArg_ParseTuple(args, "ssss", &destination_service_name, &object_path, &interface_name, &property_name, NULL));
#endif
        SdBusMessageObject* new_message_object CLEANUP_SD_BUS_MESSAGE =
            (SdBusMessageObject*)CALL_PYTHON_AND_CHECK(SD_BUS_PY_CLASS_DUNDER_NEW(SdBusMessage_class));
        CALL_SD_BUS_AND_CHECK(sd_bus_message_new_method_call(self->sd_bus_ref, &new_message_object->message_ref, destination_service_name, object_path,
                                                             "org.freedesktop.DBus.Properties", "Set"));

        // Add property_name
        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(new_message_object->message_ref, 's', interface_name));
        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(new_message_object->message_ref, 's', property_name));

        Py_INCREF(new_message_object);
        return new_message_object;
}

#ifndef Py_LIMITED_API
static SdBusMessageObject* SdBus_new_signal_message(SdBusObject* self, PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(3);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(0, PyUnicode_Check);  // Path
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(1, PyUnicode_Check);  // Interface
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(2, PyUnicode_Check);  // Member

        const char* object_path = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]);
        const char* interface_name = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[1]);
        const char* member_name = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[2]);
#else
static SdBusMessageObject* SdBus_new_signal_message(SdBusObject* self, PyObject* args) {
        char* object_path = NULL;
        const char* interface_name = NULL;
        const char* member_name = NULL;
        CALL_PYTHON_BOOL_CHECK(PyArg_ParseTuple(args, "sss", &object_path, &interface_name, &member_name, NULL));
#endif
        SdBusMessageObject* new_message_object CLEANUP_SD_BUS_MESSAGE =
            (SdBusMessageObject*)CALL_PYTHON_AND_CHECK(SD_BUS_PY_CLASS_DUNDER_NEW(SdBusMessage_class));

        CALL_SD_BUS_AND_CHECK(sd_bus_message_new_signal(self->sd_bus_ref, &new_message_object->message_ref, object_path, interface_name, member_name));

        Py_INCREF(new_message_object);
        return new_message_object;
}

static SdBusMessageObject* SdBus_call(SdBusObject* self, PyObject* arg) {
        SdBusMessageObject* call_message = NULL;
        CALL_PYTHON_BOOL_CHECK(PyArg_Parse(arg, "O!", SdBusMessage_class, &call_message, NULL));

        SdBusMessageObject* reply_message_object CLEANUP_SD_BUS_MESSAGE =
            (SdBusMessageObject*)CALL_PYTHON_AND_CHECK(SD_BUS_PY_CLASS_DUNDER_NEW(SdBusMessage_class));

        sd_bus_error error __attribute__((cleanup(sd_bus_error_free))) = SD_BUS_ERROR_NULL;

        int return_value = sd_bus_call(self->sd_bus_ref, call_message->message_ref, (uint64_t)0, &error, &reply_message_object->message_ref);

        if (sd_bus_error_get_errno(&error)) {
                PyObject* error_name_str CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyUnicode_FromString(error.name));
                PyObject* exception_to_raise = PyDict_GetItemWithError(dbus_error_to_exception_dict, error_name_str);

                if (PyErr_Occurred()) {
                        return NULL;
                }

                if (exception_to_raise == NULL) {
                        PyObject* exception_tuple CLEANUP_PY_OBJECT = Py_BuildValue("(ss)", error.name, error.message);
                        PyErr_SetObject(unmapped_error_exception, exception_tuple);
                        return NULL;
                } else {
                        PyErr_SetString(exception_to_raise, error.message);
                        return NULL;
                }
        }

        CALL_SD_BUS_AND_CHECK(return_value);

        Py_INCREF(reply_message_object);
        return reply_message_object;
}

int future_set_exception_from_message(PyObject* future, sd_bus_message* message) {
        const sd_bus_error* callback_error = sd_bus_message_get_error(message);

        PyObject* error_name_str CLEANUP_PY_OBJECT = CALL_PYTHON_CHECK_RETURN_NEG1(PyUnicode_FromString(callback_error->name));
        PyObject* error_message_str CLEANUP_PY_OBJECT = CALL_PYTHON_CHECK_RETURN_NEG1(PyUnicode_FromString(callback_error->message));

        PyObject* exception_to_raise = PyDict_GetItemWithError(dbus_error_to_exception_dict, error_name_str);

        PyObject* exception_occurred = PyErr_Occurred();
        if (exception_occurred) {
                Py_XDECREF(CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallMethodObjArgs(future, set_exception_str, exception_occurred, NULL)));
                return 0;
        }

        if (exception_to_raise) {
                PyObject* new_exception CLEANUP_PY_OBJECT =
                    CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallFunctionObjArgs(exception_to_raise, error_message_str, NULL));
                Py_XDECREF(CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallMethodObjArgs(future, set_exception_str, new_exception, NULL)));
        } else {
                PyObject* new_exception CLEANUP_PY_OBJECT =
                    CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallFunctionObjArgs(unmapped_error_exception, error_name_str, error_message_str, NULL));
                Py_XDECREF(CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallMethodObjArgs(future, set_exception_str, new_exception, NULL)));
        }

        return 0;
}

static PyObject* SdBus_get_fd(SdBusObject* self, PyObject* Py_UNUSED(args)) {
        int file_descriptor = CALL_SD_BUS_AND_CHECK(sd_bus_get_fd(self->sd_bus_ref));

        return PyLong_FromLong((long)file_descriptor);
}

static PyObject* SdBus_asyncio_update_fd_watchers(SdBusObject* self);

#define CHECK_ASYNCIO_WATCHERS ({ CALL_PYTHON_EXPECT_NONE(SdBus_asyncio_update_fd_watchers(self)); })

static PyObject* _get_or_bind_loop(SdBusObject* self) {
        if (NULL == self->loop) {
                self->loop = CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(asyncio_get_running_loop, NULL));
        }
        return self->loop;
}

static PyObject* SdBus_process(SdBusObject* self, PyObject* Py_UNUSED(args)) {
        int return_value = 1;
        while (return_value > 0) {
                return_value = sd_bus_process(self->sd_bus_ref, NULL);
                if (return_value < 0) {
                        if (-ECONNRESET == return_value) {
                                // Connection gracefully terminated
                                break;
                        } else {
                                // Error occurred processing sdbus
                                CALL_SD_BUS_AND_CHECK(return_value);
                                return NULL;
                        }
                }

                if (PyErr_Occurred()) {
                        return NULL;
                }
        }
        CHECK_ASYNCIO_WATCHERS;

        Py_RETURN_NONE;
}

int SdBus_async_callback(sd_bus_message* m,
                         void* userdata,  // Should be the asyncio.Future
                         sd_bus_error* Py_UNUSED(ret_error)) {
        sd_bus_message* reply_message __attribute__((cleanup(sd_bus_message_unrefp))) = sd_bus_message_ref(m);
        PyObject* py_future = userdata;
        PyObject* is_cancelled CLEANUP_PY_OBJECT = PyObject_CallMethod(py_future, "cancelled", "");
        if (Py_True == is_cancelled) {
                // A bit unpythonic but SdBus_process does not error out
                return 0;
        }

        if (!sd_bus_message_is_method_error(m, NULL)) {
                // Not Error, set Future result to new message object

                SdBusMessageObject* reply_message_object CLEANUP_SD_BUS_MESSAGE = (SdBusMessageObject*)SD_BUS_PY_CLASS_DUNDER_NEW(SdBusMessage_class);
                if (reply_message_object == NULL) {
                        return -1;
                }
                _SdBusMessage_set_messsage(reply_message_object, reply_message);
                PyObject* return_object CLEANUP_PY_OBJECT = PyObject_CallMethod(py_future, "set_result", "O", reply_message_object);
                if (return_object == NULL) {
                        return -1;
                }
        } else {
                // An Error, set exception
                if (future_set_exception_from_message(py_future, m) < 0) {
                        return -1;
                }
        }

        return 0;
}

static PyObject* SdBus_call_async(SdBusObject* self, PyObject* arg) {
        SdBusMessageObject* call_message = NULL;
        CALL_PYTHON_BOOL_CHECK(PyArg_Parse(arg, "O!", SdBusMessage_class, &call_message, NULL));

        PyObject* running_loop = CALL_PYTHON_AND_CHECK(_get_or_bind_loop(self));

        PyObject* new_future = CALL_PYTHON_AND_CHECK(PyObject_CallMethod(running_loop, "create_future", ""));

        SdBusSlotObject* new_slot_object CLEANUP_SD_BUS_SLOT = (SdBusSlotObject*)CALL_PYTHON_AND_CHECK(SD_BUS_PY_CLASS_DUNDER_NEW(SdBusSlot_class));

        CALL_SD_BUS_AND_CHECK(
            sd_bus_call_async(self->sd_bus_ref, &new_slot_object->slot_ref, call_message->message_ref, SdBus_async_callback, new_future, (uint64_t)0));

        if (PyObject_SetAttrString(new_future, "_sd_bus_py_slot", (PyObject*)new_slot_object) < 0) {
                return NULL;
        }
        CHECK_ASYNCIO_WATCHERS;
        return new_future;
}

#ifndef Py_LIMITED_API
static int _check_is_sdbus_interface(PyObject* type_to_check) {
        return PyType_IsSubtype(Py_TYPE(type_to_check), (PyTypeObject*)SdBusInterface_class);
}

static PyObject* SdBus_add_interface(SdBusObject* self, PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(3);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(0, _check_is_sdbus_interface);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(1, PyUnicode_Check);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(2, PyUnicode_Check);

        SdBusInterfaceObject* interface_object = (SdBusInterfaceObject*)args[0];
        const char* path_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[1]);
        const char* interface_name_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[2]);
#else
static PyObject* SdBus_add_interface(SdBusObject* self, PyObject* args) {
        SdBusInterfaceObject* interface_object = NULL;
        const char* path_char_ptr = NULL;
        const char* interface_name_char_ptr = NULL;
        CALL_PYTHON_BOOL_CHECK(PyArg_ParseTuple(args, "Oss", &interface_object, &path_char_ptr, &interface_name_char_ptr, NULL));
#endif
        PyObject* create_vtable_name CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyUnicode_FromString("_create_vtable"));

        Py_XDECREF(CALL_PYTHON_AND_CHECK(PyObject_CallMethodObjArgs((PyObject*)interface_object, create_vtable_name, NULL)));

        CALL_SD_BUS_AND_CHECK(sd_bus_add_object_vtable(self->sd_bus_ref, &interface_object->interface_slot->slot_ref, path_char_ptr, interface_name_char_ptr,
                                                       interface_object->vtable, interface_object));

        Py_RETURN_NONE;
}

int _SdBus_signal_callback(sd_bus_message* m, void* userdata, sd_bus_error* Py_UNUSED(ret_error)) {
        PyObject* signal_callback = userdata;

        PyObject* running_loop CLEANUP_PY_OBJECT = CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallFunctionObjArgs(asyncio_get_running_loop, NULL));

        SdBusMessageObject* new_message_object CLEANUP_SD_BUS_MESSAGE =
            (SdBusMessageObject*)CALL_PYTHON_CHECK_RETURN_NEG1(SD_BUS_PY_CLASS_DUNDER_NEW(SdBusMessage_class));
        _SdBusMessage_set_messsage(new_message_object, m);

        Py_XDECREF(CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallMethodObjArgs(running_loop, call_soon_str, signal_callback, new_message_object, NULL)));

        return 0;
}

int _SdBus_match_signal_instant_callback(sd_bus_message* m, void* userdata, sd_bus_error* Py_UNUSED(ret_error)) {
        PyObject* new_future = userdata;

        if (!sd_bus_message_is_method_error(m, NULL)) {
                SdBusSlotObject* slot_object CLEANUP_SD_BUS_SLOT =
                    (SdBusSlotObject*)CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_GetAttrString(new_future, "_sd_bus_slot"));

                Py_XDECREF(CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallMethodObjArgs(new_future, set_result_str, slot_object, NULL)));

                PyObject* signal_callback = CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_GetAttrString(new_future, "_sd_bus_signal_callback"));

                sd_bus_slot_set_userdata(slot_object->slot_ref, signal_callback);
                sd_bus_slot_set_destroy_callback(slot_object->slot_ref, (sd_bus_destroy_t)Py_DecRef);
        } else {
                if (future_set_exception_from_message(new_future, m) < 0) {
                        return -1;
                }
        }

        return 0;
}

#ifndef Py_LIMITED_API

static int _unicode_or_none(PyObject* some_object) {
        return (PyUnicode_Check(some_object) || (Py_None == some_object));
}

static PyObject* SdBus_match_signal_async(SdBusObject* self, PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(5);

        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(0, _unicode_or_none);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(1, _unicode_or_none);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(2, _unicode_or_none);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(3, _unicode_or_none);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(4, PyCallable_Check);

        const char* sender_service_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR_OPTIONAL(args[0]);
        const char* path_name_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR_OPTIONAL(args[1]);
        const char* interface_name_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR_OPTIONAL(args[2]);
        const char* member_name_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR_OPTIONAL(args[3]);
        PyObject* signal_callback = args[4];
#else
static PyObject* SdBus_match_signal_async(SdBusObject* self, PyObject* args) {
        const char* sender_service_char_ptr = NULL;
        const char* path_name_char_ptr = NULL;
        const char* interface_name_char_ptr = NULL;
        const char* member_name_char_ptr = NULL;
        PyObject* signal_callback = NULL;
        CALL_PYTHON_BOOL_CHECK(PyArg_ParseTuple(args, "zzzzO", &sender_service_char_ptr, &path_name_char_ptr, &interface_name_char_ptr, &member_name_char_ptr,
                                                &signal_callback, NULL));
#endif
        PyObject* running_loop = CALL_PYTHON_AND_CHECK(_get_or_bind_loop(self));
        PyObject* new_future CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_CallMethod(running_loop, "create_future", ""));

        SdBusSlotObject* new_slot CLEANUP_SD_BUS_SLOT = (SdBusSlotObject*)CALL_PYTHON_AND_CHECK(SD_BUS_PY_CLASS_DUNDER_NEW(SdBusSlot_class));

        // Bind lifetime of the slot to the Future
        CALL_PYTHON_INT_CHECK(PyObject_SetAttrString(new_future, "_sd_bus_slot", (PyObject*)new_slot));
        CALL_PYTHON_INT_CHECK(PyObject_SetAttrString(new_future, "_sd_bus_signal_callback", signal_callback));

        CALL_SD_BUS_AND_CHECK(sd_bus_match_signal_async(self->sd_bus_ref, &new_slot->slot_ref, sender_service_char_ptr, path_name_char_ptr,
                                                        interface_name_char_ptr, member_name_char_ptr, _SdBus_signal_callback,
                                                        _SdBus_match_signal_instant_callback, new_future));

        CHECK_ASYNCIO_WATCHERS;
        Py_INCREF(new_future);
        return new_future;
}

int SdBus_request_name_callback(sd_bus_message* m,
                                void* userdata,  // Should be the asyncio.Future
                                sd_bus_error* Py_UNUSED(ret_error)) {
        PyObject* py_future = userdata;
        PyObject* is_cancelled CLEANUP_PY_OBJECT = PyObject_CallMethod(py_future, "cancelled", "");
        if (Py_True == is_cancelled) {
                // A bit unpythonic but SdBus_process does not error out
                return 0;
        }

        if (!sd_bus_message_is_method_error(m, NULL)) {
                uint32_t request_name_result = 0;
                CALL_SD_BUS_CHECK_RETURN_NEG1(sd_bus_message_read_basic(m, 'u', &request_name_result));
                if (1 == request_name_result) {
                        // Successfully acquired the name
                        Py_XDECREF(CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallMethod(py_future, "set_result", "O", Py_None)));
                        return 0;
                }

                PyObject* exception_to_raise CLEANUP_PY_OBJECT = NULL;
                switch (request_name_result) {
                        case 2:
                                exception_to_raise = CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallFunctionObjArgs(exception_request_name_in_queue, NULL));
                                break;
                        case 3:
                                exception_to_raise = CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallFunctionObjArgs(exception_request_name_exists, NULL));
                                break;
                        case 4:
                                exception_to_raise = CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallFunctionObjArgs(exception_request_name_already_owner, NULL));
                                break;
                        default:
                                exception_to_raise = CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallFunctionObjArgs(exception_request_name, NULL));
                                break;
                }
                Py_XDECREF(CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallMethod(py_future, "set_exception", "O", exception_to_raise)));
                return -1;
        } else {
                // An Error, set exception
                if (future_set_exception_from_message(py_future, m) < 0) {
                        return -1;
                }
        }

        return 0;
}

#ifndef Py_LIMITED_API
static PyObject* SdBus_request_name_async(SdBusObject* self, PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(2);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(0, PyUnicode_Check);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(1, PyLong_Check);

        const char* service_name_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]);
        uint64_t flags = PyLong_AsUnsignedLongLong(args[1]);
        if (PyErr_Occurred()) {
                return NULL;
        }
#else
static PyObject* SdBus_request_name_async(SdBusObject* self, PyObject* args) {
        const char* service_name_char_ptr = NULL;
        unsigned long long flags_long_long = 0;
        CALL_PYTHON_BOOL_CHECK(PyArg_ParseTuple(args, "sK", &service_name_char_ptr, &flags_long_long, NULL));
        uint64_t flags = (uint64_t)flags_long_long;
#endif
        PyObject* running_loop = CALL_PYTHON_AND_CHECK(_get_or_bind_loop(self));
        PyObject* new_future = CALL_PYTHON_AND_CHECK(PyObject_CallMethod(running_loop, "create_future", ""));
        SdBusSlotObject* new_slot_object CLEANUP_SD_BUS_SLOT = (SdBusSlotObject*)CALL_PYTHON_AND_CHECK(SD_BUS_PY_CLASS_DUNDER_NEW(SdBusSlot_class));

        CALL_SD_BUS_AND_CHECK(
            sd_bus_request_name_async(self->sd_bus_ref, &new_slot_object->slot_ref, service_name_char_ptr, flags, SdBus_request_name_callback, new_future));

        CALL_PYTHON_INT_CHECK(PyObject_SetAttrString(new_future, "_sd_bus_py_slot", (PyObject*)new_slot_object));
        CHECK_ASYNCIO_WATCHERS;
        return new_future;
}

#ifndef Py_LIMITED_API
static PyObject* SdBus_request_name(SdBusObject* self, PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(2);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(0, PyUnicode_Check);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(1, PyLong_Check);

        const char* service_name_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]);
        uint64_t flags = PyLong_AsUnsignedLongLong(args[1]);
        if (PyErr_Occurred()) {
                return NULL;
        }
#else
static PyObject* SdBus_request_name(SdBusObject* self, PyObject* args) {
        const char* service_name_char_ptr = NULL;
        unsigned long long flags_long_long = 0;
        CALL_PYTHON_BOOL_CHECK(PyArg_ParseTuple(args, "sK", &service_name_char_ptr, &flags_long_long, NULL));
        uint64_t flags = (uint64_t)flags_long_long;
#endif
        int request_name_return_code = sd_bus_request_name(self->sd_bus_ref, service_name_char_ptr, flags);
        switch (request_name_return_code) {
                case -EEXIST:
                        return PyErr_Format(exception_request_name_exists, "Name \"%s\" already owned.", service_name_char_ptr, NULL);
                        break;
                case -EALREADY:
                        return PyErr_Format(exception_request_name_already_owner, "Already own name \"%s\".", service_name_char_ptr, NULL);
                        break;
                case 0:
                        return PyErr_Format(exception_request_name_in_queue, "Queued up to acquire name \"%s\".", service_name_char_ptr, NULL);
                        break;
                case 1:
                        Py_RETURN_NONE;
                        break;
                default:
                        CALL_SD_BUS_AND_CHECK(request_name_return_code);
                        break;
        }
        Py_UNREACHABLE();
}

#ifndef Py_LIMITED_API
static SdBusSlotObject* SdBus_add_object_manager(SdBusObject* self, PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(1);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(0, PyUnicode_Check);

        const char* object_manager_path = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]);
#else
static SdBusSlotObject* SdBus_add_object_manager(SdBusObject* self, PyObject* args) {
        const char* object_manager_path = NULL;
        CALL_PYTHON_BOOL_CHECK(PyArg_ParseTuple(args, "s", &object_manager_path, NULL));
#endif
        SdBusSlotObject* new_slot_object CLEANUP_SD_BUS_SLOT = (SdBusSlotObject*)CALL_PYTHON_AND_CHECK(SD_BUS_PY_CLASS_DUNDER_NEW(SdBusSlot_class));

        CALL_SD_BUS_AND_CHECK(sd_bus_add_object_manager(self->sd_bus_ref, &new_slot_object->slot_ref, object_manager_path));

        Py_INCREF(new_slot_object);
        return new_slot_object;
}

#ifndef Py_LIMITED_API
static PyObject* SdBus_emit_object_added(SdBusObject* self, PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(1);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(0, PyUnicode_Check);

        const char* added_object_path = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]);
#else
static PyObject* SdBus_emit_object_added(SdBusObject* self, PyObject* args) {
        const char* added_object_path = NULL;
        CALL_PYTHON_BOOL_CHECK(PyArg_ParseTuple(args, "s", &added_object_path, NULL));
#endif
        CALL_SD_BUS_AND_CHECK(sd_bus_emit_object_added(self->sd_bus_ref, added_object_path));

        Py_RETURN_NONE;
}

#ifndef Py_LIMITED_API
static PyObject* SdBus_emit_object_removed(SdBusObject* self, PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(1);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(0, PyUnicode_Check);

        const char* removed_object_path = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]);
#else
static PyObject* SdBus_emit_object_removed(SdBusObject* self, PyObject* args) {
        const char* removed_object_path = NULL;
        CALL_PYTHON_BOOL_CHECK(PyArg_ParseTuple(args, "s", &removed_object_path, NULL));
#endif
        CALL_SD_BUS_AND_CHECK(sd_bus_emit_object_removed(self->sd_bus_ref, removed_object_path));

        Py_RETURN_NONE;
}

static PyObject* SdBus_close(SdBusObject* self, PyObject* Py_UNUSED(args)) {
        sd_bus_close(self->sd_bus_ref);
        if (NULL != self->loop && NULL != self->bus_fd) {
                Py_XDECREF(CALL_PYTHON_AND_CHECK(PyObject_CallMethodObjArgs(self->loop, remove_reader_str, self->bus_fd, NULL)));
                Py_XDECREF(CALL_PYTHON_AND_CHECK(PyObject_CallMethodObjArgs(self->loop, remove_writer_str, self->bus_fd, NULL)));
        }
        if (NULL != self->timer_fd) {
                Py_XDECREF(PyObject_CallMethodObjArgs(self->loop, remove_reader_str, self->timer_fd, NULL));
                // TODO: Close timerfd
        }
        Py_RETURN_NONE;
}

static PyObject* SdBus_start(SdBusObject* self, PyObject* Py_UNUSED(args)) {
        CALL_SD_BUS_AND_CHECK(sd_bus_start(self->sd_bus_ref));
        Py_RETURN_NONE;
}

static inline int sd_bus_get_events_zero_on_closed(SdBusObject* self) {
        int events = sd_bus_get_events(self->sd_bus_ref);
        if (-ENOTCONN == events) {
                return 0;
        }
        return events;
};

static inline int sd_bus_get_timeout_uint_max_on_closed(SdBusObject* self, uint64_t* timeout_usec) {
        int r = sd_bus_get_timeout(self->sd_bus_ref, timeout_usec);
        if (-ENOTCONN == r) {
                *timeout_usec = UINT64_MAX;
                return 0;
        }
        return r;
}

static PyObject* SdBus_asyncio_update_fd_watchers(SdBusObject* self) {
        PyObject* running_loop = CALL_PYTHON_AND_CHECK(_get_or_bind_loop(self));
        PyObject* drive_method CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_GetAttrString((PyObject*)self, "process"));

        if (NULL == self->timer_fd) {
                self->timer_fd_int = CALL_SD_BUS_AND_CHECK(timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK | TFD_CLOEXEC));
                if (self->timer_fd_int < 0) {
                        PyErr_SetFromErrno(PyExc_OSError);
                }
                PyObject* timer_fd CLEANUP_PY_OBJECT = PyLong_FromLong((int)self->timer_fd_int);
                Py_XDECREF(CALL_PYTHON_AND_CHECK(PyObject_CallMethodObjArgs(running_loop, add_reader_str, timer_fd, drive_method, NULL)));
                Py_INCREF(timer_fd);
                self->timer_fd = timer_fd;
        }

        uint64_t timeout_usec = UINT64_MAX;
        CALL_SD_BUS_AND_CHECK(sd_bus_get_timeout_uint_max_on_closed(self, &timeout_usec));

        struct itimerspec bus_timer = {0};
        if (timeout_usec == UINT64_MAX) {
                // Setting bus_timer to zero disarms timer.
        } else if (timeout_usec != 0) {
                bus_timer.it_value.tv_sec = timeout_usec / 1000000;
                bus_timer.it_value.tv_nsec = (timeout_usec % 1000000) * 1000;
        } else if (timeout_usec == 0) {
                Py_XDECREF(CALL_PYTHON_AND_CHECK(PyObject_CallMethodObjArgs(running_loop, call_soon_str, drive_method, NULL)));
        }

        CALL_SD_BUS_AND_CHECK(timerfd_settime(self->timer_fd_int, TFD_TIMER_ABSTIME, &bus_timer, NULL));

        int events_to_watch = CALL_SD_BUS_AND_CHECK(sd_bus_get_events_zero_on_closed(self));
        if (events_to_watch == self->asyncio_watchers_last_state) {
                // Do not update the watchers because state is the same
                Py_RETURN_NONE;
        } else {
                self->asyncio_watchers_last_state = events_to_watch;
        }

        if (NULL == self->bus_fd) {
                self->bus_fd = CALL_PYTHON_AND_CHECK(SdBus_get_fd(self, NULL));
        }

        if (events_to_watch & POLLIN) {
                Py_XDECREF(CALL_PYTHON_AND_CHECK(PyObject_CallMethodObjArgs(running_loop, add_reader_str, self->bus_fd, drive_method, NULL)));
        } else {
                Py_XDECREF(CALL_PYTHON_AND_CHECK(PyObject_CallMethodObjArgs(running_loop, remove_reader_str, self->bus_fd, NULL)));
        }

        if (events_to_watch & POLLOUT) {
                Py_XDECREF(CALL_PYTHON_AND_CHECK(PyObject_CallMethodObjArgs(running_loop, add_writer_str, self->bus_fd, drive_method, NULL)));
        } else {
                Py_XDECREF(CALL_PYTHON_AND_CHECK(PyObject_CallMethodObjArgs(running_loop, remove_writer_str, self->bus_fd, NULL)));
        }

        Py_RETURN_NONE;
}

static PyMethodDef SdBus_methods[] = {
    {"call", (PyCFunction)SdBus_call, METH_O, PyDoc_STR("Send message and block until the reply.")},
    {"call_async", (PyCFunction)SdBus_call_async, METH_O, PyDoc_STR("Async send message, returns awaitable future.")},
    {"process", (PyCFunction)SdBus_process, METH_NOARGS, PyDoc_STR("Process pending IO work.")},
    {"get_fd", (SD_BUS_PY_FUNC_TYPE)SdBus_get_fd, SD_BUS_PY_METH, PyDoc_STR("Get file descriptor to poll on.")},
    {"new_method_call_message", (SD_BUS_PY_FUNC_TYPE)SdBus_new_method_call_message, SD_BUS_PY_METH, PyDoc_STR("Create new empty method call message.")},
    {"new_property_get_message", (SD_BUS_PY_FUNC_TYPE)SdBus_new_property_get_message, SD_BUS_PY_METH, PyDoc_STR("Create new empty property get message.")},
    {"new_property_set_message", (SD_BUS_PY_FUNC_TYPE)SdBus_new_property_set_message, SD_BUS_PY_METH, PyDoc_STR("Create new empty property set message.")},
    {"new_signal_message", (SD_BUS_PY_FUNC_TYPE)SdBus_new_signal_message, SD_BUS_PY_METH, PyDoc_STR("Create new empty signal message.")},
    {"add_interface", (SD_BUS_PY_FUNC_TYPE)SdBus_add_interface, SD_BUS_PY_METH, PyDoc_STR("Add interface to the bus.")},
    {"match_signal_async", (SD_BUS_PY_FUNC_TYPE)SdBus_match_signal_async, SD_BUS_PY_METH,
     PyDoc_STR("Register signal callback asynchronously. Returns a Future that returns a SdBusSlot.")},
    {"request_name_async", (SD_BUS_PY_FUNC_TYPE)SdBus_request_name_async, SD_BUS_PY_METH, PyDoc_STR("Request D-Bus name async.")},
    {"request_name", (SD_BUS_PY_FUNC_TYPE)SdBus_request_name, SD_BUS_PY_METH, PyDoc_STR("Request D-Bus name blocking.")},
    {"add_object_manager", (SD_BUS_PY_FUNC_TYPE)SdBus_add_object_manager, SD_BUS_PY_METH, PyDoc_STR("Add object manager at the path.")},
    {"emit_object_added", (SD_BUS_PY_FUNC_TYPE)SdBus_emit_object_added, SD_BUS_PY_METH, PyDoc_STR("Emit signal that object was added.")},
    {"emit_object_removed", (SD_BUS_PY_FUNC_TYPE)SdBus_emit_object_removed, SD_BUS_PY_METH, PyDoc_STR("Emit signal that object was removed.")},
    {"close", (PyCFunction)SdBus_close, METH_NOARGS, PyDoc_STR("Close connection.")},
    {"start", (PyCFunction)SdBus_start, METH_NOARGS, PyDoc_STR("Start connection.")},
    {NULL, NULL, 0, NULL},
};

static PyObject* SdBus_address_getter(SdBusObject* self, void* Py_UNUSED(closure)) {
        const char* bus_address = NULL;
        int get_address_result = sd_bus_get_address(self->sd_bus_ref, &bus_address);
        if (-ENODATA == get_address_result) {
                // Bus has not been set yet
                Py_RETURN_NONE;
        } else {
                CALL_SD_BUS_AND_CHECK(get_address_result);
        }
        return PyUnicode_FromString(bus_address);
}

static PyObject* SdBus_method_call_timeout_usec_getter(SdBusObject* self, void* Py_UNUSED(closure)) {
        uint64_t timeout_usec = 0;
        CALL_SD_BUS_AND_CHECK(sd_bus_get_method_call_timeout(self->sd_bus_ref, &timeout_usec));

        return PyLong_FromUnsignedLongLong((unsigned long long)timeout_usec);
}

static int SdBus_method_call_timeout_usec_setter(SdBusObject* self, PyObject* new_value, void* Py_UNUSED(closure)) {
        if (NULL == new_value) {
                PyErr_SetString(PyExc_ValueError, "Cannot delete method call timeout value");
                return -1;
        }

        unsigned long long new_timeout_usec = PyLong_AsUnsignedLongLong(new_value);
        if ((((unsigned long long)-1) == new_timeout_usec) && (PyErr_Occurred() != NULL)) {
                return -1;
        }
        CALL_SD_BUS_CHECK_RETURN_NEG1(sd_bus_set_method_call_timeout(self->sd_bus_ref, (uint64_t)new_timeout_usec));
        return 0;
}

static PyGetSetDef SdBus_properies[] = {
    {"address", (getter)SdBus_address_getter, NULL, PyDoc_STR("Bus address."), NULL},
    {"method_call_timeout_usec", (getter)SdBus_method_call_timeout_usec_getter, (setter)SdBus_method_call_timeout_usec_setter,
     PyDoc_STR("D-Bus call timeout in microseconds."), NULL},
    {0},
};

PyType_Spec SdBusType = {
    .name = "sd_bus_internals.SdBus",
    .basicsize = sizeof(SdBusObject),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT,
    .slots =
        (PyType_Slot[]){
            {Py_tp_new, PyType_GenericNew},
            {Py_tp_init, (initproc)SdBus_init},
            {Py_tp_dealloc, (destructor)SdBus_dealloc},
            {Py_tp_methods, SdBus_methods},
            {Py_tp_getset, SdBus_properies},
            {0, NULL},
        },
};
