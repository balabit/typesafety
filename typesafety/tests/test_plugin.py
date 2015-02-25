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

import nose
import unittest
import optparse
import shlex
import mock

from ..noseplugin import TypesafetyPlugin


class TestPlugin(unittest.TestCase):
    def __activate_call(self, *, filter_func=None):
        self.filter = filter_func

    def setUp(self):
        self.filter = None
        self.plugin = TypesafetyPlugin(activate=self.__activate_call)

    def test_is_nose_plugin(self):
        self.assertIsInstance(self.plugin, nose.plugins.Plugin)

    def __get_options(self, enable_for=()):
        res = type(
            'Options',
            (object,),
            {
                'enable_typesafety': list(enable_for),
                'keep_typesafety_trace': False,
            }
        )

        return res()

    def test_not_enabled_by_default(self):
        self.assertFalse(self.plugin.enabled)

    def test_name(self):
        self.assertEqual('typesafety', self.plugin.name)

    def test_options(self):
        parser = optparse.OptionParser()
        self.plugin.options(parser, {})

        try:
            opts, _ = parser.parse_args(
                shlex.split(
                    'nosetests3 --enable-typesafety example ' +
                    '--enable-typesafety example2'
                )
            )

        except SystemExit as exc:
            self.fail('Option parser exited with code {}'.format(exc))

        self.assertEqual(
            ['example', 'example2'],
            opts.enable_typesafety
        )

    def test_not_enabled_without_modules_given(self):
        self.plugin.configure(self.__get_options(), None)

        self.assertFalse(self.plugin.enabled)

    def test_enabled_with_at_least_one_module_given(self):
        self.plugin.configure(
            self.__get_options(('example',)),
            None
        )

        self.assertTrue(self.plugin.enabled)

    def test_activate_called_with_filter_func(self):
        self.plugin.configure(
            self.__get_options(('example', 'example2')),
            None
        )

        self.assertTrue(self.filter('example'))
        self.assertTrue(self.filter('example2'))
        self.assertFalse(self.filter('example3'))
        self.assertTrue(self.filter('example.submodule'))
