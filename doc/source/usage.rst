============================
Usage of the typesafety tool
============================

Type safety checker module for python. The type safety checker uses
a debugger to check each function call and return and check the
value types according to the annotations specified.

Turning on the type safety checker
==================================

The safety checker mechanism is used through the :class:`typesafety.Typesafety`
singleton class. The :func:`typesafety.activate` function can turn
the checking on and the :func:`typesafety.deactivate` can turn it off.

Module testmod:

.. code-block:: python

    def my_function(x : int):
        return x + 1

Main:

.. code-block:: python

    import typesafety
    import imp
    import testmod

    testmod.my_function(1.0)      # No error

    typesafety.activate()
    testmod = imp.reload(testmod)
    testmod.my_function(1.0)      # Will throw a TypeError

Specifying functions
====================

A function with argument or return value annotations will be used
to implement the type safety check mechanism. For further information
on how annotations work, see the Python documentation.

Type annotations
----------------

The simplest type safety check is when a singular type is specified
for an argument:

.. code-block:: python

    def my_function(x : int) -> float:
        return float(x) + 1.0

    my_function(1)      # Will return 2.0
    my_function(1.0)    # Will throw a TypeError

In this case on each call the type safety checker will validate that
the argument is an `int` and the return value is a `float`.

Callable annotations
--------------------

Some conditions cannot be checked by `isinstance`. If the parameter needs
to be a callable object (i.e. function, object with `__call__` implemented,
etc.) we can annotate the argument or return value with a callable:

.. code-block:: python

    def decorator(func : callable) -> callable:
        # ...
        return res

    @decorator
    def my_function(x):
        pass

    decorator(1)    # Will throw a TypeError

Multiple annotations
--------------------

If a tuple is specified in the annotation, then at least
one of the specified conditions must apply to the argument.

.. code-block:: python

    def multiple_argument_types(number : (int, float)) -> (int, float):
        return number + 1

    multiple_argument_types(1)          # Will return 2
    multiple_argument_types(1.0)        # Will return 2.0
    multiple_argument_types('string')   # Will throw a TypeError

Generating documentation using annotations with Sphinx autodoc
==============================================================

To avoid having to write parameter documentation manually, the
``typesafety.sphinxautodoc`` Sphinx extension is provided. It will
automatically add the typesafety annotations to the signatures that
Sphinx autodoc puts into the documentation.

Decorator functions
-------------------

Custom decorator functions often work like the following:

.. code-block:: python

    from functools import wraps

    def some_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Do some additional stuff, and then...
            return func(*args, **kwargs)

        return wrapper

    @some_decorator
    def my_annotated_function(x: int):
        pass

This way the documentation for ``my_annotated_function`` will use the
signature of the decorated function, ie. it will be just ``*args,
**kwargs`` which is not very helpful. Sadly, there is no out-of-the-box
solution for this problem, however, if the decorator is extended with
setting the ``decorated_function`` attribute of the wrapper function it
returns, then ``typesafety.sphinxautodoc`` will use that attribute to
read the signature from:

.. code-block:: python

    def some_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Do some additional stuff, and then...
            return func(*args, **kwargs)


        wrapper.decorated_function = func

        return wrapper

Using the above version of ``@some_decorator`` will enable
``typesafety.sphinxautodoc`` to generate the proper signature
documentation for ``my_annotated_function()``, ie. ``(x: int)``.
