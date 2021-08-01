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
#include "sd_bus_internals.h"

static void SdBus_dealloc(SdBusObject* self) {
        sd_bus_unref(self->sd_bus_ref);
        Py_XDECREF(self->reader_fd);

        SD_BUS_DEALLOC_TAIL;
}

static int SdBus_init(SdBusObject* self, PyObject* Py_UNUSED(args), PyObject* Py_UNUSED(kwds)) {
        self->sd_bus_ref = NULL;
        self->reader_fd = NULL;
        return 0;
}

#ifndef Py_LIMITED_API
static SdBusMessageObject* SdBus_new_method_call_message(SdBusObject* self, PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(4);
        SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_TYPE(2, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_TYPE(3, PyUnicode_Type);

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
            (SdBusMessageObject*)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(SdBusMessage_class, NULL));

        CALL_SD_BUS_AND_CHECK(
            sd_bus_message_new_method_call(self->sd_bus_ref, &new_message_object->message_ref, destination_bus_name, object_path, interface_name, member_name));

        Py_INCREF(new_message_object);
        return new_message_object;
}

#ifndef Py_LIMITED_API
static SdBusMessageObject* SdBus_new_property_get_message(SdBusObject* self, PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(4);
        SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_TYPE(2, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_TYPE(3, PyUnicode_Type);

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
            (SdBusMessageObject*)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(SdBusMessage_class, NULL));
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
        SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_TYPE(2, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_TYPE(3, PyUnicode_Type);

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
            (SdBusMessageObject*)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(SdBusMessage_class, NULL));
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
        SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);  // Path
        SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);  // Interface
        SD_BUS_PY_CHECK_ARG_TYPE(2, PyUnicode_Type);  // Member

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
            (SdBusMessageObject*)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(SdBusMessage_class, NULL));

        CALL_SD_BUS_AND_CHECK(sd_bus_message_new_signal(self->sd_bus_ref, &new_message_object->message_ref, object_path, interface_name, member_name));

        Py_INCREF(new_message_object);
        return new_message_object;
}

#ifndef Py_LIMITED_API
static int _check_sdbus_message(PyObject* something) {
        return PyType_IsSubtype(Py_TYPE(something), (PyTypeObject*)SdBusMessage_class);
}

static SdBusMessageObject* SdBus_call(SdBusObject* self, PyObject* const* args, Py_ssize_t nargs) {
        // TODO: Check reference counting
        SD_BUS_PY_CHECK_ARGS_NUMBER(1);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(0, _check_sdbus_message);

        SdBusMessageObject* call_message = (SdBusMessageObject*)args[0];
#else
static SdBusMessageObject* SdBus_call(SdBusObject* self, PyObject* args) {
        SdBusMessageObject* call_message = NULL;
        CALL_PYTHON_BOOL_CHECK(PyArg_ParseTuple(args, "O", &call_message, NULL));
#endif
        SdBusMessageObject* reply_message_object CLEANUP_SD_BUS_MESSAGE =
            (SdBusMessageObject*)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(SdBusMessage_class, NULL));

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

        PyObject* exception_occured = PyErr_Occurred();
        if (exception_occured) {
                Py_XDECREF(CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallMethodObjArgs(future, set_exception_str, exception_occured, NULL)));
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

static PyObject* SdBus_drive(SdBusObject* self, PyObject* Py_UNUSED(args));

static PyObject* SdBus_get_fd(SdBusObject* self, PyObject* Py_UNUSED(args)) {
        int file_descriptor = CALL_SD_BUS_AND_CHECK(sd_bus_get_fd(self->sd_bus_ref));

        return PyLong_FromLong((long)file_descriptor);
}

#define CHECK_SD_BUS_READER            \
        if (self->reader_fd == NULL) { \
                register_reader(self); \
        }

PyObject* register_reader(SdBusObject* self) {
        PyObject* running_loop CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(asyncio_get_running_loop, NULL));
        PyObject* new_reader_fd CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(SdBus_get_fd(self, NULL));
        PyObject* drive_method CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_GetAttrString((PyObject*)self, "drive"));
        Py_XDECREF(CALL_PYTHON_AND_CHECK(PyObject_CallMethodObjArgs(running_loop, add_reader_str, new_reader_fd, drive_method, NULL)));
        Py_INCREF(new_reader_fd);
        self->reader_fd = new_reader_fd;
        Py_RETURN_NONE;
}

