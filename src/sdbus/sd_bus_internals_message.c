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

static int SdBusMessage_init(SdBusMessageObject* self, PyObject* Py_UNUSED(args), PyObject* Py_UNUSED(kwds)) {
        self->message_ref = NULL;
        return 0;
}

void _SdBusMessage_set_messsage(SdBusMessageObject* self, sd_bus_message* new_message) {
        self->message_ref = sd_bus_message_ref(new_message);
}

static void SdBusMessage_dealloc(SdBusMessageObject* self) {
        sd_bus_message_unref(self->message_ref);

        SD_BUS_DEALLOC_TAIL;
}

static PyObject* SdBusMessage_seal(SdBusMessageObject* self, PyObject* Py_UNUSED(args)) {
        CALL_SD_BUS_AND_CHECK(sd_bus_message_seal(self->message_ref, 0, 0));
        Py_RETURN_NONE;
}

static PyObject* SdBusMessage_dump(SdBusMessageObject* self, PyObject* Py_UNUSED(args)) {
        CALL_SD_BUS_AND_CHECK(sd_bus_message_dump(self->message_ref, 0, SD_BUS_MESSAGE_DUMP_WITH_HEADER));
        CALL_SD_BUS_AND_CHECK(sd_bus_message_rewind(self->message_ref, 1));
        Py_RETURN_NONE;
}

typedef struct {
        sd_bus_message* message;
        const char* container_char_ptr;
        size_t index;
        size_t max_index;
} _Parse_state;

#define _CHECK_PARSER_NOT_NULL(parser)                                        \
        if (parser_state->container_char_ptr[parser_state->index] == '\0') {  \
                PyErr_SetString(PyExc_TypeError, "Data signature too short"); \
                return NULL;                                                  \
        }

static PyObject* _parse_complete(PyObject* complete_obj, _Parse_state* parser_state);

