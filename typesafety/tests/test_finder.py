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

import sys
import unittest

from typesafety.finder import ModuleFinder
from typesafety.autodecorator import decorate_module


def mock_decorator(func):
    func.__decorated__ = True
    return func


def isdecorated(func):
    return getattr(func, '__decorated__', False)


def undecorate(func):
    if hasattr(func, '__decorated__'):
        del func.__decorated__

    return func


class TestModuleFinder(unittest.TestCase):
    def setUp(self):
        self.finder = ModuleFinder(mock_decorator)

    def tearDown(self):
        self.finder.uninstall()

    def test_module_found(self):
        self.finder.install()
        import typesafety.tests.mockmodule
        self.assertTrue(self.finder.installed)
        self.assertTrue(
            isdecorated(typesafety.tests.mockmodule.function)
        )
        self.assertTrue(
            isdecorated(typesafety.tests.mockmodule.ModuleClass.method)
        )

    def test_module_found_but_filtered_out(self):
        self.finder.set_filter(lambda name: False)
        self.finder.install()
        import typesafety.tests.mockmodule
        self.assertFalse(
            isdecorated(typesafety.tests.mockmodule.function)
        )
        self.assertFalse(
            isdecorated(typesafety.tests.mockmodule.ModuleClass.method)
        )
