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
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
*/
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <systemd/sd-bus.h>
#include <structmember.h>

//Helpers

#define SD_BUS_PY_CHECK_ARGS_NUMBER(number_args)                                             \
    if (nargs != number_args)                                                                \
    {                                                                                        \
        PyErr_Format(PyExc_TypeError, "Expected " #number_args " arguments, got %i", nargs); \
        return NULL;                                                                         \
    }

#define SD_BUS_PY_CHECK_ARG_TYPE(arg_num, arg_expected_type)                           \
    if (Py_TYPE(args[arg_num]) != &arg_expected_type)                                  \
    {                                                                                  \
        PyErr_SetString(PyExc_TypeError, "Argument is not an " #arg_expected_type ""); \
        return NULL;                                                                   \
    }

#define SD_BUS_PY_CHECK_ARG_CHECK_FUNC(arg_num, arg_check_function)                          \
    if (!arg_check_function(args[arg_num]))                                                  \
    {                                                                                        \
        PyErr_SetString(PyExc_TypeError, "Argument failed a " #arg_check_function " check"); \
        return NULL;                                                                         \
    }

#define SD_BUS_PY_TUPLE_GET_ITEM_AND_CHECK(var_name, tuple, index) \
    PyObject *var_name = PyTuple_GetItem(tuple, index);            \
    if (var_name == NULL)                                          \
    {                                                              \
        return NULL;                                               \
    }

#define SD_BUS_PY_GET_CHAR_PTR_FROM_PY_UNICODE(var_name, py_object) \
    const char *var_name = PyUnicode_AsUTF8(py_object);             \
    if (var_name == NULL)                                           \
    {                                                               \
        return NULL;                                                \
    }

#define SD_BUS_PY_GET_INT_FROM_PY_LONG(var_name, py_object) \
    const char *var_name = PyUnicode_AsUTF8(py_object);     \
    if (var_name == NULL)                                   \
    {                                                       \
        return NULL;                                        \
    }

#define CALL_PYTHON_AND_CHECK(py_function)  \
    ({                                      \
        PyObject *new_object = py_function; \
        if (new_object == NULL)             \
        {                                   \
            return NULL;                    \
        }                                   \
        new_object;                         \
    })

#define PYTHON_ERR_OCCURED \
    if (PyErr_Occurred())  \
    {                      \
        return NULL;       \
    }

#define CALL_SD_BUS_AND_CHECK(sd_bus_function)                                                              \
    ({                                                                                                      \
        int return_int = sd_bus_function;                                                                   \
        if (return_int < 0)                                                                                 \
        {                                                                                                   \
            PyErr_Format(exception_lib, "Line: %d. " #sd_bus_function " in function %s returned error: %s", \
                         __LINE__, __FUNCTION__, strerrorname_np(-return_int));                             \
            return NULL;                                                                                    \
        }                                                                                                   \
        return_int;                                                                                         \
    })

#define CALL_SD_BUS_CHECK_RETURN_NEG1(sd_bus_function)                                                      \
    ({                                                                                                      \
        int return_int = sd_bus_function;                                                                   \
        if (return_int < 0)                                                                                 \
        {                                                                                                   \
            PyErr_Format(exception_lib, "Line: %d. " #sd_bus_function " in function %s returned error: %s", \
                         __LINE__, __FUNCTION__, strerrorname_np(-return_int));                             \
            return -1;                                                                                      \
        }                                                                                                   \
        return_int;                                                                                         \
    })

#define SD_BUS_PY_UNICODE_AS_CHAR_PTR(py_object)                \
    ({                                                          \
        const char *new_char_ptr = PyUnicode_AsUTF8(py_object); \
        if (new_char_ptr == NULL)                               \
        {                                                       \
            return NULL;                                        \
        }                                                       \
        new_char_ptr;                                           \
    })

#define CALL_PYTHON_ITER(iter, iter_end)                     \
    ({                                                       \
        PyObject *next_object = PyIter_Next(signature_iter); \
        if (next_object == NULL)                             \
                                                             \
        {                                                    \
            if (PyErr_Occurred())                            \
            {                                                \
                return NULL;                                 \
            }                                                \
            else                                             \
            {                                                \
                iter_end;                                    \
            }                                                \
        }                                                    \
        next_object;                                         \
    })

#define CALL_PYTHON_INT_CHECK(py_function) \
    ({                                     \
        int return_int = py_function;      \
        if (return_int < 0)                \
        {                                  \
            return NULL;                   \
        }                                  \
        return_int;                        \
    })

#define CALL_PYTHON_EXPECT_NONE(py_function) \
    ({                                       \
        PyObject *none_obj = py_function;    \
        if (none_obj == NULL)                \
        {                                    \
            return NULL;                     \
        }                                    \
        Py_DECREF(none_obj);                 \
    })

#define CALL_PYTHON_CHECK_RETURN_NEG1(py_function) \
    ({                                             \
        PyObject *py_object = py_function;         \
        if (py_object == NULL)                     \
        {                                          \
            return -1;                             \
        }                                          \
        py_object;                                 \
    })

static PyObject *dbus_error_to_exception_dict = NULL;
static PyObject *exception_to_dbus_error_dict = NULL;
static PyObject *exception_unmapped_message = NULL;
static PyObject *exception_base = NULL;
static PyObject *exception_lib = NULL;
static PyTypeObject *async_future_type = NULL;
static PyObject *asyncio_get_running_loop = NULL;
static PyObject *asyncio_queue_class = NULL;
static PyObject *is_coroutine_function = NULL;
// Str objects
static PyObject *set_result_str = NULL;
static PyObject *set_exception_str = NULL;
static PyObject *put_no_wait_str = NULL;
static PyObject *add_reader_str = NULL;
static PyObject *remove_reader_str = NULL;
static PyObject *empty_str = NULL;
static PyObject *null_str = NULL;
static PyObject *extend_str = NULL;
static PyObject *append_str = NULL;

void _cleanup_char_ptr(const char **ptr)
{
    if (*ptr != NULL)
    {
        free((char *)*ptr);
    }
}

#define CLEANUP_STR_MALLOC __attribute__((cleanup(_cleanup_char_ptr)))

void PyObject_cleanup(PyObject **object)
{
    Py_XDECREF(*object);
}

#define CLEANUP_PY_OBJECT __attribute__((cleanup(PyObject_cleanup)))

//SdBusSlot
typedef struct
{
    PyObject_HEAD;
    sd_bus_slot *slot_ref;
} SdBusSlotObject;

void cleanup_SdBusSlot(SdBusSlotObject **object)
{
    Py_XDECREF(*object);
}

#define CLEANUP_SD_BUS_SLOT __attribute__((cleanup(cleanup_SdBusSlot)))

static int
SdBusSlot_init(SdBusSlotObject *self, PyObject *Py_UNUSED(args), PyObject *Py_UNUSED(kwds))
{
    self->slot_ref = NULL;
    return 0;
}

static void
SdBusSlot_free(SdBusSlotObject *self)
{
    sd_bus_slot_unref(self->slot_ref);
    PyObject_Free(self);
}

static PyTypeObject SdBusSlotType = {
    PyVarObject_HEAD_INIT(NULL, 0)
        .tp_name = "sd_bus_internals.SdBusSlot",
    .tp_basicsize = sizeof(SdBusSlotObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)SdBusSlot_init,
    .tp_free = (freefunc)SdBusSlot_free,
    .tp_methods = NULL,
};

// SdBusInterface
// TODO: adding interface to different buses, recalculating vtable

typedef struct
{
    PyObject_HEAD;
    SdBusSlotObject *interface_slot;
    PyObject *method_list;
    PyObject *method_dict;
    PyObject *property_list;
    PyObject *property_get_dict;
    PyObject *property_set_dict;
    PyObject *signal_list;
    sd_bus_vtable *vtable;
} SdBusInterfaceObject;

static int
SdBusInterface_init(SdBusInterfaceObject *self, PyObject *Py_UNUSED(args), PyObject *Py_UNUSED(kwds))
{
    self->interface_slot = (SdBusSlotObject *)CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallFunctionObjArgs((PyObject *)&SdBusSlotType, NULL));
    self->method_list = CALL_PYTHON_CHECK_RETURN_NEG1(PyList_New((Py_ssize_t)0));
    self->method_dict = CALL_PYTHON_CHECK_RETURN_NEG1(PyDict_New());
    self->property_list = CALL_PYTHON_CHECK_RETURN_NEG1(PyList_New((Py_ssize_t)0));
    self->property_get_dict = CALL_PYTHON_CHECK_RETURN_NEG1(PyDict_New());
    self->property_set_dict = CALL_PYTHON_CHECK_RETURN_NEG1(PyDict_New());
    self->signal_list = CALL_PYTHON_CHECK_RETURN_NEG1(PyList_New((Py_ssize_t)0));
    self->vtable = NULL;
    return 0;
}

static void
SdBusInterface_free(SdBusInterfaceObject *self)
{
    Py_XDECREF(self->interface_slot);
    Py_XDECREF(self->method_list);
    Py_XDECREF(self->method_dict);
    Py_XDECREF(self->property_list);
    Py_XDECREF(self->property_get_dict);
    Py_XDECREF(self->property_set_dict);
    Py_XDECREF(self->signal_list);
    if (self->vtable)
    {
        free(self->vtable);
    }
    PyObject_Free(self);
}

inline int _check_callable_or_none(PyObject *some_object)
{
    return PyCallable_Check(some_object) || (Py_None == some_object);
}

static PyObject *
SdBusInterface_add_property(SdBusInterfaceObject *self,
                            PyObject *const *args,
                            Py_ssize_t nargs)
{
    // Arguments
    // Name, Signature, Get, Set, Flags
    SD_BUS_PY_CHECK_ARGS_NUMBER(5);
    SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_CHECK_FUNC(2, PyCallable_Check);
    SD_BUS_PY_CHECK_ARG_CHECK_FUNC(3, _check_callable_or_none);
    SD_BUS_PY_CHECK_ARG_CHECK_FUNC(4, PyLong_Check);

    PyObject *new_tuple CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyTuple_Pack(4, args[0], args[1], args[4], args[3]));

    CALL_PYTHON_INT_CHECK(PyList_Append(self->property_list, new_tuple));
    CALL_PYTHON_INT_CHECK(PyDict_SetItem(self->property_get_dict, args[0], args[2]));
    CALL_PYTHON_INT_CHECK(PyDict_SetItem(self->property_set_dict, args[0], args[3]));

    Py_RETURN_NONE;
}

static PyObject *
SdBusInterface_add_method(SdBusInterfaceObject *self,
                          PyObject *const *args,
                          Py_ssize_t nargs)
{
    // Arguments
    // Member name, signature, names of input values, result signature, names of result values, callback function or coroutine, flags
    SD_BUS_PY_CHECK_ARGS_NUMBER(7);
    SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_CHECK_FUNC(2, PySequence_Check);
    SD_BUS_PY_CHECK_ARG_TYPE(3, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_CHECK_FUNC(4, PySequence_Check);
    SD_BUS_PY_CHECK_ARG_CHECK_FUNC(5, PyLong_Check);
    SD_BUS_PY_CHECK_ARG_CHECK_FUNC(6, PyCallable_Check);

    PyObject *argument_name_list CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyList_New(0));
    CALL_PYTHON_EXPECT_NONE(PyObject_CallMethodObjArgs(argument_name_list, extend_str, args[2], NULL));
    CALL_PYTHON_EXPECT_NONE(PyObject_CallMethodObjArgs(argument_name_list, extend_str, args[4], NULL));
    // HACK: add a null separator to the end of the array
    CALL_PYTHON_EXPECT_NONE(PyObject_CallMethodObjArgs(argument_name_list, append_str, null_str, NULL));

    PyObject *argument_names_string CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyUnicode_Join(null_str, argument_name_list));
    // Method name, input signature, return signature, arguments names, flags
    PyObject *new_tuple CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyTuple_Pack(5, args[0], args[1], args[3], argument_names_string, args[5]));

    CALL_PYTHON_INT_CHECK(PyList_Append(self->method_list, new_tuple));
    CALL_PYTHON_INT_CHECK(PyDict_SetItem(self->method_dict, args[0], args[6]));

    Py_RETURN_NONE;
}

