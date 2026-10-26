import functools
import inspect
import warnings
import regex as re
import textwrap


def deprecator(reason, version, deprecated_args=None):
    """
    PyMC deprecation helper. This decorator emits deprecated warnings.
    """    
    if deprecated_args is not None:
        deprecated_args = set(deprecated_args.split())
    cause = reason
    if cause is not None and version is not None:
        reason = ", since version " + version + " " + "("+cause+")"

    if cause is not None and version is None:
        reason = "("+ str(cause) + ")"

    if cause is None and version is not None :
        reason = ", since version " + version
    #this function is an edited version of the source code taken from the library Deprecated
    #https://github.com/tantale/deprecated (MIT License)
    def sphinxformatter(version, reason):
        fmtsphinx = ".. deprecated:: {version}" if version else ".. deprecated::"
        sphinxtext = [fmtsphinx.format(directive = "deprecated", version=version)]
        width = 2 ** 16
        reason = reason.lstrip()
        for paragraph in reason.splitlines():
            if paragraph:
                sphinxtext.extend(
                    textwrap.fill(
                        paragraph,
                        width=width,
                        initial_indent="   ",
                        subsequent_indent="   ",
                    ).splitlines()
                )
            else:
                sphinxtext.append("")
        return sphinxtext


    def decorator(func):
        if deprecated_args is None:
            if inspect.isclass(func):
                fmt = "Class {name} is deprecated{reason}."
            else:
                fmt = "Function or method {name} is deprecated{reason}."
        else:
            fmt = "Parameter(s) {name} deprecated{reason}"
            
        docstring = textwrap.dedent(func.__doc__ or "")
        if docstring:
            docstring = re.sub(r"\n+$", "", docstring, flags=re.DOTALL) + "\n\n"
        else:
            docstring = "\n"
            
        sphinxtext = sphinxformatter(version, cause)
        docstring += "".join("{}\n".format(line) for line in sphinxtext)
        func.__doc__ = docstring       

        @functools.wraps(func)
        def new_func(*args, **kwargs):
            if deprecated_args is None:
                name = func.__name__
            else:
                argstodeprecate = deprecated_args.intersection(kwargs)
                if argstodeprecate is not None:
                    name = ', '.join(repr(arg) for arg in argstodeprecate)

            if name!="":
                warnings.simplefilter('always', DeprecationWarning)
                warnings.warn(
                    fmt.format(name=name, reason=reason),
                    category=DeprecationWarning,
                    stacklevel=2
                )
            return func
        
        return new_func
    
    return decorator
