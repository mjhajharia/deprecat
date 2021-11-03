"""
Sphinx directive integration
============================

The purpose of this module is to defined decorators which adds this Sphinx directives
to the docstring of your function and classes. Additionally, the ``@deprecat`` decorator will emit a deprecation warning
when the function/method is called or the class is constructed.

"""
import re
import textwrap
import functools
import wrapt

from deprecat.classic import ClassicAdapter
from deprecat.classic import deprecat as _classic_deprecat

class SphinxAdapter(ClassicAdapter):
    """
    Sphinx adapter overrides the :class:`~deprecat.classic.ClassicAdapter`
    in order to add the Sphinx directives to the end of the function/class docstring.
    Such a directive is a `Paragraph-level markup <http://www.sphinx-doc.org/en/stable/markup/para.html>`_

    - The version number is added if provided.
    - The reason message is added in the directive block if not empty.
    
    
    
    .. seealso::
       We use the admonition directive with the class specification "attention" to render deprecation messages in Sphinx documentation. `[ref] <https://pradyunsg.me/furo/reference/admonitions/?highlight=warning#custom-titles>`_
    """

    def __init__(
        self,
        reason="",
        version="",
        action=None,
        category=DeprecationWarning,
        line_length=70,
        deprecated_args=None
    ):
        """
        Construct a wrapper adapter.

        :type  reason: str
        :param reason:
            Reason for deprecation.

        :type  version: str
        :param version:
            Version of your project which deprecates this feature.

        :type  action: str
        :param action:
            A warning filter used to specify the deprecation warning.
            Can be one of "error", "ignore", "always", "default", "module", or "once".
            If ``None`` or empty, the the global filtering mechanism is used.

        :type  category: type
        :param category:
            The warning category to use for the deprecation warning.
            By default, the category class is :class:`~DeprecationWarning`,
            you can inherit this class to define your own deprecation warning category.

        :type  line_length: int
        :param line_length:
            Max line length of the directive text. If non null, a long text is wrapped in several lines.
            
        :type deprecated_args: str
        :param deprecated_args:
            String of kwargs to be deprecated, e.g. "x y" to deprecate `x` and `y`.
        """
        if not version:
            raise ValueError("'version' argument is required in Sphinx directives")
        self.directive = "admonition"
        self.line_length = line_length
        self.deprecated_args = deprecated_args
        super(SphinxAdapter, self).__init__(reason=reason, version=version, action=action, category=category, deprecated_args=deprecated_args)

    def __call__(self, wrapped):
        """
        Add the Sphinx directive to your class or function.

        :param wrapped: Wrapped class or function.

        :return: the decorated class or function.
        """
        fmt = ".. {directive}:: Deprecated since v{version}\n   :class: attention\n" if self.version else ".. {directive}:: Deprecated\n   :class: attention\n"
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
        return super(SphinxAdapter, self).__call__(wrapped)

    def get_deprecated_msg(self, wrapped, instance, kwargs):
        """
        Get the deprecation warning message (without Sphinx cross-referencing syntax) for the user.

        :param wrapped: Wrapped class or function.

        :param instance: The object to which the wrapped function was bound when it was called.
        
        :param kwargs: The keyword arguments of the wrapped function

        :return: The warning message.

        """
        msg = super(SphinxAdapter, self).get_deprecated_msg(wrapped, instance, kwargs)
        # Strip Sphinx cross reference syntax (like ":function:", ":py:func:" and ":py:meth:")
        # Possible values are ":role:`foo`", ":domain:role:`foo`"
        # where ``role`` and ``domain`` should match "[a-zA-Z]+"
        
        if msg:
            msg = re.sub(r"(?: : [a-zA-Z]+ )? : [a-zA-Z]+ : (`[^`]*`)", r"\1", msg, flags=re.X)
                
        return msg




def deprecat(reason="", version="", line_length=70, deprecated_args=None, **kwargs):
    """
    This decorator can be used to insert a "deprecated" directive
    in your function/class docstring in order to documents the
    version of the project which deprecates this functionality in your library.

    :param str reason:
        Reason message which documents the deprecation in your library (can be omitted).

    :param str version:
        Version of your project which deprecates this feature.
        If you follow the `Semantic Versioning <https://semver.org/>`_,
        the version number has the format "MAJOR.MINOR.PATCH".

    :type  line_length: int
    :param line_length:
        Max line length of the directive text. If non nul, a long text is wrapped in several lines.
        
    :type deprecated_args: str
        :param deprecated_args:
            String of kwargs to be deprecated, e.g. "x y" to deprecate `x` and `y`.
    Keyword arguments can be:

    -   "action":
        A warning filter used to activate or not the deprecation warning.
        Can be one of "error", "ignore", "always", "default", "module", or "once".
        If ``None``, empty or missing, the the global filtering mechanism is used.

    -   "category":
        The warning category to use for the deprecation warning.
        By default, the category class is :class:`~DeprecationWarning`,
        you can inherit this class to define your own deprecation warning category.

    :return: a decorator used to deprecate a function.

    """
    adapter_cls = kwargs.pop('adapter_cls', SphinxAdapter)
    kwargs["reason"] = reason
    kwargs["version"] = version
    kwargs["line_length"] = line_length
    kwargs["deprecated_args"] = deprecated_args

    return _classic_deprecat(adapter_cls=adapter_cls, **kwargs)

@deprecat(
    reason=""" this is very buggy say bye""",
    version='0.3.0')
def myfunction(x):
    """    
    Here's an example function!!

    Calculate the square of a number.

    :param x: a number
    :return: number * number
    """
    return x*x
