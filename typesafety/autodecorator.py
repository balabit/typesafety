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

'''
Scan some class or module object and decorate it's functions and methods with
the supplied decorator function.

Usage:

>>> class MyClass(object):
...     def mymethod(self):
...         return 0
>>> def log(func):
...     def __wrapper(*args, **kwargs):
...         print('Called function %s' % func.__name__)
...         return func(*args, **kwargs)
...     return __wrapper
>>> decorate_module(MyClass, decorator=log)
>>> obj = MyClass()
>>> print(obj.mymethod())
Called function mymethod
0
'''

import inspect


class ModuleDecorator(object):
    '''
    Decorate a module automatically with the supplied decorator.
    This is just a helper class for the :func:`decorate` module function.

    The `decorator` argument is the decorator to be applied to functions.
    '''

    def __init__(self, decorator):
        self.__decorator = decorator

    def decorate(self, module):
        self.__decorate(module, use_dict=module.__dict__)

    def __is_attribute_mutable(self, object_dict, attr):
        if '__slots__' not in object_dict:
            return True

        return attr in object_dict['__slots__']

    def __decorate(self, module, *, use_dict):
        for key, value in use_dict.items():
            if not self.__is_attribute_mutable(use_dict, key):
                continue

            if inspect.isfunction(value):
                self.__decorate_function(module, key, value)

            elif inspect.isclass(value):
                self.__decorate(value, use_dict=value.__dict__)

            elif inspect.ismodule(value):
                if self.__submodule_of(value, module):
                    self.__decorate(value, use_dict=value.__dict__)

            elif isinstance(value, property):
                self.__decorate_property(module, key, value)

            elif isinstance(value, (staticmethod, classmethod)):
                self.__decorate_special_method(module, key, value)

    def __decorate_function(self, module, key, value):
        setattr(module, key, self.__decorator(value))

    def __decorate_property(self, module, key, value):
        fget = None
        fset = None
        fdel = None

        if value.fget is not None:
            fget = self.__decorator(value.fget)

        if value.fset is not None:
            fset = self.__decorator(value.fset)

        if value.fdel is not None:
            fdel = self.__decorator(value.fdel)

        setattr(module, key, property(fget=fget, fset=fset, fdel=fdel))

    def __decorate_special_method(self, module, key, value):
        func = self.__decorator(value.__func__)
        decorated = value.__class__(func)

        setattr(module, key, decorated)

    def __submodule_of(self, basemodule, submodule):
        return submodule.__name__.startswith(basemodule.__name__ + '.')


def decorate_module(module, *, decorator):
    ModuleDecorator(decorator).decorate(module)


__all__ = ['decorate_module']
