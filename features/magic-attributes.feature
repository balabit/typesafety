
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

Feature: Librariess depending on magic attributes of functions should not be affected by typesafety

  As a developer
  In order to be able to use abstract classes in my code
  I want typesafety to not interfere with them
  or any other library using magic attributes on functions


  Scenario: abstract classes should not be instantiable in any circumstances

    Given that "mylib.py" contains the following code:
          """
          import abc

          class AbstractClass(metaclass=abc.ABCMeta):
              @abc.abstractmethod
              def abstract_method(self, arg: int):
                  pass

          """
    And that "myapp.py" contains the following code:
          """
          from typesafety.validator import Validator
          import typesafety

          typesafety.activate(filter_func=lambda _: True)

          # import annotated code _after_ activating typesafety
          import mylib

          class AbstractDerivedClass(mylib.AbstractClass):
              pass

          AbstractDerivedClass()


          """
     When "python3 myapp.py" is run
     Then it must fail
          """
          TypeError: Can't instantiate abstract class AbstractDerivedClass with abstract methods abstract_method
          """