static PyObject* _parse_basic(PyObject* basic_obj, _Parse_state* parser_state) {
        char basic_type = parser_state->container_char_ptr[parser_state->index];
        switch (basic_type) {
                // Unsigned
                case 'y': {
                        unsigned long long the_ulong_long = PyLong_AsUnsignedLongLong(basic_obj);
                        PYTHON_ERR_OCCURED;
                        if (UINT8_MAX < the_ulong_long) {
                                PyErr_Format(PyExc_OverflowError,
                                             "Cannot convert int to "
                                             "'y' type, overflow. 'y' "
                                             "is max %llu",
                                             (unsigned long long)UINT8_MAX);
                                return NULL;
                        }
                        uint8_t byte_to_add = (uint8_t)the_ulong_long;
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(parser_state->message, basic_type, &byte_to_add));
                        break;
                }
                case 'q': {
                        unsigned long long the_ulong_long = PyLong_AsUnsignedLongLong(basic_obj);
                        PYTHON_ERR_OCCURED;
                        if (UINT16_MAX < the_ulong_long) {
                                PyErr_Format(PyExc_OverflowError,
                                             "Cannot convert int to "
                                             "'q' type, overflow. 'q' "
                                             "is max %llu",
                                             (unsigned long long)UINT16_MAX);
                                return NULL;
                        }
                        uint16_t q_to_add = (uint16_t)the_ulong_long;
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(parser_state->message, basic_type, &q_to_add));
                        break;
                }
                case 'u': {
                        unsigned long long the_ulong_long = PyLong_AsUnsignedLongLong(basic_obj);
                        PYTHON_ERR_OCCURED;
                        if (UINT32_MAX < the_ulong_long) {
                                PyErr_Format(PyExc_OverflowError,
                                             "Cannot convert int to "
                                             "'u' type, overflow. 'u' "
                                             "is max %lu",
                                             (unsigned long)UINT32_MAX);
                                return NULL;
                        }
                        uint32_t u_to_add = (uint32_t)the_ulong_long;
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(parser_state->message, basic_type, &u_to_add));
                        break;
                }
                case 't': {
                        unsigned long long the_ulong_long = PyLong_AsUnsignedLongLong(basic_obj);
                        PYTHON_ERR_OCCURED;
                        uint64_t t_to_add = the_ulong_long;
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(parser_state->message, basic_type, &t_to_add));
                        break;
                }
                // Signed
                case 'n': {
                        long long the_long_long = PyLong_AsLongLong(basic_obj);
                        PYTHON_ERR_OCCURED;
                        if (INT16_MAX < the_long_long) {
                                PyErr_Format(PyExc_OverflowError,
                                             "Cannot convert int to "
                                             "'n' type, overflow. 'n' "
                                             "is max %lli",
                                             (long long)INT16_MAX);
                                return NULL;
                        }
                        if (INT16_MIN > the_long_long) {
                                PyErr_Format(PyExc_OverflowError,
                                             "Cannot convert int to "
                                             "'n' type, underflow. 'n' "
                                             "is min %lli",
                                             (long long)INT16_MIN);
                                return NULL;
                        }
                        int16_t n_to_add = (int16_t)the_long_long;
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(parser_state->message, basic_type, &n_to_add));
                        break;
                }
                case 'i': {
                        long long the_long_long = PyLong_AsLongLong(basic_obj);
                        PYTHON_ERR_OCCURED;
                        if (INT32_MAX < the_long_long) {
                                PyErr_Format(PyExc_OverflowError,
                                             "Cannot convert int to "
                                             "'i' type, overflow. 'i' "
                                             "is max %lli",
                                             (long long)INT32_MAX);
                                return NULL;
                        }
                        if (INT32_MIN > the_long_long) {
                                PyErr_Format(PyExc_OverflowError,
                                             "Cannot convert int to "
                                             "'i' type, underflow. 'i' "
                                             "is min %lli",
                                             (long long)INT32_MIN);
                                return NULL;
                        }
                        int32_t i_to_add = (int32_t)the_long_long;
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(parser_state->message, basic_type, &i_to_add));
                        break;
                }
                case 'x': {
                        long long the_long_long = PyLong_AsLongLong(basic_obj);
                        PYTHON_ERR_OCCURED;
                        int64_t x_to_add = the_long_long;
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(parser_state->message, basic_type, &x_to_add));
                        break;
                }
                case 'h': {
                        long long the_long_long = PyLong_AsLongLong(basic_obj);
                        PYTHON_ERR_OCCURED;
                        int h_to_add = (int)the_long_long;
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(parser_state->message, basic_type, &h_to_add));
                        break;
                }
                case 'b': {
                        if (!PyBool_Check(basic_obj)) {
                                PyErr_Format(PyExc_TypeError,
                                             "Message append error, "
                                             "expected bool got %R",
                                             basic_obj);
                                return NULL;
                        }
                        int bool_to_add = (basic_obj == Py_True);
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(parser_state->message, basic_type, &bool_to_add));
                        break;
                }
                case 'd': {
                        if (!PyFloat_Check(basic_obj)) {
                                PyErr_Format(PyExc_TypeError,
                                             "Message append error, "
                                             "expected double got %R",
                                             basic_obj);
                                return NULL;
                        }
                        double double_to_add = PyFloat_AsDouble(basic_obj);
                        PYTHON_ERR_OCCURED;
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_append_basic(parser_state->message, basic_type, &double_to_add));
                        break;
                }
                case 'o':
                case 'g':
                case 's': {
                        if (!PyUnicode_Check(basic_obj)) {
                                PyErr_Format(PyExc_TypeError,
                                             "Message append error, "
                                             "expected str got %R",
                                             basic_obj);
                                return NULL;
                        }
#ifndef Py_LIMITED_API
                        const char* char_ptr_to_append = SD_BUS_PY_UNICODE_AS_CHAR_PTR(basic_obj);
#else
                        PyObject* bytes_to_append CLEANUP_PY_OBJECT = SD_BUS_PY_UNICODE_AS_BYTES(basic_obj);
                        const char* char_ptr_to_append = SD_BUS_PY_BYTES_AS_CHAR_PTR(bytes_to_append);
#endif
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

static size_t _find_struct_end(const char* container_char_ptr, size_t current_index) {
        // Initial state
        // "...(...)..."
        //      ^
        int round_bracket_count = 1;
        for (; container_char_ptr[current_index] != '\0'; ++current_index) {
                char current_char = container_char_ptr[current_index];
                if (current_char == ')') {
                        --round_bracket_count;
                }

                if (current_char == '(') {
                        ++round_bracket_count;
                }

                if (round_bracket_count == 0) {
                        return current_index;
                }

                if (round_bracket_count < 0) {
                        PyErr_SetString(PyExc_TypeError,
                                        "Round braces count <0. Check "
                                        "your signature.");
                        return 0;
                }
        }
        PyErr_SetString(PyExc_TypeError, "Reached the end of signature before the struct end");
        return 0;
}

static size_t _find_dict_end(const char* container_char_ptr, size_t current_index) {
        // Initial state
        // "...a{..}..."
        //      ^
        int curly_bracket_count = 0;
        for (; container_char_ptr[current_index] != '\0'; ++current_index) {
                char current_char = container_char_ptr[current_index];
                if (current_char == '}') {
                        --curly_bracket_count;
                }

                if (current_char == '{') {
                        ++curly_bracket_count;
                }

                if (curly_bracket_count == 0) {
                        // "...a{..}..."
                        //         ^
                        return current_index;
                }

                if (curly_bracket_count < 0) {
                        PyErr_SetString(PyExc_TypeError,
                                        "Curly braces count <0. Check "
                                        "your signature.");
                        return 0;
                }
        }
        PyErr_SetString(PyExc_TypeError, "Reached the end of signature before the struct end");
        return 0;
}

static size_t _find_array_end(const char* container_char_ptr, size_t current_index) {
        // Initial state
        // "...as..."
        //     ^
        // "...a{sx}.."
        //     ^
        // "...a(as)..."
        //     ^

        while (container_char_ptr[current_index] == 'a') {
                current_index++;
        }
        char current_char = container_char_ptr[current_index];
        // "...as..."
        //      ^
        // "...a{sx}.."
        //      ^
        // "...a(as)..."
        //      ^
        if (current_char == '\0') {
                PyErr_SetString(PyExc_TypeError,
                                "Reached the end of signature before "
                                "the array end");
                return 0;
        }
        if (current_char == '{') {
                // "...a{sx}.."
                //      ^
                return _find_dict_end(container_char_ptr, current_index);
        }
        if (current_char == '(') {
                current_index++;
                // "...a(as)..."
                //       ^
                return _find_struct_end(container_char_ptr, current_index);
        }

        return current_index;
}

static const char* _subscript_char_ptr(const char* old_char_ptr, size_t start, size_t end) {
        // "abc(def)..."
        //  01234 |
        //  0123456
        // 6 - 4 = 2
        // Actual string
        // 'def\0'
        // 3 string length without \0
        // 4 string length with \0
        size_t new_string_size = (end - start) + 1;
        char* new_string = malloc(new_string_size + 1);
        if (new_string == NULL) {
                return NULL;
        }
        memcpy(new_string, old_char_ptr + start, new_string_size);
        // Set last byte to NUL
        new_string[new_string_size] = '\0';
        return new_string;
}

static PyObject* _parse_dict(PyObject* dict_object, _Parse_state* parser_state) {
        // parser_state->container_char_ptr
        // "{sx}"
        //  ^
        if (!PyDict_Check(dict_object)) {
                PyErr_Format(PyExc_TypeError, "Message append error, expected dict got %R", dict_object);
                return NULL;
        }

        const char* dict_sig_char_ptr CLEANUP_STR_MALLOC = _subscript_char_ptr(parser_state->container_char_ptr, 1, parser_state->max_index - 2);
        // "sx"
        parser_state->container_char_ptr = dict_sig_char_ptr;  // This is OK because its cleanup from
                                                               // outside
        parser_state->max_index = strlen(dict_sig_char_ptr);

        PyObject *key, *value;
        Py_ssize_t pos = 0;

        while (PyDict_Next(dict_object, &pos, &key, &value)) {
                CALL_SD_BUS_AND_CHECK(sd_bus_message_open_container(parser_state->message, 'e', dict_sig_char_ptr));
                parser_state->index = 0;
                CALL_PYTHON_EXPECT_NONE(_parse_basic(key, parser_state));
                CALL_PYTHON_EXPECT_NONE(_parse_complete(value, parser_state));
                CALL_SD_BUS_AND_CHECK(sd_bus_message_close_container(parser_state->message));
        }

        Py_RETURN_NONE;
}

static PyObject* _parse_array(PyObject* array_object, _Parse_state* parser_state) {
        // Initial state
        // "...as..."
        //     ^
        // "...a{sx}.."
        //     ^
        // "...a(as)..."
        //     ^
        size_t array_end = _find_array_end(parser_state->container_char_ptr, parser_state->index);
        if (array_end == 0) {
                return NULL;
        }
        // Array end points to
        // "...as..."
        //      ^
        // "...a{sx}.."
        //         ^
        // "...a(as)..."
        //         ^
        const char* array_sig_char_ptr CLEANUP_STR_MALLOC = _subscript_char_ptr(parser_state->container_char_ptr, parser_state->index + 1, array_end);
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
        if (array_parser.container_char_ptr[0] == '{') {
                CALL_SD_BUS_AND_CHECK(sd_bus_message_open_container(parser_state->message, 'a', array_sig_char_ptr));
                CALL_PYTHON_EXPECT_NONE(_parse_dict(array_object, &array_parser));
                CALL_SD_BUS_AND_CHECK(sd_bus_message_close_container(parser_state->message));
        } else if (array_parser.container_char_ptr[0] == 'y') {
                char* char_ptr_to_add = NULL;
                ssize_t size_of_array = 0;
                if (PyByteArray_Check(array_object)) {
                        char_ptr_to_add = PyByteArray_AsString(array_object);
                        if (char_ptr_to_add == NULL) {
                                return NULL;
                        }
                        size_of_array = PyByteArray_Size(array_object);
                        if (size_of_array == -1) {
                                return NULL;
                        }
                } else if (PyBytes_Check(array_object)) {
                        char_ptr_to_add = PyBytes_AsString(array_object);
                        if (char_ptr_to_add == NULL) {
                                return NULL;
                        }
                        size_of_array = PyBytes_Size(array_object);
                        if (size_of_array == -1) {
                                return NULL;
                        }
                } else {
                        PyErr_Format(PyExc_TypeError,
                                     "Expected bytes or byte "
                                     "array, got %R",
                                     array_object);
                        return NULL;
                }
                CALL_SD_BUS_AND_CHECK(sd_bus_message_append_array(parser_state->message, 'y', char_ptr_to_add, (size_t)size_of_array));
        } else {
                if (!PyList_Check(array_object)) {
                        PyErr_Format(PyExc_TypeError,
                                     "Message append error, "
                                     "expected array got %R",
                                     array_object);
                        return NULL;
                }

                // "...as..."
                //     "s"
                // "...aa{sx}.."
                //     "a{sx}"
                // "...a(as)..."
                //     "(as)"
                CALL_SD_BUS_AND_CHECK(sd_bus_message_open_container(parser_state->message, 'a', array_sig_char_ptr));
                for (Py_ssize_t i = 0; i < SD_BUS_PY_LIST_GET_SIZE(array_object); ++i) {
                        CALL_PYTHON_EXPECT_NONE(_parse_complete(SD_BUS_PY_LIST_GET_ITEM(array_object, i), &array_parser));
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

static PyObject* _parse_struct(PyObject* tuple_object, _Parse_state* parser_state) {
        // Initial state
        // "...(...)..."
        //     ^
        if (!PyTuple_Check(tuple_object)) {
                PyErr_Format(PyExc_TypeError, "Message append error, expected tuple got %R", tuple_object);
                return NULL;
        }
        parser_state->index++;
        // "...(...)..."
        //      ^
        size_t struct_end = _find_struct_end(parser_state->container_char_ptr, parser_state->index);

        if (struct_end == 0) {
                return NULL;
        }
        // Struct end points to
        // "...(...)..."
        //         ^
        const char* struct_signature CLEANUP_STR_MALLOC = _subscript_char_ptr(parser_state->container_char_ptr, parser_state->index, struct_end - 1);
        // struct_signature should be
        // "...(...)..."
        //     ^   ^
        //     "..."
        CALL_SD_BUS_AND_CHECK(sd_bus_message_open_container(parser_state->message, 'r', struct_signature));
        for (Py_ssize_t i = 0; i < SD_BUS_PY_TUPLE_GET_SIZE(tuple_object); ++i) {
                // Use original parser as there is not much reason to
                // create new one
                CALL_PYTHON_EXPECT_NONE(_parse_complete(SD_BUS_PY_TUPLE_GET_ITEM(tuple_object, i), parser_state));
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

static PyObject* _parse_variant(PyObject* tuple_object, _Parse_state* parser_state) {
        // Initial state "...v..."
        //                   ^
        if (!PyTuple_Check(tuple_object)) {
                PyErr_Format(PyExc_TypeError, "Message append error, expected tuple got %R", tuple_object);
                return NULL;
        }
        if (SD_BUS_PY_TUPLE_GET_SIZE(tuple_object) != 2) {
                PyErr_Format(PyExc_TypeError, "Expected tuple of only 2 elements got %zi", SD_BUS_PY_TUPLE_GET_SIZE(tuple_object));
                return NULL;
        }
        PyObject* variant_signature = SD_BUS_PY_TUPLE_GET_ITEM(tuple_object, 0);
#ifndef Py_LIMITED_API
        const char* variant_signature_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(variant_signature);
#else
        PyObject* variant_signature_bytes CLEANUP_PY_OBJECT = SD_BUS_PY_UNICODE_AS_BYTES(variant_signature);
        const char* variant_signature_char_ptr = SD_BUS_PY_BYTES_AS_CHAR_PTR(variant_signature_bytes);
#endif
        _Parse_state variant_parser = {
            .message = parser_state->message,
            .max_index = strlen(variant_signature_char_ptr),
            .container_char_ptr = variant_signature_char_ptr,
            .index = 0,
        };

        CALL_SD_BUS_AND_CHECK(sd_bus_message_open_container(parser_state->message, 'v', variant_signature_char_ptr));
        PyObject* variant_body = SD_BUS_PY_TUPLE_GET_ITEM(tuple_object, 1);
        CALL_PYTHON_EXPECT_NONE(_parse_complete(variant_body, &variant_parser));
        CALL_SD_BUS_AND_CHECK(sd_bus_message_close_container(parser_state->message));

        // Final state "...v..."
        //                  ^
        parser_state->index++;
        Py_RETURN_NONE;
}

static PyObject* _parse_complete(PyObject* complete_obj, _Parse_state* parser_state) {
        // Initial state "..."
        //                ^
        _CHECK_PARSER_NOT_NULL(parser_state);
        char next_char = parser_state->container_char_ptr[parser_state->index];
        switch (next_char) {
                case '}': {
                        PyErr_SetString(PyExc_TypeError,
                                        "End of dict reached instead "
                                        "of complete type");
                        return NULL;
                }
                case ')': {
                        PyErr_SetString(PyExc_TypeError,
                                        "End of struct reached "
                                        "instead of complete type");
                        return NULL;
                }
                case '(': {
                        // Struct == Tuple
                        CALL_PYTHON_EXPECT_NONE(_parse_struct(complete_obj, parser_state));
                        break;
                }
                case '{': {
                        // Dict
                        PyErr_SetString(PyExc_TypeError, "Dbus dict can't be outside of array");
                        return NULL;
                        break;
                }
                case 'a': {
                        // Array
                        CALL_PYTHON_EXPECT_NONE(_parse_array(complete_obj, parser_state));
                        break;
                }
                case 'v': {
                        // Variant == (signature, data))
                        CALL_PYTHON_EXPECT_NONE(_parse_variant(complete_obj, parser_state));
                        break;
                }
                default: {
                        // Basic type
                        CALL_PYTHON_EXPECT_NONE(_parse_basic(complete_obj, parser_state));
                        break;
                }
        }
        Py_RETURN_NONE;
}

#ifndef Py_LIMITED_API
static PyObject* SdBusMessage_append_data(SdBusMessageObject* self, PyObject* const* args, Py_ssize_t nargs) {
        if (nargs < 2) {
                PyErr_SetString(PyExc_TypeError, "Minimum 2 args required");
                return NULL;
        }
        SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);

        const char* signature_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]);

        _Parse_state parser_state = {
            .message = self->message_ref,
            .container_char_ptr = signature_char_ptr,
            .index = 0,
            .max_index = strlen(signature_char_ptr),
        };

        for (Py_ssize_t i = 1; i < nargs; ++i) {
                CALL_PYTHON_EXPECT_NONE(_parse_complete(args[i], &parser_state));
        }
#else
static PyObject* SdBusMessage_append_data(SdBusMessageObject* self, PyObject* args) {
        Py_ssize_t num_args = PyTuple_Size(args);
        if (num_args < 2) {
                PyErr_SetString(PyExc_TypeError, "Minimum 2 args required");
                return NULL;
        }
        PyObject* signature_str = PyTuple_GetItem(args, 0);
        PyObject* signature_bytes CLEANUP_PY_OBJECT = SD_BUS_PY_UNICODE_AS_BYTES(signature_str);
        const char* signature_char_ptr = SD_BUS_PY_BYTES_AS_CHAR_PTR(signature_bytes);

        _Parse_state parser_state = {
            .message = self->message_ref,
            .container_char_ptr = signature_char_ptr,
            .index = 0,
            .max_index = strlen(signature_char_ptr),
        };

        for (Py_ssize_t i = 1; i < num_args; ++i) {
                CALL_PYTHON_EXPECT_NONE(_parse_complete(PyTuple_GetItem(args, i), &parser_state));
        }
#endif
        Py_RETURN_NONE;
}

#ifndef Py_LIMITED_API
static PyObject* SdBusMessage_open_container(SdBusMessageObject* self, PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(2);
        SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);

        const char* container_type_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]);
        const char* container_contents_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[1]);
#else
static PyObject* SdBusMessage_open_container(SdBusMessageObject* self, PyObject* args) {
        const char* container_type_char_ptr = NULL;
        const char* container_contents_char_ptr = NULL;
        CALL_PYTHON_BOOL_CHECK(PyArg_ParseTuple(args, "ss", &container_type_char_ptr, &container_contents_char_ptr, NULL));
#endif
        CALL_SD_BUS_AND_CHECK(sd_bus_message_open_container(self->message_ref, container_type_char_ptr[0], container_contents_char_ptr));

        Py_RETURN_NONE;
}

static PyObject* SdBusMessage_close_container(SdBusMessageObject* self, PyObject* Py_UNUSED(args)) {
        CALL_SD_BUS_AND_CHECK(sd_bus_message_close_container(self->message_ref));

        Py_RETURN_NONE;
}

#ifndef Py_LIMITED_API
static PyObject* SdBusMessage_enter_container(SdBusMessageObject* self, PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(2);
        SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);

        const char* container_type_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]);
        const char* container_contents_char_ptr = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[1]);
