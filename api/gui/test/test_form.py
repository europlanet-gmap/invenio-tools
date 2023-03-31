import pytest

from copy import deepcopy

from .. import form, Form

assert form.Form is Form


_widgets_defaults = {

    'string': {
        'type': form.widgets.Text,
        'value': ""
    },

    'number': {
        'type': form.widgets.FloatText, 
        'value': 0
    },

    'array': {
        'type': form.widgets.VBox
    }
}


def test_empty():
    """
    An empty schema should raise an error
    """
    with pytest.raises(TypeError, match=r"missing .* 'schema'") as excinfo:
        Form()

    with pytest.raises(AssertionError, match="type") as excinfo:
        Form(schema={})


def test_schema_type():
    """
    Form is made to work with 'object' types
    """
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
    """
    Form from empty object properties is a valid, empty Form
    """
    schema = {
        'type': 'object',
        'properties': {}
    }
    f = Form(schema)

    assert isinstance(f, dict), f
    assert len(f) == len(schema['properties'])
    assert isinstance(f.widget, (form.widgets.Widget))
    assert isinstance(f.widget, (form.widgets.VBox)) # default, VBox


def _check_default_types_in_properties(_f, _props:dict):
    """
    Utility function for default types (in properties)
    """
    for prop_name, prop_obj in _props.items():
        _js_type = prop_obj['type']
        assert prop_name in _f 
        # assert type(_f[prop_name]) == _widgets_defaults[_js_type]['type']
        assert isinstance(_f[prop_name], _widgets_defaults[_js_type]['type'])
        if 'value' in _js_type:
            assert _f[prop_name].value == _widgets_defaults[_js_type]['value']


def test_string_property():
    """
    Test optional string field
    """
    schema = {
        'type': 'object',
        'properties': {
            'word': { 'type': 'string'}
        }
    }
    f = Form(schema)

    assert isinstance(f, dict), f
    assert len(f) == len(schema['properties'])
    # assert 'word' in f
    # assert f['word'].value == ''
    _check_default_types_in_properties(f, schema['properties'])


def test_number_property():
    """
    Test optional number field
    """
    schema = {
        'type': 'object',
        'properties': {
            'num': { 'type': 'number'}
        }
    }
    f = Form(schema)

    assert isinstance(f, dict), f
    assert len(f) == len(schema['properties'])
    # assert 'num' in f
    # assert type(f['num']) == _widgets_defaults['number']['type']
    # assert f['num'].value == _widgets_defaults['number']['value']
    _check_default_types_in_properties(f, schema['properties'])


def test_array_property():
    """
    Test optional array field
    """
    schema = {
        'type': 'object',
        'properties': {
            'arr': { 'type': 'array' }
        }
    }

    # Array elements demand 'items' field...
    with pytest.raises(AssertionError):
        Form(schema)

    # ... and only 'items':
    with pytest.raises(AssertionError):
        _schema = deepcopy(schema)
        _schema['properties']['arr'].update({'prefixItems': [{}]})
        Form(_schema)

    with pytest.raises(AssertionError):
        _schema = deepcopy(schema)
        _schema['properties']['arr'].update({'items': {}})
        Form(_schema)

    schema['properties']['arr'].update({'items': {'type': 'string'}})
    f = Form(schema)

    assert isinstance(f, dict), f
    assert len(f) == len(schema['properties'])
    _check_default_types_in_properties(f, schema['properties'])
