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

import sys
import collections

from . import mockmodule2
from .version import is_above_version

# External objects not native to this module
from .externalmodule import UndecoratedClass, undecorated_function


if not is_above_version('3.2'):
    class ClassWithSlots:
        __slots__ = ['mutable']

        @property
        def immutable(self):
            return 1

        @property
        def mutable(self):
            return 2


def function():
    pass


class ModuleClass(object):
    def __init__(self):
        super(ModuleClass, self).__init__()

    def method(self):
        pass

    @property
    def value(self):
        pass

    @classmethod
    def clsmethod(cls):
        pass

    @staticmethod
    def staticmethod():
        pass
