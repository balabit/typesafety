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

from typesafety.typing_inspect import is_union_type, get_union_args


class TestTypingInspect(unittest.TestCase):
    def test_inspect_union_type(self):
        self.assertTrue(is_union_type(typing.Union[int, str]))
        self.assertTrue(is_union_type(typing.Optional[int]))
        self.assertFalse(is_union_type(typing.List[int]))
        self.assertFalse(is_union_type(typing.Any))

    def test_get_union_args(self):
        self.assertEqual((int, str), get_union_args(typing.Union[int, str]))
        self.assertEqual((int, type(None)), get_union_args(typing.Optional[int]))
        self.assertRaises(TypeError, get_union_args, typing.List[int])
        self.assertRaises(TypeError, get_union_args, typing.Any)
