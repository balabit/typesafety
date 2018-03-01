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
import os.path
import shlex
import subprocess
import re

from nose.tools import *
from behave import given, when, then


assert_equal.__self__.maxDiff = None


@given('that "{file_name}" contains the following code')
def write_file(context, file_name):
    with open(os.path.join(context.test_dir, file_name), "w") as f:
        print(context.text, file=f)


@when('"{command}" is run')
def execute_command(context, command: str):
    command = re.sub(r'^python3', sys.executable, command)
    args = shlex.split(command)
    process = subprocess.Popen(
        args,
        stdin=None,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={"PYTHONPATH": "{}:{}".format(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), sys.path)}
    )
    output = process.communicate()[0].decode()
    return_code = process.returncode

    context.commands.append((command, return_code, output))


@then('it must fail')
def assert_failure(context):
    expected_output = context.text
    command, return_code, output = context.commands[-1]

    assert_in(expected_output, output, "Unexpected output of {!r}".format(command))
    assert_not_equal(0, return_code, "Unexpected return code of {!r}".format(command))


@then('it must pass')
def assert_success(context):
    command, return_code, output = context.commands[-1]

    assert_equal(
        0, return_code,
        "Unexpected return code of {!r}\nSTDOUT:\n{}".format(command, output)
    )
