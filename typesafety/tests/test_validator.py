#
# Copyright (c) 2013-2018 Balabit
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
import typing
import unittest

from typesafety.validator import Validator, TypesafetyError


def func_arg_validate(
        intarg: int,
        funcarg: callable,
        tuplearg: (int, float)
) -> int:
    return 1


# Is a test suite, can have as many public methods as needed.
class TestValidator(unittest.TestCase):  # pylint: disable=too-many-public-methods
    def setUp(self):
        self._validator = Validator(func_arg_validate)

    def test_function_has_no_annotation(self):
        def func_no_annotation(arg0, arg1, arg2):
            pass

        validator = Validator(func_no_annotation)
        self.assertFalse(validator.need_validate_arguments)
        self.assertFalse(validator.need_validate_return_value)

    def test_function_has_arg_annotation(self):
        def func_arg_annotated(arg: type):
            pass

        validator = Validator(func_arg_annotated)
        self.assertTrue(validator.need_validate_arguments)
        self.assertFalse(validator.need_validate_return_value)

    def test_function_has_ret_annotation(self):
        def func_ret_annotated(arg) -> type:
            pass

        validator = Validator(func_ret_annotated)
        self.assertFalse(validator.need_validate_arguments)
        self.assertTrue(validator.need_validate_return_value)

    def test_invalid_annotations_are_ignored(self):
        def func_ignore_annotation(arg: 1) -> (2,):
            pass

        validator = Validator(func_ignore_annotation)
        self.assertFalse(validator.need_validate_arguments)
        self.assertFalse(validator.need_validate_return_value)

    def test_valid_arguments(self):
        self._validator.validate_arguments(
            dict(intarg=1, funcarg=func_arg_validate, tuplearg=1.0)
        )
        self._validator.validate_arguments(
            dict(intarg=1, funcarg=func_arg_validate, tuplearg=1)
        )

    def test_invalid_arguments(self):
        self.assertRaises(
            TypesafetyError,
            self._validator.validate_arguments,
            dict(intarg=1, funcarg=1, tuplearg=1)
        )

    def test_valid_return_value(self):
        self._validator.validate_return_value(1)

    def test_invalid_return_value(self):
        self.assertTrue(self._validator.need_validate_return_value)
        self.assertRaises(
            TypesafetyError,
            self._validator.validate_return_value,
            1.0
        )

    def test_validate_arguments_without_annotations(self):
        def func_no_annotation(arg):
            pass

        Validator(func_no_annotation).validate_arguments(1)

    def test_validate_return_value_without_annotations(self):
        def func_no_annotation():
            pass

        Validator(func_no_annotation).validate_return_value(1)

    def test_validate_with_ignored_annotations(self):
        def func_ignore_annotation(arg: 1):
            pass

        Validator(func_ignore_annotation).validate_arguments(dict(x=1))

    def test_call_validator(self):
        self._validator(1, func_arg_validate, 1.0)

    def test_call_validator_with_bad_argument(self):
        self.assertRaises(TypesafetyError, self._validator, 1, 2, 1.0)

    def test_call_validator_with_bad_return_value(self):
        def func_bad_return() -> int:
            pass

        self.assertRaises(TypesafetyError, Validator(func_bad_return))

    def test_decorate_validated_function(self):
        @Validator.decorate
        def func_validate() -> int:
            return 1

        self.assertTrue(Validator.is_function_validated(func_validate))

    def test_decorate_non_validated_function(self):
        def func_dont_validate():
            pass

        self.assertEqual(
            func_dont_validate,
            Validator.decorate(func_dont_validate)
        )

    def test_undecorate_decorated_function(self):
        def func_validate() -> int:
            pass

        self.assertEqual(
            func_validate,
            Validator.undecorate(Validator.decorate(func_validate))
        )

    def test_undecorate_not_decorated_function(self):
        def func_dont_validate():
            pass

        self.assertEqual(
            func_dont_validate,
            Validator.undecorate(func_dont_validate)
        )

    def test_check_order_of_validation(self):
        def func_has_an_error(intarg: int):
            raise RuntimeError('error')

        self.assertRaises(TypesafetyError, Validator(func_has_an_error), 'a')

    def test_missing_required_argument(self):
        def func_has_required_arg(intarg: int):
            pass

        self.assertRaises(TypesafetyError, Validator(func_has_required_arg))

    def test_skip_typesafety_check_for_function(self):
        def skip_typesafety_check(arg: int) -> int:
            return "string"

        skip_typesafety_check.typesafety_skip = True

        self.assertEqual(
            skip_typesafety_check,
            Validator.decorate(skip_typesafety_check)
        )

    def test_validating_multiple_types(self):
        def func(arg: (str, int)):
            pass

        validator = Validator(func)
        validator("str")
        validator(42)

        with self.assertRaises(TypesafetyError) as error:
            validator(4.2)

        self.assertIn("expected: (str, int)", str(error.exception))

    def test_validating_multiple_types_or_none(self):
        def func(arg: (str, int, None)):
            pass

        validator = Validator(func)
        validator("str")
        validator(42)
        validator(None)

        with self.assertRaises(TypesafetyError) as error:
            validator(4.2)

        self.assertIn("expected: (str, int, None)", str(error.exception))

    def test_validate_typing_callable(self):
        def func(args: typing.Callable):
            return args

        def args_example():
            pass

        validator = Validator(func)

        self.assertEqual(args_example, validator(args_example))
        self.assertRaises(TypesafetyError, validator, None)

    def test_validate_typing_union(self):
        def func(arg: typing.Union[int, str]):
            return arg

        validator = Validator(func)

        self.assertEqual(1, validator(1))
        self.assertEqual("spam", validator("spam"))
        with self.assertRaises(TypesafetyError) as context:
            validator([])
        self.assertIn('typing.Union[int, str]', str(context.exception))
