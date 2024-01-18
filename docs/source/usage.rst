.. _usage:

Usage
========


Deprecated function
-------------------

.. code-block:: python

  from deprecat import deprecat

  @deprecat(reason="this is a bad function", version = "2.0")
  def some_deprecated_function(x, y):
      return x+y

If the user tries to use the deprecated function ``some_deprecated_function(2, 3)``, they will have a warning:

.. code-block:: sh

  5

  DeprecationWarning: Call to deprecated function (or staticmethod) some_deprecated_function. (this is a bad function) -- Deprecated since version 2.0.
  
  some_deprecated_function(2, 3)
  


Deprecated method
-----------------

.. code-block:: python

  from deprecat import deprecat

  class thisclassisuseful:
      
      def __init__(self,value):
          self.value = value

      @deprecat(reason="this is a bad method", version = "2.0")
      def some_deprecated_function(self):
          print(self.value)

Let's try running this:

.. code-block:: python

  x = thisclassisuseful('abc')
  x.some_deprecated_function()

Here's what we get:

.. code-block:: sh

  abc

  DeprecationWarning: Call to deprecated method some_deprecated_function. 
  (this is a bad method) -- Deprecated since version 2.0.

  x.some_deprecated_function()

Deprecated class
----------------

.. code-block:: python

  from deprecat import deprecat

  @deprecat(reason="useless", version = "2.0")
  class badclass:
      
      def __init__(self):
          print("you just ran this class")
  
Now when we call ``badclass()`` we get:

.. code-block:: sh

  you just ran this class

  DeprecationWarning: Call to deprecated class badclass. 
  (useless) -- Deprecated since version 2.0.
  
  badclass()


Sphinx Decorator - Functions
----------------------------

You can use the sphinx decorator in deprecat to emit warnings and add a sphinx warning directive with custom title (using admonition) in docstring. Let's say this is our function (this can be done for methods and classes as well, just like the classic deprecat decorator)

.. code-block:: python

  from deprecat.sphinx import deprecat

  @deprecat(
      reason=""" this is very buggy say bye""",
      version='0.3.0')
  def myfunction(x):
      """
      Calculate the square of a number.

      :param x: a number
      :return: number * number
      """
      return x*x

Now when we try to use this as ``myfunction(3)`` we get the warning as usual:

.. code-block:: sh

  DeprecationWarning: Call to deprecated function (or staticmethod) myfunction. ( this is very buggy say bye) -- Deprecated since version 0.3.0.
  
  myfunction(3)

  9

Additionally, we have a modified docstring (``print(myfunction.__doc__``) as follows:

.. code-block:: sh

  Calculate the square of a number.

  :param x: a number
  :return: number * number

  .. deprecated:: 0.3.0
    this is very buggy say bye


Deprecated kwargs
-----------------

Suppose you have this function where two of the keyword arguments are not useful anymore so you can deprecate them like this.

.. code-block:: python

  from deprecat.sphinx import deprecat

  @deprecat(deprecated_args={'a':{'version':'4.0','reason':'nothing'}, 'b':{'version':'3.0','reason':'something'}})
  def multiply(a, b, c):
      """
      Compute the product

      Parameters
      ----------
      a: float
          a is a nice number

      b: float
          b is also a nice number

      c: float
          c is ok too
      """
      return a*b*c

This is the output we get when we try to run ``multiply(a=1,b=2,c=3)``

.. code-block:: sh

  DeprecationWarning: Call to deprecated Parameter b. (something) -- Deprecated since v3.0.
  multiply(a=1,b=2,c=3)

  DeprecationWarning: Call to deprecated Parameter a. (nothing) -- Deprecated since v4.0.
  multiply(a=1,b=2,c=3)
  
  6

Adding Removal Version 
----------------------

You can add a removal version to the deprecation warning by adding the ``removal_version`` parameter to the decorator. This will add a warning to the user that the function will be removed in the next versions.

.. code-block:: python

  from deprecat.sphinx import deprecat

  @deprecat(reason="this is a bad function", version = "2.0", remove_version = "3.0")
  def some_deprecated_function(x, y):
      """
      Parameters
      ----------
      x: float
          x is a nice number
      
      y: float
          y is also a nice number
      """
      return x+y

This is the output we get when we try to run ``some_deprecated_function(x=2, y=3)``

.. code-block:: sh

  DeprecationWarning: Call to deprecated method randomfunction. useless
  Warning: This deprecated feature will be removed in version 3.0 -- Deprecated since version 2.0. -- Will be removed in version 3.0.

Live Examples
-------------
If you want to see the sphinx admonitions in action, `check this out <https://deprecat.readthedocs.io/en/latest/source/api.html#examples>`__