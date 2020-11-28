// SPDX-License-Identifier: LGPL-2.1-or-later
/*
    Copyright (C) 2020  igo95862

    This file is part of py_sd_bus

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

#define SD_BUS_PY_CHECK_RETURN_VALUE(_exception_to_raise)                          \
    if (return_value < 0)                                                          \
    {                                                                              \
        PyErr_Format(_exception_to_raise, "Line: %d sd-bus returned error %i: %s", \
                     __LINE__, -return_value, strerror(-return_value));            \
        return NULL;                                                               \
    }

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

#define CALL_SD_BUS_AND_CHECK(sd_bus_function)                                                                   \
    ({                                                                                                           \
        int return_int = sd_bus_function;                                                                        \
        if (return_int < 0)                                                                                      \
        {                                                                                                        \
            PyErr_Format(PyExc_RuntimeError, "Line: %d. " #sd_bus_function " in function %s returned error: %s", \
                         __LINE__, __FUNCTION__, strerrorname_np(-return_int));                                  \
            return NULL;                                                                                         \
        }                                                                                                        \
        return_int;                                                                                              \
    })

static PyObject *exception_dict = NULL;
static PyObject *exception_default = NULL;
static PyObject *exception_generic = NULL;
static PyTypeObject *async_future_type = NULL;
static PyObject *asyncio_get_running_loop = NULL;
static PyObject *asyncio_queue_class = NULL;
// Str objects
static PyObject *set_result_str = NULL;
static PyObject *set_exception_str = NULL;
static PyObject *put_no_wait_str = NULL;

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
// TODO: adding interface to different busses, recalculating vtable

typedef struct
{
    PyObject_HEAD;
    SdBusSlotObject *interface_slot;
    PyObject *interface_list;
    PyObject *method_dict;
    sd_bus_vtable *vtable;
} SdBusInterfaceObject;

static int
SdBusInterface_init(SdBusInterfaceObject *self, PyObject *Py_UNUSED(args), PyObject *Py_UNUSED(kwds))
{
    self->interface_slot = (SdBusSlotObject *)PyObject_CallFunctionObjArgs((PyObject *)&SdBusSlotType, NULL);
    if (self->interface_slot == NULL)
    {
        return -1;
    }
    self->interface_list = PyList_New((Py_ssize_t)0);
    if (self->interface_list == NULL)
    {
        return -1;
    }
    self->method_dict = PyDict_New();
    if (self->method_dict == NULL)
    {
        return -1;
    }
    self->vtable = NULL;
    return 0;
}

static void
SdBusInterface_free(SdBusInterfaceObject *self)
{
    Py_XDECREF(self->interface_slot);
    Py_XDECREF(self->interface_list);
    Py_XDECREF(self->method_dict);
    if (self->vtable)
    {
        free(self->vtable);
    }
    PyObject_Free(self);
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
    SD_BUS_PY_CHECK_ARG_CHECK_FUNC(5, PyCallable_Check);
    SD_BUS_PY_CHECK_ARG_CHECK_FUNC(6, PyLong_Check);

    PyObject *null_separator CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyUnicode_FromStringAndSize("\0", 1));
    PyObject *extend_string CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyUnicode_FromString("extend"));
    PyObject *append_string CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyUnicode_FromString("append"));
    PyObject *argument_name_list CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyList_New(0));
    PyObject *should_be_none_one CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_CallMethodObjArgs(argument_name_list, extend_string, args[2], NULL));
    PyObject *should_be_none_two CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_CallMethodObjArgs(argument_name_list, extend_string, args[4], NULL));
    // HACK: add a null separator to the end of the array
    PyObject *should_be_none_three CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_CallMethodObjArgs(argument_name_list, append_string, null_separator, NULL));

    PyObject *argument_names_string CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyUnicode_Join(null_separator, argument_name_list));
    // Method name, input signature, return signature, arguments names, flags
    PyObject *new_tuple CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyTuple_Pack(5, args[0], args[1], args[3], argument_names_string, args[6]));

    int return_value = PyList_Append(self->interface_list, new_tuple);
    if (return_value < 0)
    {
        return NULL;
    }
    return_value = PyDict_SetItem(self->method_dict, args[0], args[5]);
    if (return_value < 0)
    {
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject *call_soon_str = NULL;
static PyObject *create_task_str = NULL;

static int _SdBusInterface_callback(sd_bus_message *m, void *userdata, sd_bus_error *ret_error);

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

    unsigned num_of_methods = (unsigned)PyList_Size(self->interface_list);

    self->vtable = malloc(sizeof(sd_bus_vtable) * (num_of_methods + 2));
    if (self->vtable == NULL)
    {
        return PyErr_NoMemory();
    }

    sd_bus_vtable start_vtable = SD_BUS_VTABLE_START(0);
    self->vtable[0] = start_vtable;
    size_t current_index = 1;
    for (; current_index < num_of_methods + 1; ++current_index)
    {
        PyObject *method_tuple = CALL_PYTHON_AND_CHECK(PyList_GetItem(self->interface_list, current_index - 1));

        SD_BUS_PY_TUPLE_GET_ITEM_AND_CHECK(method_name_object, method_tuple, 0);
        SD_BUS_PY_GET_CHAR_PTR_FROM_PY_UNICODE(method_name_char_ptr, method_name_object);

        SD_BUS_PY_TUPLE_GET_ITEM_AND_CHECK(input_signature_object, method_tuple, 1);
        SD_BUS_PY_GET_CHAR_PTR_FROM_PY_UNICODE(input_signature_char_ptr, input_signature_object);

        SD_BUS_PY_TUPLE_GET_ITEM_AND_CHECK(result_signature_object, method_tuple, 2);
        SD_BUS_PY_GET_CHAR_PTR_FROM_PY_UNICODE(result_signature_char_ptr, result_signature_object);

        SD_BUS_PY_TUPLE_GET_ITEM_AND_CHECK(argument_names_string, method_tuple, 3);

        const char *argument_names_char_ptr = PyUnicode_AsUTF8(argument_names_string);
        if (argument_names_char_ptr == NULL)
        {
            return NULL;
        }

        SD_BUS_PY_TUPLE_GET_ITEM_AND_CHECK(flags_object, method_tuple, 4);
        long flags_long = PyLong_AsLong(flags_object);
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
    sd_bus_vtable end_vtable = SD_BUS_VTABLE_END;
    self->vtable[current_index] = end_vtable;

    Py_RETURN_NONE;
}

static PyMethodDef SdBusInterface_methods[] = {
    {"add_method", (void *)SdBusInterface_add_method, METH_FASTCALL, "Add method to the dbus interface"},
    {"_create_vtable", (void *)SdBusInterface_create_vtable, METH_FASTCALL, "Creates the vtable"},
    {NULL, NULL, 0, NULL},
};

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

    int return_value = sd_bus_message_dump(self->message_ref, 0, SD_BUS_MESSAGE_DUMP_WITH_HEADER);
    SD_BUS_PY_CHECK_RETURN_VALUE(PyExc_RuntimeError);
    return_value = sd_bus_message_rewind(self->message_ref, 1);
    SD_BUS_PY_CHECK_RETURN_VALUE(PyExc_RuntimeError);
    Py_RETURN_NONE;
}

static PyObject *
SdBusMessage_add_bytes_array(SdBusMessageObject *self,
                             PyObject *const *args,
                             Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(1);
    PyObject *bytes_or_b_array = args[0];
    char *char_ptr_to_add = NULL;
    ssize_t size_of_array = 0;
    if (PyByteArray_Check(bytes_or_b_array))
    {
        char_ptr_to_add = PyByteArray_AsString(bytes_or_b_array);
        if (char_ptr_to_add == NULL)
        {
            return NULL;
        }
        size_of_array = PyByteArray_Size(bytes_or_b_array);
        if (size_of_array == -1)
        {
            return NULL;
        }
    }
    else if (PyBytes_Check(bytes_or_b_array))
    {
        char_ptr_to_add = PyBytes_AsString(bytes_or_b_array);
        if (char_ptr_to_add == NULL)
        {
            return NULL;
        }
        size_of_array = PyBytes_Size(bytes_or_b_array);
        if (size_of_array == -1)
        {
            return NULL;
        }
    }
    else
    {
        PyErr_SetString(PyExc_TypeError, "Not a bytes or byte array object passed.");
        return NULL;
    }

    int return_value = sd_bus_message_append_array(self->message_ref, 'y', char_ptr_to_add, (size_t)size_of_array);
    SD_BUS_PY_CHECK_RETURN_VALUE(PyExc_RuntimeError);
    Py_RETURN_NONE;
}

#define SD_BUS_PY_APPEND_INT_CASE(var_type, var_name, pylong_func)                       \
    ;                                                                                    \
    var_type var_name = (var_type)pylong_func(current_arg);                              \
    if (PyErr_Occurred())                                                                \
    {                                                                                    \
        return NULL;                                                                     \
    }                                                                                    \
    return_value = sd_bus_message_append_basic(self->message_ref, type_char, &var_name); \
    SD_BUS_PY_CHECK_RETURN_VALUE(PyExc_RuntimeError);

static PyObject *
SdBusMessage_append_basic(SdBusMessageObject *self,
                          PyObject *const *args,
                          Py_ssize_t nargs)
{
    if (nargs < 2)
    {
        PyErr_SetString(PyExc_TypeError, "Minimum 2 arguments required");
        return NULL;
    }
    // Get the string iterator
    SD_BUS_PY_CHECK_ARG_CHECK_FUNC(0, PyUnicode_Check);
    PyObject *type_str_iter CLEANUP_PY_OBJECT = PyObject_GetIter(args[0]);

    int return_value = 0;

    int current_index = 1;
    PyObject *current_arg = args[current_index];

    for (;;)
    {
        //Get the string
        PyObject *next_type_str = PyIter_Next(type_str_iter);
        if (next_type_str == NULL)
        {
            if (PyErr_Occurred())
            {
                return NULL;
            }
            else
            {
                Py_RETURN_NONE;
            }
        }

        if (!PyUnicode_Check(next_type_str))
        {
            PyErr_SetString(PyExc_TypeError, "Dbus type character is not a string");
            return NULL;
        }
        SD_BUS_PY_GET_CHAR_PTR_FROM_PY_UNICODE(next_type_char_ptr, next_type_str);
        const char type_char = next_type_char_ptr[0];

        switch (type_char)
        {
        case 'y':
            SD_BUS_PY_APPEND_INT_CASE(uint8_t, the_byte, PyLong_AsUnsignedLong);
            break;
        case 'n':
            SD_BUS_PY_APPEND_INT_CASE(int16_t, the_int16, PyLong_AsLong);
            break;
        case 'q':
            SD_BUS_PY_APPEND_INT_CASE(uint16_t, the_uint16, PyLong_AsUnsignedLong);
            break;
        case 'i':
            SD_BUS_PY_APPEND_INT_CASE(int32_t, the_int, PyLong_AsLong);
            break;
        case 'u':
            SD_BUS_PY_APPEND_INT_CASE(uint32_t, the_uint32, PyLong_AsUnsignedLong);
            break;
        case 'x':
            SD_BUS_PY_APPEND_INT_CASE(int64_t, the_int64, PyLong_AsLongLong);
            break;
        case 't':
            SD_BUS_PY_APPEND_INT_CASE(uint64_t, the_uint64, PyLong_AsUnsignedLongLong);
            break;
        case 'h':
            SD_BUS_PY_APPEND_INT_CASE(int, the_fd, PyLong_AsLong);
            break;

        case 'b':;
            if (!PyBool_Check(current_arg))
            {
                PyErr_SetString(PyExc_TypeError, "Expected boolean");
                return NULL;
            }
            int bool_to_add = (current_arg == Py_True);
            return_value = sd_bus_message_append_basic(self->message_ref, type_char, &bool_to_add);
            SD_BUS_PY_CHECK_RETURN_VALUE(PyExc_RuntimeError);
            break;
        case 'd':;
            double double_to_add = PyFloat_AsDouble(current_arg);
            if (PyErr_Occurred())
            {
                return NULL;
            }
            return_value = sd_bus_message_append_basic(self->message_ref, type_char, &double_to_add);
            SD_BUS_PY_CHECK_RETURN_VALUE(PyExc_RuntimeError);
            break;
        case 'o':
        case 'g':
        case 's':;
            SD_BUS_PY_GET_CHAR_PTR_FROM_PY_UNICODE(the_string, current_arg);
            return_value = sd_bus_message_append_basic(self->message_ref, type_char, the_string);
            SD_BUS_PY_CHECK_RETURN_VALUE(PyExc_RuntimeError);
            break;
        default:
            PyErr_SetString(PyExc_ValueError, "Uknown type");
            return NULL;
            break;
        }
        ++current_index;
        current_arg = args[current_index];
    }
    Py_UNREACHABLE();
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

    int return_value = sd_bus_message_open_container(self->message_ref, container_type_char_ptr[0], container_contents_char_ptr);
    SD_BUS_PY_CHECK_RETURN_VALUE(PyExc_RuntimeError);
    Py_RETURN_NONE;
}

static PyObject *
SdBusMessage_close_container(SdBusMessageObject *self,
                             PyObject *const *Py_UNUSED(args),
                             Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(0);
    int return_value = sd_bus_message_close_container(self->message_ref);
    SD_BUS_PY_CHECK_RETURN_VALUE(PyExc_RuntimeError);
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

    int return_value = sd_bus_message_enter_container(self->message_ref, container_type_char_ptr[0], container_contents_char_ptr);
    SD_BUS_PY_CHECK_RETURN_VALUE(PyExc_RuntimeError);
    Py_RETURN_NONE;
}

static PyObject *
SdBusMessage_exit_container(SdBusMessageObject *self,
                            PyObject *const *Py_UNUSED(args),
                            Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(0);
    int return_value = sd_bus_message_exit_container(self->message_ref);
    SD_BUS_PY_CHECK_RETURN_VALUE(PyExc_RuntimeError);
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
    int return_value = sd_bus_send(NULL, self->message_ref, NULL);
    SD_BUS_PY_CHECK_RETURN_VALUE(PyExc_RuntimeError);
    Py_RETURN_NONE;
}

PyObject *_iter_message_array(SdBusMessageObject *self, const char *array_type);
PyObject *_iter_message_structure(SdBusMessageObject *self, int force_tuple);
PyObject *_iter_message_dictionary(SdBusMessageObject *self);
PyObject *_iter_message_variant(SdBusMessageObject *self, const char *container_type);
PyObject *_iter_message_basic_type(SdBusMessageObject *self, char basic_type);

PyObject *_iter_message_array(SdBusMessageObject *self, const char *array_type)
{
    PyObject *new_list CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyList_New(0));

    switch (array_type[0])
    {
    case SD_BUS_TYPE_DICT_ENTRY_BEGIN:
    {
        CALL_SD_BUS_AND_CHECK(sd_bus_message_enter_container(self->message_ref, 'a', array_type));
        PyObject *new_dict = CALL_PYTHON_AND_CHECK(_iter_message_dictionary(self));
        CALL_SD_BUS_AND_CHECK(sd_bus_message_exit_container(self->message_ref));
        return new_dict;
    }
    case 'a':
    {
        CALL_SD_BUS_AND_CHECK(sd_bus_message_enter_container(self->message_ref, array_type[0], array_type));
        while (CALL_SD_BUS_AND_CHECK(sd_bus_message_at_end(self->message_ref, 0)) == 0)
        {
            PyObject *new_nested_array CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(_iter_message_array(self, array_type + 1));
            if (PyList_Append(new_list, new_nested_array) < 0)
            {
                return NULL;
            }
        }
        CALL_SD_BUS_AND_CHECK(sd_bus_message_exit_container(self->message_ref));
        break;
    }
    case 'v':
    {
        char peek_type = '\0';
        const char *container_type = NULL;

        CALL_SD_BUS_AND_CHECK(sd_bus_message_enter_container(self->message_ref, 'a', "v"));
        while (CALL_SD_BUS_AND_CHECK(sd_bus_message_peek_type(self->message_ref, &peek_type, &container_type)) > 0)
        {
            CALL_SD_BUS_AND_CHECK(sd_bus_message_enter_container(self->message_ref, peek_type, container_type));
            PyObject *new_variant CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(_iter_message_variant(self, container_type));

            if (PyList_Append(new_list, new_variant) < 0)
            {
                return NULL;
            }
            CALL_SD_BUS_AND_CHECK(sd_bus_message_exit_container(self->message_ref));
        }
        CALL_SD_BUS_AND_CHECK(sd_bus_message_exit_container(self->message_ref));

        break;
    }
    default:
    {
        if (strcmp(array_type, "y") != 0)
        {
            CALL_SD_BUS_AND_CHECK(sd_bus_message_enter_container(self->message_ref, 'a', array_type));
            for (;;)
            {
                PyObject *new_object CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(_iter_message_basic_type(self, array_type[0]));

                if (new_object == Py_None)
                {
                    break;
                }

                if (PyList_Append(new_list, new_object) < 0)
                {
                    return NULL;
                }
            }
            CALL_SD_BUS_AND_CHECK(sd_bus_message_exit_container(self->message_ref));
        }
        else
        {
            // Array of bytes will be converted to Bytes object
            const void *char_array = NULL;
            size_t array_size = 0;
            CALL_SD_BUS_AND_CHECK(sd_bus_message_read_array(self->message_ref, 'y', &char_array, &array_size));
            return PyBytes_FromStringAndSize(char_array, (Py_ssize_t)array_size);
        }

        break;
    }
    }
    Py_INCREF(new_list);
    return new_list;
}

PyObject *_iter_message_structure(SdBusMessageObject *self, int force_tuple)
{
    PyObject *new_structure_list CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyList_New(0));

    char peek_type = '\0';
    const char *container_type = NULL;
    while (CALL_SD_BUS_AND_CHECK(sd_bus_message_peek_type(self->message_ref, &peek_type, &container_type)) > 0)
    {
        switch (peek_type)
        {

        case SD_BUS_TYPE_ARRAY:
        {
            PyObject *new_array_list CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(_iter_message_array(self, container_type));
            if (PyList_Append(new_structure_list, new_array_list) < 0)
            {
                return NULL;
            }
            break;
        }
        case SD_BUS_TYPE_DICT_ENTRY:
        {
            PyObject *new_dict CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(_iter_message_dictionary(self));
            if (PyList_Append(new_structure_list, new_dict) < 0)
            {
                return NULL;
            }
            break;
        }
        case SD_BUS_TYPE_STRUCT:
        {
            CALL_SD_BUS_AND_CHECK(sd_bus_message_enter_container(self->message_ref, peek_type, container_type));
            PyObject *new_struct CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(_iter_message_structure(self, 1));
            if (PyList_Append(new_structure_list, new_struct) < 0)
            {
                return NULL;
            }
            CALL_SD_BUS_AND_CHECK(sd_bus_message_exit_container(self->message_ref));
            break;
        }
        case SD_BUS_TYPE_VARIANT:
        {
            CALL_SD_BUS_AND_CHECK(sd_bus_message_enter_container(self->message_ref, peek_type, container_type));
            PyObject *new_variant CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(_iter_message_variant(self, container_type));
            CALL_SD_BUS_AND_CHECK(sd_bus_message_exit_container(self->message_ref));
            if (PyList_Append(new_structure_list, new_variant) < 0)
            {
                return NULL;
            }
            break;
        }
        default:
        {
            PyObject *new_basic CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(_iter_message_basic_type(self, peek_type));
            if (PyList_Append(new_structure_list, new_basic) < 0)
            {
                return NULL;
            }
            break;
        }
        }
    }

    if (force_tuple || (PyList_GET_SIZE(new_structure_list) > 1))
    {
        return PySequence_Tuple(new_structure_list);
    }
    else
    {
        PyObject *first_item = CALL_PYTHON_AND_CHECK(PyList_GetItem(new_structure_list, 0));
        Py_INCREF(first_item);
        return first_item;
    }
}

PyObject *_iter_message_dictionary(SdBusMessageObject *self)
{
    PyObject *new_dict CLEANUP_PY_OBJECT = PyDict_New();

    char peek_type = '\0';
    const char *container_type = NULL;
    while (CALL_SD_BUS_AND_CHECK(sd_bus_message_peek_type(self->message_ref, &peek_type, &container_type)) > 0)
    {
        if (peek_type != SD_BUS_TYPE_DICT_ENTRY)
        {
            PyErr_SetString(PyExc_TypeError, "Expected dict entry.");
            return NULL;
        }
        CALL_SD_BUS_AND_CHECK(sd_bus_message_enter_container(self->message_ref, peek_type, container_type));
        PyObject *key_object CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(_iter_message_basic_type(self, container_type[0]));
        PyObject *value_object CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(_iter_message_structure(self, 0));
        CALL_SD_BUS_AND_CHECK(sd_bus_message_exit_container(self->message_ref));
        if (PyDict_SetItem(new_dict, key_object, value_object) < 0)
        {
            return NULL;
        }
    }

    Py_INCREF(new_dict);
    return new_dict;
}

PyObject *_iter_message_variant(SdBusMessageObject *self, const char *container_type)
{
    PyObject *value_object CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(_iter_message_structure(self, 0));
    return PyTuple_Pack(2, CALL_PYTHON_AND_CHECK(PyUnicode_FromString(container_type)), value_object);
}

#define _ITER_RETURN_NONE_ON_ZERO(other_func) \
    if (other_func == 0)                      \
    {                                         \
        Py_RETURN_NONE;                       \
    }

PyObject *_iter_message_basic_type(SdBusMessageObject *self, char basic_type)
{
    switch (basic_type)
    {
    case 'b':;
        int new_int = 0;
        _ITER_RETURN_NONE_ON_ZERO(CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(self->message_ref, basic_type, &new_int)));
        return PyBool_FromLong(new_int);
        break;

    case 'y':;
        uint8_t new_char = 0;
        _ITER_RETURN_NONE_ON_ZERO(CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(self->message_ref, basic_type, &new_char)));
        return PyLong_FromUnsignedLong((unsigned long)new_char);
        break;
    case 'n':;
        int16_t new_short = 0;
        _ITER_RETURN_NONE_ON_ZERO(CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(self->message_ref, basic_type, &new_short)));
        return PyLong_FromLong((long)new_short);
        break;

    case 'i':;
        int32_t new_long = 0;
        _ITER_RETURN_NONE_ON_ZERO(CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(self->message_ref, basic_type, &new_long)));
        return PyLong_FromLong((long)new_long);
        break;

    case 'x':;
        int64_t new_long_long = 0;
        _ITER_RETURN_NONE_ON_ZERO(CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(self->message_ref, basic_type, &new_long_long)));
        return PyLong_FromLongLong((long long)new_long_long);
        break;

    case 'q':;
        uint16_t new_u_short = 0;
        _ITER_RETURN_NONE_ON_ZERO(CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(self->message_ref, basic_type, &new_u_short)));
        return PyLong_FromUnsignedLong((unsigned long)new_u_short);
        break;
    case 'u':;
        uint32_t new_u_long = 0;
        _ITER_RETURN_NONE_ON_ZERO(CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(self->message_ref, basic_type, &new_u_long)));
        return PyLong_FromUnsignedLong((unsigned long)new_u_long);
        break;
    case 't':;
        uint64_t new_u_long_long = 0;
        CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(self->message_ref, basic_type, &new_u_long_long));
        return PyLong_FromUnsignedLongLong((unsigned long long)new_u_long_long);
        break;

    case 'd':;
        double new_double = 0.0;
        _ITER_RETURN_NONE_ON_ZERO(CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(self->message_ref, basic_type, &new_double)));
        return PyFloat_FromDouble(new_double);
        break;
    case 'h':;
        int new_fd = 0;
        _ITER_RETURN_NONE_ON_ZERO(CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(self->message_ref, basic_type, &new_fd)));
        return PyLong_FromLong((long)new_fd);
        break;

    case 'g':
    case 'o':
    case 's':;
        const char *new_string = NULL;
        _ITER_RETURN_NONE_ON_ZERO(CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(self->message_ref, basic_type, &new_string)));
        return PyUnicode_FromString(new_string);
        break;

    default:
        PyErr_SetString(PyExc_NotImplementedError, "Dbus type unknown or not implemented yet");
        return NULL;
        break;
    }
}

static PyObject *
SdBusMessage_get_contents(SdBusMessageObject *self,
                          PyObject *Py_UNUSED(args))
{
    return _iter_message_structure(self, 1);
}

static PyMethodDef SdBusMessage_methods[] = {
    {"add_bytes_array", (void *)SdBusMessage_add_bytes_array, METH_FASTCALL, "Add bytes array to message. Takes either bytes or byte array object"},
    {"append_basic", (void *)SdBusMessage_append_basic, METH_FASTCALL, "Append basic data based on signature."},
    {"open_container", (void *)SdBusMessage_open_container, METH_FASTCALL, "Open container for writting"},
    {"close_container", (void *)SdBusMessage_close_container, METH_FASTCALL, "Close container"},
    {"enter_container", (void *)SdBusMessage_enter_container, METH_FASTCALL, "Enter container for reading"},
    {"exit_container", (void *)SdBusMessage_exit_container, METH_FASTCALL, "Exit container"},
    {"dump", (void *)SdBusMessage_dump, METH_FASTCALL, "Dump message to stdout"},
    {"seal", (void *)SdBusMessage_seal, METH_FASTCALL, "Seal message contents"},
    {"get_contents", (PyCFunction)SdBusMessage_get_contents, METH_NOARGS, "Iterate over message contents"},
    {"create_reply", (void *)SdBusMessage_create_reply, METH_FASTCALL, "Create reply message"},
    {"send", (void *)SdBusMessage_send, METH_FASTCALL, "Queue message to be sent"},
    {NULL, NULL, 0, NULL},
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
};

static SdBusMessageObject *
SdBusMessage_create_reply(SdBusMessageObject *self,
                          PyObject *const *Py_UNUSED(args),
                          Py_ssize_t nargs)
{
    SD_BUS_PY_CHECK_ARGS_NUMBER(0);
    SdBusMessageObject *new_reply_message CLEANUP_SD_BUS_MESSAGE = (SdBusMessageObject *)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs((PyObject *)&SdBusMessageType, NULL));

    int return_value = sd_bus_message_new_method_return(self->message_ref, &new_reply_message->message_ref);
    SD_BUS_PY_CHECK_RETURN_VALUE(PyExc_RuntimeError);
    Py_INCREF(new_reply_message);
    return new_reply_message;
}

// SdBus
typedef struct
{
    PyObject_HEAD;
    sd_bus *sd_bus_ref;
    PyObject *sd_bus_fd;
} SdBusObject;

int _SdBus_start_drive(SdBusObject *self);

static void
SdBus_free(SdBusObject *self)
{
    sd_bus_unref(self->sd_bus_ref);
    PyObject_Free(self);
}

static int
SdBus_init(SdBusObject *self, PyObject *Py_UNUSED(args), PyObject *Py_UNUSED(kwds))
{
    self->sd_bus_ref = NULL;
    self->sd_bus_fd = NULL;
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

    const char *destination_bus_name = PyUnicode_AsUTF8(args[0]);
    const char *object_path = PyUnicode_AsUTF8(args[1]);
    const char *interface_name = PyUnicode_AsUTF8(args[2]);
    const char *member_name = PyUnicode_AsUTF8(args[3]);

    SdBusMessageObject *new_message_object CLEANUP_SD_BUS_MESSAGE = (SdBusMessageObject *)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs((PyObject *)&SdBusMessageType, NULL));

    int return_value = sd_bus_message_new_method_call(
        self->sd_bus_ref,
        &new_message_object->message_ref,
        destination_bus_name,
        object_path,
        interface_name,
        member_name);
    SD_BUS_PY_CHECK_RETURN_VALUE(PyExc_RuntimeError);
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

    SdBusMessageObject *reply_message_object = (SdBusMessageObject *)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs((PyObject *)&SdBusMessageType, NULL));

    sd_bus_error error __attribute__((cleanup(sd_bus_error_free))) = SD_BUS_ERROR_NULL;

    int return_value = sd_bus_call(
        self->sd_bus_ref,
        call_message->message_ref,
        (uint64_t)0,
        &error,
        &reply_message_object->message_ref);

    if (error.name != NULL)
    {
        PyObject *exception_to_raise = PyDict_GetItemString(exception_dict, error.name);
        if (exception_to_raise == NULL)
        {
            exception_to_raise = exception_generic;
        }
        PyErr_SetObject(exception_to_raise, Py_BuildValue("(ss)", error.name, error.message));
        return NULL;
    }
    else
    {
        SD_BUS_PY_CHECK_RETURN_VALUE(PyExc_RuntimeError);
    }

    return reply_message_object;
}

int future_set_exception_from_message(PyObject *future, sd_bus_message *message)
{
    const sd_bus_error *callback_error = sd_bus_message_get_error(message);

    PyObject *exception_data CLEANUP_PY_OBJECT = Py_BuildValue("(ss)", callback_error->name, callback_error->message);
    if (exception_data == NULL)
    {
        return -1;
    }

    PyObject *exception_to_raise_type = PyDict_GetItemString(exception_dict, callback_error->name);
    if (exception_to_raise_type == NULL)
    {
        exception_to_raise_type = exception_generic;
    }
    PyObject *new_exception CLEANUP_PY_OBJECT = PyObject_Call(exception_to_raise_type, exception_data, NULL);
    if (new_exception == NULL)
    {
        return -1;
    }

    PyObject *return_object CLEANUP_PY_OBJECT = PyObject_CallMethodObjArgs(future, set_exception_str, new_exception, NULL);
    if (return_object == NULL)
    {
        return -1;
    }
    return 0;
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

    int return_value = _SdBus_start_drive(self);
    if (return_value < 0)
    {
        return NULL;
    }

    PyObject *new_future = CALL_PYTHON_AND_CHECK(PyObject_CallMethod(running_loop, "create_future", ""));
    if (new_future == NULL)
    {
        return NULL;
    }

    SdBusSlotObject *new_slot_object CLEANUP_SD_BUS_SLOT = (SdBusSlotObject *)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs((PyObject *)&SdBusSlotType, NULL));

    return_value = sd_bus_call_async(
        self->sd_bus_ref,
        &new_slot_object->slot_ref,
        call_message->message_ref,
        SdBus_async_callback,
        new_future,
        (uint64_t)0);

    SD_BUS_PY_CHECK_RETURN_VALUE(PyExc_RuntimeError);

    return_value = PyObject_SetAttrString(new_future, "_sd_bus_py_slot", (PyObject *)new_slot_object);
    if (return_value < 0)
    {
        return NULL;
    }

    return new_future;
}

static PyObject *
SdBus_drive(SdBusObject *self,
            PyObject *Py_UNUSED(args))
{
    int return_value = 1;
    while (return_value > 0)
    {
        return_value = sd_bus_process(self->sd_bus_ref, NULL);
        SD_BUS_PY_CHECK_RETURN_VALUE(PyExc_RuntimeError);

        if (PyErr_Occurred())
        {
            return NULL;
        }
    }

    Py_RETURN_NONE;
}

static PyObject *
SdBus_get_fd(SdBusObject *self,
             PyObject *Py_UNUSED(args))
{
    int return_value = sd_bus_get_fd(self->sd_bus_ref);
    SD_BUS_PY_CHECK_RETURN_VALUE(PyExc_RuntimeError);

    return PyLong_FromLong((long)return_value);
}

int _SdBus_start_drive(SdBusObject *self)
{
    if (self->sd_bus_fd != NULL)
    {
        return 0;
    }

    PyObject *running_loop CLEANUP_PY_OBJECT = PyObject_CallFunctionObjArgs(asyncio_get_running_loop, NULL);
    if (running_loop == NULL)
    {
        return -1;
    }

    PyObject *new_fd CLEANUP_PY_OBJECT = SdBus_get_fd(self, NULL);
    if (new_fd == NULL)
    {
        return -1;
    }

    PyObject *drive_method CLEANUP_PY_OBJECT = PyObject_GetAttrString((PyObject *)self, "drive");
    if (drive_method == NULL)
    {
        return -1;
    }

    PyObject *should_be_none = PyObject_CallMethod(running_loop, "add_reader", "OO", new_fd, drive_method);
    if (should_be_none == NULL)
    {
        return -1;
    }

    self->sd_bus_fd = new_fd;
    return 0;
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

    int return_value = sd_bus_add_object_vtable(self->sd_bus_ref, &interface_object->interface_slot->slot_ref,
                                                path_char_ptr, interface_name_char_ptr,
                                                interface_object->vtable,
                                                args[0]);

    SD_BUS_PY_CHECK_RETURN_VALUE(PyExc_RuntimeError);

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
    int return_value = PyObject_SetAttrString(new_queue, "_sd_bus_slot", (PyObject *)new_slot);
    if (return_value < 0)
    {
        return NULL;
    }

    PyObject *running_loop CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(asyncio_get_running_loop, NULL));

    PyObject *new_future CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_CallMethod(running_loop, "create_future", ""));

    // Bind lifetime of the queue to future
    return_value = PyObject_SetAttrString(new_future, "_sd_bus_queue", new_queue);
    if (return_value < 0)
    {
        return NULL;
    }

    return_value = sd_bus_match_signal_async(self->sd_bus_ref, &new_slot->slot_ref,
                                             sender_service_char_ptr, path_name_char_ptr, interface_name_char_ptr, member_name_char_ptr,
                                             _SdBus_signal_callback, _SdBus_match_signal_instant_callback, new_future);
    SD_BUS_PY_CHECK_RETURN_VALUE(PyExc_RuntimeError);

    Py_INCREF(new_future);
    return new_future;
}

static PyMethodDef SdBus_methods[] = {
    {"call", (void *)SdBus_call, METH_FASTCALL, "Send message and get reply"},
    {"call_async", (void *)SdBus_call_async, METH_FASTCALL, "Async send message, returns awaitable future"},
    {"drive", (void *)SdBus_drive, METH_FASTCALL, "Drive connection"},
    {"get_fd", (void *)SdBus_get_fd, METH_FASTCALL, "Get file descriptor to await on"},
    {"new_method_call_message", (void *)SdBus_new_method_call_message, METH_FASTCALL, NULL},
    {"add_interface", (void *)SdBus_add_interface, METH_FASTCALL, "Add interface to the bus"},
    {"get_signal_queue_async", (void *)SdBus_get_signal_queue, METH_FASTCALL, "Returns a future that returns a queue that queues signal messages"},
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

static PyObject *is_coroutine_function = NULL;

static int _SdBusInterface_callback(sd_bus_message *m, void *userdata, sd_bus_error *ret_error)
{
    SdBusInterfaceObject *self = userdata;
    // Get the memeber name from the message
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

static SdBusObject *
get_default_sd_bus(PyObject *Py_UNUSED(self),
                   PyObject *Py_UNUSED(ignored))
{
    SdBusObject *new_sd_bus = (SdBusObject *)PyObject_CallFunctionObjArgs((PyObject *)&SdBusType, NULL);

    int return_value = sd_bus_default(&(new_sd_bus->sd_bus_ref));
    SD_BUS_PY_CHECK_RETURN_VALUE(PyExc_RuntimeError);
    return new_sd_bus;
}

void _cleanup_encode(char **ptr)
{
    if (*ptr != NULL)
    {
        free(*ptr);
    }
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

    char *new_char_ptr __attribute__((cleanup(_cleanup_encode))) = NULL;

    int return_value = sd_bus_path_encode(prefix_char_ptr, external_char_ptr, &new_char_ptr);
    SD_BUS_PY_CHECK_RETURN_VALUE(PyExc_RuntimeError);

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

    char *new_char_ptr __attribute__((cleanup(_cleanup_encode))) = NULL;

    int return_value = sd_bus_path_decode(full_path_char_ptr, prefix_char_ptr, &new_char_ptr);
    SD_BUS_PY_CHECK_RETURN_VALUE(PyExc_RuntimeError);

    if (new_char_ptr)
    {
        return PyUnicode_FromString(new_char_ptr);
    }
    else
    {
        return PyUnicode_FromString("");
    }
}

static PyMethodDef SdBusPyInternal_methods[] = {
    {"get_default_bus", (PyCFunction)get_default_sd_bus, METH_NOARGS, "Get default bus. Session bus running as user or system bus as daemon"},
    {"encode_object_path", (void *)encode_object_path, METH_FASTCALL, "Encode object path with object path prefix and arbitrary string"},
    {"decode_object_path", (void *)decode_object_path, METH_FASTCALL, "Decode object path with object path prefix and arbitrary string"},
    {NULL, NULL, 0, NULL},
};

static PyModuleDef sd_bus_internals_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "sd_bus_internals",
    .m_doc = "Sd bus internals module.",
    .m_methods = SdBusPyInternal_methods,
    .m_size = -1,
};

#define TEST_FAILURE(test_statement) \
    if (test_statement)              \
    {                                \
        Py_DECREF(m);                \
        return NULL;                 \
    }

PyMODINIT_FUNC
PyInit_sd_bus_internals(void)
{
    PyObject *m;
    if (PyType_Ready(&SdBusType) < 0)
    {
        return NULL;
    }
    if (PyType_Ready(&SdBusMessageType) < 0)
    {
        return NULL;
    }
    if (PyType_Ready(&SdBusSlotType) < 0)
    {
        return NULL;
    }
    if (PyType_Ready(&SdBusInterfaceType) < 0)
    {
        return NULL;
    }

    m = PyModule_Create(&sd_bus_internals_module);
    if (m == NULL)
    {
        return NULL;
    }

    Py_INCREF(&SdBusType);
    if (PyModule_AddObject(m, "SdBus", (PyObject *)&SdBusType) < 0)
    {
        Py_DECREF(&SdBusType);
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddObject(m, "SdBusMessage", (PyObject *)&SdBusMessageType) < 0)
    {
        Py_DECREF(&SdBusMessageType);
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddObject(m, "SdBusSlot", (PyObject *)&SdBusSlotType) < 0)
    {
        Py_DECREF(&SdBusSlotType);
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddObject(m, "SdBusInterface", (PyObject *)&SdBusInterfaceType) < 0)
    {
        Py_DECREF(&SdBusInterfaceType);
        Py_DECREF(m);
        return NULL;
    }

    // Exception map
    exception_dict = PyDict_New();
    if (exception_dict == NULL)
    {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddObject(m, "_ExceptionsMap", exception_dict) < 0)
    {
        Py_XDECREF(exception_dict);
        Py_DECREF(m);
        return NULL;
    }

    // TODO: check if PyErr_NewException can return NULL
    PyObject *new_base_exception = PyErr_NewException("sd_bus_internals.DbusBaseError", NULL, NULL);
    if (PyModule_AddObject(m, "DbusBaseError", new_base_exception) < 0)
    {
        Py_XDECREF(new_base_exception);
        Py_DECREF(m);
        return NULL;
    }
    exception_default = new_base_exception;

    PyObject *new_exception = NULL;
#define SD_BUS_PY_ADD_EXCEPTION(exception_name, dbus_string)                                              \
    new_exception = PyErr_NewException("sd_bus_internals." #exception_name "", new_base_exception, NULL); \
    PyDict_SetItemString(exception_dict, dbus_string, new_exception);                                     \
    if (PyModule_AddObject(m, #exception_name, new_exception) < 0)                                        \
    {                                                                                                     \
        Py_XDECREF(new_exception);                                                                        \
        Py_DECREF(m);                                                                                     \
        return NULL;                                                                                      \
    }

    SD_BUS_PY_ADD_EXCEPTION(DbusFailedError, SD_BUS_ERROR_FAILED);
    SD_BUS_PY_ADD_EXCEPTION(DbusNoMemoryError, SD_BUS_ERROR_NO_MEMORY);
    SD_BUS_PY_ADD_EXCEPTION(DbusServiceUnknownError, SD_BUS_ERROR_SERVICE_UNKNOWN);
    SD_BUS_PY_ADD_EXCEPTION(DbusNameHasNoOwnerError, SD_BUS_ERROR_NAME_HAS_NO_OWNER);
    SD_BUS_PY_ADD_EXCEPTION(DbusNoReplyError, SD_BUS_ERROR_NO_REPLY);
    SD_BUS_PY_ADD_EXCEPTION(DbusIOError, SD_BUS_ERROR_IO_ERROR);
    SD_BUS_PY_ADD_EXCEPTION(DbusBadAddressError, SD_BUS_ERROR_BAD_ADDRESS);
    SD_BUS_PY_ADD_EXCEPTION(DbusNotSupportedError, SD_BUS_ERROR_NOT_SUPPORTED);
    SD_BUS_PY_ADD_EXCEPTION(DbusLimitsExceededError, SD_BUS_ERROR_LIMITS_EXCEEDED);
    SD_BUS_PY_ADD_EXCEPTION(DbusAccessDeniedError, SD_BUS_ERROR_ACCESS_DENIED);
    SD_BUS_PY_ADD_EXCEPTION(DbusAuthFailedError, SD_BUS_ERROR_AUTH_FAILED);
    SD_BUS_PY_ADD_EXCEPTION(DbusNoServerError, SD_BUS_ERROR_NO_SERVER);
    SD_BUS_PY_ADD_EXCEPTION(DbusTimeoutError, SD_BUS_ERROR_TIMEOUT);
    SD_BUS_PY_ADD_EXCEPTION(DbusNoNetworkError, SD_BUS_ERROR_NO_NETWORK);
    SD_BUS_PY_ADD_EXCEPTION(DbusAddressInUseError, SD_BUS_ERROR_ADDRESS_IN_USE);
    SD_BUS_PY_ADD_EXCEPTION(DbusDisconnectedError, SD_BUS_ERROR_DISCONNECTED);
    SD_BUS_PY_ADD_EXCEPTION(DbusInvalidArgsError, SD_BUS_ERROR_INVALID_ARGS);
    SD_BUS_PY_ADD_EXCEPTION(DbusFileExistsError, SD_BUS_ERROR_FILE_EXISTS);
    SD_BUS_PY_ADD_EXCEPTION(DbusUnknownMethodError, SD_BUS_ERROR_UNKNOWN_METHOD);
    SD_BUS_PY_ADD_EXCEPTION(DbusUnknownObjectError, SD_BUS_ERROR_UNKNOWN_OBJECT);
    SD_BUS_PY_ADD_EXCEPTION(DbusUnknownInterfaceError, SD_BUS_ERROR_UNKNOWN_INTERFACE);
    SD_BUS_PY_ADD_EXCEPTION(DbusUnknownPropertyError, SD_BUS_ERROR_UNKNOWN_PROPERTY);
    SD_BUS_PY_ADD_EXCEPTION(DbusPropertyReadOnlyError, SD_BUS_ERROR_PROPERTY_READ_ONLY);
    SD_BUS_PY_ADD_EXCEPTION(DbusUnixProcessIdUnknownError, SD_BUS_ERROR_UNIX_PROCESS_ID_UNKNOWN);
    SD_BUS_PY_ADD_EXCEPTION(DbusInvalidSignatureError, SD_BUS_ERROR_INVALID_SIGNATURE);
    SD_BUS_PY_ADD_EXCEPTION(DbusInconsistentMessageError, SD_BUS_ERROR_INCONSISTENT_MESSAGE);
    SD_BUS_PY_ADD_EXCEPTION(DbusMatchRuleNotFound, SD_BUS_ERROR_MATCH_RULE_NOT_FOUND);
    SD_BUS_PY_ADD_EXCEPTION(DbusMatchRuleInvalidError, SD_BUS_ERROR_MATCH_RULE_INVALID);
    SD_BUS_PY_ADD_EXCEPTION(DbusInteractiveAuthorizationRequiredError, SD_BUS_ERROR_INTERACTIVE_AUTHORIZATION_REQUIRED);

    exception_generic = PyErr_NewException("sd_bus_internals.DbusGenericError", new_base_exception, NULL);
    if (PyModule_AddObject(m, "DbusGenericError", exception_generic) < 0)
    {
        Py_XDECREF(exception_generic);
        Py_DECREF(m);
        return NULL;
    }

    PyObject *asyncio_module = PyImport_ImportModule("asyncio");
    TEST_FAILURE(asyncio_module == NULL);
    async_future_type = (PyTypeObject *)PyObject_GetAttrString(asyncio_module, "Future");
    TEST_FAILURE(async_future_type == NULL);
    TEST_FAILURE(!PyType_Check(async_future_type));
    TEST_FAILURE(PyType_Ready(async_future_type) < 0);

    asyncio_get_running_loop = PyObject_GetAttrString(asyncio_module, "get_running_loop");
    TEST_FAILURE(asyncio_get_running_loop == NULL);

    asyncio_queue_class = PyObject_GetAttrString(asyncio_module, "Queue");
    TEST_FAILURE(asyncio_queue_class == NULL)

    set_result_str = PyUnicode_FromString("set_result");
    TEST_FAILURE(set_result_str == NULL);
    set_exception_str = PyUnicode_FromString("set_exception");
    TEST_FAILURE(set_exception_str == NULL);
    put_no_wait_str = PyUnicode_FromString("put_nowait");
    TEST_FAILURE(put_no_wait_str == NULL);

    call_soon_str = PyUnicode_FromString("call_soon");
    TEST_FAILURE(call_soon_str == NULL);
    create_task_str = PyUnicode_FromString("create_task");
    TEST_FAILURE(create_task_str == NULL);

    PyObject *inspect_module = PyImport_ImportModule("inspect");
    TEST_FAILURE(inspect_module == NULL)
    is_coroutine_function = PyObject_GetAttrString(inspect_module, "iscoroutinefunction");
    TEST_FAILURE(is_coroutine_function == NULL);

    return m;
}