PyObject* unregister_reader(SdBusObject* self) {
        PyObject* running_loop CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(asyncio_get_running_loop, NULL));
        Py_XDECREF(CALL_PYTHON_AND_CHECK(PyObject_CallMethodObjArgs(running_loop, remove_reader_str, self->reader_fd, NULL)));
        Py_RETURN_NONE;
}

static PyObject* SdBus_drive(SdBusObject* self, PyObject* Py_UNUSED(args)) {
        int return_value = 1;
        while (return_value > 0) {
                return_value = sd_bus_process(self->sd_bus_ref, NULL);
                if (return_value == -104)  // -ECONNRESET
                {
                        CALL_PYTHON_AND_CHECK(unregister_reader(self));
                        Py_RETURN_NONE;
                }
                CALL_SD_BUS_AND_CHECK(return_value);

                if (PyErr_Occurred()) {
                        return NULL;
                }
        }

        Py_RETURN_NONE;
}

int SdBus_async_callback(sd_bus_message* m,
                         void* userdata,  // Should be the asyncio.Future
                         sd_bus_error* Py_UNUSED(ret_error)) {
        sd_bus_message* reply_message __attribute__((cleanup(sd_bus_message_unrefp))) = sd_bus_message_ref(m);
        PyObject* py_future = userdata;
        PyObject* is_cancelled CLEANUP_PY_OBJECT = PyObject_CallMethod(py_future, "cancelled", "");
        if (Py_True == is_cancelled) {
                // A bit unpythonic but SdBus_drive does not error out
                return 0;
        }

        if (!sd_bus_message_is_method_error(m, NULL)) {
                // Not Error, set Future result to new message object

                SdBusMessageObject* reply_message_object CLEANUP_SD_BUS_MESSAGE = (SdBusMessageObject*)PyObject_CallFunctionObjArgs(SdBusMessage_class, NULL);
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

#ifndef Py_LIMITED_API
static PyObject* SdBus_call_async(SdBusObject* self, PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(1);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(0, _check_sdbus_message);

        SdBusMessageObject* call_message = (SdBusMessageObject*)args[0];
#else
static PyObject* SdBus_call_async(SdBusObject* self, PyObject* args) {
        SdBusMessageObject* call_message = NULL;
        CALL_PYTHON_BOOL_CHECK(PyArg_ParseTuple(args, "O", &call_message, NULL));
#endif
        PyObject* running_loop CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(asyncio_get_running_loop, NULL));

        PyObject* new_future = CALL_PYTHON_AND_CHECK(PyObject_CallMethod(running_loop, "create_future", ""));

        SdBusSlotObject* new_slot_object CLEANUP_SD_BUS_SLOT = (SdBusSlotObject*)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(SdBusSlot_class, NULL));

        CALL_SD_BUS_AND_CHECK(
            sd_bus_call_async(self->sd_bus_ref, &new_slot_object->slot_ref, call_message->message_ref, SdBus_async_callback, new_future, (uint64_t)0));

        if (PyObject_SetAttrString(new_future, "_sd_bus_py_slot", (PyObject*)new_slot_object) < 0) {
                return NULL;
        }
        CHECK_SD_BUS_READER;
        return new_future;
}

#ifndef Py_LIMITED_API
static int _check_is_sdbus_interface(PyObject* type_to_check) {
        return PyType_IsSubtype(Py_TYPE(type_to_check), (PyTypeObject*)SdBusInterface_class);
}

static PyObject* SdBus_add_interface(SdBusObject* self, PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(3);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(0, _check_is_sdbus_interface);
        SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_TYPE(2, PyUnicode_Type);

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
        PyObject* async_queue = userdata;

        SdBusMessageObject* new_message_object CLEANUP_SD_BUS_MESSAGE = (SdBusMessageObject*)PyObject_CallFunctionObjArgs(SdBusMessage_class, NULL);
        if (new_message_object == NULL) {
                return -1;
        }
        _SdBusMessage_set_messsage(new_message_object, m);
        PyObject* should_be_none CLEANUP_PY_OBJECT = PyObject_CallMethodObjArgs(async_queue, put_no_wait_str, new_message_object, NULL);
        if (should_be_none == NULL) {
                return -1;
        }
        return 0;
}

int _SdBus_match_signal_instant_callback(sd_bus_message* m, void* userdata, sd_bus_error* Py_UNUSED(ret_error)) {
        PyObject* new_future = userdata;

        if (!sd_bus_message_is_method_error(m, NULL)) {
                PyObject* new_queue CLEANUP_PY_OBJECT = PyObject_GetAttrString(new_future, "_sd_bus_queue");
                if (new_queue == NULL) {
                        return -1;
                }

                PyObject* should_be_none CLEANUP_PY_OBJECT = PyObject_CallMethodObjArgs(new_future, set_result_str, new_queue, NULL);
                if (should_be_none == NULL) {
                        return -1;
                }

                SdBusSlotObject* slot_object CLEANUP_SD_BUS_SLOT = (SdBusSlotObject*)PyObject_GetAttrString(new_queue, "_sd_bus_slot");
                if (slot_object == NULL) {
                        return -1;
                }
                sd_bus_slot_set_userdata(slot_object->slot_ref, new_queue);
        } else {
                if (future_set_exception_from_message(new_future, m) < 0) {
                        return -1;
                }
        }

        return 0;
}

#ifndef Py_LIMITED_API
static PyObject* SdBus_get_signal_queue(SdBusObject* self, PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(4);
        SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_TYPE(2, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_TYPE(3, PyUnicode_Type);

        const char* sender_service_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]);
        const char* path_name_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[1]);
        const char* interface_name_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[2]);
        const char* member_name_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[3]);
