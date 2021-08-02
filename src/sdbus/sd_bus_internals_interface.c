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

// TODO: adding interface to different buses, recalculating vtable

static int SdBusInterface_init(SdBusInterfaceObject* self, PyObject* Py_UNUSED(args), PyObject* Py_UNUSED(kwds)) {
        self->interface_slot = (SdBusSlotObject*)CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallFunctionObjArgs(SdBusSlot_class, NULL));
        self->method_list = CALL_PYTHON_CHECK_RETURN_NEG1(PyList_New((Py_ssize_t)0));
        self->method_dict = CALL_PYTHON_CHECK_RETURN_NEG1(PyDict_New());
        self->property_list = CALL_PYTHON_CHECK_RETURN_NEG1(PyList_New((Py_ssize_t)0));
        self->property_get_dict = CALL_PYTHON_CHECK_RETURN_NEG1(PyDict_New());
        self->property_set_dict = CALL_PYTHON_CHECK_RETURN_NEG1(PyDict_New());
        self->signal_list = CALL_PYTHON_CHECK_RETURN_NEG1(PyList_New((Py_ssize_t)0));
        self->vtable = NULL;
        return 0;
}

static void SdBusInterface_dealloc(SdBusInterfaceObject* self) {
        Py_XDECREF(self->interface_slot);
        Py_XDECREF(self->method_list);
        Py_XDECREF(self->method_dict);
        Py_XDECREF(self->property_list);
        Py_XDECREF(self->property_get_dict);
        Py_XDECREF(self->property_set_dict);
        Py_XDECREF(self->signal_list);
        if (self->vtable) {
                free(self->vtable);
        }

        SD_BUS_DEALLOC_TAIL;
}

inline int _check_callable_or_none(PyObject* some_object) {
        return PyCallable_Check(some_object) || (Py_None == some_object);
}

#ifndef Py_LIMITED_API
static PyObject* SdBusInterface_add_property(SdBusInterfaceObject* self, PyObject* const* args, Py_ssize_t nargs) {
        // Arguments
        // Name, Signature, Get, Set, Flags
        SD_BUS_PY_CHECK_ARGS_NUMBER(5);
        SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(2, PyCallable_Check);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(3, _check_callable_or_none);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(4, PyLong_Check);

        PyObject* name = args[0];
        PyObject* signature = args[1];
        PyObject* getter = args[2];
        PyObject* setter = args[3];
        PyObject* flags = args[4];
#else
static PyObject* SdBusInterface_add_property(SdBusInterfaceObject* self, PyObject* args) {
        PyObject* name = NULL;
        PyObject* signature = NULL;
        PyObject* getter = NULL;
        PyObject* setter = NULL;
        PyObject* flags = NULL;

        CALL_PYTHON_BOOL_CHECK(PyArg_ParseTuple(args, "OOOOO", &name, &signature, &getter, &setter, &flags, NULL));
#endif
        PyObject* name_bytes CLEANUP_PY_OBJECT = SD_BUS_PY_UNICODE_AS_BYTES(name);
        PyObject* signature_bytes CLEANUP_PY_OBJECT = SD_BUS_PY_UNICODE_AS_BYTES(signature);
        PyObject* new_tuple CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyTuple_Pack(4, name_bytes, signature_bytes, flags, setter));

        CALL_PYTHON_INT_CHECK(PyList_Append(self->property_list, new_tuple));
        CALL_PYTHON_INT_CHECK(PyDict_SetItem(self->property_get_dict, name_bytes, getter));
        CALL_PYTHON_INT_CHECK(PyDict_SetItem(self->property_set_dict, name_bytes, setter));

        Py_RETURN_NONE;
}