#else
static PyObject* SdBusMessage_enter_container(SdBusMessageObject* self, PyObject* args) {
        const char* container_type_char_ptr = NULL;
        const char* container_contents_char_ptr = NULL;
        CALL_PYTHON_BOOL_CHECK(PyArg_ParseTuple(args, "ss", &container_type_char_ptr, &container_contents_char_ptr, NULL));
#endif
        CALL_SD_BUS_AND_CHECK(sd_bus_message_enter_container(self->message_ref, container_type_char_ptr[0], container_contents_char_ptr));

        Py_RETURN_NONE;
}

static PyObject* SdBusMessage_exit_container(SdBusMessageObject* self, PyObject* Py_UNUSED(args)) {
        CALL_SD_BUS_AND_CHECK(sd_bus_message_exit_container(self->message_ref));

        Py_RETURN_NONE;
}

static SdBusMessageObject* SdBusMessage_create_reply(SdBusMessageObject* self, PyObject* Py_UNUSED(args)) {
        SdBusMessageObject* new_reply_message CLEANUP_SD_BUS_MESSAGE =
            (SdBusMessageObject*)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(SdBusMessage_class, NULL));

        CALL_SD_BUS_AND_CHECK(sd_bus_message_new_method_return(self->message_ref, &new_reply_message->message_ref));

        Py_INCREF(new_reply_message);
        return new_reply_message;
}