static PyObject *
SdBusInterface_add_signal(SdBusInterfaceObject *self,
                          PyObject *const *args,
                          Py_ssize_t nargs)
{
    // Arguments
    // Signal name, signature, names of input values, flags
    SD_BUS_PY_CHECK_ARGS_NUMBER(4);
    SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_CHECK_FUNC(2, PySequence_Check);
    SD_BUS_PY_CHECK_ARG_CHECK_FUNC(3, PyLong_Check);

    PyObject *argument_name_list CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyList_New(0));
    CALL_PYTHON_EXPECT_NONE(PyObject_CallMethodObjArgs(argument_name_list, extend_str, args[2], NULL));
    // HACK: add a null separator to the end of the array
    CALL_PYTHON_EXPECT_NONE(PyObject_CallMethodObjArgs(argument_name_list, append_str, null_str, NULL));

    PyObject *argument_names_string CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyUnicode_Join(null_str, argument_name_list));
    // Signal name, signature, names of input values, flags
    PyObject *new_tuple CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyTuple_Pack(4, args[0], args[1], argument_names_string, args[3]));

    CALL_PYTHON_INT_CHECK(PyList_Append(self->signal_list, new_tuple));

    Py_RETURN_NONE;
}

static PyObject *call_soon_str = NULL;
static PyObject *create_task_str = NULL;

static int _SdBusInterface_callback(sd_bus_message *m, void *userdata, sd_bus_error *ret_error);

static int _SdBusInterface_property_get_callback(
    sd_bus *bus,
    const char *path, const char *interface,
    const char *property,
    sd_bus_message *reply,
    void *userdata,
    sd_bus_error *ret_error);

static int _SdBusInterface_property_set_callback(
    sd_bus *bus,
    const char *path,
    const char *interface, const char *property,
    sd_bus_message *value,
    void *userdata,
    sd_bus_error *ret_error);

static PyObject *
SdBusInterface_create_vtable(SdBusInterfaceObject *self,
                             PyObject *const *Py_UNUSED(args),
                             Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(0);

    if (self->vtable)
    {
        Py_RETURN_NONE;
    }

    Py_ssize_t num_of_methods = PyList_Size(self->method_list);
    Py_ssize_t num_of_properties = PyList_Size(self->property_list);
    Py_ssize_t num_of_signals = PyList_Size(self->signal_list);

    self->vtable = calloc(num_of_signals + num_of_properties + num_of_methods + 2, sizeof(sd_bus_vtable));
    if (self->vtable == NULL)
    {
        return PyErr_NoMemory();
    }

    sd_bus_vtable start_vtable = SD_BUS_VTABLE_START(0);
    self->vtable[0] = start_vtable;
    Py_ssize_t current_index = 1;
    // Iter method definitions
    for (Py_ssize_t i = 0; i < num_of_methods; ({++i; ++current_index; }))
    {
        PyObject *method_tuple = CALL_PYTHON_AND_CHECK(PyList_GetItem(self->method_list, i));

        PyObject *method_name_object = CALL_PYTHON_AND_CHECK(PyTuple_GetItem(method_tuple, 0));
        const char *method_name_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(method_name_object);

        PyObject *input_signature_object = CALL_PYTHON_AND_CHECK(PyTuple_GetItem(method_tuple, 1));
        const char *input_signature_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(input_signature_object);

        PyObject *result_signature_object = CALL_PYTHON_AND_CHECK(PyTuple_GetItem(method_tuple, 2));
        const char *result_signature_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(result_signature_object);

        PyObject *argument_names_string = CALL_PYTHON_AND_CHECK(PyTuple_GetItem(method_tuple, 3));

        const char *argument_names_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(argument_names_string);

        PyObject *flags_object = CALL_PYTHON_AND_CHECK(PyTuple_GetItem(method_tuple, 4));
        unsigned long long flags_long = PyLong_AsUnsignedLongLong(flags_object);
        if (PyErr_Occurred())
        {
            return NULL;
        }

        sd_bus_vtable temp_vtable = SD_BUS_METHOD_WITH_NAMES_OFFSET(
            method_name_char_ptr,
            input_signature_char_ptr,
            argument_names_char_ptr,
            result_signature_char_ptr,
            ,
            _SdBusInterface_callback,
            0,
            flags_long);
        self->vtable[current_index] = temp_vtable;
    }

    for (Py_ssize_t i = 0; i < num_of_properties; ({++i; ++current_index; }))
    {
        PyObject *property_tuple = PyList_GET_ITEM(self->property_list, i);

        PyObject *property_name_str = PyTuple_GET_ITEM(property_tuple, 0);
        PyObject *property_signature_str = PyTuple_GET_ITEM(property_tuple, 1);
        PyObject *property_flags = PyTuple_GET_ITEM(property_tuple, 2);
        PyObject *setter_or_none = PyTuple_GET_ITEM(property_tuple, 3);

        const char *property_name_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(property_name_str);
        const char *property_signature_const_char = SD_BUS_PY_UNICODE_AS_CHAR_PTR(property_signature_str);

        unsigned long long flags_long = PyLong_AsUnsignedLongLong(property_flags);
        if (PyErr_Occurred())
        {
            return NULL;
        }

        if (setter_or_none == Py_None)
        {
            sd_bus_vtable temp_vtable = SD_BUS_PROPERTY(
                property_name_char_ptr,                // Name
                property_signature_const_char,         // Signature
                _SdBusInterface_property_get_callback, // Get
                0,                                     // Offset
                flags_long                             // Flags
            );
            self->vtable[current_index] = temp_vtable;
        }
        else
        {
            sd_bus_vtable temp_vtable = SD_BUS_WRITABLE_PROPERTY(
                property_name_char_ptr,                // Name
                property_signature_const_char,         // Signature
                _SdBusInterface_property_get_callback, // Get
                _SdBusInterface_property_set_callback, // Set
                0,                                     // Offset
                flags_long                             // Flags
            );
            self->vtable[current_index] = temp_vtable;
        }
    }

    for (Py_ssize_t i = 0; i < num_of_signals; ({++i; ++current_index; }))
    {
        PyObject *signal_tuple = PyList_GET_ITEM(self->signal_list, i);

        PyObject *signal_name_str = PyTuple_GET_ITEM(signal_tuple, 0);
        PyObject *signal_signature_str = PyTuple_GET_ITEM(signal_tuple, 1);
        PyObject *signal_input_names = PyTuple_GET_ITEM(signal_tuple, 2);
        PyObject *signal_flags = PyTuple_GET_ITEM(signal_tuple, 3);

        const char *signal_name_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(signal_name_str);
        const char *signal_signature_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(signal_signature_str);
        const char *signal_args_names_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(signal_input_names);

        unsigned long long flags_long = PyLong_AsUnsignedLongLong(signal_flags);
        if (PyErr_Occurred())
        {
            return NULL;
        }

        sd_bus_vtable temp_vtable = SD_BUS_SIGNAL_WITH_NAMES(
            signal_name_char_ptr,
            signal_signature_char_ptr,
            signal_args_names_char_ptr,
            flags_long);
        self->vtable[current_index] = temp_vtable;
    }

    sd_bus_vtable end_vtable = SD_BUS_VTABLE_END;
    self->vtable[current_index] = end_vtable;

    Py_RETURN_NONE;
}

static PyMethodDef SdBusInterface_methods[] = {
    {"add_method", (void *)SdBusInterface_add_method, METH_FASTCALL, "Add method to the dbus interface"},
    {"add_property", (void *)SdBusInterface_add_property, METH_FASTCALL, "Add property to the dbus interface"},
    {"add_signal", (void *)SdBusInterface_add_signal, METH_FASTCALL, "Add signal to the dbus interface"},
    {"_create_vtable", (void *)SdBusInterface_create_vtable, METH_FASTCALL, "Creates the vtable"},
    {NULL, NULL, 0, NULL},
};

static PyMemberDef SdBusInterface_members[] = {
    {"method_list", T_OBJECT, offsetof(SdBusInterfaceObject, method_list), READONLY, NULL},
    {"method_dict", T_OBJECT, offsetof(SdBusInterfaceObject, method_dict), READONLY, NULL},
    {"property_list", T_OBJECT, offsetof(SdBusInterfaceObject, property_list), READONLY, NULL},
    {"property_get_dict", T_OBJECT, offsetof(SdBusInterfaceObject, property_get_dict), READONLY, NULL},
    {"property_set_dict", T_OBJECT, offsetof(SdBusInterfaceObject, property_set_dict), READONLY, NULL},
    {"signal_list", T_OBJECT, offsetof(SdBusInterfaceObject, signal_list), READONLY, NULL},
    {NULL}};

static PyTypeObject SdBusInterfaceType = {
    PyVarObject_HEAD_INIT(NULL, 0)
        .tp_name = "sd_bus_internals.SdBusInterface",
    .tp_basicsize = sizeof(SdBusInterfaceObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)SdBusInterface_init,
    .tp_free = (freefunc)SdBusInterface_free,
    .tp_methods = SdBusInterface_methods,
    .tp_members = SdBusInterface_members,
};

// SdBusMessage
typedef struct
{
    PyObject_HEAD;
    sd_bus_message *message_ref;
} SdBusMessageObject;

void cleanup_SdBusMessage(SdBusMessageObject **object)
{
    Py_XDECREF(*object);
}

#define CLEANUP_SD_BUS_MESSAGE __attribute__((cleanup(cleanup_SdBusMessage)))

static int
SdBusMessage_init(SdBusMessageObject *self, PyObject *Py_UNUSED(args), PyObject *Py_UNUSED(kwds))
{
    self->message_ref = NULL;
    return 0;
}

static void
_SdBusMessage_set_messsage(SdBusMessageObject *self, sd_bus_message *new_message)
{
    self->message_ref = sd_bus_message_ref(new_message);
}

static void
SdBusMessage_free(SdBusMessageObject *self)
{
    sd_bus_message_unref(self->message_ref);
    PyObject_Free(self);
}

static PyObject *
SdBusMessage_seal(SdBusMessageObject *self,
                  PyObject *const *Py_UNUSED(args),
                  Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(0);
    CALL_SD_BUS_AND_CHECK(sd_bus_message_seal(self->message_ref, 0, 0));
    Py_RETURN_NONE;
}

static PyObject *
SdBusMessage_dump(SdBusMessageObject *self,
                  PyObject *const *Py_UNUSED(args),
                  Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(0);

    CALL_SD_BUS_AND_CHECK(sd_bus_message_dump(self->message_ref, 0, SD_BUS_MESSAGE_DUMP_WITH_HEADER));
    CALL_SD_BUS_AND_CHECK(sd_bus_message_rewind(self->message_ref, 1));
    Py_RETURN_NONE;
}

typedef struct
{
    sd_bus_message *message;
    const char *container_char_ptr;
    size_t index;
    size_t max_index;
} _Parse_state;

#define _CHECK_PARSER_NOT_NULL(parser)                                 \
    if (parser_state->container_char_ptr[parser_state->index] == '\0') \
    {                                                                  \
        PyErr_SetString(PyExc_TypeError, "Data signature too short");  \
        return NULL;                                                   \
    }

PyObject *_parse_complete(PyObject *complete_obj, _Parse_state *parser_state);

