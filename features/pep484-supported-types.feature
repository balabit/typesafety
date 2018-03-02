Feature: typing types are supported in annotations

  As a developer
  In order to write PEP-484 compliant code
  I want to use the typing module

  Scenario: calling a function expecting a typing.Callable argument passes with callable argument
    Given that "mylib.py" contains the following code:
          """
          import typing

          def apply_func(func: typing.Callable, *args):
              return func(*args)
          """
    And that "myapp.py" contains the following type checked code:
          """
          import mylib

          mylib.apply_func(lambda a, b: (b, a), 1, 2)
          """
     When "python3 myapp.py" is run
     Then it must pass

  Scenario: calling a function expecting a typing.Callable argument fails with non-callable argument
    Given that "mylib.py" contains the following code:
          """
          import typing

          def apply_func(func: typing.Callable, *args):
              return func(*args)
          """
    And that "myapp.py" contains the following type checked code:
          """
          import mylib

          mylib.apply_func(None, 1, 2, 3)
          """
     When "python3 myapp.py" is run
     Then it must fail
          """
          TypesafetyError: Argument 'func' of function 'apply_func' is invalid (expected: Callable; got: NoneType)
          """

  Scenario: calling a function expecting a typing.Union argument passes
    Given that "mylib.py" contains the following type checked code:
          """
          import typing

          def func(arg: typing.Union[int, str]):
              return arg
          """
    And that "myapp.py" contains the following code:
          """
          import mylib

          mylib.func(42)
          mylib.func("42")
          """
    When "python3 myapp.py" is run
    Then it must pass

  Scenario: calling a function expecting a typing.Union argument fails with wrong argument
    Given that "mylib.py" contains the following code:
          """
          import typing

          def func(arg: typing.Union[int, str]):
              return arg
          """
    And that "myapp.py" contains the following type checked code:
          """
          import mylib

          mylib.func(None)
          """
    When "python3 myapp.py" is run
    Then it must fail
          """
          TypesafetyError: Argument 'arg' of function 'func' is invalid (expected: typing.Union[int, str]; got: NoneType)
          """

  Scenario: calling a function expecting a typing.Optional argument passes
    Given that "mylib.py" contains the following code:
          """
          import typing

          def func(arg: typing.Optional[bool]):
              return arg
          """
    And that "myapp.py" contains the following type checked code:
          """
          import mylib

          mylib.func(False)
          mylib.func(None)
          """
    When "python3 myapp.py" is run
    Then it must pass

  Scenario: calling a function expecting a typing.Optional argument fails with wrong argument
    Given that "mylib.py" contains the following code:
          """
          import typing

          def func(arg: typing.Optional[float]):
              return arg
          """
    And that "myapp.py" contains the following type checked code:
          """
          import mylib

          mylib.func('spam')
          """
    When "python3 myapp.py" is run
    Then it must fail
          """
          TypesafetyError: Argument 'arg' of function 'func' is invalid (expected: typing.Union[float, NoneType]; got: str)
          """
