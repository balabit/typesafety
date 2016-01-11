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

Feature: Issue #21: AttributeError on overridden read only properties

  As a developer
  In order to avoid crashing because of an undecorable function
  I want typesafety to ignore errors when decorating and issuing a warning


  Scenario: if autodecorator fails to decorate a function, it should ignore the function but warn the user
    Given that "mylib.py" contains the following code:
          """
          class Poc:
              @property
              def __dict__(self) -> dict:
                  return {}
          """
      And that "myapp.py" contains the following code:
          """
          import warnings

          from typesafety.validator import Validator
          import typesafety; typesafety.activate(filter_func=lambda _: True)

          with warnings.catch_warnings(record=True) as warn:
              from mylib import *

          assert not Validator.is_function_validated(Poc.__dict__), \
              "Poc.__dict__ should not be validated but it is."
          assert len(warn) == 1, "Exactly one warning must be issued"
          assert warn[0].message.args[0] == 'Could not decorate mylib.Poc.__dict__', \
              "Wrong message received: {}".format(warn[0].message.args[0])
          """
     When "python3 myapp.py" is run
     Then it must pass
