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
"""
Test module for the pytest plugin; named "check_*" instead of "test_*" so
nosetests doesn't try to collect it.
"""
import pytest

# pylint: disable=invalid-name
pytest_plugins = 'pytester'


@pytest.mark.parametrize('enabled', [True, False])
def test_enabled(testdir, enabled):
    testdir.makepyfile(
        identity='''
            def identity(i: int):
                return i
        ''',
        test_identity='''
            from identity import identity
            def test_identity():
                assert identity("name") == "name"
        ''')

    args = ['test_identity.py']
    if enabled:
        args = ['--enable-typesafety', 'identity'] + args
    result = testdir.runpytest(*args)

    expected = "*1 failed*" if enabled else "*1 passed*"
    result.stdout.fnmatch_lines([expected])
