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
import warnings

from deprecat.classic import ClassicAdapter
from deprecat.classic import deprecat as _classic_deprecat

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
        
class SphinxAdapter(ClassicAdapter):

    """

    Construct a wrapper adapter.

    Parameters
    ----------
    reason: str
        Reason for deprecation.

    version: str
        Version of your project which deprecates this feature.

    remove_version: str
        Version of your project which removes this method or class.

    action: str
        A warning filter used to specify the deprecation warning.
        Can be one of "error", "ignore", "always", "default", "module", or "once".
        If ``None`` or empty, the the global filtering mechanism is used.

    deprecated_args: dict
        Dictionary in the following format to deprecate `x` and `y`
        deprecated_args = {'x': {'reason': 'some reason','version': '1.0'},'y': {'reason': 'another reason','version': '2.0'}}

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

    * The directive can be one of "versionadded", "versionchanged" or "deprecated".
    * The version number is added if provided.
    * The reason message is added in the directive block if not empty.

    .. seealso::
        We use admonitions in sphinx to render warnings for every deprecated argument just below its description in docstring.
        refer to `this <https://pradyunsg.me/furo/reference/admonitions/?highlight=warning#custom-titles>`_ link for more information.
    
    Warnings
    --------
    deprecat supports docstring modification for deprecated_args only in the numpydoc format, if your documentation uses any other format, this won't work. 
    Later we might add support for other formats, for now there are no such plans.

    """

    def __init__(
        self,
        directive,
        reason="",
        version="",
        remove_version="",
        action=None,
        category=DeprecationWarning,
        line_length=70,
        deprecated_args=None
    ):
        self.deprecated_args = deprecated_args
        self.directive = directive
        self.line_length = line_length
        super(SphinxAdapter, self).__init__(reason=reason, version=version, remove_version=remove_version, action=action, category=category, deprecated_args=deprecated_args)

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
        docstring = textwrap.dedent(wrapped.__doc__ or "")
        if docstring:
        # An empty line must separate the original docstring and the directive.
            docstring = re.sub(r"\n+$", "", docstring, flags=re.DOTALL) + "\n\n"
        else:
        # Avoid "Explicit markup ends without a blank line" when the decorated function has no docstring
            docstring = "\n"

        width = self.line_length - 3 if self.line_length > 3 else 2 ** 16
        reason = self.reason
        if self.remove_version!="":
            reason += f'\n\nWarning: This deprecated feature will be removed in version {self.remove_version}'
        reason = textwrap.dedent(reason).strip()

        if self.deprecated_args is None:
            fmt = ".. {directive}:: {version}" if self.version else ".. {directive}::"
            div_lines = [fmt.format(directive=self.directive, version=self.version)]
            
            #formatting for docstring
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
            # -- append the directive division to the docstring
            docstring += "".join("{}\n".format(line) for line in div_lines)

        else:
            if docstring=="\n":
                warnings.warn("Missing docstring, consider adding a numpydoc style docstring for the decorator to work (Sphinx directive won't be added)" , category=UserWarning, stacklevel=_class_stacklevel)
            else:
                for arg in set(self.deprecated_args.keys()):
                    #first we search for the location of the parameters section
                    search = re.search("Parameters[\\s]*\n[\\s]*----------", docstring)
                    if search is None:
                        warnings.warn("Missing Parameter section, consider adding a numpydoc style parameters section in your docstring for the decorator to work (Sphinx directive won't be added)" , category=UserWarning, stacklevel=_class_stacklevel)
                    else:
                        params_string = docstring[search.start():search.end()]

                        #we store the indentation of the values 
                        indentsize = re.search("----------", params_string).start() - re.search("Parameters[\\s]*\n", params_string).end()
                        indent = ' '*indentsize

                        # we check if there is another section after parameters
                        if re.search(f"\n{indent}-----", docstring[search.end():]) is not None:
                            #if yes then we find the range of the parameters section
                            params_section_end = search.end() + re.search(f"\n{indent}-----", docstring[search.end():]).start()
                            dashes_in_next_section = docstring[params_section_end:].count('-')
                            params_section_end = params_section_end - dashes_in_next_section
                            params_section = docstring[search.start():params_section_end]
                        else:
                            #else the entire remaining docstring is in the parameters section
                            params_section = docstring[search.start():]

                        #we search for the description of the particular parameter we care about
                        if re.search(f"\n{indent}{arg}\\s*:", params_section) is not None:
                            description_start = re.search(f"\n{indent}{arg}\\s*:", params_section).end()
                            #we check whether there are more parameters after this one, or if its the last parameter described in the secion
                            #and store the position where we insert the warning

                            if re.search(f"\n{indent}\\S", params_section[description_start:]):
                                insert_pos = re.search(f"\n{indent}\\S", params_section[description_start:]).start()
                            else:
                                insert_pos = len(params_section[description_start:])
                            
                            #finally we store the warning fmt string
                            if self.deprecated_args[arg].get('version') is not None:
                                #the spaces are specifically cherrypicked for numpydoc docstrings
                                fmt = "\n\n    .. admonition:: Deprecated\n      :class: warning\n\n      Parameter {arg} deprecated since {version}"
                                if self.deprecated_args[arg].get('remove_version') is not None:
                                    fmt += " and will be removed in version {remove_version}."
                                    div_lines = [fmt.format(version=self.deprecated_args[arg]['version'],arg=arg, remove_version=self.deprecated_args[arg]['remove_version'])]
                                else:
                                    div_lines = [fmt.format(version=self.deprecated_args[arg]['version'],arg=arg)]
                            else:
                                fmt = "\n\n    .. admonition:: Deprecated\n      :class: warning\n\n      Parameter {arg} deprecated"
                                div_lines = [fmt.format(version=self.deprecated_args[arg]['version'],arg=arg)]
                            width = 2**16
                            if self.remove_version!="":
                                self.reason += f'\n\nWarning: This deprecated feature will be removed in version {self.remove_version}'
                            reason = textwrap.dedent(self.reason).strip()
                            #formatting for docstring
                            for paragraph in reason.splitlines():
                                div_lines.extend(
                                    textwrap.fill(
                                        paragraph,
                                        width=width,
                                        initial_indent=indent,
                                        subsequent_indent=indent,
                                    ).splitlines()
                                )
                            # -- append the directive division to the docstring
                            a=''
                            a += "".join("{}\n".format(line) for line in div_lines)
                            a = textwrap.indent(a, indent)
                            docstring = docstring[:search.start() + description_start+insert_pos]+"\n\n"+a+"\n\n"+docstring[search.start() + description_start+insert_pos:]
                            docstring = re.sub(r"[\n]{3,}", "\n\n", docstring)
                        else:
                            warnings.warn(f"Missing description for parameter {arg}, consider adding a numpydoc style description for the decorator to work (Sphinx directive won't be added)" , category=UserWarning, stacklevel=_class_stacklevel)

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
        
        #remember the msg variable is a dict
        if msg:
            for key, value in msg.items():
                msg[key] = re.sub(r"(?: : [a-zA-Z]+ )? : [a-zA-Z]+ : (`[^`]*`)", r"\1", value, flags=re.X)
                
        return msg

