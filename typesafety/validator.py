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

import functools
import inspect
import warnings

from typing_inspect import is_union_type, get_args


class TypesafetyError(Exception):
    '''
    A type error detected by the Typesafety tool. Does not interfere
    with the builtin TypeError so one does not accidentally write an
    assertion in a unit test on a Typesafety error when intending to
    assert on a TypeError raised by actual production code.
    '''


class Validator(object):
    '''
    A Validator is a class that can check the function argument
    and return value types as specified in the function annotations.

    The `function` argument must be a function, method or generator.

    The given function and it's annotations will be checked if they
    conform to the following rules:

    * The annotation is a class (subclass of `type`),
    * the annotation is a callable object (`callable` returns true on it) or
    * is a tuple whose elements conform to the same rules.

    Any annotations not conforming to the above rules will be ignored
    as they might belong to a different purpose.
    '''

    ARG_TYPE_ERROR_MESSAGE = "Argument {0} of function {1!r} is invalid " + \
                             "(expected: {2}; got: {3})"
    RET_TYPE_ERROR_MESSAGE = "Return value of function {0!r} is invalid " + \
                             "(expected: {1}; got: {2})"

    @classmethod
    def get_function_validator(cls, function):
        '''
        Return the validator bound to `function` or None if the function
        is not validated.
        '''

        return getattr(function, '__validator__', None)

    @classmethod
    def is_function_validated(cls, function):
        '''
        Return True if the function has a bound validator.
        '''

        return cls.get_function_validator(function) is not None

    @classmethod
    def decorate(cls, function):
        '''
        Decorate a function so the function call is checked whenever
        a call is made. The calls that do not need any checks are skipped.

        The `function` argument is the function to be decorated.

        The return value will be either

        * the function itself, if there is nothing to validate, or
        * a proxy function that will execute the validation.
        '''

        should_skip = getattr(function, 'typesafety_skip', False)
        if cls.is_function_validated(function) or should_skip:
            return function

        validator = cls(function)

        if not validator.need_validate_arguments and \
                not validator.need_validate_return_value:
            return function

        @functools.wraps(function)
        def __wrapper(*args, **kwargs):
            return validator(*args, **kwargs)

        __wrapper.__validator__ = validator

        return __wrapper

    @classmethod
    def undecorate(cls, function):
        '''
        Remove validator decoration from a function.

        The `function` argument is the function to be cleaned from
        the validator decorator.
        '''

        if cls.is_function_validated(function):
            return cls.get_function_validator(function).function

        return function

    def __init__(self, function):
        self.__function = function
        self.__spec = inspect.getfullargspec(function)
        self.__argument_annotation = {}
        self.__return_annotation = None
        self.__defaults = {}

        self.__process_type_annotations()
        self.__process_return_value_annotation()
        self.__process_default_values()

    @property
    def need_validate_arguments(self):
        '''
        True if any of the function arguments need to be checked.
        '''

        return bool(self.__argument_annotation)

    @property
    def need_validate_return_value(self):
        '''
        True if the return value of the function needs to be be checked.
        '''

        return self.__return_annotation is not None

    @property
    def function(self):
        '''
        The raw function value.
        '''

        return self.__function

    def validate_arguments(self, locals_dict):
        '''
        Validate the arguments passed to a function. If an error occurred,
        the function will throw a TypesafetyError.

        The `locals_dict` argument should be the local value dictionary of
        the function. An example call would be like:
        '''

        for key, value, validator in self.__map_arguments(locals_dict):
            if not self.__is_valid(value, validator):
                key_name = repr(key)
                func_name = self.__function.__name__
                annotation = self.__argument_annotation.get(key)
                message = self.ARG_TYPE_ERROR_MESSAGE.format(
                    key_name,
                    func_name,
                    self.__format_expectation(annotation),
                    value.__class__.__name__)
                raise TypesafetyError(message)

    def __format_expectation(self, annotation):
        if isinstance(annotation, tuple):
            return "({})".format(
                ", ".join(self.__format_expectation(a) for a in annotation)
            )

        if annotation is None:
            return "None"

        return getattr(annotation, '__name__', str(annotation))

    def validate_return_value(self, retval):
        '''
        Validate the return value of a function call. If an error occurred,
        the function will throw a TypesafetyError.

        The `retval` should contain the return value of the function call.
        '''

        if self.__return_annotation is None:
            return

        if not self.__is_valid(retval, self.__return_annotation):
            func_name = self.__function.__name__
            msg = self.RET_TYPE_ERROR_MESSAGE.format(
                func_name,
                self.__format_expectation(self.__return_annotation),
                retval.__class__.__name__
            )
            raise TypesafetyError(msg)

    def __call__(self, *args, **kwargs):
        '''
        Proxy function to the function call including the validations.
        '''

        locals_dict = self.__collect_argument_dictionary(args, kwargs)
        self.validate_arguments(locals_dict)

        # The function property is callable, but pylint sees it as a
        # simple property object.
        return_value = self.function(*args, **kwargs)  # pylint: disable=E1102

        self.validate_return_value(return_value)
        return return_value

    def __process_type_annotations(self):
        for name, value in self.__spec.annotations.items():
            if name == 'return' or \
                    not self.__is_valid_typecheck_annotation(value):
                continue

            self.__argument_annotation[name] = value

    def __process_return_value_annotation(self):
        if 'return' in self.__spec.annotations:
            return_annotation = self.__spec.annotations['return']
            if self.__is_valid_typecheck_annotation(return_annotation):
                self.__return_annotation = return_annotation

    def __process_default_values(self):
        if self.__spec.defaults is not None:
            args_with_defaults = self.__spec.args[-len(self.__spec.defaults):]
            for index, name in enumerate(args_with_defaults):
                self.__defaults[name] = self.__spec.defaults[index]

        if self.__spec.kwonlydefaults is not None:
            for name in self.__spec.kwonlyargs:
                if name in self.__spec.kwonlydefaults:
                    self.__defaults[name] = self.__spec.kwonlydefaults[name]

    def __collect_argument_dictionary(self, args, kwargs):
        locals_dict = dict(self.__defaults)

        for index, value in enumerate(args):
            if index < len(self.__spec.args):
                locals_dict[self.__spec.args[index]] = value

        for name, value in kwargs.items():
            locals_dict[name] = value

        return locals_dict

    def __map_arguments(self, locals_dict):
        for name in self.__spec.args + self.__spec.kwonlyargs:
            if name not in self.__argument_annotation:
                continue

            if name not in locals_dict:
                msg = 'Missing required argument {!r}'.format(name)
                raise TypesafetyError(msg)

            annotation = self.__argument_annotation[name]
            yield name, locals_dict[name], annotation

    def __is_valid(self, value, validator):
        if isinstance(validator, tuple):
            return any(
                self.__is_valid(value, subvalidator)
                for subvalidator in validator
            )

        if is_union_type(validator):
            return any(
                self.__is_valid(value, subvalidator)
                for subvalidator in get_args(validator)
            )

        if isinstance(validator, type):
            return isinstance(value, validator)

        if hasattr(validator, '__call__'):
            return validator(value)

        if validator is None:
            return value is None

        # This line will probably never be reached
        return True

    def __is_valid_typecheck_annotation(self, validator):
        if isinstance(validator, tuple):
            is_valid = all(
                self.__is_valid_typecheck_annotation(subvalidator)
                for subvalidator in validator
            )
            if is_valid:
                warnings.warn("Tuple notation is deprecated, use typing.Union or typing.Optional", DeprecationWarning)

            return is_valid

        if is_union_type(validator):
            return all(
                self.__is_valid_typecheck_annotation(subvalidator)
                for subvalidator in get_args(validator)
            )

        if isinstance(validator, type):
            return True

        if callable(validator):
            if validator == callable:
                warnings.warn(
                    "Using callable() as a notation is deprecated, use typing.Callable instead",
                    DeprecationWarning
                )
            return True

        if validator is None:
            return True

        return False


__tracebackhide__ = True
__all__ = ['Validator']
