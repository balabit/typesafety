#
# Copyright (c) 2013-2015 BalaBit
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import unittest
import collections

from functools import wraps
from .version import skip_above_version, skip_below_or_at_version

from typesafety.sphinxautodoc import add_annotations_to_signature


class TestAnnotatedDocsForMethodSignatures(unittest.TestCase):
    def test_only_functions_classes_and_and_methods_are_considered(self):
        self.__assert_signature_docs_override(
            None,
            "module",
            "unittest",
            unittest
        )

    def __assert_signature_docs_override(
            self,
            expected_override,
            type_str,
            fully_qualified_name_suffix,
            obj
    ):
        signature_override = add_annotations_to_signature(
            app=None,
            what=type_str,
            name="%s.%s" % (self.__module__, fully_qualified_name_suffix),
            obj=obj,
            options={},
            signature="()",
            return_annotation=None
        )
        self.assertEqual(expected_override, signature_override)

    def test_when_there_are_no_annots_then_sign_docs_are_not_overridden(self):
        self.__assert_signature_docs_override(
            None,
            "function",
            "function_without_annotations",
            function_without_annotations
        )

    def test_when_args_have_annots_then_signature_docs_are_overridden(self):
        self.__assert_signature_docs_override(
            ("(an_int: int)", ""),
            "method",
            "ExampleClass.classmethod_with_builtin_type_annotations",
            ExampleClass.classmethod_with_builtin_type_annotations
        )

    def test_when_retval_has_annot_then_signature_docs_are_overridden(self):
        self.__assert_signature_docs_override(
            ("()", "str"),
            "function",
            "function_with_return_annotation_only",
            function_with_return_annotation_only
        )

    def test_class_signatures_are_overridden_according_to_their_init(self):
        self.__assert_signature_docs_override(
            ("(an_int: int)", ""),
            "class",
            "ExampleClass",
            ExampleClass
        )

    def test_cls_sign_are_not_overridden_when_their_init_dont_cont_annot(self):
        self.__assert_signature_docs_override(
            None,
            "class",
            "SomeClass",
            SomeClass
        )
        self.__assert_signature_docs_override(
            None,
            "class",
            "SomeOtherClass",
            SomeOtherClass
        )

    def test_default_values_are_added_to_positional_args(self):
        self.__assert_signature_docs_override(
            ("(a_float: float, an_int: int=42, an_str: str='')", ""),
            "method",
            "ExampleClass.method_with_default_value",
            ExampleClass.method_with_default_value
        )

    def test_first_arg_of_methods_is_ign_even_if_it_has_a_default_value(self):
        self.__assert_signature_docs_override(
            ("(an_int: int=42)", ""),
            "method",
            "ExampleClass.method_with_default_value_for_self",
            ExampleClass.method_with_default_value_for_self
        )

    def test_default_value_can_be_complex(self):
        self.__assert_signature_docs_override(
            ("(a_tuple: tuple=(1, 2, 3))", ""),
            "function",
            "function_with_complex_default_value",
            function_with_complex_default_value
        )

    def test_mixed_types_are_represented_as_tuples(self):
        self.__assert_signature_docs_override(
            ("(something: (None, int)=None)", "(int, None)"),
            "function",
            "function_with_mixed_types",
            function_with_mixed_types
        )

    def test_string_annotations_dont_cause_infinite_recursion(self):
        self.__assert_signature_docs_override(
            ("(an_arg: 'some string')", ""),
            "function",
            "function_with_string_annotation",
            function_with_string_annotation
        )

    def test_varargs_are_added_into_the_signature_when_present(self):
        self.__assert_signature_docs_override(
            ("(an_int: int, *varargs, **varkwargs)", ""),
            "method",
            "ExampleClass.method_with_varargs",
            ExampleClass.method_with_varargs
        )

    def test_varargs_can_be_annotated(self):
        self.__assert_signature_docs_override(
            ("(an_int, *varargs: list, **varkwargs: dict)", ""),
            "function",
            "function_with_annotated_varargs",
            function_with_annotated_varargs
        )

    def test_kwonly_args_are_appended_after_an_asterisk(self):
        self.__assert_signature_docs_override(
            ("(a_float: float, *, an_int: int)", ""),
            "method",
            "ExampleClass.method_with_kwonly_arg",
            ExampleClass.method_with_kwonly_arg
        )

    def test_class_names_are_fully_qualified(self):
        self.__assert_signature_docs_override(
            (
                "(an_object: %s.SomeClass)" % self.__module__,
                "%s.SomeClass" % self.__module__
            ),
            "method",
            "ExampleClass.method_with_class_names",
            ExampleClass.method_with_class_names
        )

    def test_type_annotations_can_be_functions(self):
        self.__assert_signature_docs_override(
            ("(a_callable: callable)", "callable"),
            "method",
            "ExampleClass.method_with_function_annotations",
            ExampleClass.method_with_function_annotations
        )

    def test_type_annotations_can_be_named_tuples(self):
        self.__assert_signature_docs_override(
            ("(a_tuple: %s.SomeNamedTuple)" % self.__module__, ""),
            "function",
            "function_with_named_tuple",
            function_with_named_tuple
        )

    def test_decorated_methods_are_resolved_when_decor_func_attr_is_set(self):
        self.__assert_signature_docs_override(
            ("(an_int: int)", "str"),
            "method",
            "ExampleClass.method_with_decorators",
            ExampleClass.method_with_decorators
        )

    @skip_above_version(
        "3.3",
        "For some reason, version(s) 3.3+ handle annotations of decorated "
        "functions differently. In 3.4 this seems to be fixed."
    )
    def test_decorated_methods_should_not_trigger_inifinite_loop(self):
        self.__assert_signature_docs_override(
            ("(*args, **kwargs)", ""),
            "method",
            "ExampleClass.method_with_recursive_decorator",
            ExampleClass.method_with_recursive_decorator
        )

    @skip_below_or_at_version("3.3", "See the exact explanation above")
    def test_decorated_methods_dont_trigger_inf_loop_but_return_none(self):
        self.__assert_signature_docs_override(
            None,
            "method",
            "ExampleClass.method_with_recursive_decorator",
            ExampleClass.method_with_recursive_decorator
        )

    @skip_above_version(
        "3.3",
        "For some reason, version(s) 3.3+ handle annotations of decorated " +
        "functions differently. In 3.4 this seems to be fixed."
    )
    def test_decorated_methods_should_not_trigger_errors(self):
        self.__assert_signature_docs_override(
            ("(*args, **kwargs)", ""),
            "method",
            "ExampleClass.method_with_messed_up_decorator",
            ExampleClass.method_with_messed_up_decorator
        )

    @skip_below_or_at_version("3.3", "See the exact explanation above")
    def test_decorated_methods_should_not_trigger_errors_but_return_none(self):
        self.__assert_signature_docs_override(
            None,
            "method",
            "ExampleClass.method_with_messed_up_decorator",
            ExampleClass.method_with_messed_up_decorator
        )

    def test_integration(self):
        self.__assert_signature_docs_override(
            (
                "(an_int: int, a_string: (None, str)=None, " +
                "*, a_callable: (None, callable)=None, **kwargs: dict)",
                "str"
            ),
            "method",
            "ExampleClass.integration",
            ExampleClass.integration
        )


