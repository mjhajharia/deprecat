# coding: utf-8
from packaging import version
import deprecat


def test_deprecat_has_docstring():
    # The deprecat package must have a docstring
    assert deprecat.__doc__ is not None
    assert "deprecat" in deprecat.__doc__


def test_deprecat_has_version():
    # The deprecat package must have a valid version number
    assert deprecat.__version__ is not None
    version_ = version.parse(deprecat.__version__)

    assert 'Legacy' not in version_.__class__.__name__
