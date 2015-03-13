============================
Usage of the typesafety tool
============================

Typesafety is a tool for Python (3.2 or newer) that - using annotations -
checks if the arguments for function calls are valid. For example, consider
the following piece of code:

.. code-block:: python

   def sign(x):
       if not isinstance(x, int):
           raise TypeError('Invalid type {!r}, expected int'.format(x))
 
       if x < 0:
           return -1
 
       if x > 0:
           return 1
 
       return 0

The manual type check can become cumbersome really fast, especially when
there are multiple arguments, complex checks, etc. Wouldn't it be cool if
for internal (i.e. not API) code the checks could be done more concisely?
If you could write:

.. code-block:: python

    def sign(x: int):
        # ...

Testing with typesafety
=======================

Typesafety is meant to be used during testing. True, the checker can be
turned on in production code but the performace slowdown can make this
undesirable.

Currently, our preferred tool for running unit tests is nosetests. Using
the typesafety tool with nose is very simple:

::

   $ nosetests --enable-typesafety mymodule

And voila! Type checking is enabled for the module ``mymodule``.

Enabling typesafety manually
----------------------------

The typesafety tool can also be enabled "manually," using the
``typesafety.activate`` function. Consider the module ``testmod``:

.. code-block:: python

    def my_function(x: int) -> int:
        return x + 1

Before importing ``testmod``, we need to enable typesafety:

.. code-block:: python

    import typesafety
    import imp
    import testmod

    testmod.my_function(1.0)      # No error, since typesafety is not enabled

    # Note that the filter_func optional argument can be used to filter
    # which modules will be type checked.
    typesafety.activate(filter_func=lambda name: name.startswith('testmod.'))
    testmod = imp.reload(testmod)
    testmod.my_function(1.0)      # Will throw a TypesafetyError

**NOTE**: We use the exception ``TypesafetyError`` instead of the more
appropriate, built-in ``TypeError`` since raising a ``TypeError`` would cause
tests asserting for ``TypeError`` to pass if the arguments are wrong.

Specifying typesafety checks
----------------------------

A function with argument or return value annotations will be used
to implement the type safety check mechanism. For further information
on how annotations work, see the Python documentation.

Type annotations
................

The simplest type safety check is when a singular type is specified
for an argument or return value:

.. code-block:: python

    def my_function(x: int) -> float:
        return float(x) + 1.0

    my_function(1)      # Will return 2.0
    my_function(1.0)    # Will throw a TypesafetyError

In this case on each call the type safety checker will validate that
the argument is an ``int`` and the return value is a ``float``.

Callable annotations
....................

Some conditions cannot be checked by ``isinstance``. If the parameter needs
to be a callable object (i.e. function, object with ``__call__`` implemented,
etc.) we can annotate the argument or return value with a callable:

.. code-block:: python

    def decorator(func: callable) -> callable:
        # ...
        return res

    @decorator
    def my_function(x):
        pass

    decorator(1)    # Will throw a TypesafetyError

Multiple annotations
....................

If a tuple is specified in the annotation, then at least
one of the specified conditions must apply to the argument.

.. code-block:: python

    def multiple_argument_types(number: (int, float)) -> (int, float):
        return number + 1

    multiple_argument_types(1)          # Will return 2
    multiple_argument_types(1.0)        # Will return 2.0
    multiple_argument_types('string')   # Will throw a TypesafetyError

Generating documentation using annotations with Sphinx autodoc
==============================================================

To avoid having to write parameter documentation manually, the
``typesafety.sphinxautodoc`` Sphinx extension is provided. It will
automatically add the typesafety annotations to the signatures that
Sphinx autodoc puts into the documentation.

Usage
-----

In your Sphinx config file, simply add ``typesafety.sphinxautodoc`` to the
extension list:

.. code-block:: python

    extensions.append('typesafety.sphinxautodoc')

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