#else
static PyObject* SdBus_get_signal_queue(SdBusObject* self, PyObject* args) {
        const char* sender_service_char_ptr = NULL;
        const char* path_name_char_ptr = NULL;
        const char* interface_name_char_ptr = NULL;
        const char* member_name_char_ptr = NULL;
        CALL_PYTHON_BOOL_CHECK(
            PyArg_ParseTuple(args, "ssss", &sender_service_char_ptr, &path_name_char_ptr, &interface_name_char_ptr, &member_name_char_ptr, NULL));
#endif
        SdBusSlotObject* new_slot CLEANUP_SD_BUS_SLOT = (SdBusSlotObject*)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(SdBusSlot_class, NULL));

        PyObject* new_queue CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(asyncio_queue_class, NULL));

        // Bind lifetime of the slot to the queue
        CALL_PYTHON_INT_CHECK(PyObject_SetAttrString(new_queue, "_sd_bus_slot", (PyObject*)new_slot));

        PyObject* running_loop CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(asyncio_get_running_loop, NULL));

        PyObject* new_future CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_CallMethod(running_loop, "create_future", ""));

        // Bind lifetime of the queue to future
        CALL_PYTHON_INT_CHECK(PyObject_SetAttrString(new_future, "_sd_bus_queue", new_queue));

        CALL_SD_BUS_AND_CHECK(sd_bus_match_signal_async(self->sd_bus_ref, &new_slot->slot_ref, sender_service_char_ptr, path_name_char_ptr,
                                                        interface_name_char_ptr, member_name_char_ptr, _SdBus_signal_callback,
                                                        _SdBus_match_signal_instant_callback, new_future));

        CHECK_SD_BUS_READER
        Py_INCREF(new_future);
        return new_future;
}

int SdBus_request_callback(sd_bus_message* m,
                           void* userdata,  // Should be the asyncio.Future
                           sd_bus_error* Py_UNUSED(ret_error)) {
        PyObject* py_future = userdata;
        PyObject* is_cancelled CLEANUP_PY_OBJECT = PyObject_CallMethod(py_future, "cancelled", "");
        if (Py_True == is_cancelled) {
                // A bit unpythonic but SdBus_drive does not error out
                return 0;
        }

        if (!sd_bus_message_is_method_error(m, NULL)) {
                // Not Error, set Future result to new message object
                PyObject* return_object CLEANUP_PY_OBJECT = PyObject_CallMethod(py_future, "set_result", "O", Py_None);
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

#ifndef Py_LIMITED_API
static PyObject* SdBus_request_name_async(SdBusObject* self, PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(2);
        SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_TYPE(1, PyLong_Type);

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
        PyObject* running_loop CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(asyncio_get_running_loop, NULL));
        PyObject* new_future = CALL_PYTHON_AND_CHECK(PyObject_CallMethod(running_loop, "create_future", ""));
        SdBusSlotObject* new_slot_object CLEANUP_SD_BUS_SLOT = (SdBusSlotObject*)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(SdBusSlot_class, NULL));

        CALL_SD_BUS_AND_CHECK(
            sd_bus_request_name_async(self->sd_bus_ref, &new_slot_object->slot_ref, service_name_char_ptr, flags, SdBus_request_callback, new_future));

        if (PyObject_SetAttrString(new_future, "_sd_bus_py_slot", (PyObject*)new_slot_object) < 0) {
                return NULL;
        }
        CHECK_SD_BUS_READER;
        return new_future;
}

