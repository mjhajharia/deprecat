# deprecator
Decorator to deprecate functions or classes. Additionally, auto-adds sphinx directive `deprecated`

### Example

```
from deprecator import deprecator
@deprecator(version="1.0", reason="some reason")
def basicfunc(x,y):
    """
    something
    """
    return x+y
basicfunc(x = 3,y =4)
```

Output: 

```
DeprecationWarning: Function or method basicfunc is deprecated, since version 1.0 (some reason).
```

#### Sphinx stuff

```
print(basicfunc.__doc__)
```
Output:
```
something

.. deprecated:: 1.0
   some reason
```
#### Credits / Sources / Note

Some of the sphinx part is from the library [Deprecated](https://github.com/tantale/deprecated). For a more robust framework on deprecating functions, check them out. I made the custom version mainly to integrate deprecated arguments, which was needed for PyMC3. Although you can find similar stuff on that [here](https://stackoverflow.com/a/54949947/4451315), I'd recommend not using classes for decorators in python if you want to use functools, it can be done i guess, but it gets messy with namespace stuff. Anyway, this is a random snippet, anyone is free to do anything, I scrolled through a lot of code trying to make it work for my case, if someone thinks i missed giving credit to something or someone, let me know. I don't need any credit if you want to use this!