static PyObject* SdBusMessage_send(SdBusMessageObject* self, PyObject* Py_UNUSED(args)) {
        CALL_SD_BUS_AND_CHECK(sd_bus_send(NULL, self->message_ref, NULL));

        Py_RETURN_NONE;
}

static size_t _container_size(const char* container_sig) {
        size_t container_size = 0;
        size_t index = 0;

        while ((container_sig[index]) != '\0') {
                char current_char = container_sig[index];
                index++;
                if (current_char == 'a') {
                        index = _find_array_end(container_sig, index);
                        index++;
                }

                if (current_char == '(') {
                        index = _find_struct_end(container_sig, index);
                        index++;
                }

                if (index == 0) {
                        PyErr_SetString(PyExc_TypeError, "Failed to find container size");
                        return 0;
                }

                container_size++;
        }
        return container_size;
}

static PyObject* _iter_complete(_Parse_state* parser);

static PyObject* _iter_basic(sd_bus_message* message, char basic_type) {
        switch (basic_type) {
                case 'b': {
                        int new_int = 0;
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(message, basic_type, &new_int));
                        return PyBool_FromLong(new_int);
                        break;
                }
                case 'y': {
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

                case 'i': {
                        int32_t new_long = 0;
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(message, basic_type, &new_long));
                        return PyLong_FromLong((long)new_long);
                        break;
                }
                case 'x': {
                        int64_t new_long_long = 0;
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(message, basic_type, &new_long_long));
                        return PyLong_FromLongLong((long long)new_long_long);
                        break;
                }
                case 'q': {
                        uint16_t new_u_short = 0;
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(message, basic_type, &new_u_short));
                        return PyLong_FromUnsignedLong((unsigned long)new_u_short);
                        break;
                }
                case 'u': {
                        uint32_t new_u_long = 0;
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(message, basic_type, &new_u_long));
                        return PyLong_FromUnsignedLong((unsigned long)new_u_long);
                        break;
                }
                case 't': {
                        uint64_t new_u_long_long = 0;
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(message, basic_type, &new_u_long_long));
                        return PyLong_FromUnsignedLongLong((unsigned long long)new_u_long_long);
                        break;
                }

                case 'd': {
                        double new_double = 0.0;
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(message, basic_type, &new_double));
                        return PyFloat_FromDouble(new_double);
                        break;
                }
                case 'h': {
                        int new_fd = 0;
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(message, basic_type, &new_fd));
                        return PyLong_FromLong((long)new_fd);
                        break;
                }
                case 'g':
                case 'o':
                case 's': {
                        const char* new_string = NULL;
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_read_basic(message, basic_type, &new_string));
                        return PyUnicode_FromString(new_string);
                        break;
                }
                default: {
                        int code = (int)basic_type;
                        PyObject* error_string CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyUnicode_FromFormat("%c", code));
                        PyErr_Format(PyExc_TypeError, "Dbus type %R is unknown", error_string);
                        return NULL;
                        break;
                }
        }
}

