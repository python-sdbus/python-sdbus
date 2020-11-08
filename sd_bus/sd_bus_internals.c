#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <systemd/sd-bus.h>

typedef struct
{
    PyObject_HEAD;
    sd_bus *sd_bus_ref;
} SdBusObject;

static PyObject *
SdBus_test(SdBusObject *self, PyObject *args)
{
    sd_bus_error error = SD_BUS_ERROR_NULL;
    sd_bus_message *m = NULL;
    const char *name = NULL;

    int return_value = sd_bus_call_method(
        self->sd_bus_ref,
        "org.freedesktop.DBus",
        "/org/freedesktop/DBus",
        "org.freedesktop.DBus.Peer",
        "GetMachineId",
        &error,
        &m,
        "");
    if (return_value < 0)
    {
        PyErr_SetString(PyExc_RuntimeError, "Failed to call");
        return NULL;
    }
    return_value = sd_bus_message_read(m, "s", &name);
    if (return_value < 0)
    {
        PyErr_SetString(PyExc_RuntimeError, "Failed to read message");
        return NULL;
    }
    return PyUnicode_FromString(name);
    sd_bus_error_free(&error);
    sd_bus_message_unref(m);
}

static void
SdBus_free(SdBusObject *self)
{
    sd_bus_unref(self->sd_bus_ref);
}

static PyMethodDef SdBus_methods[] = {
    {"test", (PyCFunction)SdBus_test, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL},
};

static PyTypeObject SdBusType = {
    PyVarObject_HEAD_INIT(NULL, 0)
        .tp_name = "sd_bus_internals.SdBus",
    .tp_basicsize = sizeof(SdBusObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_free = (freefunc)SdBus_free,
    .tp_methods = SdBus_methods,
};

static SdBusObject *
get_default_sd_bus(PyObject *self,
                   PyObject *Py_UNUSED(ignored))
{
    SdBusObject *new_sd_bus = PyObject_New(SdBusObject, &SdBusType);
    int return_value = sd_bus_default(&(new_sd_bus->sd_bus_ref));
    if (return_value < 0)
    {
        PyErr_SetString(PyExc_RuntimeError, "Failed to get default sd_bus");
        return NULL;
    }
    else
    {
        return new_sd_bus;
    }
}

static PyMethodDef SdBusPyInternal_methods[] = {
    {"get_default_sdbus", (PyCFunction)get_default_sd_bus, METH_NOARGS, "Get default sd_bus."},
    {NULL, NULL, 0, NULL},
};

static PyModuleDef sd_bus_internals_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "sd_bus_internals",
    .m_doc = "Sd bus internals module.",
    .m_methods = SdBusPyInternal_methods,
    .m_size = -1,
};

PyMODINIT_FUNC
PyInit_sd_bus_internals(void)
{
    PyObject *m;
    if (PyType_Ready(&SdBusType) < 0)
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

    return m;
}