PyObject *_parse_basic(PyObject *basic_obj, _Parse_state *parser_state)
{
    char basic_type = parser_state->container_char_ptr[parser_state->index];
    switch (basic_type)
    {
    // Unsigned
    case 'y':
    {
        unsigned long long the_ulong_long = PyLong_AsUnsignedLongLong(basic_obj);
        PYTHON_ERR_OCCURED;
        if (UINT8_MAX < the_ulong_long)
        {
            PyErr_Format(PyExc_OverflowError, "Cannot convert int to 'y' type, overflow. 'y' is max %llu", (unsigned long long)UINT8_MAX);
            return NULL;
        }
        uint8_t byte_to_add = (uint8_t)the_ulong_long;
        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(parser_state->message, basic_type, &byte_to_add));
        break;
    }
    case 'q':
    {
        unsigned long long the_ulong_long = PyLong_AsUnsignedLongLong(basic_obj);
        PYTHON_ERR_OCCURED;
        if (UINT16_MAX < the_ulong_long)
        {
            PyErr_Format(PyExc_OverflowError, "Cannot convert int to 'q' type, overflow. 'q' is max %llu", (unsigned long long)UINT16_MAX);
            return NULL;
        }
        uint16_t q_to_add = (uint16_t)the_ulong_long;
        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(parser_state->message, basic_type, &q_to_add));
        break;
    }
    case 'u':
    {
        unsigned long long the_ulong_long = PyLong_AsUnsignedLongLong(basic_obj);
        PYTHON_ERR_OCCURED;
        if (UINT32_MAX < the_ulong_long)
        {
            PyErr_Format(PyExc_OverflowError, "Cannot convert int to 'u' type, overflow. 'u' is max %lu", (unsigned long)UINT32_MAX);
            return NULL;
        }
        uint32_t u_to_add = (uint32_t)the_ulong_long;
        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(parser_state->message, basic_type, &u_to_add));
        break;
    }
    case 't':
    {
        unsigned long long the_ulong_long = PyLong_AsUnsignedLongLong(basic_obj);
        PYTHON_ERR_OCCURED;
        uint64_t t_to_add = the_ulong_long;
        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(parser_state->message, basic_type, &t_to_add));
        break;
    }
    //Signed
    case 'n':
    {
        long long the_long_long = PyLong_AsLongLong(basic_obj);
        PYTHON_ERR_OCCURED;
        if (INT16_MAX < the_long_long)
        {
            PyErr_Format(PyExc_OverflowError, "Cannot convert int to 'n' type, overflow. 'n' is max %lli", (long long)INT16_MAX);
            return NULL;
        }
        if (INT16_MIN > the_long_long)
        {
            PyErr_Format(PyExc_OverflowError, "Cannot convert int to 'n' type, underflow. 'n' is min %lli", (long long)INT16_MIN);
            return NULL;
        }
        int16_t n_to_add = (int16_t)the_long_long;
        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(parser_state->message, basic_type, &n_to_add));
        break;
    }
    case 'i':
    {
        long long the_long_long = PyLong_AsLongLong(basic_obj);
        PYTHON_ERR_OCCURED;
        if (INT32_MAX < the_long_long)
        {
            PyErr_Format(PyExc_OverflowError, "Cannot convert int to 'i' type, overflow. 'i' is max %lli", (long long)INT32_MAX);
            return NULL;
        }
        if (INT32_MIN > the_long_long)
        {
            PyErr_Format(PyExc_OverflowError, "Cannot convert int to 'i' type, underflow. 'i' is min %lli", (long long)INT32_MIN);
            return NULL;
        }
        int32_t i_to_add = (int32_t)the_long_long;
        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(parser_state->message, basic_type, &i_to_add));
        break;
    }
    case 'x':
    {
        long long the_long_long = PyLong_AsLongLong(basic_obj);
        PYTHON_ERR_OCCURED;
        int64_t x_to_add = the_long_long;
        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(parser_state->message, basic_type, &x_to_add));
        break;
    }
    case 'h':
    {
        long long the_long_long = PyLong_AsLongLong(basic_obj);
        PYTHON_ERR_OCCURED;
        int h_to_add = (int)the_long_long;
        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(parser_state->message, basic_type, &h_to_add));
        break;
    }
    case 'b':
    {
        if (!PyBool_Check(basic_obj))
        {
            PyErr_Format(PyExc_TypeError, "Message append error, expected bool got %R", basic_obj);
            return NULL;
        }
        int bool_to_add = (basic_obj == Py_True);
        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(parser_state->message, basic_type, &bool_to_add));
        break;
    }
    case 'd':
    {
        if (!PyFloat_Check(basic_obj))
        {
            PyErr_Format(PyExc_TypeError, "Message append error, expected double got %R", basic_obj);
            return NULL;
        }
        double double_to_add = PyFloat_AsDouble(basic_obj);
        PYTHON_ERR_OCCURED;
        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(parser_state->message, basic_type, &double_to_add));
        break;
    }
    case 'o':
    case 'g':
    case 's':
    {
        if (!PyUnicode_Check(basic_obj))
        {
            PyErr_Format(PyExc_TypeError, "Message append error, expected str got %R", basic_obj);
            return NULL;
        }

        const char *char_ptr_to_append = SD_BUS_PY_UNICODE_AS_CHAR_PTR(basic_obj);
        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(parser_state->message, basic_type, char_ptr_to_append));
        break;
    }
    default:
        PyErr_Format(PyExc_ValueError, "Unknown message append type: %c", (int)basic_type);
        return NULL;
        break;
    }
    parser_state->index++;
    Py_RETURN_NONE;
}

size_t _find_struct_end(const char *container_char_ptr, size_t current_index)
{
    // Initial state
    // "...(...)..."
    //      ^
    int round_bracket_count = 1;
    for (;
         container_char_ptr[current_index] != '\0';
         ++current_index)
    {
        char current_char = container_char_ptr[current_index];
        if (current_char == ')')
        {
            --round_bracket_count;
        }

        if (current_char == '(')
        {
            ++round_bracket_count;
        }

        if (round_bracket_count == 0)
        {
            return current_index;
        }

        if (round_bracket_count < 0)
        {
            PyErr_SetString(PyExc_TypeError, "Round braces count <0. Check your signature.");
            return 0;
        }
    }
    PyErr_SetString(PyExc_TypeError, "Reached the end of signature before the struct end");
    return 0;
}

size_t _find_dict_end(const char *container_char_ptr, size_t current_index)
{
    // Initial state
    // "...a{..}..."
    //      ^
    int curly_bracket_count = 0;
    for (;
         container_char_ptr[current_index] != '\0';
         ++current_index)
    {
        char current_char = container_char_ptr[current_index];
        if (current_char == '}')
        {
            --curly_bracket_count;
        }

        if (current_char == '{')
        {
            ++curly_bracket_count;
        }

        if (curly_bracket_count == 0)
        {
            // "...a{..}..."
            //         ^
            return current_index;
        }

        if (curly_bracket_count < 0)
        {
            PyErr_SetString(PyExc_TypeError, "Curly braces count <0. Check your signature.");
            return 0;
        }
    }
    PyErr_SetString(PyExc_TypeError, "Reached the end of signature before the struct end");
    return 0;
}

size_t _find_array_end(const char *container_char_ptr, size_t current_index)
{
    // Initial state
    // "...as..."
    //     ^
    // "...a{sx}.."
    //     ^
    // "...a(as)..."
    //     ^

    while (container_char_ptr[current_index] == 'a')
    {
        current_index++;
    }
    char current_char = container_char_ptr[current_index];
    // "...as..."
    //      ^
    // "...a{sx}.."
    //      ^
    // "...a(as)..."
    //      ^
    if (current_char == '\0')
    {
        PyErr_SetString(PyExc_TypeError, "Reached the end of signature before the array end");
        return 0;
    }
    if (current_char == '{')
    {
        // "...a{sx}.."
        //      ^
        return _find_dict_end(container_char_ptr, current_index);
    }
    if (current_char == '(')
    {
        current_index++;
        // "...a(as)..."
        //       ^
        return _find_struct_end(container_char_ptr, current_index);
    }

    return current_index;
}

const char *_subscript_char_ptr(const char *old_char_ptr, size_t start, size_t end)
{
    // "abc(def)..."
    //  01234 |
    //  0123456
    // 6 - 4 = 2
    // Actual string
    // 'def\0'
    // 3 string length without \0
    // 4 string length with \0
    size_t new_string_size = (end - start) + 1;
    char *new_string = malloc(new_string_size + 1);
    if (new_string == NULL)
    {
        return NULL;
    }
    memcpy(new_string,
           old_char_ptr + start,
           new_string_size);
    // Set last byte to NUL
    new_string[new_string_size] = '\0';
    return new_string;
}

PyObject *_parse_dict(PyObject *dict_object, _Parse_state *parser_state)
{
    // parser_state->container_char_ptr
    // "{sx}"
    //  ^
    if (!PyDict_Check(dict_object))
    {
        PyErr_Format(PyExc_TypeError, "Message append error, expected dict got %R", dict_object);
        return NULL;
    }

    const char *dict_sig_char_ptr CLEANUP_STR_MALLOC = _subscript_char_ptr(
        parser_state->container_char_ptr,
        1,
        parser_state->max_index - 2);
    // "sx"
    parser_state->container_char_ptr = dict_sig_char_ptr; // This is OK because its cleanup from outside
    parser_state->max_index = strlen(dict_sig_char_ptr);

    PyObject *key, *value;
    Py_ssize_t pos = 0;

    while (PyDict_Next(dict_object, &pos, &key, &value))
    {
        CALL_SD_BUS_AND_CHECK(sd_bus_message_open_container(parser_state->message, 'e', dict_sig_char_ptr));
        parser_state->index = 0;
        CALL_PYTHON_EXPECT_NONE(_parse_basic(key, parser_state));
        CALL_PYTHON_EXPECT_NONE(_parse_complete(value, parser_state));
        CALL_SD_BUS_AND_CHECK(sd_bus_message_close_container(parser_state->message));
    }

    Py_RETURN_NONE;
}

PyObject *_parse_array(PyObject *array_object, _Parse_state *parser_state)
{
    // Initial state
    // "...as..."
    //     ^
    // "...a{sx}.."
    //     ^
    // "...a(as)..."
    //     ^
    size_t array_end = _find_array_end(parser_state->container_char_ptr, parser_state->index);
    if (array_end == 0)
    {
        return NULL;
    }
    // Array end points to
    // "...as..."
    //      ^
    // "...a{sx}.."
    //         ^
    // "...a(as)..."
    //         ^
    const char *array_sig_char_ptr CLEANUP_STR_MALLOC = _subscript_char_ptr(
        parser_state->container_char_ptr,
        parser_state->index + 1,
        array_end);
    // array_sig_char_ptr
    // "...as..."
    //     "s"
    // "...a{sx}.."
    //     "{sx}"
    // "...a(as)..."
    //     "(as)"
    _Parse_state array_parser = {
        .message = parser_state->message,
        .container_char_ptr = array_sig_char_ptr,
        .index = 0,
        .max_index = strlen(array_sig_char_ptr),
    };
    if (array_parser.container_char_ptr[0] == '{')
    {
        CALL_SD_BUS_AND_CHECK(sd_bus_message_open_container(parser_state->message, 'a', array_sig_char_ptr));
        CALL_PYTHON_EXPECT_NONE(_parse_dict(array_object, &array_parser));
        CALL_SD_BUS_AND_CHECK(sd_bus_message_close_container(parser_state->message));
    }
    else if (array_parser.container_char_ptr[0] == 'y')
    {
        char *char_ptr_to_add = NULL;
        ssize_t size_of_array = 0;
        if (PyByteArray_Check(array_object))
        {
            char_ptr_to_add = PyByteArray_AsString(array_object);
            if (char_ptr_to_add == NULL)
            {
                return NULL;
            }
            size_of_array = PyByteArray_Size(array_object);
            if (size_of_array == -1)
            {
                return NULL;
            }
        }
        else if (PyBytes_Check(array_object))
        {
            char_ptr_to_add = PyBytes_AsString(array_object);
            if (char_ptr_to_add == NULL)
            {
                return NULL;
            }
            size_of_array = PyBytes_Size(array_object);
            if (size_of_array == -1)
            {
                return NULL;
            }
        }
        else
        {
            PyErr_Format(PyExc_TypeError, "Expected bytes or byte array, got %R", array_object);
            return NULL;
        }
        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_array(parser_state->message, 'y', char_ptr_to_add, (size_t)size_of_array));
    }
    else
    {
        if (!PyList_Check(array_object))
        {
            PyErr_Format(PyExc_TypeError, "Message append error, expected array got %R", array_object);
            return NULL;
        }

        // "...as..."
        //     "s"
        // "...aa{sx}.."
        //     "a{sx}"
        // "...a(as)..."
        //     "(as)"
        CALL_SD_BUS_AND_CHECK(sd_bus_message_open_container(parser_state->message, 'a', array_sig_char_ptr));
        for (Py_ssize_t i = 0; i < PyList_GET_SIZE(array_object); ++i)
        {
            CALL_PYTHON_EXPECT_NONE(_parse_complete(PyList_GET_ITEM(array_object, i), &array_parser));
            array_parser.index = 0;
        }
        CALL_SD_BUS_AND_CHECK(sd_bus_message_close_container(parser_state->message));
    }
    parser_state->index = array_end + 1;
    // index points to
    // "...as..."
    //       ^
    // "...a{sx}.."
    //          ^
    // "...a(as)..."
    //          ^
    Py_RETURN_NONE;
}