#ifndef Py_LIMITED_API
static PyObject* SdBusInterface_add_method(SdBusInterfaceObject* self, PyObject* const* args, Py_ssize_t nargs) {
        // Arguments
        // Method name, signature, names of input values, result signature,
        // names of result values, flags, callback function or coroutine
        SD_BUS_PY_CHECK_ARGS_NUMBER(7);
        SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(2, PySequence_Check);
        SD_BUS_PY_CHECK_ARG_TYPE(3, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(4, PySequence_Check);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(5, PyLong_Check);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(6, PyCallable_Check);

        PyObject* method_name = args[0];
        PyObject* input_signature = args[1];
        PyObject* input_names = args[2];
        PyObject* result_signature = args[3];
        PyObject* result_names = args[4];
        PyObject* flags = args[5];
        PyObject* callback_func = args[6];

#else
static PyObject* SdBusInterface_add_method(SdBusInterfaceObject* self, PyObject* args) {
        PyObject* method_name = NULL;
        PyObject* input_signature = NULL;
        PyObject* input_names = NULL;
        PyObject* result_signature = NULL;
        PyObject* result_names = NULL;
        PyObject* flags = NULL;
        PyObject* callback_func = NULL;

        CALL_PYTHON_BOOL_CHECK(
            PyArg_ParseTuple(args, "OOOOOOO", &method_name, &input_signature, &input_names, &result_signature, &result_names, &flags, &callback_func, NULL));
#endif
        PyObject* method_name_bytes CLEANUP_PY_OBJECT = SD_BUS_PY_UNICODE_AS_BYTES(method_name);
        PyObject* input_signature_bytes CLEANUP_PY_OBJECT = SD_BUS_PY_UNICODE_AS_BYTES(input_signature);
        PyObject* result_signature_bytes CLEANUP_PY_OBJECT = SD_BUS_PY_UNICODE_AS_BYTES(result_signature);

        PyObject* argument_name_list CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyList_New(0));
        CALL_PYTHON_EXPECT_NONE(PyObject_CallMethodObjArgs(argument_name_list, extend_str, input_names, NULL));
        CALL_PYTHON_EXPECT_NONE(PyObject_CallMethodObjArgs(argument_name_list, extend_str, result_names, NULL));
        // HACK: add a null separator to the end of the array
        CALL_PYTHON_EXPECT_NONE(PyObject_CallMethodObjArgs(argument_name_list, append_str, null_str, NULL));

        PyObject* argument_names_string CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyUnicode_Join(null_str, argument_name_list));
        PyObject* argument_names_bytes CLEANUP_PY_OBJECT = SD_BUS_PY_UNICODE_AS_BYTES(argument_names_string);
        // Method name, input signature, return signature, arguments names,
        // flags
        PyObject* new_tuple CLEANUP_PY_OBJECT =
            CALL_PYTHON_AND_CHECK(PyTuple_Pack(5, method_name_bytes, input_signature_bytes, result_signature_bytes, argument_names_bytes, flags));

        CALL_PYTHON_INT_CHECK(PyList_Append(self->method_list, new_tuple));
        CALL_PYTHON_INT_CHECK(PyDict_SetItem(self->method_dict, method_name_bytes, callback_func));

        Py_RETURN_NONE;
}

#ifndef Py_LIMITED_API
static PyObject* SdBusInterface_add_signal(SdBusInterfaceObject* self, PyObject* const* args, Py_ssize_t nargs) {
        // Arguments
        // Signal name, signature, names of input values, flags
        SD_BUS_PY_CHECK_ARGS_NUMBER(4);
        SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(2, PySequence_Check);
        SD_BUS_PY_CHECK_ARG_CHECK_FUNC(3, PyLong_Check);

        PyObject* signal_name = args[0];
        PyObject* signature = args[1];
        PyObject* input_names = args[2];
        PyObject* flags = args[3];
#else
static PyObject* SdBusInterface_add_signal(SdBusInterfaceObject* self, PyObject* args) {
        PyObject* signal_name = NULL;
        PyObject* signature = NULL;
        PyObject* input_names = NULL;
        PyObject* flags = NULL;
        CALL_PYTHON_BOOL_CHECK(PyArg_ParseTuple(args, "OOOO", &signal_name, &signature, &input_names, &flags, NULL));
#endif
        PyObject* signal_name_bytes CLEANUP_PY_OBJECT = SD_BUS_PY_UNICODE_AS_BYTES(signal_name);
        PyObject* signature_bytes CLEANUP_PY_OBJECT = SD_BUS_PY_UNICODE_AS_BYTES(signature);

        PyObject* argument_name_list CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyList_New(0));
        CALL_PYTHON_EXPECT_NONE(PyObject_CallMethodObjArgs(argument_name_list, extend_str, input_names, NULL));
        // HACK: add a null separator to the end of the array
        CALL_PYTHON_EXPECT_NONE(PyObject_CallMethodObjArgs(argument_name_list, append_str, null_str, NULL));

        PyObject* argument_names_string CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyUnicode_Join(null_str, argument_name_list));
        PyObject* argument_names_bytes CLEANUP_PY_OBJECT = SD_BUS_PY_UNICODE_AS_BYTES(argument_names_string);
        // Signal name, signature, names of input values, flags
        PyObject* new_tuple CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyTuple_Pack(4, signal_name_bytes, signature_bytes, argument_names_bytes, flags));

        CALL_PYTHON_INT_CHECK(PyList_Append(self->signal_list, new_tuple));

        Py_RETURN_NONE;
}