static PyObject* _iter_bytes_array(_Parse_state* parser) {
        // Byte array
        const void* char_array = NULL;
        size_t array_size = 0;
        CALL_SD_BUS_AND_CHECK(sd_bus_message_read_array(parser->message, 'y', &char_array, &array_size));
        return PyBytes_FromStringAndSize(char_array, (Py_ssize_t)array_size);
}

static PyObject* _iter_dict(_Parse_state* parser) {
        PyObject* new_dict CLEANUP_PY_OBJECT = PyDict_New();

        char peek_type = '\0';
        const char* container_type = NULL;
        while (CALL_SD_BUS_AND_CHECK(sd_bus_message_peek_type(parser->message, &peek_type, &container_type)) > 0) {
                if (peek_type != SD_BUS_TYPE_DICT_ENTRY) {
                        PyErr_SetString(PyExc_TypeError, "Expected dict entry.");
                        return NULL;
                }
                CALL_SD_BUS_AND_CHECK(sd_bus_message_enter_container(parser->message, peek_type, container_type));
                PyObject* key_object CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(_iter_basic(parser->message, container_type[0]));
                PyObject* value_object CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(_iter_complete(parser));
                CALL_SD_BUS_AND_CHECK(sd_bus_message_exit_container(parser->message));
                if (PyDict_SetItem(new_dict, key_object, value_object) < 0) {
                        return NULL;
                }
        }

        Py_INCREF(new_dict);
        return new_dict;
}

