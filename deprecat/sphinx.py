
"""
Sphinx directive integration
============================

The purpose of this module is to defined decorators which adds this Sphinx directives
to the docstring of your function and classes. Additionally, the ``@deprecat`` decorator will emit a deprecation warning
when the function/method is called or the class is constructed.

We usually need to document the life-cycle of functions and classes:
when they are created, modified or deprecated. To do that, `Sphinx <http://www.sphinx-doc.org>`_ has a set
of `Paragraph-level markups <http://www.sphinx-doc.org/en/stable/markup/para.html>`_:

- ``deprecated``: to document a deprecated feature.

"""
import re
import textwrap
import functools
import wrapt

from deprecat.classic import ClassicAdapter
from deprecat.classic import deprecat as _classic_deprecat

class SphinxAdapter(ClassicAdapter):

    """

    Construct a wrapper adapter.

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

    deprecated_args: str
        String of kwargs to be deprecated, e.g. "x y" to deprecate `x` and `y`.

    category: class
        The warning category to use for the deprecation warning.
        By default, the category class is :class:`~DeprecationWarning`,
        you can inherit this class to define your own deprecation warning category.
    
    line_length: numeric
        Max line length of the directive text. If non null, a long text is wrapped in several lines.

    directive: {"versionadded", "versionchanged", "deprecated"}
        Sphinx directive

    Notes
    -----
    Sphinx adapter overrides the :class:`~deprecat.classic.ClassicAdapter`
    in order to add the Sphinx directives to the end of the function/class docstring.
    Such a directive is a `Paragraph-level markup <http://www.sphinx-doc.org/en/stable/markup/para.html>`_

    - The directive can be one of "versionadded", "versionchanged" or "deprecated".
    - The version number is added if provided.
    - The reason message is added in the directive block if not empty.

    """

    def __init__(
        self,
        directive,
        reason="",
        version="",
        action=None,
        category=DeprecationWarning,
        line_length=70,
        deprecated_args=None
    ):

        if not version:
            raise ValueError("'version' argument is required in Sphinx directives")
        self.directive = directive
        self.line_length = line_length
        self.deprecated_args = deprecated_args
        super(SphinxAdapter, self).__init__(reason=reason, version=version, action=action, category=category, deprecated_args=deprecated_args)

    def __call__(self, wrapped):
        """
        Add the Sphinx directive to your class or function.

        Parameters
        ----------

        wrapped: object
            Wrapped class or function.

        Returns
        -------
        the decorated class or function.
        """
        fmt = ".. {directive}:: {version}" if self.version else ".. {directive}::"
        div_lines = [fmt.format(directive=self.directive, version=self.version)]
        width = self.line_length - 3 if self.line_length > 3 else 2 ** 16
        reason = textwrap.dedent(self.reason).strip()
        for paragraph in reason.splitlines():
            if paragraph:
                div_lines.extend(
                    textwrap.fill(
                        paragraph,
                        width=width,
                        initial_indent="   ",
                        subsequent_indent="   ",
                    ).splitlines()
                )
            else:
                div_lines.append("")

        # -- get the docstring, normalize the trailing newlines
        docstring = textwrap.dedent(wrapped.__doc__ or "")
        if docstring:
            # An empty line must separate the original docstring and the directive.
            docstring = re.sub(r"\n+$", "", docstring, flags=re.DOTALL) + "\n\n"
        else:
            # Avoid "Explicit markup ends without a blank line" when the decorated function has no docstring
            docstring = "\n"

        # -- append the directive division to the docstring
        docstring += "".join("{}\n".format(line) for line in div_lines)

        wrapped.__doc__ = docstring
        if self.directive in {"versionadded", "versionchanged"}:
             return wrapped

        return super(SphinxAdapter, self).__call__(wrapped)

    def get_deprecated_msg(self, wrapped, instance, kwargs):
        """
        Get the deprecation warning message (without Sphinx cross-referencing syntax) for the user.

        Parameters
        ----------

        wrapped:
            Wrapped class or function.

        instance:
            The object to which the wrapped function was bound when it was called.

        kwargs:
            The kwargs of the wrapped function.
        
        Returns
        -------
        The warning message.
        """
        msg = super(SphinxAdapter, self).get_deprecated_msg(wrapped, instance, kwargs)
        # Strip Sphinx cross reference syntax (like ":function:", ":py:func:" and ":py:meth:")
        # Possible values are ":role:`foo`", ":domain:role:`foo`"
        # where ``role`` and ``domain`` should match "[a-zA-Z]+"
        
        if msg:
            msg = re.sub(r"(?: : [a-zA-Z]+ )? : [a-zA-Z]+ : (`[^`]*`)", r"\1", msg, flags=re.X)
                
        return msg


def versionadded(reason="", version="", line_length=70):
    """
    This decorator can be used to insert a "versionadded" directive
    in your function/class docstring in order to documents the
    version of the project which adds this new functionality in your library.

    Parameters
    ----------
    reason: str
        Reason for deprecation.

    version: str
        Version of your project which deprecates this feature.
    
    line_length: numeric
        Max line length of the directive text. If non null, a long text is wrapped in several lines.

    Returns
    -------
    Decorator used to modify docstring.

    """
    adapter = SphinxAdapter(
        'versionadded',
        reason=reason,
        version=version,
        line_length=line_length,
    )
    return adapter


def versionchanged(reason="", version="", line_length=70):
    """
    This decorator can be used to insert a "versionchanged" directive
    in your function/class docstring in order to documents the
    version of the project which modifies this functionality in your library.

    Parameters
    ----------
    reason: str
        Reason for deprecation.

    version: str
        Version of your project which deprecates this feature.
    
    line_length: numeric
        Max line length of the directive text. If non null, a long text is wrapped in several lines.

    Returns
    -------
    Decorator used to modify docstring.
    """
    adapter = SphinxAdapter(
        'versionchanged',
        reason=reason,
        version=version,
        line_length=line_length,
     )
    return adapter


def deprecat(reason="", version="", line_length=70, deprecated_args=None, **kwargs):
    """
    This decorator can be used to insert a "deprecated" directive
    in your function/class docstring in order to documents the
    version of the project which deprecates this functionality in your library.

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

    deprecated_args: str
        String of kwargs to be deprecated, e.g. "x y" to deprecate `x` and `y`.

    category: class
        The warning category to use for the deprecation warning.
        By default, the category class is :class:`~DeprecationWarning`,
        you can inherit this class to define your own deprecation warning category.
    
    line_length: numeric
        Max line length of the directive text. If non null, a long text is wrapped in several lines.

    Returns
    -------
    Decorator used to deprecate a function.

    """
    directive = kwargs.pop('directive', 'deprecated')
    adapter_cls = kwargs.pop('adapter_cls', SphinxAdapter)
    kwargs["reason"] = reason
    kwargs["version"] = version
    kwargs["line_length"] = line_length
    kwargs["deprecated_args"] = deprecated_args

    return _classic_deprecat(directive=directive, adapter_cls=adapter_cls, **kwargs)