#ifndef Py_LIMITED_API
static PyObject* SdBus_request_name(SdBusObject* self, PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(2);
        SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_TYPE(1, PyLong_Type);

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
        CALL_SD_BUS_AND_CHECK(sd_bus_request_name(self->sd_bus_ref, service_name_char_ptr, flags));
        Py_RETURN_NONE;
}

#ifndef Py_LIMITED_API
static SdBusSlotObject* SdBus_add_object_manager(SdBusObject* self, PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(1);
        SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);

        const char* object_manager_path = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]);
#else
static SdBusSlotObject* SdBus_add_object_manager(SdBusObject* self, PyObject* args) {
        const char* object_manager_path = NULL;
        CALL_PYTHON_BOOL_CHECK(PyArg_ParseTuple(args, "s", &object_manager_path, NULL));
#endif
        SdBusSlotObject* new_slot_object CLEANUP_SD_BUS_SLOT = (SdBusSlotObject*)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(SdBusSlot_class, NULL));

        CALL_SD_BUS_AND_CHECK(sd_bus_add_object_manager(self->sd_bus_ref, &new_slot_object->slot_ref, object_manager_path));

        Py_INCREF(new_slot_object);
        return new_slot_object;
}

#ifndef Py_LIMITED_API
static PyObject* SdBus_emit_object_added(SdBusObject* self, PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(1);
        SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);

        const char* added_object_path = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]);
#else
static PyObject* SdBus_emit_object_added(SdBusObject* self, PyObject* args) {
        const char* added_object_path = NULL;
        CALL_PYTHON_BOOL_CHECK(PyArg_ParseTuple(args, "s", &added_object_path, NULL));
#endif
        CALL_SD_BUS_AND_CHECK(sd_bus_emit_object_added(self->sd_bus_ref, added_object_path));

        Py_RETURN_NONE;
}

static PyMethodDef SdBus_methods[] = {
    {"call", (SD_BUS_PY_FUNC_TYPE)SdBus_call, SD_BUS_PY_METH, "Send message and get reply"},
    {"call_async", (SD_BUS_PY_FUNC_TYPE)SdBus_call_async, SD_BUS_PY_METH, "Async send message, returns awaitable future"},
    {"drive", (PyCFunction)SdBus_drive, METH_NOARGS, "Drive connection"},
    {"get_fd", (SD_BUS_PY_FUNC_TYPE)SdBus_get_fd, SD_BUS_PY_METH, "Get file descriptor to await on"},
    {"new_method_call_message", (SD_BUS_PY_FUNC_TYPE)SdBus_new_method_call_message, SD_BUS_PY_METH, NULL},
    {"new_property_get_message", (SD_BUS_PY_FUNC_TYPE)SdBus_new_property_get_message, SD_BUS_PY_METH, NULL},
    {"new_property_set_message", (SD_BUS_PY_FUNC_TYPE)SdBus_new_property_set_message, SD_BUS_PY_METH,
     "Set object/interface property. User must add variant data to "
     "message"},
    {"new_signal_message", (SD_BUS_PY_FUNC_TYPE)SdBus_new_signal_message, SD_BUS_PY_METH, "Create new signal message. User must data to message and send it"},
    {"add_interface", (SD_BUS_PY_FUNC_TYPE)SdBus_add_interface, SD_BUS_PY_METH, "Add interface to the bus"},
    {"get_signal_queue_async", (SD_BUS_PY_FUNC_TYPE)SdBus_get_signal_queue, SD_BUS_PY_METH,
     "Returns a future that returns a queue that queues signal "
     "messages"},
    {"request_name_async", (SD_BUS_PY_FUNC_TYPE)SdBus_request_name_async, SD_BUS_PY_METH, "Request dbus name async"},
    {"request_name", (SD_BUS_PY_FUNC_TYPE)SdBus_request_name, SD_BUS_PY_METH, "Request dbus name blocking"},
    {"add_object_manager", (SD_BUS_PY_FUNC_TYPE)SdBus_add_object_manager, SD_BUS_PY_METH, "Add object manager at the path"},
    {"emit_object_added", (SD_BUS_PY_FUNC_TYPE)SdBus_emit_object_added, SD_BUS_PY_METH, "Emit signal that object was added"},
    {NULL, NULL, 0, NULL},
};

PyType_Spec SdBusType = {
    .name = "sd_bus_internals.SdBus",
    .basicsize = sizeof(SdBusObject),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT,
    .slots =
        (PyType_Slot[]){
            {Py_tp_init, (initproc)SdBus_init},
            {Py_tp_dealloc, (destructor)SdBus_dealloc},
            {Py_tp_methods, SdBus_methods},
            {0, NULL},
        },
};
