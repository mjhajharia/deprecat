[![Documentation Status](https://readthedocs.org/projects/deprecat/badge/?version=latest)](https://deprecat.readthedocs.io/en/latest/?badge=latest)

# deprecat decorator

Python ``@deprecat`` decorator to deprecate old python classes, functions or methods.

## Installation

```shell
pip install deprecat
```

## Compatibility

Python >=3.6

## Usage

Deprecated function
-------------------

``` {.sourceCode .python}
from deprecat import deprecat

@deprecat(reason="this is a bad function", version = '2.0')
def some_deprecated_function(x, y):
    return x+y
```

If the user tries to use the deprecated function
`some_deprecated_function(2, 3)`, they will have a warning:

``` {.sourceCode .sh}
5

DeprecationWarning: Call to deprecated function (or staticmethod) some_deprecated_function. (this is a bad function) -- Deprecated since version 2.0.

some_deprecated_function(2, 3)
```

Deprecated method
-----------------

``` {.sourceCode .python}
from deprecat import deprecat

class thisclassisuseful:

    def __init__(self,value):
        self.value = value

    @deprecat(reason="this is a bad method", version = 2.0)
    def some_deprecated_function(self):
        print(self.value)
```

Let's try running this:

``` {.sourceCode .python}
x = thisclassisuseful('abc')
x.some_deprecated_function()
```

Here's what we get:

``` {.sourceCode .sh}
abc

DeprecationWarning: Call to deprecated method some_deprecated_function. 
(this is a bad method) -- Deprecated since version 2.0.

x.some_deprecated_function()
```

Deprecated class
----------------

``` {.sourceCode .python}
from deprecat import deprecat

@deprecat(reason="useless", version = 2.0)
class badclass:

    def __init__(self):
        print("you just ran this class")
```

Now when we call `badclass()` we get:

``` {.sourceCode .sh}
you just ran this class

DeprecationWarning: Call to deprecated class badclass. 
(useless) -- Deprecated since version 2.0.

badclass()
```

Sphinx Decorator - Functions
----------------------------

You can use the sphinx decorator in deprecat to emit warnings and add a
sphinx warning directive with custom title (using admonition) in
docstring. Let's say this is our function (this can be done for methods
and classes as well, just like the classic deprecat decorator)

``` {.sourceCode .python}
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
```

Now when we try to use this as `myfunction(3)` we get the warning as
usual:

``` {.sourceCode .sh}
DeprecationWarning: Call to deprecated function (or staticmethod) myfunction. ( this is very buggy say bye) -- Deprecated since version 0.3.0.

myfunction(3)

9
```

Additionally, we have a modified docstring (`print(myfunction.__doc__`)
as follows:

``` {.sourceCode .sh}
Calculate the square of a number.

:param x: a number
:return: number * number

.. deprecated:: 0.3.0
  this is very buggy say bye
```

Deprecated kwargs
-----------------

Suppose you have this function where two of the keyword arguments are
not useful anymore so you can deprecate them like this.

``` {.sourceCode .python}
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
```

This is the output we get when we try to run `multiply(a=1,b=2,c=3)`

``` {.sourceCode .sh}
DeprecationWarning: Call to deprecated Parameter b. (something) -- Deprecated since v3.0.
multiply(a=1,b=2,c=3)

DeprecationWarning: Call to deprecated Parameter a. (nothing) -- Deprecated since v4.0.
multiply(a=1,b=2,c=3)

6
```

Now, the cool part is your docstring (`multiply.__doc__`) get's modified
as well. [This](https://deprecat.readthedocs.io/en/latest/source/usage.html#docstring) is how it renders in Sphinx



## Authors

The authors of this library are:
[Marcos CARDOSO](https://github.com/vrcmarcos), and
[Laurent LAPORTE](https://github.com/tantale).
The original code was made in [this StackOverflow post](https://stackoverflow.com/questions/2536307) by
[Leandro REGUEIRO](https://stackoverflow.com/users/1336250/leandro-regueiro),
[Patrizio BERTONI](https://stackoverflow.com/users/1315480/patrizio-bertoni), and
[Eric WIESER](https://stackoverflow.com/users/102441/eric).


Modified and now maintained by: [Meenal Jhajharia](https://github.com/mjhajharia) 
