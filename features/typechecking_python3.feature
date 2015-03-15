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

Feature: type checking Python 3 code

  As a developer
  In order to keep my code self-documenting
  I want to add runtime verified type annotations to my functions and methods

  Scenario: verifying function arguments
    Given that "somelib.py" contains the following code:
          """
          def some_function(x: int):
              return x + 1
          """
      And that "someprogram.py" contains the following code:
          """
          import typesafety; typesafety.activate(filter_func=lambda _: True)

          from somelib import some_function

          some_function("not an int")
          """
     When "python3 someprogram.py" is run
     Then it must fail:
          """
          typesafety.validator.TypesafetyError: Argument 'x' of function 'some_function' is invalid (expected: int; got: str)
          """

  Scenario: verifying function return values
    Given that "somelib.py" contains the following code:
          """
          def some_function() -> int:
              return "not an int"
          """
      And that "someprogram.py" contains the following code:
          """
          import typesafety; typesafety.activate(filter_func=lambda _: True)

          from somelib import some_function

          some_function()
          """
     When "python3 someprogram.py" is run
     Then it must fail:
          """
          typesafety.validator.TypesafetyError: Return value of function some_function is invalid
          """

  Scenario: allowing multiple types
    Given that "somelib.py" contains the following code:
          """
          def some_function(x: (str, int)):
              return x
          """
      And that "someprogram.py" contains the following code:
          """
          import typesafety; typesafety.activate(filter_func=lambda _: True)

          from somelib import some_function

          some_function("some str")
          some_function(42)
          some_function(4.2)
          """
     When "python3 someprogram.py" is run
     Then it must fail:
          """
          typesafety.validator.TypesafetyError: Argument 'x' of function 'some_function' is invalid (expected: (str, int); got: float)
          """

  Scenario: marking a function to be skipped
    Given that "skipped_function.py" contains the following code:
          """
          def unchecked(x: int) -> int:
              return "not an int"

          unchecked.typesafety_skip = True

          def checked(x: int) -> int:
              return "not an int"
          """
      And that "someprogram.py" contains the following code:
          """
          import typesafety; typesafety.activate(filter_func=lambda _: True)

          from skipped_function import unchecked, checked

          unchecked("hello")

          try:
              checked(1)

          except typesafety.TypesafetyError as exc:
              exit(0)

          exit(1)
          """
     When "python3 someprogram.py" is run
     Then it must pass
