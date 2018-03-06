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

'''
This module contains helper methods for dealing with the contents of the typing module. This
module is not really stable so there are differences even between minor versions. See:

    https://docs.python.org/3.6/library/typing.html

Note that this module is flaky and very hacky, but hopefully later we can use some external
tool for this.
'''

# There is no good, idiomatic way to determine if an annotation is a union or not,
# so we're saddled with this hacky solution.
# pylint: disable=unidiomatic-typecheck,protected-access
import typing


def is_union_type(cls):
    if hasattr(typing, '_Union'):
        return type(cls) is typing._Union

    return type(cls) is typing.UnionMeta


def get_union_args(cls):
    if not is_union_type(cls):
        raise TypeError('expected union type')

    if hasattr(cls, '__args__'):
        res = cls.__args__

    else:
        res = cls.__union_params__

    return res if res is not None else ()