PyObject *_parse_struct(PyObject *tuple_object, _Parse_state *parser_state)
{
    // Initial state
    // "...(...)..."
    //     ^
    if (!PyTuple_Check(tuple_object))
    {
        PyErr_Format(PyExc_TypeError, "Message append error, expected tuple got %R", tuple_object);
        return NULL;
    }
    parser_state->index++;
    // "...(...)..."
    //      ^
    size_t struct_end = _find_struct_end(parser_state->container_char_ptr, parser_state->index);

    if (struct_end == 0)
    {
        return NULL;
    }
    // Struct end points to
    // "...(...)..."
    //         ^
    const char *struct_signature CLEANUP_STR_MALLOC = _subscript_char_ptr(
        parser_state->container_char_ptr,
        parser_state->index, struct_end - 1);
    // struct_signature should be
    // "...(...)..."
    //     ^   ^
    //     "..."
    CALL_SD_BUS_AND_CHECK(sd_bus_message_open_container(parser_state->message, 'r', struct_signature));
    for (Py_ssize_t i = 0; i < PyTuple_GET_SIZE(tuple_object); ++i)
    {
        // Use original parser as there is not much reason to create new one
        CALL_PYTHON_EXPECT_NONE(_parse_complete(PyTuple_GET_ITEM(tuple_object, i), parser_state));
    }
    CALL_SD_BUS_AND_CHECK(sd_bus_message_close_container(parser_state->message));
    // "...(...)..."
    //         ^
    parser_state->index++;
    // Final state
    // "...(...)..."
    //          ^
    Py_RETURN_NONE;
}

PyObject *_parse_variant(PyObject *tuple_object, _Parse_state *parser_state)
{
    // Initial state "...v..."
    //                   ^
    if (!PyTuple_Check(tuple_object))
    {
        PyErr_Format(PyExc_TypeError, "Message append error, expected tuple got %R", tuple_object);
        return NULL;
    }
    if (PyTuple_GET_SIZE(tuple_object) != 2)
    {
        PyErr_Format(PyExc_TypeError, "Expected tuple of only 2 elements got %zi", PyTuple_GET_SIZE(tuple_object));
        return NULL;
    }
    PyObject *variant_signature = PyTuple_GET_ITEM(tuple_object, 0);
    const char *variant_signature_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(variant_signature);
    _Parse_state variant_parser = {
        .message = parser_state->message,
        .max_index = strlen(variant_signature_char_ptr),
        .container_char_ptr = variant_signature_char_ptr,
        .index = 0,
    };

    CALL_SD_BUS_AND_CHECK(sd_bus_message_open_container(parser_state->message, 'v', variant_signature_char_ptr));
    PyObject *variant_body = PyTuple_GET_ITEM(tuple_object, 1);
    CALL_PYTHON_EXPECT_NONE(_parse_complete(variant_body, &variant_parser));
    CALL_SD_BUS_AND_CHECK(sd_bus_message_close_container(parser_state->message));

    // Final state "...v..."
    //                  ^
    parser_state->index++;
    Py_RETURN_NONE;
}

PyObject *_parse_complete(PyObject *complete_obj, _Parse_state *parser_state)
{
    // Initial state "..."
    //                ^
    _CHECK_PARSER_NOT_NULL(parser_state);
    char next_char = parser_state->container_char_ptr[parser_state->index];
    switch (next_char)
    {
    case '}':
    {
        PyErr_SetString(PyExc_TypeError, "End of dict reached instead of complete type");
        return NULL;
    }
    case ')':
    {
        PyErr_SetString(PyExc_TypeError, "End of struct reached instead of complete type");
        return NULL;
    }
    case '(':
    {
        // Struct == Tuple
        CALL_PYTHON_EXPECT_NONE(_parse_struct(complete_obj, parser_state));
        break;
    }
    case '{':
    {
        // Dict
        PyErr_SetString(PyExc_TypeError, "Dbus dict can't be outside of array");
        return NULL;
        break;
    }
    case 'a':
    {
        // Array
        CALL_PYTHON_EXPECT_NONE(_parse_array(complete_obj, parser_state));
        break;
    }
    case 'v':
    {
        // Variant == (signature, data))
        CALL_PYTHON_EXPECT_NONE(_parse_variant(complete_obj, parser_state));
        break;
    }
    default:
    {
        // Basic type
        CALL_PYTHON_EXPECT_NONE(_parse_basic(complete_obj, parser_state));
        break;
    }
    }
    Py_RETURN_NONE;
}

static PyObject *
SdBusMessage_append_data(SdBusMessageObject *self,
                         PyObject *const *args,
                         Py_ssize_t nargs)
{
    if (nargs < 2)
    {
        PyErr_SetString(PyExc_TypeError, "Minimum 2 args required");
        return NULL;
    }
    SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);

    const char *signature_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]);

    _Parse_state parser_state = {
        .message = self->message_ref,
        .container_char_ptr = signature_char_ptr,
        .index = 0,
        .max_index = strlen(signature_char_ptr),
    };

    for (Py_ssize_t i = 1; i < nargs; ++i)
    {
        CALL_PYTHON_EXPECT_NONE(_parse_complete(args[i], &parser_state));
    }
    Py_RETURN_NONE;
}

static PyObject *
SdBusMessage_open_container(SdBusMessageObject *self,
                            PyObject *const *args,
                            Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(2);
    SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);

    SD_BUS_PY_GET_CHAR_PTR_FROM_PY_UNICODE(container_type_char_ptr, args[0]);
    SD_BUS_PY_GET_CHAR_PTR_FROM_PY_UNICODE(container_contents_char_ptr, args[1]);

    CALL_SD_BUS_AND_CHECK(sd_bus_message_open_container(self->message_ref, container_type_char_ptr[0], container_contents_char_ptr));

    Py_RETURN_NONE;
}

static PyObject *
SdBusMessage_close_container(SdBusMessageObject *self,
                             PyObject *const *Py_UNUSED(args),
                             Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(0);

    CALL_SD_BUS_AND_CHECK(sd_bus_message_close_container(self->message_ref));

    Py_RETURN_NONE;
}

static PyObject *
SdBusMessage_enter_container(SdBusMessageObject *self,
                             PyObject *const *args,
                             Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(2);
    SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);

    SD_BUS_PY_GET_CHAR_PTR_FROM_PY_UNICODE(container_type_char_ptr, args[0]);
    SD_BUS_PY_GET_CHAR_PTR_FROM_PY_UNICODE(container_contents_char_ptr, args[1]);

    CALL_SD_BUS_AND_CHECK(sd_bus_message_enter_container(self->message_ref, container_type_char_ptr[0], container_contents_char_ptr));

    Py_RETURN_NONE;
}

static PyObject *
SdBusMessage_exit_container(SdBusMessageObject *self,
                            PyObject *const *Py_UNUSED(args),
                            Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(0);

    CALL_SD_BUS_AND_CHECK(sd_bus_message_exit_container(self->message_ref));

    Py_RETURN_NONE;
}

static SdBusMessageObject *
SdBusMessage_create_reply(SdBusMessageObject *self,
                          PyObject *const *args,
                          Py_ssize_t nargs);

static PyObject *
SdBusMessage_send(SdBusMessageObject *self,
                  PyObject *const *Py_UNUSED(args),
                  Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(0);

    CALL_SD_BUS_AND_CHECK(sd_bus_send(NULL, self->message_ref, NULL));

    Py_RETURN_NONE;
}

size_t _container_size(const char *container_sig)
{
    size_t container_size = 0;
    size_t index = 0;

    while ((container_sig[index]) != '\0')
    {
        char current_char = container_sig[index];
        index++;
        if (current_char == 'a')
        {
            index = _find_array_end(container_sig, index);
            index++;
        }

        if (current_char == '(')
        {
            index = _find_struct_end(container_sig, index);
            index++;
        }

        if (index == 0)
        {
            PyErr_SetString(PyExc_TypeError, "Failed to find container size");
            return 0;
        }

        container_size++;
    }
    return container_size;
}

PyObject *_iter_complete(_Parse_state *parser);

PyObject *_iter_basic(sd_bus_message *message, char basic_type)
{
    switch (basic_type)
    {
    case 'b':
    {
        int new_int = 0;
        CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(message, basic_type, &new_int));
        return PyBool_FromLong(new_int);
        break;
    }
    case 'y':
    {
        uint8_t new_char = 0;
        CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(message, basic_type, &new_char));
        return PyLong_FromUnsignedLong((unsigned long)new_char);
        break;
    }
    case 'n':;
        int16_t new_short = 0;
        CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(message, basic_type, &new_short));
        return PyLong_FromLong((long)new_short);
        break;

    case 'i':
    {
        int32_t new_long = 0;
        CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(message, basic_type, &new_long));
        return PyLong_FromLong((long)new_long);
        break;
    }
    case 'x':
    {
        int64_t new_long_long = 0;
        CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(message, basic_type, &new_long_long));
        return PyLong_FromLongLong((long long)new_long_long);
        break;
    }
    case 'q':
    {
        uint16_t new_u_short = 0;
        CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(message, basic_type, &new_u_short));
        return PyLong_FromUnsignedLong((unsigned long)new_u_short);
        break;
    }
    case 'u':
    {
        uint32_t new_u_long = 0;
        CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(message, basic_type, &new_u_long));
        return PyLong_FromUnsignedLong((unsigned long)new_u_long);
        break;
    }
    case 't':
    {
        uint64_t new_u_long_long = 0;
        CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(message, basic_type, &new_u_long_long));
        return PyLong_FromUnsignedLongLong((unsigned long long)new_u_long_long);
        break;
    }

    case 'd':
    {
        double new_double = 0.0;
        CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(message, basic_type, &new_double));
        return PyFloat_FromDouble(new_double);
        break;
    }
    case 'h':
    {
        int new_fd = 0;
        CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(message, basic_type, &new_fd));
        return PyLong_FromLong((long)new_fd);
        break;
    }
    case 'g':
    case 'o':
    case 's':
    {
        const char *new_string = NULL;
        CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(message, basic_type, &new_string));
        return PyUnicode_FromString(new_string);
        break;
    }
    default:
    {
        int code = (int)basic_type;
        PyObject *error_string CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyUnicode_FromFormat("%c", code));
        PyErr_Format(PyExc_TypeError, "Dbus type %R is unknown", error_string);
        return NULL;
        break;
    }
    }
}

PyObject *_iter_bytes_array(_Parse_state *parser)
{
    // Byte array
    const void *char_array = NULL;
    size_t array_size = 0;
    CALL_SD_BUS_AND_CHECK(sd_bus_message_read_array(parser->message, 'y', &char_array, &array_size));
    return PyBytes_FromStringAndSize(char_array, (Py_ssize_t)array_size);
}

