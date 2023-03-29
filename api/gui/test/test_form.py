import pytest

from .. import Form

def test_empty():
    """An empty schema should raise an error"""
    with pytest.raises(TypeError, match=r"missing .* 'schema'") as excinfo:
        Form()

    with pytest.raises(KeyError, match="type") as excinfo:
        Form(schema={})