static int _SdBusInterface_callback(sd_bus_message* m, void* userdata, sd_bus_error* ret_error);

static int _SdBusInterface_property_get_callback(sd_bus* bus,
                                                 const char* path,
                                                 const char* interface,
                                                 const char* property,
                                                 sd_bus_message* reply,
                                                 void* userdata,
                                                 sd_bus_error* ret_error);

static int _SdBusInterface_property_set_callback(sd_bus* bus,
                                                 const char* path,
                                                 const char* interface,
                                                 const char* property,
                                                 sd_bus_message* value,
                                                 void* userdata,
                                                 sd_bus_error* ret_error);

static PyObject* SdBusInterface_create_vtable(SdBusInterfaceObject* self, PyObject* const* Py_UNUSED(args)) {
        if (self->vtable) {
                Py_RETURN_NONE;
        }

        Py_ssize_t num_of_methods = PyList_Size(self->method_list);
        Py_ssize_t num_of_properties = PyList_Size(self->property_list);
        Py_ssize_t num_of_signals = PyList_Size(self->signal_list);

        self->vtable = calloc(num_of_signals + num_of_properties + num_of_methods + 2, sizeof(sd_bus_vtable));
        if (self->vtable == NULL) {
                return PyErr_NoMemory();
        }

        sd_bus_vtable start_vtable = SD_BUS_VTABLE_START(0);
        self->vtable[0] = start_vtable;
        Py_ssize_t current_index = 1;
        // Iter method definitions
        for (Py_ssize_t i = 0; i < num_of_methods; ({
                     ++i;
                     ++current_index;
             })) {
                PyObject* method_tuple = CALL_PYTHON_AND_CHECK(PyList_GetItem(self->method_list, i));

                PyObject* method_name_object = CALL_PYTHON_AND_CHECK(PyTuple_GetItem(method_tuple, 0));
                PyObject* input_signature_object = CALL_PYTHON_AND_CHECK(PyTuple_GetItem(method_tuple, 1));
                PyObject* result_signature_object = CALL_PYTHON_AND_CHECK(PyTuple_GetItem(method_tuple, 2));
                PyObject* argument_names_string = CALL_PYTHON_AND_CHECK(PyTuple_GetItem(method_tuple, 3));

                const char* method_name_char_ptr = SD_BUS_PY_BYTES_AS_CHAR_PTR(method_name_object);
                const char* input_signature_char_ptr = SD_BUS_PY_BYTES_AS_CHAR_PTR(input_signature_object);
                const char* result_signature_char_ptr = SD_BUS_PY_BYTES_AS_CHAR_PTR(result_signature_object);
                const char* argument_names_char_ptr = SD_BUS_PY_BYTES_AS_CHAR_PTR(argument_names_string);

                PyObject* flags_object = CALL_PYTHON_AND_CHECK(PyTuple_GetItem(method_tuple, 4));
                unsigned long long flags_long = PyLong_AsUnsignedLongLong(flags_object);
                if (PyErr_Occurred()) {
                        return NULL;
                }

                sd_bus_vtable temp_vtable = SD_BUS_METHOD_WITH_NAMES_OFFSET(method_name_char_ptr, input_signature_char_ptr, argument_names_char_ptr,
                                                                            result_signature_char_ptr, , _SdBusInterface_callback, 0, flags_long);
                self->vtable[current_index] = temp_vtable;
        }

        for (Py_ssize_t i = 0; i < num_of_properties; ({
                     ++i;
                     ++current_index;
             })) {
                PyObject* property_tuple = SD_BUS_PY_LIST_GET_ITEM(self->property_list, i);

                PyObject* property_name_str = SD_BUS_PY_TUPLE_GET_ITEM(property_tuple, 0);
                PyObject* property_signature_str = SD_BUS_PY_TUPLE_GET_ITEM(property_tuple, 1);
                PyObject* property_flags = SD_BUS_PY_TUPLE_GET_ITEM(property_tuple, 2);
                PyObject* setter_or_none = SD_BUS_PY_TUPLE_GET_ITEM(property_tuple, 3);

                const char* property_name_char_ptr = SD_BUS_PY_BYTES_AS_CHAR_PTR(property_name_str);
                const char* property_signature_const_char = SD_BUS_PY_BYTES_AS_CHAR_PTR(property_signature_str);

                unsigned long long flags_long = PyLong_AsUnsignedLongLong(property_flags);
                if (PyErr_Occurred()) {
                        return NULL;
                }

                if (setter_or_none == Py_None) {
                        sd_bus_vtable temp_vtable = SD_BUS_PROPERTY(property_name_char_ptr,                 // Name
                                                                    property_signature_const_char,          // Signature
                                                                    _SdBusInterface_property_get_callback,  // Get
                                                                    0,                                      // Offset
                                                                    flags_long                              // Flags
                        );
                        self->vtable[current_index] = temp_vtable;
                } else {
                        sd_bus_vtable temp_vtable = SD_BUS_WRITABLE_PROPERTY(property_name_char_ptr,                 // Name
                                                                             property_signature_const_char,          // Signature
                                                                             _SdBusInterface_property_get_callback,  // Get
                                                                             _SdBusInterface_property_set_callback,  // Set
                                                                             0,                                      // Offset
                                                                             flags_long                              // Flags
                        );
                        self->vtable[current_index] = temp_vtable;
                }
        }

        for (Py_ssize_t i = 0; i < num_of_signals; ({
                     ++i;
                     ++current_index;
             })) {
                PyObject* signal_tuple = SD_BUS_PY_LIST_GET_ITEM(self->signal_list, i);

                PyObject* signal_name_str = SD_BUS_PY_TUPLE_GET_ITEM(signal_tuple, 0);
                PyObject* signal_signature_str = SD_BUS_PY_TUPLE_GET_ITEM(signal_tuple, 1);
                PyObject* signal_input_names = SD_BUS_PY_TUPLE_GET_ITEM(signal_tuple, 2);
                PyObject* signal_flags = SD_BUS_PY_TUPLE_GET_ITEM(signal_tuple, 3);

                const char* signal_name_char_ptr = SD_BUS_PY_BYTES_AS_CHAR_PTR(signal_name_str);
                const char* signal_signature_char_ptr = SD_BUS_PY_BYTES_AS_CHAR_PTR(signal_signature_str);
                const char* signal_args_names_char_ptr = SD_BUS_PY_BYTES_AS_CHAR_PTR(signal_input_names);

                unsigned long long flags_long = PyLong_AsUnsignedLongLong(signal_flags);
                if (PyErr_Occurred()) {
                        return NULL;
                }

                sd_bus_vtable temp_vtable = SD_BUS_SIGNAL_WITH_NAMES(signal_name_char_ptr, signal_signature_char_ptr, signal_args_names_char_ptr, flags_long);
                self->vtable[current_index] = temp_vtable;
        }

        sd_bus_vtable end_vtable = SD_BUS_VTABLE_END;
        self->vtable[current_index] = end_vtable;

        Py_RETURN_NONE;
}