PyObject *_iter_dict(_Parse_state *parser)
{
    PyObject *new_dict CLEANUP_PY_OBJECT = PyDict_New();

    char peek_type = '\0';
    const char *container_type = NULL;
    while (CALL_SD_BUS_AND_CHECK(sd_bus_message_peek_type(parser->message, &peek_type, &container_type)) > 0)
    {
        if (peek_type != SD_BUS_TYPE_DICT_ENTRY)
        {
            PyErr_SetString(PyExc_TypeError, "Expected dict entry.");
            return NULL;
        }
        CALL_SD_BUS_AND_CHECK(sd_bus_message_enter_container(parser->message, peek_type, container_type));
        PyObject *key_object CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(_iter_basic(parser->message, container_type[0]));
        PyObject *value_object CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(_iter_complete(parser));
        CALL_SD_BUS_AND_CHECK(sd_bus_message_exit_container(parser->message));
        if (PyDict_SetItem(new_dict, key_object, value_object) < 0)
        {
            return NULL;
        }
    }

    Py_INCREF(new_dict);
    return new_dict;
}

PyObject *_iter_array(_Parse_state *parser)
{
    PyObject *new_list CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyList_New(0));
    char peek_type = '\0';
    const char *container_type = NULL;

    while (CALL_SD_BUS_AND_CHECK(sd_bus_message_peek_type(parser->message, &peek_type, &container_type)) > 0)
    {
        PyObject *new_object CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(_iter_complete(parser));
        if (PyList_Append(new_list, new_object) < 0)
        {
            return NULL;
        }
    }
    Py_INCREF(new_list);
    return new_list;
}

PyObject *_iter_struct(_Parse_state *parser)
{
    const char *container_sig = sd_bus_message_get_signature(parser->message, 0);
    if (container_sig == NULL)
    {
        PyErr_SetString(PyExc_TypeError, "Failed to get container signature");
        return NULL;
    }
    size_t tuple_size = _container_size(container_sig);

    if (tuple_size == 0)
    {
        return NULL;
    }

    PyObject *new_tuple CLEANUP_PY_OBJECT = PyTuple_New((Py_ssize_t)tuple_size);
    for (size_t i = 0; i < tuple_size; ++i)
    {
        PyObject *new_complete = CALL_PYTHON_AND_CHECK(_iter_complete(parser));
        PyTuple_SET_ITEM(new_tuple, i, new_complete);
    }
    Py_INCREF(new_tuple);
    return new_tuple;
}

PyObject *_iter_variant(_Parse_state *parser)
{
    const char *container_sig = sd_bus_message_get_signature(parser->message, 0);
    PyObject *value_object CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(_iter_complete(parser));
    PyObject *variant_sig_str CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyUnicode_FromString(container_sig));
    return PyTuple_Pack(2, variant_sig_str, value_object);
}

PyObject *_iter_complete(_Parse_state *parser)
{
    const char *container_signature = NULL;
    char complete_type = '\0';
    // TODO: can be optimized with custom parser instead of constantly peeking
    CALL_SD_BUS_AND_CHECK(sd_bus_message_peek_type(parser->message, &complete_type, &container_signature));
    switch (complete_type)
    {
    case 'a':
    {
        if (strcmp(container_signature, "y") == 0)
        {
            return _iter_bytes_array(parser);
        }

        if (container_signature[0] == '{')
        {
            CALL_SD_BUS_AND_CHECK(sd_bus_message_enter_container(parser->message, complete_type, container_signature));
            PyObject *new_dict = CALL_PYTHON_AND_CHECK(_iter_dict(parser));
            CALL_SD_BUS_AND_CHECK(sd_bus_message_exit_container(parser->message));
            return new_dict;
        }
        CALL_SD_BUS_AND_CHECK(sd_bus_message_enter_container(parser->message, complete_type, container_signature));
        PyObject *new_array = CALL_PYTHON_AND_CHECK(_iter_array(parser));
        CALL_SD_BUS_AND_CHECK(sd_bus_message_exit_container(parser->message));
        return new_array;
        break;
    }
    case 'v':
    {
        CALL_SD_BUS_AND_CHECK(sd_bus_message_enter_container(parser->message, complete_type, container_signature));
        PyObject *new_variant = CALL_PYTHON_AND_CHECK(_iter_variant(parser));
        CALL_SD_BUS_AND_CHECK(sd_bus_message_exit_container(parser->message));
        return new_variant;
        break;
    }
    case 'r':
    {
        CALL_SD_BUS_AND_CHECK(sd_bus_message_enter_container(parser->message, complete_type, container_signature));
        PyObject *new_tuple = CALL_PYTHON_AND_CHECK(_iter_struct(parser));
        CALL_SD_BUS_AND_CHECK(sd_bus_message_exit_container(parser->message));
        return new_tuple;
        break;
    }
    default:
    {
        return _iter_basic(parser->message, complete_type);
        break;
    }
    }
}

PyObject *iter_tuple_or_single(_Parse_state *parser)
{
    // Calculate the length of message data
    size_t container_size = _container_size(parser->container_char_ptr);
    if (container_size == 0)
    {
        return NULL;
    }

    if (container_size == 1)
    {
        return _iter_complete(parser);
    }
    else
    {
        return _iter_struct(parser);
    }
}

PyObject *
SdBusMessage_get_contents2(SdBusMessageObject *self, PyObject *Py_UNUSED(args))
{
    const char *message_signature = sd_bus_message_get_signature(self->message_ref, 0);

    if (message_signature == NULL)
    {
        PyErr_SetString(PyExc_TypeError, "Failed to get message signature.");
        return NULL;
    }
    if (message_signature[0] == '\0')
    {
        // Empty message
        Py_RETURN_NONE;
    }

    _Parse_state read_parser = {
        .message = self->message_ref,
        .container_char_ptr = message_signature,
        .index = 0,
        .max_index = strlen(message_signature),
    };
    /* Parsing strategy
     Either return a single object (single string, single int, single array)
     or a tuple of single objects. This mirrors the python function returns.
    */
    return iter_tuple_or_single(&read_parser);
}

static PyObject *SdBusMessage_get_member(SdBusMessageObject *self, PyObject *Py_UNUSED(args))
{
    const char *member_char_ptr = sd_bus_message_get_member(self->message_ref);
    if (member_char_ptr == NULL)
    {
        PyErr_SetString(PyExc_RuntimeError, "Failed to get message member field");
        return NULL;
    }
    return PyUnicode_FromString(member_char_ptr);
}

static SdBusMessageObject *
SdBusMessage_create_error_reply(SdBusMessageObject *self,
                                PyObject *const *args,
                                Py_ssize_t nargs);

static PyMethodDef SdBusMessage_methods[] = {
    {"append_data", (void *)SdBusMessage_append_data, METH_FASTCALL, "Append basic data based on signature."},
    {"open_container", (void *)SdBusMessage_open_container, METH_FASTCALL, "Open container for writing"},
    {"close_container", (void *)SdBusMessage_close_container, METH_FASTCALL, "Close container"},
    {"enter_container", (void *)SdBusMessage_enter_container, METH_FASTCALL, "Enter container for reading"},
    {"exit_container", (void *)SdBusMessage_exit_container, METH_FASTCALL, "Exit container"},
    {"dump", (void *)SdBusMessage_dump, METH_FASTCALL, "Dump message to stdout"},
    {"seal", (void *)SdBusMessage_seal, METH_FASTCALL, "Seal message contents"},
    {"get_contents", (PyCFunction)SdBusMessage_get_contents2, METH_NOARGS, "Iterate over message contents"},
    {"get_member", (PyCFunction)SdBusMessage_get_member, METH_NOARGS, "Get message member field"},
    {"create_reply", (void *)SdBusMessage_create_reply, METH_FASTCALL, "Create reply message"},
    {"create_error_reply", (void *)SdBusMessage_create_error_reply, METH_FASTCALL, "Create error reply with error name and error message"},
    {"send", (void *)SdBusMessage_send, METH_FASTCALL, "Queue message to be sent"},
    {NULL, NULL, 0, NULL},
};

static PyObject *
SdBusMessage_expect_reply_getter(SdBusMessageObject *self, void *Py_UNUSED(closure))
{
    return PyBool_FromLong(CALL_SD_BUS_AND_CHECK(sd_bus_message_get_expect_reply(self->message_ref)));
}

static int
SdBusMessage_expect_reply_setter(SdBusMessageObject *self, PyObject *new_value, void *Py_UNUSED(closure))
{
    if (NULL == new_value)
    {
        PyErr_SetString(PyExc_AttributeError, "Can't delete expect_reply");
        return -1;
    }

    if (!PyBool_Check(new_value))
    {
        PyErr_Format(PyExc_TypeError, "Expected bool, got %R", new_value);
        return -1;
    }

    CALL_SD_BUS_CHECK_RETURN_NEG1(sd_bus_message_set_expect_reply(self->message_ref, Py_True == new_value));

    return 0;
}

static PyGetSetDef SdBusMessage_properies[] = {
    {"expect_reply", (getter)SdBusMessage_expect_reply_getter, (setter)SdBusMessage_expect_reply_setter, "Expect reply message?", NULL},
    {0},
};

static PyTypeObject SdBusMessageType = {
    PyVarObject_HEAD_INIT(NULL, 0)
        .tp_name = "sd_bus_internals.SdBusMessage",
    .tp_basicsize = sizeof(SdBusMessageObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)SdBusMessage_init,
    .tp_free = (freefunc)SdBusMessage_free,
    .tp_methods = SdBusMessage_methods,
    .tp_getset = SdBusMessage_properies,
};

static SdBusMessageObject *
SdBusMessage_create_error_reply(SdBusMessageObject *self,
                                PyObject *const *args,
                                Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(2);
    SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);

    SdBusMessageObject *new_reply_message CLEANUP_SD_BUS_MESSAGE = (SdBusMessageObject *)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs((PyObject *)&SdBusMessageType, NULL));

    CALL_SD_BUS_AND_CHECK(sd_bus_message_new_method_errorf(
        self->message_ref,
        &new_reply_message->message_ref,
        SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]),
        "%s",
        SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[1])));

    Py_INCREF(new_reply_message);
    return new_reply_message;
}

static SdBusMessageObject *
SdBusMessage_create_reply(SdBusMessageObject *self,
                          PyObject *const *Py_UNUSED(args),
                          Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(0);
    SdBusMessageObject *new_reply_message CLEANUP_SD_BUS_MESSAGE = (SdBusMessageObject *)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs((PyObject *)&SdBusMessageType, NULL));

    CALL_SD_BUS_AND_CHECK(sd_bus_message_new_method_return(self->message_ref, &new_reply_message->message_ref));

    Py_INCREF(new_reply_message);
    return new_reply_message;
}

// SdBus
typedef struct
{
    PyObject_HEAD;
    sd_bus *sd_bus_ref;
    PyObject *reader_fd;
} SdBusObject;

static void
SdBus_free(SdBusObject *self)
{
    sd_bus_unref(self->sd_bus_ref);
    Py_XDECREF(self->reader_fd);
    PyObject_Free(self);
}

static int
SdBus_init(SdBusObject *self, PyObject *Py_UNUSED(args), PyObject *Py_UNUSED(kwds))
{
    self->sd_bus_ref = NULL;
    self->reader_fd = NULL;
    return 0;
}

static SdBusMessageObject *
SdBus_new_method_call_message(SdBusObject *self,
                              PyObject *const *args,
                              Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(4);
    SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_TYPE(2, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_TYPE(3, PyUnicode_Type);

    const char *destination_bus_name = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]);
    const char *object_path = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[1]);
    const char *interface_name = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[2]);
    const char *member_name = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[3]);

    SdBusMessageObject *new_message_object CLEANUP_SD_BUS_MESSAGE = (SdBusMessageObject *)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs((PyObject *)&SdBusMessageType, NULL));

    CALL_SD_BUS_AND_CHECK(sd_bus_message_new_method_call(
        self->sd_bus_ref,
        &new_message_object->message_ref,
        destination_bus_name,
        object_path,
        interface_name,
        member_name));

    Py_INCREF(new_message_object);
    return new_message_object;
}