class SomeClass:
    def __init__(self):
        pass


class SomeOtherClass:
    def __init__(self):
        pass


SomeNamedTuple = collections.namedtuple("SomeNamedTuple", "x")


def function_without_annotations(an_int):
    pass


def function_with_return_annotation_only() -> str:
    return "sample return value"


def function_with_mixed_types(something: (None, int)=None) -> (int, None):
    return something


def function_with_named_tuple(a_tuple: SomeNamedTuple):
    pass


def function_with_annotated_varargs(an_int, *varargs: list, **varkwargs: dict):
    pass


def function_with_complex_default_value(a_tuple: tuple=(1, 2, 3)):
    pass


def function_with_string_annotation(an_arg: "some string"):
    pass


def some_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    wrapper.decorated_function = func

    return wrapper


def recursive_decorator(func):
    wrapper = some_decorator(func)
    wrapper.decorated_function = wrapper

    return wrapper


def messed_up_decorator(func):
    wrapper = some_decorator(func)
    wrapper.decorated_function = "this is not a function"

    return wrapper


class ExampleClass:
    @classmethod
    def classmethod_with_builtin_type_annotations(cls, an_int: int):
        pass

    def __init__(self, an_int: int):
        pass

    def method_with_default_value(
            self,
            a_float: float,
            an_int: int=42,
            an_str: str=""
    ):
        pass

    def method_with_varargs(self, an_int: int, *varargs, **varkwargs):
        pass

    def method_with_kwonly_arg(self, a_float: float, *, an_int: int):
        pass

    def method_with_default_value_for_self(self=None, an_int: int=42):
        pass

    def method_with_class_names(self, an_object: SomeClass) -> SomeClass:
        return an_object

    def method_with_function_annotations(
            self,
            a_callable: callable
    ) -> callable:
        return a_callable

    @some_decorator
    @some_decorator
    def method_with_decorators(self, an_int: int) -> str:
        return ""

    @recursive_decorator
    def method_with_recursive_decorator(self, an_int: int):
        return ""

    @messed_up_decorator
    def method_with_messed_up_decorator(self, an_int: int):
        return ""

    # This method is an example for some argument checks, so those
    # arguments are needed even though they are not used.
    # pylint: disable=W0612
    def integration(
            self,
            an_int: int,
            a_string: (None, str)=None,
            *,
            a_callable: (None, callable)=None,
            **kwargs: dict
    ) -> str:
        return "sample return value"