static PyMethodDef SdBusInterface_methods[] = {
    {"add_method", (SD_BUS_PY_FUNC_TYPE)SdBusInterface_add_method, SD_BUS_PY_METH, "Add method to the dbus interface"},
    {"add_property", (SD_BUS_PY_FUNC_TYPE)SdBusInterface_add_property, SD_BUS_PY_METH, "Add property to the dbus interface"},
    {"add_signal", (SD_BUS_PY_FUNC_TYPE)SdBusInterface_add_signal, SD_BUS_PY_METH, "Add signal to the dbus interface"},
    {"_create_vtable", (PyCFunction)SdBusInterface_create_vtable, METH_NOARGS, "Creates the vtable"},
    {NULL, NULL, 0, NULL},
};

static PyMemberDef SdBusInterface_members[] = {{"method_list", T_OBJECT, offsetof(SdBusInterfaceObject, method_list), READONLY, NULL},
                                               {"method_dict", T_OBJECT, offsetof(SdBusInterfaceObject, method_dict), READONLY, NULL},
                                               {"property_list", T_OBJECT, offsetof(SdBusInterfaceObject, property_list), READONLY, NULL},
                                               {"property_get_dict", T_OBJECT, offsetof(SdBusInterfaceObject, property_get_dict), READONLY, NULL},
                                               {"property_set_dict", T_OBJECT, offsetof(SdBusInterfaceObject, property_set_dict), READONLY, NULL},
                                               {"signal_list", T_OBJECT, offsetof(SdBusInterfaceObject, signal_list), READONLY, NULL},
                                               {0}};

PyType_Spec SdBusInterfaceType = {
    .name = "sd_bus_internals.SdBusInterface",
    .basicsize = sizeof(SdBusInterfaceObject),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT,
    .slots =
        (PyType_Slot[]){
            {Py_tp_init, (initproc)SdBusInterface_init},
            {Py_tp_dealloc, (destructor)SdBusInterface_dealloc},
            {Py_tp_methods, SdBusInterface_methods},
            {Py_tp_members, SdBusInterface_members},
            {0, NULL},
        },
};

