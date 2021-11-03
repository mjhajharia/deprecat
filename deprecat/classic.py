"""
Classic deprecation warning
===========================

Classic ``@deprecat`` decorator to deprecate python classes, functions, methods or kwargs.

"""
import functools
import inspect
import platform
import warnings

import wrapt

try:
    # If the C extension for wrapt was compiled and wrapt/_wrappers.pyd exists, then the
    # stack level that should be passed to warnings.warn should be 2. However, if using
    # a pure python wrapt, a extra stacklevel is required.
    import wrapt._wrappers

    _routine_stacklevel = 2
    _class_stacklevel = 2
except ImportError:
    _routine_stacklevel = 3
    if platform.python_implementation() == "PyPy":
        _class_stacklevel = 2
    else:
        _class_stacklevel = 3

string_types = (type(b''), type(u''))


class ClassicAdapter(wrapt.AdapterFactory):
    """
    Classic adapter is used to get the deprecation message according to the wrapped object type:
    class, function, standard method, static method, or class method. This is the base class of the :class:`~deprecat.sphinx.SphinxAdapter` class
    which is used to update the wrapped object docstring. You can also inherit this class to change the deprecation message.

    Parameters
    ----------
    reason: str
        Reason for deprecation.

    version: str
        Version of your project which deprecates this feature.
    
    action: str
        A warning filter used to specify the deprecation warning.
        Can be one of "error", "ignore", "always", "default", "module", or "once".
        If ``None`` or empty, the the global filtering mechanism is used.

    deprecated_arg: str
        String of kwargs to be deprecated, e.g. "x y" to deprecate `x` and `y`.

    category: class
        The warning category to use for the deprecation warning.
        By default, the category class is :class:`~DeprecationWarning`,
        you can inherit this class to define your own deprecation warning category.
    """

    def __init__(self, reason="", version="", action=None, deprecated_arg=None, category=DeprecationWarning):
        self.reason = reason or ""
        self.version = version or ""
        self.action = action
        self.category = category
        self.deprecated_arg=deprecated_arg
        super(ClassicAdapter, self).__init__()

    def get_deprecated_msg(self, wrapped, instance, kwargs):
        """
        Get the deprecation warning message for the user.

        Parameters
        ----------

        wrapped: object
            Wrapped class or function.

        instance: object
            The object to which the wrapped function was bound when it was called.

        kwargs:
            The kwargs of the wrapped function.

        Returns
        -------
        The warning message.
        """
        if instance is None:
            if inspect.isclass(wrapped):
                fmt = "Call to deprecated class {name}."
            else:
                fmt = "Call to deprecated function (or staticmethod) {name}."
        else:
            if inspect.isclass(instance):
                fmt = "Call to deprecated class method {name}."
            else:
                fmt = "Call to deprecated method {name}."
        if self.deprecated_arg is None:
            name = wrapped.__name__
        if self.deprecated_arg is not None:
            fmt = "Call to deprecated Parameter(s) {name}."
            deprecated_arg = set(self.deprecated_arg.split())
            argstodeprecate = deprecated_arg.intersection(kwargs)
            if len(argstodeprecate)!=0:
                name = ", ".join(repr(arg) for arg in argstodeprecate)
            else:
                name=""
        if name=="":
            return None
        if self.reason:
            fmt += " ({reason})"
        if self.version:
            fmt += " -- Deprecated since version {version}."
        return fmt.format(name=name, reason=self.reason or "", version=self.version or "")


    def __call__(self, wrapped):
        """
        Decorate your class or function.
        
        Parameters
        ----------

        wrapped: object
            Wrapped class or function.

        Returns
        -------
        Decorated class or function.

        """
        if inspect.isclass(wrapped):
            old_new1 = wrapped.__new__

            def wrapped_cls(cls, *args, **kwargs):
                msg = self.get_deprecated_msg(wrapped=wrapped, instance=None, kwargs=kwargs)
                if self.action:
                    with warnings.catch_warnings():
                        warnings.simplefilter(self.action, self.category)
                        warnings.warn(msg, category=self.category, stacklevel=_class_stacklevel)
                else:
                    warnings.warn(msg, category=self.category, stacklevel=_class_stacklevel)
                if old_new1 is object.__new__:
                    return old_new1(cls)
                # actually, we don't know the real signature of *old_new1*
                return old_new1(cls, *args, **kwargs)

            wrapped.__new__ = staticmethod(wrapped_cls)

        return wrapped


def deprecat(*args, **kwargs):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.
    """
    if args and isinstance(args[0], string_types):
        kwargs['reason'] = args[0]
        args = args[1:]

    if args and not callable(args[0]):
        raise TypeError(repr(type(args[0])))

    if args:
        action = kwargs.get('action')
        category = kwargs.get('category', DeprecationWarning)
        adapter_cls = kwargs.pop('adapter_cls', ClassicAdapter)
        adapter = adapter_cls(**kwargs)

        wrapped = args[0]
        if inspect.isclass(wrapped):
            wrapped = adapter(wrapped)
            return wrapped

        elif inspect.isroutine(wrapped):

            @wrapt.decorator(adapter=adapter)
            def wrapper_function(wrapped_, instance_, args_, kwargs_):
                msg = adapter.get_deprecated_msg(wrapped_, instance_, kwargs_)
                if msg:
                    if action:
                        with warnings.catch_warnings():
                            warnings.simplefilter(action, category)
                            warnings.warn(msg, category=category, stacklevel=_routine_stacklevel)
                    else:
                        warnings.warn(msg, category=category, stacklevel=_routine_stacklevel)
                return wrapped_(*args_, **kwargs_)

            return wrapper_function(wrapped)

        else:
            raise TypeError(repr(type(wrapped)))

    return functools.partial(deprecat, **kwargs)
