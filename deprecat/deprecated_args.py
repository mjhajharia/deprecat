def regex_for_deprecated_arg(docstring, deprecated_arg):
        """
        This function uses regex for positioning deprecation warnings for parameters with their documentation.

        "\\n{1}\\w+:{1}"  - looks for the next parameter(formatted as [line break followed by some string ending with a colon ]) 
        that is defined in the documentation, so we introduce the warning right before that

        "\\n{1}\\w+\\n{1}-+\\n{1}" - looks for the next documentation section like "Parameters", "Examples", "Returns"
        these are followed by a line of dashes (------).

        we look through all of these possible endings to find the "endpoint" of the param definition and insert the deprecation warning there

        """
        doc=docstring.split(f'\n{deprecated_arg}:')[1]
        nextitem = re.search("\\n{1}\\w+:{1}", doc)
        nextsection = re.search("\\n{1}\\w+\\n{1}-+\\n{1}",doc)
        last = len(doc)
        n = min(nextitem.start(), nextsection.start(), last)
        y = len(docstring.split(f'\n{deprecated_arg}:')[0]) + len(f'\n{deprecated_arg}:')
        docstring = docstring[:y+n] + str(sphinxtext) + docstring[y+n:]
        return docstring

    