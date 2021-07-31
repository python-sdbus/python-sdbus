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

// Python functions and objects
PyObject* unmapped_error_exception = NULL;
PyObject* dbus_error_to_exception_dict = NULL;
PyObject* exception_to_dbus_error_dict = NULL;
PyObject* exception_base = NULL;
PyObject* exception_lib = NULL;
PyObject* asyncio_get_running_loop = NULL;
PyObject* asyncio_queue_class = NULL;
PyObject* is_coroutine_function = NULL;
// Str objects
PyObject* set_result_str = NULL;
PyObject* set_exception_str = NULL;
PyObject* put_no_wait_str = NULL;
PyObject* add_reader_str = NULL;
PyObject* remove_reader_str = NULL;
PyObject* empty_str = NULL;
PyObject* null_str = NULL;
PyObject* extend_str = NULL;
PyObject* append_str = NULL;
PyObject* call_soon_str = NULL;
PyObject* create_task_str = NULL;

// SdBusSlot

static int SdBusSlot_init(SdBusSlotObject* self, PyObject* Py_UNUSED(args), PyObject* Py_UNUSED(kwds)) {
        self->slot_ref = NULL;
        return 0;
}

static void SdBusSlot_dealloc(SdBusSlotObject* self) {
        sd_bus_slot_unref(self->slot_ref);

        SD_BUS_DEALLOC_TAIL;
}

PyType_Spec SdBusSlotType = {
    .name = "sd_bus_internals.SdBusSlot",
    .basicsize = sizeof(SdBusSlotObject),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT,
    .slots =
        (PyType_Slot[]){
            {Py_tp_init, (initproc)SdBusSlot_init},
            {Py_tp_dealloc, (destructor)SdBusSlot_dealloc},
            {0, NULL},
        },
};

static PyModuleDef sd_bus_internals_module = {
    PyModuleDef_HEAD_INIT, .m_name = "sd_bus_internals", .m_doc = "Sd bus internals module.", .m_methods = SdBusPyInternal_methods, .m_size = -1,
};

PyObject* SdBus_class = NULL;
PyObject* SdBusMessage_class = NULL;
PyObject* SdBusSlot_class = NULL;
PyObject* SdBusInterface_class = NULL;

#define SD_BUS_PY_INIT_TYPE_READY(type_slots)                                  \
        ({                                                                     \
                PyObject* class = PyType_FromSpecWithBases(&type_slots, NULL); \
                if (class == NULL) {                                           \
                        return NULL;                                           \
                }                                                              \
                class;                                                         \
        })

#define SD_BUS_PY_INIT_ADD_OBJECT(type_name, class)                   \
        if (PyModule_AddObject(m, type_name, (PyObject*)class) < 0) { \
                Py_DECREF((PyObject*)class);                          \
                return NULL;                                          \
        }

PyMODINIT_FUNC PyInit_sd_bus_internals(void) {
        PyObject* m CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyModule_Create(&sd_bus_internals_module));

        SdBus_class = SD_BUS_PY_INIT_TYPE_READY(SdBusType);
        SD_BUS_PY_INIT_ADD_OBJECT("SdBus", SdBus_class);

        SdBusMessage_class = SD_BUS_PY_INIT_TYPE_READY(SdBusMessageType);
        SD_BUS_PY_INIT_ADD_OBJECT("SdBusMessage", SdBusMessage_class);

        SdBusSlot_class = SD_BUS_PY_INIT_TYPE_READY(SdBusSlotType);
        SD_BUS_PY_INIT_ADD_OBJECT("SdBusSlot", SdBusSlot_class);

        SdBusInterface_class = SD_BUS_PY_INIT_TYPE_READY(SdBusInterfaceType);
        SD_BUS_PY_INIT_ADD_OBJECT("SdBusInterface", SdBusInterface_class);

        // Exception map
        dbus_error_to_exception_dict = CALL_PYTHON_AND_CHECK(PyDict_New());
        SD_BUS_PY_INIT_ADD_OBJECT("DBUS_ERROR_TO_EXCEPTION", dbus_error_to_exception_dict);

        exception_to_dbus_error_dict = CALL_PYTHON_AND_CHECK(PyDict_New());
        SD_BUS_PY_INIT_ADD_OBJECT("EXCEPTION_TO_DBUS_ERROR", exception_to_dbus_error_dict);

        PyObject* new_base_exception CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyErr_NewException("sd_bus_internals.SdBusBaseError", NULL, NULL));
        SD_BUS_PY_INIT_ADD_OBJECT("SdBusBaseError", new_base_exception);
        exception_base = new_base_exception;

        PyObject* new_unmapped_error_exception CLEANUP_PY_OBJECT =
            CALL_PYTHON_AND_CHECK(PyErr_NewException("sd_bus_internals.SdBusUnmappedMessageError", new_base_exception, NULL));
        SD_BUS_PY_INIT_ADD_OBJECT("SdBusUnmappedMessageError", new_unmapped_error_exception);
        unmapped_error_exception = new_unmapped_error_exception;

        PyObject* library_exception CLEANUP_PY_OBJECT =
            CALL_PYTHON_AND_CHECK(PyErr_NewException("sd_bus_internals.SdBusLibraryError", new_base_exception, NULL));
        SD_BUS_PY_INIT_ADD_OBJECT("SdBusLibraryError", library_exception);
        exception_lib = library_exception;

        PyObject* asyncio_module = CALL_PYTHON_AND_CHECK(PyImport_ImportModule("asyncio"));

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

        PyObject* inspect_module = CALL_PYTHON_AND_CHECK(PyImport_ImportModule("inspect"));
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
