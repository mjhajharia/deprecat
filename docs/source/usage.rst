.. _usage:

Usage
========


Deprecated function
-------------------

.. code-block:: python

  from deprecat import deprecat

  @deprecat(reason="this is a bad function", version = '2.0')
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

      @deprecat(reason="this is a bad method", version = 2.0)
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

  @deprecat(reason="useless", version = 2.0)
  class badclass:
      
      def __init__(self):
          print("you just ran this class")
  
Now when we call ``badclass()`` we get:

.. code-block:: sh

  you just ran this class

  DeprecationWarning: Call to deprecated class badclass. 
  (useless) -- Deprecated since version 2.0.
  
  badclass()


Sphinx Decorator
----------------

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


from deprecat.sphinx import deprecat
@deprecat(
    reason="""i dont like y""", deprecated_arg="y",
    version='0.3.0')
def myfunction(x,y,z):
    """
    Parameters
    ----------

    x: float
      x is some number

    y: float
      y is another number
    
    z: float
      z is a bad number

    Returns
    -------
    Product
    """
    return x*y*z