static PyObject* _iter_array(_Parse_state* parser) {
        PyObject* new_list CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyList_New(0));
        char peek_type = '\0';
        const char* container_type = NULL;

        while (CALL_SD_BUS_AND_CHECK(sd_bus_message_peek_type(parser->message, &peek_type, &container_type)) > 0) {
                PyObject* new_object CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(_iter_complete(parser));
                if (PyList_Append(new_list, new_object) < 0) {
                        return NULL;
                }
        }
        Py_INCREF(new_list);
        return new_list;
}

static PyObject* _iter_struct(_Parse_state* parser) {
        const char* container_sig = sd_bus_message_get_signature(parser->message, 0);
        if (container_sig == NULL) {
                PyErr_SetString(PyExc_TypeError, "Failed to get container signature");
                return NULL;
        }
        size_t tuple_size = _container_size(container_sig);

        if (tuple_size == 0) {
                return NULL;
        }

        PyObject* new_tuple CLEANUP_PY_OBJECT = PyTuple_New((Py_ssize_t)tuple_size);
        for (size_t i = 0; i < tuple_size; ++i) {
                PyObject* new_complete = CALL_PYTHON_AND_CHECK(_iter_complete(parser));
                SD_BUS_PY_TUPLE_SET_ITEM(new_tuple, i, new_complete);
        }
        Py_INCREF(new_tuple);
        return new_tuple;
}