static SdBusMessageObject *
SdBus_new_property_get_message(SdBusObject *self,
                               PyObject *const *args,
                               Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(4);
    SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_TYPE(2, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_TYPE(3, PyUnicode_Type);

    const char *destination_service_name = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]);
    const char *object_path = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[1]);
    const char *interface_name = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[2]);
    const char *property_name = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[3]);

    SdBusMessageObject *new_message_object CLEANUP_SD_BUS_MESSAGE = (SdBusMessageObject *)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs((PyObject *)&SdBusMessageType, NULL));
    CALL_SD_BUS_AND_CHECK(
        sd_bus_message_new_method_call(
            self->sd_bus_ref,
            &new_message_object->message_ref,
            destination_service_name,
            object_path,
            "org.freedesktop.DBus.Properties",
            "Get"));

    // Add property_name
    CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(new_message_object->message_ref, 's', interface_name));
    CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(new_message_object->message_ref, 's', property_name));

    Py_INCREF(new_message_object);
    return new_message_object;
}

static SdBusMessageObject *
SdBus_new_property_set_message(SdBusObject *self,
                               PyObject *const *args,
                               Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(4);
    SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_TYPE(2, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_TYPE(3, PyUnicode_Type);

    const char *destination_service_name = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]);
    const char *object_path = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[1]);
    const char *interface_name = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[2]);
    const char *property_name = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[3]);

    SdBusMessageObject *new_message_object CLEANUP_SD_BUS_MESSAGE = (SdBusMessageObject *)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs((PyObject *)&SdBusMessageType, NULL));
    CALL_SD_BUS_AND_CHECK(
        sd_bus_message_new_method_call(
            self->sd_bus_ref,
            &new_message_object->message_ref,
            destination_service_name,
            object_path,
            "org.freedesktop.DBus.Properties",
            "Set"));

    // Add property_name
    CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(new_message_object->message_ref, 's', interface_name));
    CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(new_message_object->message_ref, 's', property_name));

    Py_INCREF(new_message_object);
    return new_message_object;
}

static SdBusMessageObject *
SdBus_new_signal_message(SdBusObject *self,
                         PyObject *const *args,
                         Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(3);
    SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type); // Path
    SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type); // Interface
    SD_BUS_PY_CHECK_ARG_TYPE(2, PyUnicode_Type); // Member

    const char *object_path = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]);
    const char *interface_name = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[1]);
    const char *member_name = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[2]);

    SdBusMessageObject *new_message_object CLEANUP_SD_BUS_MESSAGE = (SdBusMessageObject *)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs((PyObject *)&SdBusMessageType, NULL));

    CALL_SD_BUS_AND_CHECK(
        sd_bus_message_new_signal(
            self->sd_bus_ref,
            &new_message_object->message_ref,
            object_path,
            interface_name,
            member_name));

    Py_INCREF(new_message_object);
    return new_message_object;
}

static SdBusMessageObject *
SdBus_call(SdBusObject *self,
           PyObject *const *args,
           Py_ssize_t nargs)
{
    // TODO: Check reference counting
    SD_BUS_PY_CHECK_ARGS_NUMBER(1);
    SD_BUS_PY_CHECK_ARG_TYPE(0, SdBusMessageType);

    SdBusMessageObject *call_message = (SdBusMessageObject *)args[0];

    SdBusMessageObject *reply_message_object CLEANUP_SD_BUS_MESSAGE = (SdBusMessageObject *)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs((PyObject *)&SdBusMessageType, NULL));

    sd_bus_error error __attribute__((cleanup(sd_bus_error_free))) = SD_BUS_ERROR_NULL;

    int return_value = sd_bus_call(
        self->sd_bus_ref,
        call_message->message_ref,
        (uint64_t)0,
        &error,
        &reply_message_object->message_ref);

    if (sd_bus_error_get_errno(&error))
    {
        PyObject *error_name_str CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyUnicode_FromString(error.name));
        PyObject *exception_to_raise = PyDict_GetItemWithError(dbus_error_to_exception_dict, error_name_str);

        if (PyErr_Occurred())
        {
            return NULL;
        }

        if (exception_to_raise == NULL)
        {
            PyObject *exception_tuple CLEANUP_PY_OBJECT = Py_BuildValue("(ss)", error.name, error.message);
            PyErr_SetObject(exception_unmapped_message, exception_tuple);
            return NULL;
        }
        else
        {

            PyErr_SetString(exception_to_raise, error.message);
            return NULL;
        }
    }

    CALL_SD_BUS_AND_CHECK(return_value);

    Py_INCREF(reply_message_object);
    return reply_message_object;
}

int future_set_exception_from_message(PyObject *future, sd_bus_message *message)
{
    const sd_bus_error *callback_error = sd_bus_message_get_error(message);

    PyObject *error_name_str CLEANUP_PY_OBJECT = CALL_PYTHON_CHECK_RETURN_NEG1(PyUnicode_FromString(callback_error->name));
    PyObject *error_message_str CLEANUP_PY_OBJECT = CALL_PYTHON_CHECK_RETURN_NEG1(PyUnicode_FromString(callback_error->message));

    PyObject *exception_to_raise = PyDict_GetItemWithError(dbus_error_to_exception_dict, error_name_str);

    PyObject *exception_occured = PyErr_Occurred();
    if (exception_occured)
    {
        PyObject *should_be_none CLEANUP_PY_OBJECT = CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallMethodObjArgs(future, set_exception_str, exception_occured, NULL));
        return 0;
    }

    if (exception_to_raise)
    {
        PyObject *new_exception CLEANUP_PY_OBJECT = CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallFunctionObjArgs(exception_to_raise, error_message_str, NULL));
        PyObject *return_object CLEANUP_PY_OBJECT = CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallMethodObjArgs(future, set_exception_str, new_exception, NULL));
    }
    else
    {
        PyObject *new_exception CLEANUP_PY_OBJECT = CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallMethodObjArgs(exception_unmapped_message, error_name_str, error_message_str, NULL));
        PyObject *return_object CLEANUP_PY_OBJECT = CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallMethodObjArgs(future, set_exception_str, new_exception, NULL));
    }

    return 0;
}

static PyObject *
SdBus_drive(SdBusObject *self, PyObject *Py_UNUSED(args));

static PyObject *
SdBus_get_fd(SdBusObject *self,
             PyObject *Py_UNUSED(args))
{
    int file_descriptor = CALL_SD_BUS_AND_CHECK(sd_bus_get_fd(self->sd_bus_ref));

    return PyLong_FromLong((long)file_descriptor);
}

#define CHECK_SD_BUS_READER      \
    if (self->reader_fd == NULL) \
    {                            \
        register_reader(self);   \
    }

PyObject *register_reader(SdBusObject *self)
{
    PyObject *running_loop CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(asyncio_get_running_loop, NULL));
    PyObject *new_reader_fd CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(SdBus_get_fd(self, NULL));
    PyObject *drive_method CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_GetAttrString((PyObject *)self, "drive"));
    PyObject *should_be_none CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_CallMethodObjArgs(running_loop, add_reader_str, new_reader_fd, drive_method, NULL));
    Py_INCREF(new_reader_fd);
    self->reader_fd = new_reader_fd;
    Py_RETURN_NONE;
}

PyObject *unregister_reader(SdBusObject *self)
{
    PyObject *running_loop CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(asyncio_get_running_loop, NULL));
    PyObject *should_be_none CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_CallMethodObjArgs(running_loop, remove_reader_str, self->reader_fd, NULL));
    Py_RETURN_NONE;
}

static PyObject *
SdBus_drive(SdBusObject *self,
            PyObject *Py_UNUSED(args))
{
    int return_value = 1;
    while (return_value > 0)
    {
        return_value = sd_bus_process(self->sd_bus_ref, NULL);
        if (return_value == -104) // -ECONNRESET
        {
            CALL_PYTHON_AND_CHECK(unregister_reader(self));
            Py_RETURN_NONE;
        }
        CALL_SD_BUS_AND_CHECK(return_value);

        if (PyErr_Occurred())
        {
            return NULL;
        }
    }

    Py_RETURN_NONE;
}

int SdBus_async_callback(sd_bus_message *m,
                         void *userdata, // Should be the asyncio.Future
                         sd_bus_error *Py_UNUSED(ret_error))
{
    sd_bus_message *reply_message __attribute__((cleanup(sd_bus_message_unrefp))) = sd_bus_message_ref(m);
    PyObject *py_future = userdata;
    PyObject *is_cancelled CLEANUP_PY_OBJECT = PyObject_CallMethod(py_future, "cancelled", "");
    if (Py_True == is_cancelled)
    {
        // A bit unpythonic but SdBus_drive does not error out
        return 0;
    }

    if (!sd_bus_message_is_method_error(m, NULL))
    {
        // Not Error, set Future result to new message object

        SdBusMessageObject *reply_message_object CLEANUP_SD_BUS_MESSAGE = (SdBusMessageObject *)PyObject_CallFunctionObjArgs((PyObject *)&SdBusMessageType, NULL);
        if (reply_message_object == NULL)
        {
            return -1;
        }
        _SdBusMessage_set_messsage(reply_message_object, reply_message);
        PyObject *return_object CLEANUP_PY_OBJECT = PyObject_CallMethod(py_future, "set_result", "O", reply_message_object);
        if (return_object == NULL)
        {
            return -1;
        }
    }
    else
    {
        // An Error, set exception
        if (future_set_exception_from_message(py_future, m) < 0)
        {
            return -1;
        }
    }

    return 0;
}

static PyObject *
SdBus_call_async(SdBusObject *self,
                 PyObject *const *args,
                 Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(1);
    SD_BUS_PY_CHECK_ARG_TYPE(0, SdBusMessageType);

    SdBusMessageObject *call_message = (SdBusMessageObject *)args[0];

    PyObject *running_loop CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(asyncio_get_running_loop, NULL));

    PyObject *new_future = CALL_PYTHON_AND_CHECK(PyObject_CallMethod(running_loop, "create_future", ""));

    SdBusSlotObject *new_slot_object CLEANUP_SD_BUS_SLOT = (SdBusSlotObject *)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs((PyObject *)&SdBusSlotType, NULL));

    CALL_SD_BUS_AND_CHECK(
        sd_bus_call_async(
            self->sd_bus_ref,
            &new_slot_object->slot_ref,
            call_message->message_ref,
            SdBus_async_callback,
            new_future,
            (uint64_t)0));

    if (PyObject_SetAttrString(new_future, "_sd_bus_py_slot", (PyObject *)new_slot_object) < 0)
    {
        return NULL;
    }
    CHECK_SD_BUS_READER;
    return new_future;
}

static PyObject *
SdBus_add_interface(SdBusObject *self,
                    PyObject *const *args,
                    Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(3);
    SD_BUS_PY_CHECK_ARG_TYPE(0, SdBusInterfaceType);
    SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_TYPE(2, PyUnicode_Type);

    SdBusInterfaceObject *interface_object = (SdBusInterfaceObject *)args[0];
    SD_BUS_PY_GET_CHAR_PTR_FROM_PY_UNICODE(path_char_ptr, args[1]);
    SD_BUS_PY_GET_CHAR_PTR_FROM_PY_UNICODE(interface_name_char_ptr, args[2]);

    PyObject *create_vtable_name CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyUnicode_FromString("_create_vtable"));

    PyObject *should_be_none CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_CallMethodObjArgs((PyObject *)interface_object, create_vtable_name, NULL));

    CALL_SD_BUS_AND_CHECK(
        sd_bus_add_object_vtable(self->sd_bus_ref, &interface_object->interface_slot->slot_ref,
                                 path_char_ptr, interface_name_char_ptr,
                                 interface_object->vtable,
                                 args[0]));

    Py_RETURN_NONE;
}

