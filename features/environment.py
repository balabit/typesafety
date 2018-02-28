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

import os
import tempfile
import shutil


def before_scenario(context, scenario):
    context.commands = []
    context.test_dir = tempfile.mkdtemp(prefix="typesafety_test")
    os.chdir(context.test_dir)

    with open(os.path.join(context.test_dir, "__init__.py"), "w") as f:
        f.write("")


def after_scenario(context, scenariot):
    shutil.rmtree(context.test_dir, ignore_errors=True)
