"""
Examples
============================

This module contains examples for the deprecat package.
"""
import re
import textwrap
import functools
import wrapt
import warnings

from deprecat.sphinx import deprecat

@deprecat(reason="useless", version = "2.0")
class test_deprecat_on_class:
    """
    Here we test deprecation on a class, like this one. 
    """
    def __init__(self):
        pass

test_deprecat_on_class()

class test_deprecat_on_class_method:
    def __init__(self):
        pass

    @deprecat(reason="useless", version = "2.0", remove_version = "3.0")
    def randomfunction(self, a, b):
        """
        Here we test deprecation on a method of a class, like this one. 
        Note that you can also add `remove_version` to the decorator 
        to specify the version when the class/function/kwarg/feature will be removed.

        """
        return a + b

x = test_deprecat_on_class_method()
x.randomfunction(1,2)

@deprecat(reason="useless", version = "2.0")
def test_deprecat_on_function(a, b):
    """
    Here we test deprecation on a function.
    """
    return a + b

test_deprecat_on_function(1,2)

@deprecat(deprecated_args={'a':{'version':'4.0','reason':'nothing', 'remove_version': '5.0'}})
def test_deprecated_args(a, b, c=3, d=4):
    """
    Here we test deprecation on a function with arguments.

    Parameters
    ----------
    a : int
        This is the first argument.
    b : int
        This is the second argument.
    c : int, optional
        This is the third argument.
    d : int, optional
        This is the fourth argument.

    Returns : int
        This is the return value.  
    """
    return a + b + c + d

test_deprecated_args(a=2, b=3, c=4, d=5)