int _SdBus_signal_callback(sd_bus_message *m, void *userdata, sd_bus_error *Py_UNUSED(ret_error))
{
    PyObject *async_queue = userdata;

    SdBusMessageObject *new_message_object CLEANUP_SD_BUS_MESSAGE = (SdBusMessageObject *)PyObject_CallFunctionObjArgs((PyObject *)&SdBusMessageType, NULL);
    if (new_message_object == NULL)
    {
        return -1;
    }
    _SdBusMessage_set_messsage(new_message_object, m);
    PyObject *should_be_none CLEANUP_PY_OBJECT = PyObject_CallMethodObjArgs(async_queue, put_no_wait_str, new_message_object, NULL);
    if (should_be_none == NULL)
    {
        return -1;
    }
    return 0;
}

int _SdBus_match_signal_instant_callback(sd_bus_message *m, void *userdata, sd_bus_error *Py_UNUSED(ret_error))
{
    PyObject *new_future = userdata;

    if (!sd_bus_message_is_method_error(m, NULL))
    {
        PyObject *new_queue CLEANUP_PY_OBJECT = PyObject_GetAttrString(new_future, "_sd_bus_queue");
        if (new_queue == NULL)
        {
            return -1;
        }

        PyObject *should_be_none CLEANUP_PY_OBJECT = PyObject_CallMethodObjArgs(new_future, set_result_str, new_queue, NULL);
        if (should_be_none == NULL)
        {
            return -1;
        }

        SdBusSlotObject *slot_object CLEANUP_SD_BUS_SLOT = (SdBusSlotObject *)PyObject_GetAttrString(new_queue, "_sd_bus_slot");
        if (slot_object == NULL)
        {
            return -1;
        }
        sd_bus_slot_set_userdata(slot_object->slot_ref, new_queue);
    }
    else
    {
        if (future_set_exception_from_message(new_future, m) < 0)
        {
            return -1;
        }
    }

    return 0;
}

static PyObject *
SdBus_get_signal_queue(SdBusObject *self,
                       PyObject *const *args,
                       Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(4);
    SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_TYPE(2, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_TYPE(3, PyUnicode_Type);

    SD_BUS_PY_GET_CHAR_PTR_FROM_PY_UNICODE(sender_service_char_ptr, args[0]);
    SD_BUS_PY_GET_CHAR_PTR_FROM_PY_UNICODE(path_name_char_ptr, args[1]);
    SD_BUS_PY_GET_CHAR_PTR_FROM_PY_UNICODE(interface_name_char_ptr, args[2]);
    SD_BUS_PY_GET_CHAR_PTR_FROM_PY_UNICODE(member_name_char_ptr, args[3]);

    SdBusSlotObject *new_slot CLEANUP_SD_BUS_SLOT = (SdBusSlotObject *)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs((PyObject *)&SdBusSlotType, NULL));

    PyObject *new_queue CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(asyncio_queue_class, NULL));

    // Bind lifetime of the slot to the queue
    CALL_PYTHON_INT_CHECK(PyObject_SetAttrString(new_queue, "_sd_bus_slot", (PyObject *)new_slot));

    PyObject *running_loop CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(asyncio_get_running_loop, NULL));

    PyObject *new_future CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_CallMethod(running_loop, "create_future", ""));

    // Bind lifetime of the queue to future
    CALL_PYTHON_INT_CHECK(PyObject_SetAttrString(new_future, "_sd_bus_queue", new_queue));

    CALL_SD_BUS_AND_CHECK(
        sd_bus_match_signal_async(
            self->sd_bus_ref, &new_slot->slot_ref,
            sender_service_char_ptr, path_name_char_ptr, interface_name_char_ptr, member_name_char_ptr,
            _SdBus_signal_callback, _SdBus_match_signal_instant_callback, new_future));

    CHECK_SD_BUS_READER
    Py_INCREF(new_future);
    return new_future;
}

int SdBus_request_callback(sd_bus_message *m,
                           void *userdata, // Should be the asyncio.Future
                           sd_bus_error *Py_UNUSED(ret_error))
{
    PyObject *py_future = userdata;
    PyObject *is_cancelled CLEANUP_PY_OBJECT = PyObject_CallMethod(py_future, "cancelled", "");
    if (Py_True == is_cancelled)
    {
        // A bit unpythonic but SdBus_drive does not error out
        return 0;
    }

    if (!sd_bus_message_is_method_error(m, NULL))
    {
        // Not Error, set Future result to new message object
        PyObject *return_object CLEANUP_PY_OBJECT = PyObject_CallMethod(py_future, "set_result", "O", Py_None);
        if (return_object == NULL)
        {
            return -1;
        }
    }
    else
    {
        // An Error, set exception
        if (future_set_exception_from_message(py_future, m) < 0)
        {
            return -1;
        }
    }

    return 0;
}

static PyObject *
SdBus_request_name_async(SdBusObject *self,
                         PyObject *const *args,
                         Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(2);
    SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_TYPE(1, PyLong_Type);

    SD_BUS_PY_GET_CHAR_PTR_FROM_PY_UNICODE(name_char_ptr, args[0]);
    uint64_t flags = PyLong_AsUnsignedLongLong(args[1]);
    if (PyErr_Occurred())
    {
        return NULL;
    }

    PyObject *running_loop CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(asyncio_get_running_loop, NULL));
    PyObject *new_future = CALL_PYTHON_AND_CHECK(PyObject_CallMethod(running_loop, "create_future", ""));
    SdBusSlotObject *new_slot_object CLEANUP_SD_BUS_SLOT = (SdBusSlotObject *)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs((PyObject *)&SdBusSlotType, NULL));

    CALL_SD_BUS_AND_CHECK(sd_bus_request_name_async(
        self->sd_bus_ref,
        &new_slot_object->slot_ref,
        name_char_ptr, flags, SdBus_request_callback, new_future));

    if (PyObject_SetAttrString(new_future, "_sd_bus_py_slot", (PyObject *)new_slot_object) < 0)
    {
        return NULL;
    }
    CHECK_SD_BUS_READER;
    return new_future;
}

static PyMethodDef SdBus_methods[] = {
    {"call", (void *)SdBus_call, METH_FASTCALL, "Send message and get reply"},
    {"call_async", (void *)SdBus_call_async, METH_FASTCALL, "Async send message, returns awaitable future"},
    {"drive", (void *)SdBus_drive, METH_FASTCALL, "Drive connection"},
    {"get_fd", (void *)SdBus_get_fd, METH_FASTCALL, "Get file descriptor to await on"},
    {"new_method_call_message", (void *)SdBus_new_method_call_message, METH_FASTCALL, NULL},
    {"new_property_get_message", (void *)SdBus_new_property_get_message, METH_FASTCALL, NULL},
    {"new_property_set_message", (void *)SdBus_new_property_set_message, METH_FASTCALL, "Set object/interface property. User must add variant data to message"},
    {"new_signal_message", (void *)SdBus_new_signal_message, METH_FASTCALL, "Create new signal message. User must data to message and send it"},
    {"add_interface", (void *)SdBus_add_interface, METH_FASTCALL, "Add interface to the bus"},
    {"get_signal_queue_async", (void *)SdBus_get_signal_queue, METH_FASTCALL, "Returns a future that returns a queue that queues signal messages"},
    {"request_name_async", (void *)SdBus_request_name_async, METH_FASTCALL, "Request dbus name"},
    {NULL, NULL, 0, NULL},
};

static PyTypeObject SdBusType = {
    PyVarObject_HEAD_INIT(NULL, 0)
        .tp_name = "sd_bus_internals.SdBus",
    .tp_basicsize = sizeof(SdBusObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)SdBus_init,
    .tp_free = (freefunc)SdBus_free,
    .tp_methods = SdBus_methods,
};

static int _SdBusInterface_callback(sd_bus_message *m, void *userdata, sd_bus_error *ret_error)
{
    SdBusInterfaceObject *self = userdata;
    // Get the member name from the message
    const char *member_char_ptr = sd_bus_message_get_member(m);
    PyObject *callback_object = PyDict_GetItemString(self->method_dict, member_char_ptr);
    if (callback_object == NULL)
    {
        sd_bus_error_set(ret_error, SD_BUS_ERROR_UNKNOWN_METHOD, "");
        return -1;
    };

    PyObject *running_loop CLEANUP_PY_OBJECT = PyObject_CallFunctionObjArgs(asyncio_get_running_loop, NULL);
    if (running_loop == NULL)
    {
        sd_bus_error_set(ret_error, SD_BUS_ERROR_FAILED, "");
        return -1;
    }

    PyObject *new_message CLEANUP_PY_OBJECT = PyObject_CallFunctionObjArgs((PyObject *)&SdBusMessageType, NULL);
    if (new_message == NULL)
    {
        sd_bus_error_set(ret_error, SD_BUS_ERROR_FAILED, "");
        return -1;
    }
    _SdBusMessage_set_messsage((SdBusMessageObject *)new_message, m);

    PyObject *is_coroutine_test_object CLEANUP_PY_OBJECT = PyObject_CallFunctionObjArgs(is_coroutine_function, callback_object, NULL);
    if (is_coroutine_test_object == NULL)
    {
        return -1;
    }

    if (Py_True == is_coroutine_test_object)
    {
        // Create coroutine
        PyObject *coroutine_activated CLEANUP_PY_OBJECT = PyObject_CallFunctionObjArgs(callback_object, new_message, NULL);
        if (coroutine_activated == NULL)
        {
            return -1;
        }

        PyObject *task CLEANUP_PY_OBJECT = PyObject_CallMethodObjArgs(running_loop, create_task_str, coroutine_activated, NULL);
        if (task == NULL)
        {
            sd_bus_error_set(ret_error, SD_BUS_ERROR_FAILED, "");
            return -1;
        }
    }
    else
    {
        PyObject *handle CLEANUP_PY_OBJECT = PyObject_CallMethodObjArgs(running_loop, call_soon_str, callback_object, new_message, NULL);
        if (handle == NULL)
        {
            sd_bus_error_set(ret_error, SD_BUS_ERROR_FAILED, "");
            return -1;
        }
    }

    sd_bus_error_set(ret_error, NULL, NULL);

    return 1;
}

static int _SdBusInterface_property_get_callback(
    sd_bus *Py_UNUSED(bus),
    const char *Py_UNUSED(path),
    const char *Py_UNUSED(interface),
    const char *property,
    sd_bus_message *reply,
    void *userdata,
    sd_bus_error *Py_UNUSED(ret_error))
{
    SdBusInterfaceObject *self = userdata;
    PyObject *get_call = CALL_PYTHON_CHECK_RETURN_NEG1(PyDict_GetItemString(self->property_get_dict, property));

    PyObject *new_message CLEANUP_PY_OBJECT = CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallFunctionObjArgs((PyObject *)&SdBusMessageType, NULL));
    _SdBusMessage_set_messsage((SdBusMessageObject *)new_message, reply);

    PyObject *return_obj CLEANUP_PY_OBJECT = CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallFunctionObjArgs(get_call, new_message, NULL));
    return 0;
}

static int _SdBusInterface_property_set_callback(
    sd_bus *Py_UNUSED(bus),
    const char *Py_UNUSED(path),
    const char *Py_UNUSED(interface),
    const char *property,
    sd_bus_message *value,
    void *userdata,
    sd_bus_error *Py_UNUSED(ret_error))
{
    SdBusInterfaceObject *self = userdata;

    PyObject *set_call = CALL_PYTHON_CHECK_RETURN_NEG1(PyDict_GetItemString(self->property_set_dict, property));

    PyObject *new_message CLEANUP_PY_OBJECT = CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallFunctionObjArgs((PyObject *)&SdBusMessageType, NULL));
    _SdBusMessage_set_messsage((SdBusMessageObject *)new_message, value);

    PyObject *return_obj CLEANUP_PY_OBJECT = CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallFunctionObjArgs(set_call, new_message, NULL));
    return 0;
}

