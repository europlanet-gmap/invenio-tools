import pytest

from .. import form, Form

assert form.Form is Form


def test_empty():
    """An empty schema should raise an error"""
    with pytest.raises(TypeError, match=r"missing .* 'schema'") as excinfo:
        Form()

    with pytest.raises(AssertionError, match="type") as excinfo:
        Form(schema={})


def test_schema_type():
    """Form is made to work with 'object' types"""
    schema = {
        'type': 'other_than_object'
    }
    with pytest.raises(TypeError) as excinfo:
        Form(schema)

    schema['type'] = 'object'
    # 'properties' should be there also
    with pytest.raises(AssertionError, match="properties") as info:
        Form(schema)

    schema['properties'] = {}
    Form(schema)


def test_empty_object():
    """Form from empty object properties is a valid, empty Form"""
    schema = {
        'type': 'object',
        'properties': {}
        }
    f = Form(schema)

    assert isinstance(f, dict), f
    assert isinstance(f.widget, (form.widgets.Widget))
    assert isinstance(f.widget, (form.widgets.VBox)) # default, VBox
