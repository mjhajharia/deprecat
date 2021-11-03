Introduction
============

What's deprecat anyway?
-----------------------


Deprecated functions, classes or kwargs are common in large packages or APIs that are rapidly developing. Sometimes, you need to keep track of them, whether they’re renamed or permanently removed. Some of the things that need to be done in such cases are

* warn users and developers that xyz is deprecated and they should use abc (or xyz is gone forever without an alternative) because of some reason

* keep track of deprecated things along with their versions

* mention the deprecation event in your documentation for users

You can use `deprecat <https://pypi.python.org/pypi/deprecat>`_ for these!! 

Some background
---------------

There’s a relatively popular existing package `deprecated <https://pypi.python.org/pypi/deprecated>`_ which is great and I would encourage you to use it! I contribute to PyMC sometimes, and a new version is being released, so the API is changing at a large scale, a lot of things that are deprecated need to be kept track of. I decided to use `deprecated <https://pypi.python.org/pypi/deprecated>`_, but it did not support deprecating keyword arguments, which is something I needed, so i decided to make a Pull request, but maybe because it was an API change, it went stale, so I made a fork, added support for deprecated_arg and made a package for personal use, if you want to use it because you need to deprecate keyword arguments, great!! else, please consider using the package `deprecated <https://pypi.python.org/pypi/deprecated>`_, the `maintainer <https://github.com/tantale>`_ put in a lot of effort into building it and they deserve all the credit!

Why name it deprecat?
---------------------

I don't know buddy it was cute. Well deprecator, deprecate, and deprecated were taken. And, deprecat has a nice ring to it ( *depressed cat* ) also I'm not a fan of capital(ization or ism) so *d*.