static PyObject* _iter_variant(_Parse_state* parser) {
        const char* container_sig = sd_bus_message_get_signature(parser->message, 0);
        PyObject* value_object CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(_iter_complete(parser));
        PyObject* variant_sig_str CLEANUP_PY_OBJECT = CALL_PYTHON_AND_CHECK(PyUnicode_FromString(container_sig));
        return PyTuple_Pack(2, variant_sig_str, value_object);
}

static PyObject* _iter_complete(_Parse_state* parser) {
        const char* container_signature = NULL;
        char complete_type = '\0';
        // TODO: can be optimized with custom parser instead of constantly
        // peeking
        CALL_SD_BUS_AND_CHECK(sd_bus_message_peek_type(parser->message, &complete_type, &container_signature));
        switch (complete_type) {
                case 'a': {
                        if (strcmp(container_signature, "y") == 0) {
                                return _iter_bytes_array(parser);
                        }

                        if (container_signature[0] == '{') {
                                CALL_SD_BUS_AND_CHECK(sd_bus_message_enter_container(parser->message, complete_type, container_signature));
                                PyObject* new_dict = CALL_PYTHON_AND_CHECK(_iter_dict(parser));
                                CALL_SD_BUS_AND_CHECK(sd_bus_message_exit_container(parser->message));
                                return new_dict;
                        }
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_enter_container(parser->message, complete_type, container_signature));
                        PyObject* new_array = CALL_PYTHON_AND_CHECK(_iter_array(parser));
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_exit_container(parser->message));
                        return new_array;
                        break;
                }
                case 'v': {
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_enter_container(parser->message, complete_type, container_signature));
                        PyObject* new_variant = CALL_PYTHON_AND_CHECK(_iter_variant(parser));
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_exit_container(parser->message));
                        return new_variant;
                        break;
                }
                case 'r': {
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_enter_container(parser->message, complete_type, container_signature));
                        PyObject* new_tuple = CALL_PYTHON_AND_CHECK(_iter_struct(parser));
                        CALL_SD_BUS_AND_CHECK(sd_bus_message_exit_container(parser->message));
                        return new_tuple;
                        break;
                }
                default: {
                        return _iter_basic(parser->message, complete_type);
                        break;
                }
        }
}

static PyObject* iter_tuple_or_single(_Parse_state* parser) {
        // Calculate the length of message data
        size_t container_size = _container_size(parser->container_char_ptr);
        if (container_size == 0) {
                return NULL;
        }

        if (container_size == 1) {
                return _iter_complete(parser);
        } else {
                return _iter_struct(parser);
        }
}

