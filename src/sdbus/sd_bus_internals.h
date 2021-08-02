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
#pragma once
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>
#include <systemd/sd-bus.h>
// Macros

#define SD_BUS_PY_CHECK_ARGS_NUMBER(number_args)                                                     \
        if (nargs != number_args) {                                                                  \
                PyErr_Format(PyExc_TypeError, "Expected " #number_args " arguments, got %i", nargs); \
                return NULL;                                                                         \
        }

#define SD_BUS_PY_CHECK_ARG_TYPE(arg_num, arg_expected_type)                                   \
        if (Py_TYPE(args[arg_num]) != &arg_expected_type) {                                    \
                PyErr_SetString(PyExc_TypeError, "Argument is not an " #arg_expected_type ""); \
                return NULL;                                                                   \
        }

#define SD_BUS_PY_CHECK_ARG_CHECK_FUNC(arg_num, arg_check_function)                                  \
        if (!arg_check_function(args[arg_num])) {                                                    \
                PyErr_SetString(PyExc_TypeError, "Argument failed a " #arg_check_function " check"); \
                return NULL;                                                                         \
        }

#define CALL_PYTHON_AND_CHECK(py_function)          \
        ({                                          \
                PyObject* new_object = py_function; \
                if (new_object == NULL) {           \
                        return NULL;                \
                }                                   \
                new_object;                         \
        })

#define PYTHON_ERR_OCCURED      \
        if (PyErr_Occurred()) { \
                return NULL;    \
        }

#define CALL_SD_BUS_AND_CHECK(sd_bus_function)                                                                                                                \
        ({                                                                                                                                                    \
                int return_int = sd_bus_function;                                                                                                             \
                if (return_int < 0) {                                                                                                                         \
                        PyErr_Format(exception_lib, "Line: %d. " #sd_bus_function " in function %s returned error: %i", __LINE__, __FUNCTION__, -return_int); \
                        return NULL;                                                                                                                          \
                }                                                                                                                                             \
                return_int;                                                                                                                                   \
        })

#define CALL_SD_BUS_CHECK_RETURN_NEG1(sd_bus_function)                     \
        ({                                                                 \
                int return_int = sd_bus_function;                          \
                if (return_int < 0) {                                      \
                        PyErr_Format(exception_lib,                        \
                                     "Line: %d. " #sd_bus_function         \
                                     " in function %s returned "           \
                                     "error number: %i",                   \
                                     __LINE__, __FUNCTION__, -return_int); \
                        return -1;                                         \
                }                                                          \
                return_int;                                                \
        })

#define SD_BUS_PY_UNICODE_AS_BYTES(py_unicode)                              \
        ({                                                                  \
                PyObject* utf_8_bytes = PyUnicode_AsUTF8String(py_unicode); \
                if (utf_8_bytes == NULL) {                                  \
                        return NULL;                                        \
                }                                                           \
                utf_8_bytes;                                                \
        })

#define SD_BUS_PY_BYTES_AS_CHAR_PTR(py_bytes)                          \
        ({                                                             \
                const char* new_char_ptr = PyBytes_AsString(py_bytes); \
                if (new_char_ptr == NULL) {                            \
                        return NULL;                                   \
                }                                                      \
                new_char_ptr;                                          \
        })

#ifndef Py_LIMITED_API
#define SD_BUS_PY_UNICODE_AS_CHAR_PTR(py_object)                        \
        ({                                                              \
                const char* new_char_ptr = PyUnicode_AsUTF8(py_object); \
                if (new_char_ptr == NULL) {                             \
                        return NULL;                                    \
                }                                                       \
                new_char_ptr;                                           \
        })
#endif

#define CALL_PYTHON_ITER(iter, iter_end)                             \
        ({                                                           \
                PyObject* next_object = PyIter_Next(signature_iter); \
                if (next_object == NULL)                             \
                                                                     \
                {                                                    \
                        if (PyErr_Occurred()) {                      \
                                return NULL;                         \
                        } else {                                     \
                                iter_end;                            \
                        }                                            \
                }                                                    \
                next_object;                                         \
        })

#define CALL_PYTHON_INT_CHECK(py_function)    \
        ({                                    \
                int return_int = py_function; \
                if (return_int < 0) {         \
                        return NULL;          \
                }                             \
                return_int;                   \
        })

#define CALL_PYTHON_BOOL_CHECK(py_function)   \
        ({                                    \
                int return_int = py_function; \
                if (!return_int) {            \
                        return NULL;          \
                }                             \
                return_int;                   \
        })

#define CALL_PYTHON_EXPECT_NONE(py_function)      \
        ({                                        \
                PyObject* none_obj = py_function; \
                if (none_obj == NULL) {           \
                        return NULL;              \
                }                                 \
                Py_DECREF(none_obj);              \
        })

#define CALL_PYTHON_CHECK_RETURN_NEG1(py_function) \
        ({                                         \
                PyObject* py_object = py_function; \
                if (py_object == NULL) {           \
                        return -1;                 \
                }                                  \
                py_object;                         \
        })

#ifndef Py_LIMITED_API
#define SD_BUS_DEALLOC_TAIL                      \
        PyTypeObject* self_type = Py_TYPE(self); \
        self_type->tp_free(self);                \
        Py_DECREF(self_type);
#else
#define SD_BUS_DEALLOC_TAIL                                                         \
        PyTypeObject* self_type = Py_TYPE(self);                                    \
        void (*free_self)(void*) = (freefunc)PyType_GetSlot(self_type, Py_tp_free); \
        free_self(self);                                                            \
        Py_DECREF(self_type);
#endif

#ifndef Py_LIMITED_API
#define SD_BUS_PY_METH METH_FASTCALL
#else
#define SD_BUS_PY_METH METH_VARARGS
#endif

#ifndef Py_LIMITED_API
#define SD_BUS_PY_FUNC_TYPE void*
#else
#define SD_BUS_PY_FUNC_TYPE PyCFunction
#endif

#ifndef Py_LIMITED_API
#define SD_BUS_PY_LIST_GET_ITEM PyList_GET_ITEM
#else
#define SD_BUS_PY_LIST_GET_ITEM PyList_GetItem
#endif

#ifndef Py_LIMITED_API
#define SD_BUS_PY_TUPLE_GET_SIZE PyTuple_GET_SIZE
#else
#define SD_BUS_PY_TUPLE_GET_SIZE PyTuple_Size
#endif

#ifndef Py_LIMITED_API
#define SD_BUS_PY_TUPLE_GET_ITEM PyTuple_GET_ITEM
#else
#define SD_BUS_PY_TUPLE_GET_ITEM PyTuple_GetItem
#endif

#ifndef Py_LIMITED_API
#define SD_BUS_PY_TUPLE_SET_ITEM PyTuple_SET_ITEM
#else
#define SD_BUS_PY_TUPLE_SET_ITEM PyTuple_SetItem
#endif

#ifndef Py_LIMITED_API
#define SD_BUS_PY_LIST_GET_SIZE PyList_GET_SIZE
#else
#define SD_BUS_PY_LIST_GET_SIZE PyList_Size
#endif

// Python functions and objects
extern PyObject* unmapped_error_exception;
extern PyObject* dbus_error_to_exception_dict;
extern PyObject* exception_to_dbus_error_dict;
extern PyObject* exception_base;
extern PyObject* exception_lib;
extern PyObject* asyncio_get_running_loop;
extern PyObject* asyncio_queue_class;
extern PyObject* is_coroutine_function;
// Str objects
extern PyObject* set_result_str;
extern PyObject* set_exception_str;
extern PyObject* put_no_wait_str;
extern PyObject* add_reader_str;
extern PyObject* remove_reader_str;
extern PyObject* empty_str;
extern PyObject* null_str;
extern PyObject* extend_str;
extern PyObject* append_str;
extern PyObject* call_soon_str;
extern PyObject* create_task_str;

__attribute__((used)) static inline void _cleanup_char_ptr(const char** ptr) {
        if (*ptr != NULL) {
                free((char*)*ptr);
        }
}

#define CLEANUP_STR_MALLOC __attribute__((cleanup(_cleanup_char_ptr)))

__attribute__((used)) static inline void PyObject_cleanup(PyObject** object) {
        Py_XDECREF(*object);
}

#define CLEANUP_PY_OBJECT __attribute__((cleanup(PyObject_cleanup)))

// SdBusSlot
typedef struct {
        PyObject_HEAD;
        sd_bus_slot* slot_ref;
} SdBusSlotObject;

__attribute__((used)) static inline void cleanup_SdBusSlot(SdBusSlotObject** object) {
        Py_XDECREF(*object);
}

#define CLEANUP_SD_BUS_SLOT __attribute__((cleanup(cleanup_SdBusSlot)))

extern PyType_Spec SdBusSlotType;
extern PyObject* SdBusSlot_class;

// SdBusInterface
typedef struct {
        PyObject_HEAD;
        SdBusSlotObject* interface_slot;
        PyObject* method_list;
        PyObject* method_dict;
        PyObject* property_list;
        PyObject* property_get_dict;
        PyObject* property_set_dict;
        PyObject* signal_list;
        sd_bus_vtable* vtable;
} SdBusInterfaceObject;

extern PyType_Spec SdBusInterfaceType;
extern PyObject* SdBusInterface_class;

// SdBusMessage
typedef struct {
        PyObject_HEAD;
        sd_bus_message* message_ref;
} SdBusMessageObject;

__attribute__((used)) static inline void cleanup_SdBusMessage(SdBusMessageObject** object) {
        Py_XDECREF(*object);
}

extern void _SdBusMessage_set_messsage(SdBusMessageObject* self, sd_bus_message* new_message);

#define CLEANUP_SD_BUS_MESSAGE __attribute__((cleanup(cleanup_SdBusMessage)))

extern PyType_Spec SdBusMessageType;
extern PyObject* SdBusMessage_class;

// SdBus
typedef struct {
        PyObject_HEAD;
        sd_bus* sd_bus_ref;
        PyObject* reader_fd;
} SdBusObject;

extern PyType_Spec SdBusType;
extern PyObject* SdBus_class;

// Module level funcions
extern PyMethodDef SdBusPyInternal_methods[];
