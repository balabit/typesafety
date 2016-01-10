#
# Copyright (c) 2013-2016 BalaBit
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


def process_version_string(version_string):
    return tuple(int(v) for v in version_string.split('.'))


def version_skip(cond, version_string, extra_message=None):
    msg = "Test is only run in Python " + version_string
    if extra_message is not None:
        msg += ": " + str(extra_message)

    return unittest.skipIf(cond, msg)


def is_above_version(version_string):
    return sys.version_info[:2] > process_version_string(version_string)


def is_below_or_at_version(version_string):
    return sys.version_info[:2] <= process_version_string(version_string)


def skip_above_version(version_string, extra_message=None):
    return version_skip(
        is_above_version(version_string),
        version_string + '+',
        extra_message=extra_message
    )


def skip_below_or_at_version(version_string, extra_message=None):
    return version_skip(
        is_below_or_at_version(version_string),
        version_string + '-',
        extra_message=extra_message
    )
