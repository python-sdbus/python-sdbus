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

static SdBusObject* sd_bus_py_open(PyObject* Py_UNUSED(self), PyObject* Py_UNUSED(ignored)) {
        SdBusObject* new_sd_bus = (SdBusObject*)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(SdBus_class, NULL));
        CALL_SD_BUS_AND_CHECK(sd_bus_open(&(new_sd_bus->sd_bus_ref)));
        return new_sd_bus;
}

static SdBusObject* sd_bus_py_open_user(PyObject* Py_UNUSED(self), PyObject* Py_UNUSED(ignored)) {
        SdBusObject* new_sd_bus = (SdBusObject*)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(SdBus_class, NULL));
        CALL_SD_BUS_AND_CHECK(sd_bus_open_user(&(new_sd_bus->sd_bus_ref)));
        return new_sd_bus;
}

static SdBusObject* sd_bus_py_open_system(PyObject* Py_UNUSED(self), PyObject* Py_UNUSED(ignored)) {
        SdBusObject* new_sd_bus = (SdBusObject*)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(SdBus_class, NULL));
        CALL_SD_BUS_AND_CHECK(sd_bus_open_system(&(new_sd_bus->sd_bus_ref)));
        return new_sd_bus;
}

#ifndef Py_LIMITED_API
static PyObject* encode_object_path(PyObject* Py_UNUSED(self), PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(2);
        SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);

        const char* prefix_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]);
        const char* external_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[1]);

#else
static PyObject* encode_object_path(PyObject* Py_UNUSED(self), PyObject* args) {
        const char* prefix_char_ptr = NULL;
        const char* external_char_ptr = NULL;
        CALL_PYTHON_BOOL_CHECK(PyArg_ParseTuple(args, "ss", &prefix_char_ptr, &external_char_ptr, NULL));
#endif
#ifdef LIBSYSTEMD_NO_VALIDATION_FUNCS
        PyErr_SetString(PyExc_NotImplementedError, "libsystemd<0.29.0 does not support validation functions");
        return NULL;
#else

        if (!sd_bus_object_path_is_valid(prefix_char_ptr)) {
                PyErr_SetString(PyExc_ValueError, "Prefix is not a valid object path");
                return NULL;
        }

        const char* new_char_ptr CLEANUP_STR_MALLOC = NULL;

        CALL_SD_BUS_AND_CHECK(sd_bus_path_encode(prefix_char_ptr, external_char_ptr, (char**)(&new_char_ptr)));

        return PyUnicode_FromString(new_char_ptr);
#endif
}

#ifndef Py_LIMITED_API
static PyObject* decode_object_path(PyObject* Py_UNUSED(self), PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(2);
        SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);

        const char* prefix_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]);
        const char* full_path_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[1]);
#else
static PyObject* decode_object_path(PyObject* Py_UNUSED(self), PyObject* args) {
        const char* prefix_char_ptr = NULL;
        const char* full_path_char_ptr = NULL;
        CALL_PYTHON_BOOL_CHECK(PyArg_ParseTuple(args, "ss", &prefix_char_ptr, &full_path_char_ptr, NULL));
#endif

        const char* new_char_ptr CLEANUP_STR_MALLOC = NULL;

        CALL_SD_BUS_AND_CHECK(sd_bus_path_decode(full_path_char_ptr, prefix_char_ptr, (char**)(&new_char_ptr)));

        if (new_char_ptr) {
                return PyUnicode_FromString(new_char_ptr);
        } else {
                return PyUnicode_FromString("");
        }
}

#ifndef Py_LIMITED_API
static PyObject* add_exception_mapping(PyObject* Py_UNUSED(self), PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(1);
        PyObject* exception = args[0];
#else
static PyObject* add_exception_mapping(PyObject* Py_UNUSED(self), PyObject* args) {
        PyObject* exception = NULL;
        CALL_PYTHON_BOOL_CHECK(PyArg_ParseTuple(args, "O", &exception, NULL));
#endif
        PyObject* dbus_error_string CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyObject_GetAttrString(exception, "dbus_error_name"));

        if (CALL_PYTHON_INT_CHECK(PyDict_Contains(dbus_error_to_exception_dict, dbus_error_string)) > 0) {
                PyErr_Format(PyExc_ValueError, "Dbus error %R is already mapped.", dbus_error_string);
                return NULL;
        }

        if (CALL_PYTHON_INT_CHECK(PyDict_Contains(exception_to_dbus_error_dict, exception)) > 0) {
                PyErr_Format(PyExc_ValueError, "Exception %R is already mapped to dbus error.", exception);
                return NULL;
        }

        CALL_PYTHON_INT_CHECK(PyDict_SetItem(dbus_error_to_exception_dict, dbus_error_string, exception));
        CALL_PYTHON_INT_CHECK(PyDict_SetItem(exception_to_dbus_error_dict, exception, dbus_error_string));

        Py_RETURN_NONE;
}

PyMethodDef SdBusPyInternal_methods[] = {
    {"sd_bus_open", (PyCFunction)sd_bus_py_open, METH_NOARGS,
     "Open dbus connection. Session bus running as user or system bus as "
     "daemon"},
    {"sd_bus_open_user", (PyCFunction)sd_bus_py_open_user, METH_NOARGS, "Open user session dbus"},
    {"sd_bus_open_system", (PyCFunction)sd_bus_py_open_system, METH_NOARGS, "Open system dbus"},
    {"encode_object_path", (SD_BUS_PY_FUNC_TYPE)encode_object_path, SD_BUS_PY_METH, "Encode object path with object path prefix and arbitrary string"},
    {"decode_object_path", (SD_BUS_PY_FUNC_TYPE)decode_object_path, SD_BUS_PY_METH, "Decode object path with object path prefix and arbitrary string"},
    {"add_exception_mapping", (SD_BUS_PY_FUNC_TYPE)add_exception_mapping, SD_BUS_PY_METH, "Add exception to the mapping of dbus error names"},
    {NULL, NULL, 0, NULL},
};
