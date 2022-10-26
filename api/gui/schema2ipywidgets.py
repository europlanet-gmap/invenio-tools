import ipywidgets as widgets


def main(obj:dict) -> dict:
    """
    Return a representation of 'obj' schema with widgets to be used in Form
    """

    assert isinstance(obj, dict), obj
    assert obj['type'] == 'object', obj

    # First, let's validate the schema
    assert validate_schema(obj)
    
    # res = _handlers[obj['type']](obj)
    res = _object(obj)
    return res


def validate_schema(schema:dict) -> bool:
    from ..json_schema import validate
    try:
        validate.check_schema(schema)
    except Exception as err:
        print(err)
        return False 
    else:
        return True


def validate_json(obj:dict, schema:dict) -> bool:
    from jsonschema import validate
    try:
        validate(instance=obj, schema=schema)
    except Exception as err:
        print(err)
        return False 
    else:
        return True


def _object(obj:dict, required:bool=False) -> dict:
    """
    Process an 'object' element

    >>> _object({
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "type": {"const": "dataset"},
                "date": {"type": "string", "format": "date"}
            },
            "required": ["name"]
        })
    """
    # check mandatory fields
    mandatory_fields = ['type', 'properties']
    assert all([ k in obj for k in mandatory_fields ])
    assert obj['type'] == 'object'

    # desc = obj['description']

    props = _properties(obj['properties'],
                        required = obj.get('required', None))
    return props


def _array(obj:dict, name:str, required:bool) -> list:
    """
    Return a container for items' Params
    """
    # check mandatory fields
    assert all([ k in obj for k in ['type', 'items'] ]), obj
    assert obj['type'] == 'array', obj

    return _items(obj['items'], name, required,
                  minItems = obj.get('minItems', None))


def _items(obj:dict, name:str, required:bool, minItems=None, maxItems=None):
    """
    Return a list of "param types"
    """
    assert 'type' in obj
    assert obj['type'] != 'array'
    assert maxItems is None, "'maxItems' is not implemented yet"

    if 'type' in obj:
        w_cls = Items

    kwargs = {}
    if 'enum' in obj:
        w_cls = widgets.SelectMultiple
        kwargs.update({'options': obj['enum']})

    return make_widget(obj, name, required, w_cls, **kwargs)


def _string(obj:dict, name:str, required:bool):
    """ 
    Return a Text iPywidget
    """
    kwargs = {}
    if 'enum' in obj:
        w_cls = widgets.Dropdown
        kwargs.update({'options': obj['enum']})
    else:
        w_cls = widgets.Text

    return make_widget(obj, name, required, w_cls, **kwargs)


def _number(obj:dict, name:str, required:bool):
    """
    Return a FloatText iPywidget
    """
    w_cls = widgets.FloatText
    return make_widget(obj, name, required, w_cls)


def make_widget(obj:dict, name:str, required:bool, widget_class, **kwargs):
    description = name.replace('_', ' ').title()
    ro = obj['readOnly'] if 'readOnly' in obj else False

    if required:
        description = F'<strong style="color:red">{description}</strong>'
    if ro:
        description = F'<i>{description}</i>'

    kwargs.update(dict(
        description = description, 
        description_allow_html = True,
        disabled = ro
    ))

    return widget_class(**kwargs)


_type_resolvers = {
    'string': _string,
    'number': _number,
    'array': _array,
    'object': _object,
}

_handlers = _type_resolvers


def _properties(obj:dict, required:list = None) -> dict:
    """
    >>> _properties({"name": {"type": "string"}, "type": {"const": "dataset"}, "date": {"type": "string", "format": "date"}})
    """
    required = set(required) if required else set()
    _props = {}
    for name, prop_obj in obj.items():
        _props[name] = _property(prop_obj, name, required=name in required)

    return _props


def _property(schema_property:dict, name:str, required:bool = False):
    """
    Return a "Param(*args, **kwargs)" object according to "obj['type']"

    >>> _property( {"type":"string"} )
    """
    obj = schema_property

    # check supported attributes
    supported_fields = ('type', 'oneOf')
    assert any([ k in obj for k in supported_fields ]), obj

    if 'type' in obj:
        param_obj = _type_resolvers[obj['type']](obj, name, required)

    else:
        assert 'oneOf' in obj, obj
        param_objs = [ _type_resolvers[o['type']](o) for o in obj['oneOf'] ]
        # param_obj = param.Selector(param_objs)
        # param_obj = param_objs
        param_obj = { 'oneOf': param_objs }

    return param_obj


def _date(val, *args) -> tuple:
    """
    Return 'val' (and *args) as datetime.date object if not yet (eg, 'YYYY-MM-DD')
    """
    import datetime

    if val:
        assert isinstance(val, (str, datetime.date))
        val = datetime.date.fromisoformat(val) if isinstance(val, str) else val
    else:
        # val = datetime.date.today()
        val = val

    return (val, *args)


_format_args = {
    "date": _date
}

_wdgt_classes = {
    "string": widgets.Text,
    "date": widgets.DatePicker
}

def _param(obj_type, *args, **kwargs):
    """
    Return Widgets object according to '_param_classes' and 'obj_type'.

    Input:
        *args : 
    """
    wdgt_class = _wdgt_classes[obj_type]
    _format = _format_args.get(obj_type)
    args = _format(*args) if _format else args
    return wdgt_class(*args, **kwargs)


@widgets.register
class Items(widgets.VBox):

    def __init__(self, description = "Text field", **kwargs):
        self.description = description
        add_btn = widgets.Button(icon="plus")
        add_btn.on_click(lambda btn: self.add_item())
        super().__init__([add_btn])
        

    def del_item(self, value):
        def not_value(item):
            try:
                found = item.children[0].value == value
            except:
                found = False
            return not found
        
        new_items = filter(not_value, self.children)
        self.children = tuple(new_items)

        return self


    def add_item(self, value=None):
        """Create new Text input widget in items"""
        text = widgets.Text(description = self.description)
        if value is not None:
            text.value = str(value)

        del_btn = widgets.Button(icon="trash")
        del_btn.on_click(lambda btn: self.del_item(text.value))

        new_item = widgets.HBox([text, del_btn])
        
        if all(item.children[0].value.strip() 
               for item in self.children if hasattr(item, 'children')):
            self.children = tuple(list(self.children) + [new_item])

        return self
        
        
    @property 
    def value(self):
        value = [w.children[0].value for w in self.children[1:]]
        return value 

    @value.setter
    def value(self, value:list):
        for val in value:
            self.add_item(val)

