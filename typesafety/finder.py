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
On import decorate imported modules with the supplied decorator.
'''

import imp
import importlib.abc
import sys
from . import autodecorator


class ModuleLoader(object):
    '''
    Simple proxy object that will call the :func:`ModuleFinder.load_module`
    function with the proper parameters.
    '''

    def __init__(self, finder, fullname, path):
        self.__finder = finder
        self.__fullname = fullname
        if path is None:
            self.__name = fullname

        else:
            self.__name = fullname.rsplit('.', 1)[-1]

        self.__path = path
        self.__info = imp.find_module(self.__name, path)

    @property
    def fullname(self):
        return self.__fullname

    @property
    def name(self):
        return self.__name

    @property
    def info(self):
        return self.__info

    def load_module(self, fullname):
        '''
        Load the module. Required for the Python meta-loading mechanism.
        '''

        return self.__finder.load_module(self)


class ModuleFinder(object):
    '''
    Module finder and loader. When installed, modules will be
    automatically decorated with the supplied decorator.

    The `decorator` is the decorator function to apply.

    The `filter` argument is a filter function that should return
    True if the given module should be decorated. This function takes
    two arguments:

    * The full name of the module and
    * the module object itself (after import).
    '''

    __decorator = None
    __filter = None
    __loaded_modules = None

    def __init__(self, decorator):
        self.__decorator = decorator
        self.__reset()

    @property
    def installed(self):
        '''
        True if the module finder/loader has been installed.
        '''

        return self in sys.meta_path

    def set_filter(self, filter_func):
        '''
        Set the module filter function.

        The `filter_func` argument expects a callable that gets the full
        module name and the loaded module object.
        '''

        self.__filter = filter_func

    def install(self):
        '''
        Install the module finder. If already installed, this will do nothing.
        After installation, each loaded module will be decorated.
        '''

        if not self.installed:
            sys.meta_path.insert(0, self)

    def uninstall(self):
        '''
        Uninstall the module finder. If not installed, this will do nothing.
        After uninstallation, none of the newly loaded modules will be
        decorated (that is, everything will be back to normal).
        '''

        if self.installed:
            sys.meta_path.remove(self)

        # Reload all decorated items
        import_list = []
        for name in self.__loaded_modules:
            del sys.modules[name]
            import_list.append(name)

        for name in import_list:
            __import__(name)

        self.__reset()

    def find_module(self, fullname, path=None):
        '''
        Find the module. Required for the Python meta-loading mechanism.

        This will do nothing, since we use the system to locate a module.
        '''

        loader = None
        if self.__filter is None or self.__filter(fullname):
            loader = ModuleLoader(self, fullname, path)

        return loader

    def load_module(self, loader):
        '''
        Load the module. Required for the Python meta-loading mechanism.
        '''

        modfile, pathname, description = loader.info
        module = imp.load_module(
            loader.fullname,
            modfile,
            pathname,
            description
        )
        sys.modules[loader.fullname] = module
        self.__loaded_modules.add(loader.fullname)

        autodecorator.decorate_module(module, decorator=self.__decorator)

        return module

    def __reset(self):
        self.__loaded_modules = set()


importlib.abc.Loader.register(ModuleLoader)
importlib.abc.Finder.register(ModuleFinder)


__all__ = ['ModuleFinder']