static SdBusObject *
sd_bus_py_open(PyObject *Py_UNUSED(self),
               PyObject *Py_UNUSED(ignored))
{
    SdBusObject *new_sd_bus = (SdBusObject *)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs((PyObject *)&SdBusType, NULL));
    CALL_SD_BUS_AND_CHECK(sd_bus_open(&(new_sd_bus->sd_bus_ref)));
    return new_sd_bus;
}

static SdBusObject *
sd_bus_py_open_user(PyObject *Py_UNUSED(self),
                    PyObject *Py_UNUSED(ignored))
{
    SdBusObject *new_sd_bus = (SdBusObject *)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs((PyObject *)&SdBusType, NULL));
    CALL_SD_BUS_AND_CHECK(sd_bus_open_user(&(new_sd_bus->sd_bus_ref)));
    return new_sd_bus;
}

static SdBusObject *
sd_bus_py_open_system(PyObject *Py_UNUSED(self),
                      PyObject *Py_UNUSED(ignored))
{
    SdBusObject *new_sd_bus = (SdBusObject *)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs((PyObject *)&SdBusType, NULL));
    CALL_SD_BUS_AND_CHECK(sd_bus_open_system(&(new_sd_bus->sd_bus_ref)));
    return new_sd_bus;
}

static PyObject *
encode_object_path(PyObject *Py_UNUSED(self),
                   PyObject *const *args,
                   Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(2);
    SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);

    PyObject *prefix_str = args[0];
    PyObject *external_str = args[1];

    SD_BUS_PY_GET_CHAR_PTR_FROM_PY_UNICODE(prefix_char_ptr, prefix_str);
    SD_BUS_PY_GET_CHAR_PTR_FROM_PY_UNICODE(external_char_ptr, external_str);

    if (!sd_bus_object_path_is_valid(prefix_char_ptr))
    {
        PyErr_SetString(PyExc_ValueError, "Prefix is not a valid object path");
        return NULL;
    }

    const char *new_char_ptr CLEANUP_STR_MALLOC = NULL;

    CALL_SD_BUS_AND_CHECK(sd_bus_path_encode(prefix_char_ptr, external_char_ptr, (char **)(&new_char_ptr)));

    return PyUnicode_FromString(new_char_ptr);
}

static PyObject *
decode_object_path(PyObject *Py_UNUSED(self),
                   PyObject *const *args,
                   Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(2);
    SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
    SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);

    PyObject *prefix_str = args[0];
    PyObject *full_path_str = args[1];

    SD_BUS_PY_GET_CHAR_PTR_FROM_PY_UNICODE(prefix_char_ptr, prefix_str);
    SD_BUS_PY_GET_CHAR_PTR_FROM_PY_UNICODE(full_path_char_ptr, full_path_str);

    const char *new_char_ptr CLEANUP_STR_MALLOC = NULL;

    CALL_SD_BUS_AND_CHECK(sd_bus_path_decode(full_path_char_ptr, prefix_char_ptr, (char **)(&new_char_ptr)));

    if (new_char_ptr)
    {
        return PyUnicode_FromString(new_char_ptr);
    }
    else
    {
        return PyUnicode_FromString("");
    }
}

PyObject *
_add_exception_mapping(PyObject *exception)
{
    PyObject *dbus_error_string CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_GetAttrString(exception, "dbus_error_name"));

    if (CALL_PYTHON_INT_CHECK(PyDict_Contains(dbus_error_to_exception_dict, dbus_error_string)) > 0)
    {
        PyErr_Format(PyExc_ValueError, "Dbus error %R is already mapped.", dbus_error_string);
        return NULL;
    }

    if (CALL_PYTHON_INT_CHECK(PyDict_Contains(exception_to_dbus_error_dict, exception)) > 0)
    {
        PyErr_Format(PyExc_ValueError, "Exception %R is already mapped to dbus error.", exception);
        return NULL;
    }

    CALL_PYTHON_INT_CHECK(PyDict_SetItem(dbus_error_to_exception_dict, dbus_error_string, exception));
    CALL_PYTHON_INT_CHECK(PyDict_SetItem(exception_to_dbus_error_dict, exception, dbus_error_string));

    Py_RETURN_NONE;
}

static PyObject *
add_exception_mapping(PyObject *Py_UNUSED(self),
                      PyObject *const *args,
                      Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(1);
    return _add_exception_mapping(args[0]);
}

static PyMethodDef SdBusPyInternal_methods[] = {
    {"sd_bus_open", (PyCFunction)sd_bus_py_open, METH_NOARGS, "Open dbus connection. Session bus running as user or system bus as daemon"},
    {"sd_bus_open_user", (PyCFunction)sd_bus_py_open_user, METH_NOARGS, "Open user session dbus"},
    {"sd_bus_open_system", (PyCFunction)sd_bus_py_open_system, METH_NOARGS, "Open system dbus"},
    {"encode_object_path", (void *)encode_object_path, METH_FASTCALL, "Encode object path with object path prefix and arbitrary string"},
    {"decode_object_path", (void *)decode_object_path, METH_FASTCALL, "Decode object path with object path prefix and arbitrary string"},
    {"add_exception_mapping", (void *)add_exception_mapping, METH_FASTCALL, "Add exception to the mapping of dbus error names"},
    {NULL, NULL, 0, NULL},
};

static PyModuleDef sd_bus_internals_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "sd_bus_internals",
    .m_doc = "Sd bus internals module.",
    .m_methods = SdBusPyInternal_methods,
    .m_size = -1,
};

#define SD_BUS_PY_INIT_TYPE_READY(type) \
    if (PyType_Ready(&type) < 0)        \
    {                                   \
        return NULL;                    \
    }

#define SD_BUS_PY_INIT_ADD_OBJECT(type_name, type)              \
    Py_INCREF((PyObject *)type);                                \
    if (PyModule_AddObject(m, type_name, (PyObject *)type) < 0) \
    {                                                           \
        Py_DECREF((PyObject *)type);                            \
        return NULL;                                            \
    }

PyMODINIT_FUNC
PyInit_sd_bus_internals(void)
{
    SD_BUS_PY_INIT_TYPE_READY(SdBusType);
    SD_BUS_PY_INIT_TYPE_READY(SdBusMessageType);
    SD_BUS_PY_INIT_TYPE_READY(SdBusSlotType);
    SD_BUS_PY_INIT_TYPE_READY(SdBusInterfaceType);

    PyObject *m CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyModule_Create(&sd_bus_internals_module));

    SD_BUS_PY_INIT_ADD_OBJECT("SdBus", &SdBusType);
    SD_BUS_PY_INIT_ADD_OBJECT("SdBusMessage", &SdBusMessageType);
    SD_BUS_PY_INIT_ADD_OBJECT("SdBusSlot", &SdBusSlotType);
    SD_BUS_PY_INIT_ADD_OBJECT("SdBusInterface", &SdBusInterfaceType);

    // Exception map
    dbus_error_to_exception_dict = CALL_PYTHON_AND_CHECK(PyDict_New());
    SD_BUS_PY_INIT_ADD_OBJECT("DBUS_ERROR_TO_EXCEPTION", dbus_error_to_exception_dict);

    exception_to_dbus_error_dict = CALL_PYTHON_AND_CHECK(PyDict_New());
    SD_BUS_PY_INIT_ADD_OBJECT("EXCEPTION_TO_DBUS_ERROR", exception_to_dbus_error_dict);

    PyObject *new_base_exception CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyErr_NewException("sd_bus_internals.SdBusBaseError", NULL, NULL));
    SD_BUS_PY_INIT_ADD_OBJECT("SdBusBaseError", new_base_exception);
    exception_base = new_base_exception;

    PyObject *unmapped_error_exception CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyErr_NewException("sd_bus_internals.SdBusUnmappedMessageError", new_base_exception, NULL));
    SD_BUS_PY_INIT_ADD_OBJECT("SdBusUnmappedMessageError", unmapped_error_exception);
    unmapped_error_exception = unmapped_error_exception;

    PyObject *library_exception CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyErr_NewException("sd_bus_internals.SdBusLibraryError", new_base_exception, NULL));
    SD_BUS_PY_INIT_ADD_OBJECT("SdBusLibraryError", library_exception);
    exception_lib = library_exception;

    PyObject *asyncio_module = CALL_PYTHON_AND_CHECK(PyImport_ImportModule("asyncio"));
    async_future_type = (PyTypeObject *)CALL_PYTHON_AND_CHECK(PyObject_GetAttrString(asyncio_module, "Future"));

    asyncio_get_running_loop = CALL_PYTHON_AND_CHECK(PyObject_GetAttrString(asyncio_module, "get_running_loop"));

    asyncio_queue_class = CALL_PYTHON_AND_CHECK(PyObject_GetAttrString(asyncio_module, "Queue"));

    set_result_str = CALL_PYTHON_AND_CHECK(PyUnicode_FromString("set_result"));
    set_exception_str = CALL_PYTHON_AND_CHECK(PyUnicode_FromString("set_exception"));
    put_no_wait_str = CALL_PYTHON_AND_CHECK(PyUnicode_FromString("put_nowait"));
    call_soon_str = CALL_PYTHON_AND_CHECK(PyUnicode_FromString("call_soon"));
    create_task_str = CALL_PYTHON_AND_CHECK(PyUnicode_FromString("create_task"));
    remove_reader_str = CALL_PYTHON_AND_CHECK(PyUnicode_FromString("remove_reader"));
    add_reader_str = CALL_PYTHON_AND_CHECK(PyUnicode_FromString("add_reader"));
    empty_str = CALL_PYTHON_AND_CHECK(PyUnicode_FromString(""));
    null_str = CALL_PYTHON_AND_CHECK(PyUnicode_FromStringAndSize("\0", 1));
    extend_str = CALL_PYTHON_AND_CHECK(PyUnicode_FromString("extend"));
    append_str = CALL_PYTHON_AND_CHECK(PyUnicode_FromString("append"));

    PyObject *inspect_module = CALL_PYTHON_AND_CHECK(PyImport_ImportModule("inspect"));
    is_coroutine_function = CALL_PYTHON_AND_CHECK(PyObject_GetAttrString(inspect_module, "iscoroutinefunction"));

    CALL_PYTHON_INT_CHECK(PyModule_AddIntConstant(m, "DbusDeprecatedFlag", SD_BUS_VTABLE_DEPRECATED));
    CALL_PYTHON_INT_CHECK(PyModule_AddIntConstant(m, "DbusHiddenFlag", SD_BUS_VTABLE_HIDDEN));
    CALL_PYTHON_INT_CHECK(PyModule_AddIntConstant(m, "DbusUnprivilegedFlag", SD_BUS_VTABLE_UNPRIVILEGED));
    CALL_PYTHON_INT_CHECK(PyModule_AddIntConstant(m, "DbusNoReplyFlag", SD_BUS_VTABLE_METHOD_NO_REPLY));
    CALL_PYTHON_INT_CHECK(PyModule_AddIntConstant(m, "DbusPropertyConstFlag", SD_BUS_VTABLE_PROPERTY_CONST));
    CALL_PYTHON_INT_CHECK(PyModule_AddIntConstant(m, "DbusPropertyEmitsChangeFlag", SD_BUS_VTABLE_PROPERTY_EMITS_CHANGE));
    CALL_PYTHON_INT_CHECK(PyModule_AddIntConstant(m, "DbusPropertyEmitsInvalidationFlag", SD_BUS_VTABLE_PROPERTY_EMITS_INVALIDATION));
    CALL_PYTHON_INT_CHECK(PyModule_AddIntConstant(m, "DbusPropertyExplicitFlag", SD_BUS_VTABLE_PROPERTY_EXPLICIT));
    CALL_PYTHON_INT_CHECK(PyModule_AddIntConstant(m, "DbusSensitiveFlag", SD_BUS_VTABLE_SENSITIVE));

    Py_INCREF(m);
    return m;
}