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

import re
import os.path
import nose

import typesafety


# Monkey-patching the _exc_info_to_string is the only simple way to influence
# how the exception gets formatted. We can't really replace the object with a
# subclass (we use this in a nose plugin, which is one of the many classes
# modifying the TestResult class).
class ExceptionStringConverter:  # pylint: disable=W0212
    TRACE_LINE_PATTERN = re.compile(r'^  File "([^"]*)"')

    @classmethod
    def wrap_results_object(cls, result):
        result._exc_info_to_string = cls(result._exc_info_to_string)

    def __init__(self, original_converter):
        self.__original_converter = original_converter

    def __call__(self, err, test):
        res = []
        skip_line = False
        for line in self.__original_converter(err, test).split('\n'):
            if skip_line:
                skip_line = False
                continue

            match = self.TRACE_LINE_PATTERN.match(line)
            if match is not None and self.__should_skip(match.group(1)):
                skip_line = True
                continue

            res.append(line)

        return '\n'.join(res)

    def __should_skip(self, filename):
        relative = os.path.relpath(filename, typesafety.__path__[0])
        return not relative.startswith('..')


class TypesafetyPlugin(nose.plugins.Plugin):
    name = 'typesafety'
    __enabled_for = ()
    keep_typesafety_trace = False
    enabled = False

    def __init__(self, *args, activate=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.__activate = activate or typesafety.activate

    def options(self, parser, env):
        parser.add_option(
            '-T', '--enable-typesafety', action='append', metavar='MODULE',
            help='Enable typesafety for the given modules'
        )
        parser.add_option(
            '--keep-typesafety-trace', action='store_true',
            help='Do not hide typesafety traceback frames ' +
            '(useful when debugging typesafety)'
        )

    def configure(self, options, conf):
        if options.enable_typesafety:
            self.enabled = True
            self.__enabled_for = tuple(
                mod.split('.') for mod in options.enable_typesafety
            )
            try:
                self.__activate(filter_func=self.__check_need_activate)

            except RuntimeError:
                # Nose plugin was already enabled in a different thread
                return

            self.keep_typesafety_trace = options.keep_typesafety_trace

    # This is an interface function that cannot be removed (see the nose
    # plugin documentation for the meaning of this function).
    def prepareTestResult(self, result):  # pylint: disable=C0103
        if not self.keep_typesafety_trace:
            ExceptionStringConverter.wrap_results_object(result)

    def __check_need_activate(self, module_name):
        module_name = module_name.split('.')
        return any(
            module_name[:len(name)] == name for name in self.__enabled_for
        )