static int _SdBusInterface_callback(sd_bus_message* m, void* userdata, sd_bus_error* ret_error) {
        // TODO: Better error handling
        SdBusInterfaceObject* self = userdata;
        // Get the member name from the message
        const char* member_char_ptr = sd_bus_message_get_member(m);
        PyObject* member_name_bytes CLEANUP_PY_OBJECT = PyBytes_FromString(member_char_ptr);
        PyObject* callback_object = PyDict_GetItem(self->method_dict, member_name_bytes);
        if (callback_object == NULL) {
                sd_bus_error_set(ret_error, SD_BUS_ERROR_UNKNOWN_METHOD, "");
                return -1;
        };

        PyObject* running_loop CLEANUP_PY_OBJECT = PyObject_CallFunctionObjArgs(asyncio_get_running_loop, NULL);
        if (running_loop == NULL) {
                sd_bus_error_set(ret_error, SD_BUS_ERROR_FAILED, "");
                return -1;
        }

        PyObject* new_message CLEANUP_PY_OBJECT = PyObject_CallFunctionObjArgs(SdBusMessage_class, NULL);
        if (new_message == NULL) {
                sd_bus_error_set(ret_error, SD_BUS_ERROR_FAILED, "");
                return -1;
        }
        _SdBusMessage_set_messsage((SdBusMessageObject*)new_message, m);

        PyObject* is_coroutine_test_object CLEANUP_PY_OBJECT = PyObject_CallFunctionObjArgs(is_coroutine_function, callback_object, NULL);
        if (is_coroutine_test_object == NULL) {
                return -1;
        }

        if (Py_True == is_coroutine_test_object) {
                // Create coroutine
                PyObject* coroutine_activated CLEANUP_PY_OBJECT = PyObject_CallFunctionObjArgs(callback_object, new_message, NULL);
                if (coroutine_activated == NULL) {
                        return -1;
                }

                PyObject* task CLEANUP_PY_OBJECT = PyObject_CallMethodObjArgs(running_loop, create_task_str, coroutine_activated, NULL);
                if (task == NULL) {
                        sd_bus_error_set(ret_error, SD_BUS_ERROR_FAILED, "");
                        return -1;
                }
        } else {
                PyObject* handle CLEANUP_PY_OBJECT = PyObject_CallMethodObjArgs(running_loop, call_soon_str, callback_object, new_message, NULL);
                if (handle == NULL) {
                        sd_bus_error_set(ret_error, SD_BUS_ERROR_FAILED, "");
                        return -1;
                }
        }

        sd_bus_error_set(ret_error, NULL, NULL);

        return 1;
}

static int _SdBusInterface_property_get_callback(sd_bus* Py_UNUSED(bus),
                                                 const char* Py_UNUSED(path),
                                                 const char* Py_UNUSED(interface),
                                                 const char* property,
                                                 sd_bus_message* reply,
                                                 void* userdata,
                                                 sd_bus_error* Py_UNUSED(ret_error)) {
        SdBusInterfaceObject* self = userdata;
        PyObject* property_name_bytes CLEANUP_PY_OBJECT = PyBytes_FromString(property);
        PyObject* get_call = CALL_PYTHON_CHECK_RETURN_NEG1(PyDict_GetItem(self->property_get_dict, property_name_bytes));

        PyObject* new_message CLEANUP_PY_OBJECT = CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallFunctionObjArgs(SdBusMessage_class, NULL));
        _SdBusMessage_set_messsage((SdBusMessageObject*)new_message, reply);

        Py_XDECREF(CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallFunctionObjArgs(get_call, new_message, NULL)));
        return 0;
}

static int _SdBusInterface_property_set_callback(sd_bus* Py_UNUSED(bus),
                                                 const char* Py_UNUSED(path),
                                                 const char* Py_UNUSED(interface),
                                                 const char* property,
                                                 sd_bus_message* value,
                                                 void* userdata,
                                                 sd_bus_error* Py_UNUSED(ret_error)) {
        SdBusInterfaceObject* self = userdata;
        PyObject* property_name_bytes CLEANUP_PY_OBJECT = PyBytes_FromString(property);
        PyObject* set_call = CALL_PYTHON_CHECK_RETURN_NEG1(PyDict_GetItem(self->property_set_dict, property_name_bytes));

        PyObject* new_message CLEANUP_PY_OBJECT = CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallFunctionObjArgs(SdBusMessage_class, NULL));
        _SdBusMessage_set_messsage((SdBusMessageObject*)new_message, value);

        Py_XDECREF(CALL_PYTHON_CHECK_RETURN_NEG1(PyObject_CallFunctionObjArgs(set_call, new_message, NULL)));
        return 0;
}