static PyObject* SdBusMessage_get_contents2(SdBusMessageObject* self, PyObject* Py_UNUSED(args)) {
        const char* message_signature = sd_bus_message_get_signature(self->message_ref, 0);

        if (message_signature == NULL) {
                PyErr_SetString(PyExc_TypeError, "Failed to get message signature.");
                return NULL;
        }
        if (message_signature[0] == '\0') {
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

static PyObject* SdBusMessage_get_member(SdBusMessageObject* self, PyObject* Py_UNUSED(args)) {
        const char* member_char_ptr = sd_bus_message_get_member(self->message_ref);
        if (member_char_ptr == NULL) {
                PyErr_SetString(PyExc_RuntimeError, "Failed to get message member field");
                return NULL;
        }
        return PyUnicode_FromString(member_char_ptr);
}

#ifndef Py_LIMITED_API
static SdBusMessageObject* SdBusMessage_create_error_reply(SdBusMessageObject* self, PyObject* const* args, Py_ssize_t nargs) {
        SD_BUS_PY_CHECK_ARGS_NUMBER(2);
        SD_BUS_PY_CHECK_ARG_TYPE(0, PyUnicode_Type);
        SD_BUS_PY_CHECK_ARG_TYPE(1, PyUnicode_Type);

        const char* name = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[0]);
        const char* error_message = SD_BUS_PY_UNICODE_AS_CHAR_PTR(args[1]);
#else
static SdBusMessageObject* SdBusMessage_create_error_reply(SdBusMessageObject* self, PyObject* args) {
        const char* name = NULL;
        const char* error_message = NULL;
        CALL_PYTHON_BOOL_CHECK(PyArg_ParseTuple(args, "ss", &name, &error_message, NULL));
#endif
        SdBusMessageObject* new_reply_message CLEANUP_SD_BUS_MESSAGE =
            (SdBusMessageObject*)CALL_PYTHON_AND_CHECK(PyObject_CallFunctionObjArgs(SdBusMessage_class, NULL));

        CALL_SD_BUS_AND_CHECK(sd_bus_message_new_method_errorf(self->message_ref, &new_reply_message->message_ref, name, "%s", error_message));

        Py_INCREF(new_reply_message);
        return new_reply_message;
}

static PyMethodDef SdBusMessage_methods[] = {
    {"append_data", (SD_BUS_PY_FUNC_TYPE)SdBusMessage_append_data, SD_BUS_PY_METH, "Append basic data based on signature."},
    {"open_container", (SD_BUS_PY_FUNC_TYPE)SdBusMessage_open_container, SD_BUS_PY_METH, "Open container for writing"},
    {"close_container", (PyCFunction)SdBusMessage_close_container, METH_NOARGS, "Close container"},
    {"enter_container", (SD_BUS_PY_FUNC_TYPE)SdBusMessage_enter_container, SD_BUS_PY_METH, "Enter container for reading"},
    {"exit_container", (PyCFunction)SdBusMessage_exit_container, METH_NOARGS, "Exit container"},
    {"dump", (PyCFunction)SdBusMessage_dump, METH_NOARGS, "Dump message to stdout"},
    {"seal", (PyCFunction)SdBusMessage_seal, METH_NOARGS, "Seal message contents"},
    {"get_contents", (PyCFunction)SdBusMessage_get_contents2, METH_NOARGS, "Iterate over message contents"},
    {"get_member", (PyCFunction)SdBusMessage_get_member, METH_NOARGS, "Get message member field"},
    {"create_reply", (PyCFunction)SdBusMessage_create_reply, METH_NOARGS, "Create reply message"},
    {"create_error_reply", (SD_BUS_PY_FUNC_TYPE)SdBusMessage_create_error_reply, SD_BUS_PY_METH, "Create error reply with error name and error message"},
    {"send", (PyCFunction)SdBusMessage_send, METH_NOARGS, "Queue message to be sent"},
    {NULL, NULL, 0, NULL},
};

static PyObject* SdBusMessage_expect_reply_getter(SdBusMessageObject* self, void* Py_UNUSED(closure)) {
        return PyBool_FromLong(CALL_SD_BUS_AND_CHECK(sd_bus_message_get_expect_reply(self->message_ref)));
}

static int SdBusMessage_expect_reply_setter(SdBusMessageObject* self, PyObject* new_value, void* Py_UNUSED(closure)) {
        if (NULL == new_value) {
                PyErr_SetString(PyExc_AttributeError, "Can't delete expect_reply");
                return -1;
        }

        if (!PyBool_Check(new_value)) {
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

PyType_Spec SdBusMessageType = {
    .name = "sd_bus_internals.SdBusMessage",
    .basicsize = sizeof(SdBusMessageObject),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT,
    .slots =
        (PyType_Slot[]){
            {Py_tp_init, (initproc)SdBusMessage_init},
            {Py_tp_dealloc, (destructor)SdBusMessage_dealloc},
            {Py_tp_methods, SdBusMessage_methods},
            {Py_tp_getset, SdBusMessage_properies},
            {0, NULL},
        },
};
