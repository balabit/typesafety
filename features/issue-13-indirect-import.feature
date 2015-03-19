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

Feature: Issue #13: indirect imports of foreign objects should not be checked

  As a developer
  In order to avoid conflicts with external libraries
  I want typesafety to leave foreign objects alone

  Scenario: autodecorator doesn't affect objects imported from external modules
    Given that "external_lib.py" contains the following code:
          """
          def external_function(a: int) -> int:
              return 1
          """
      And that "mylib.py" contains the following code:
          """
          from external_lib import *
          """
      And that "myapp.py" contains the following code:
          """
          from typesafety.validator import Validator
          import typesafety; typesafety.activate(filter_func=lambda name: name == 'mylib')
          from mylib import *

          assert not Validator.is_function_validated(external_function), \
              "external_function should not be validated but it is."
          """
     When "python3 myapp.py" is run
     Then it must pass