#this should only be used for functions, methods or classes. NOT parameters.
def versionadded(reason="", version="", line_length=70):
    """
    This decorator can be used to insert a "versionadded" directive
    in your function/class docstring in order to documents the
    version of the project which adds this new functionality in your library.

    Parameters
    ----------
    reason: str
        Reason for deprecation of this method or class.

    version: str
        Version of your project which deprecates this method or class.
    
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


#this should only be used for functions, methods or classes. NOT parameters.
def versionchanged(reason="", version="", line_length=70):
    """
    This decorator can be used to insert a "versionchanged" directive
    in your function/class docstring in order to documents the
    version of the project which modifies this functionality in your library.

    Parameters
    ----------
    reason: str
        Reason for deprecation of this method or class.

    version: str
        Version of your project which deprecates this method or class.
    
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


def deprecat(reason="", directive="deprecated", version="", remove_version="", line_length=70, deprecated_args=None, **kwargs):
    """
    This decorator can be used to insert a "deprecated" directive
    in your function/class docstring in order to documents the
    version of the project which deprecates this functionality in your library.

    Parameters
    ----------
    reason: str
        Reason for deprecation of this method or class.

    version: str
        Version of your project which deprecates this method or class.

    remove_version: str
        Version of your project which removes this method or class.

    action: str
        A warning filter used to specify the deprecation warning.
        Can be one of "error", "ignore", "always", "default", "module", or "once".
        If ``None`` or empty, the the global filtering mechanism is used.

    : str
        String of kwargs to be deprecated, e.g. "x y" to deprecate `x` and `y`.

    category: class
        The warning category to use for the deprecation warning.
        By default, the category class is :class:`~DeprecationWarning`,
        you can inherit this class to define your own deprecation warning category.
    
    line_length: numeric
        Max line length of the directive text. If non null, a long text is wrapped in several lines.

    deprecated_args: dict
        Dictionary in the following format to deprecate `x` and `y`
        deprecated_args = {'x': {'reason': 'some reason','version': '1.0'},'y': {'reason': 'another reason', 'version': '2.0'}}

    Returns
    -------
    Decorator used to deprecate a function, method, class or kwarg.

    """
    directive = kwargs.pop('directive', 'deprecated')
    adapter_cls = kwargs.pop('adapter_cls', SphinxAdapter)
    kwargs["reason"] = reason
    kwargs["version"] = version
    kwargs["remove_version"] = remove_version
    kwargs["line_length"] = line_length
    kwargs["deprecated_args"] = deprecated_args

    return _classic_deprecat(directive=directive, adapter_cls=adapter_cls, **kwargs)
