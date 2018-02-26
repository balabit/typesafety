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
Type safety checker module for python. The type safety checker uses
a debugger to check each function call and return and check the
value types according to the annotations specified.

Accepted annotations for type checked functions are class objects,
callable objects or tuples containing class and callable objects. If
any of the annotations does not conform to this rule the annotation
will be ignored.
'''

from .validator import Validator, TypesafetyError
from .finder import ModuleFinder


class Typesafety(object):
    '''
    Singleton class for managing the type safety checker.
    '''

    __instance = None

    @classmethod
    def instance(cls):
        '''
        Return the singleton instance.
        '''

        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def __init__(self):
        self.__module_finder = None

    @property
    def active(self):
        '''
        Returns whether the type safety checker is enabled.
        '''

        return self.__module_finder is not None

    def activate(self, *, filter_func=None):
        '''
        Activate the type safety checker. After the call all functions
        that need to be checked will be.
        '''

        if self.active:
            raise RuntimeError("Type safety check already active")

        self.__module_finder = ModuleFinder(Validator.decorate)
        if filter_func is not None:
            self.__module_finder.set_filter(filter_func)
        self.__module_finder.install()

    def deactivate(self):
        '''
        Deactivate the type safety checker. After the call no functions
        will be checked.
        '''

        if not self.active:
            raise RuntimeError("Type safety check inactive")

        self.__module_finder.uninstall()


def activate(*, filter_func=None):
    '''
    Shorthand function for activating the type checking.
    '''

    Typesafety.instance().activate(filter_func=filter_func)


def deactivate():
    '''
    Shorthand function for deactivating the type checking.
    '''

    Typesafety.instance().deactivate()


__all__ = ['Typesafety', 'TypesafetyError', 'activate', 'deactivate']
