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
from typesafety import TypesafetyError


def pytest_addoption(parser):
    parser.addoption(
        '-T', '--enable-typesafety', action='append', metavar='MODULE',
        help='Enable typesafety for the given modules'
    )


def pytest_configure(config):
    if config.getoption('enable_typesafety'):
        import typesafety
        import functools

        enabled_for = tuple(
            mod.split('.') for mod in config.getoption('enable_typesafety')
        )
        filter_func = functools.partial(__check_need_activate,
                                        enabled_for=enabled_for)
        typesafety.activate(filter_func=filter_func)


def pytest_unconfigure(config):
    if config.getoption('enable_typesafety'):
        import typesafety
        typesafety.deactivate()


def pytest_runtest_makereport(item, call):
    """
    Use report maker hook for early traceback cleanup

    Have to remove typesafety from trace before py.test removes itself, for
    avoid empty trace.
    """

    excinfo = call.excinfo
    if not excinfo or excinfo.type is not TypesafetyError:
        return

    excinfo.traceback = excinfo.traceback.filter()


def __check_need_activate(module_name, enabled_for):
    module_name = module_name.split('.')
    return any(
        module_name[:len(name)] == name for name in enabled_for
    )
