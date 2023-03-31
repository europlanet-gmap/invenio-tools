import ipywidgets as widgets
from typing import Any, Union


def main(obj:dict) -> dict:
    """
    Return a representation of 'obj' schema with widgets to be used in Form
    """

    assert isinstance(obj, dict), obj
    # assert obj['type'] == 'object', obj

    # First, let's validate the schema
    assert validate_schema(obj)
    
    res = _handlers[obj['type']](obj)
    # res = _object(obj)

    if not isinstance(res, dict):
        assert isinstance(res, widgets.Widget)
        res = { res.description: res}

    assert isinstance(res, dict)
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


def _properties(obj:dict, required:list = None) -> dict:
    """
    Example:
    >>> _properties(obj = {
            "name": {"type": "string"}, 
            "type": {"const": "dataset"}, 
            "date": {"type": "string", "format": "date"}
        }, required = ['name'])
    """
    required = set(required) if required else set()
    _props = {}
    for name, prop_obj in obj.items():
        _props[name] = _property(prop_obj, name, required=name in required)

    return _props


def _property(obj:dict, name:str, required:bool = False):
    """
    Return an widget object according to "obj['type']"

    >>> _property( {"type":"string"} )
    """

    # check supported attributes
    supported_fields = ('type', 'oneOf')
    assert any([ k in obj for k in supported_fields ]), obj

    if 'type' in obj:
        _widget = _handlers[obj['type']](obj, name=name, required=required)

    else:
        assert 'oneOf' in obj, "The only supported optionals are 'oneOf'"

        _widgets = [ _handlers[o['type']](o) for o in obj['oneOf'] ]
        _widget = { 'oneOf': _widgets }

        assert None, "TODO: review this '_widget' dictionary here"

    return _widget


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
    assert obj['type'] == 'object'

    # check mandatory fields
    mandatory_fields = ['type', 'properties']
    missing_fields = list(filter(lambda f:f not in obj, mandatory_fields))
    assert len(missing_fields) == 0, f"Missing fields in {obj}: {missing_fields}"

    # desc = obj['description']

    props = _properties(obj['properties'])
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
    # assert obj['type'] != 'array'
    assert len(obj) > 0, "Expected non-empty 'items' array"

    if 'enum' in obj:
        w_cls = widgets.SelectMultiple
        kwargs = {'options': obj['enum']}
        return make_widget(obj, name, required, w_cls, **kwargs)
 
    if 'type' in obj:
        # Items have all the same schema
        return Items(obj, description=name.title())
 
 

# def _string(obj:dict, name:str, required:bool):
def _string(obj:dict, **kwargs):
    """ 
    Return a Text iPywidget
    """
    if 'enum' in obj:
        w_cls = widgets.Dropdown
        kwargs.update({'options': obj['enum']})
    else:
        w_cls = widgets.Text

    return make_widget(obj, widget_class=w_cls, **kwargs)


def _number(obj:dict, **kwargs):
    """
    Return a FloatText iPywidget
    """
    w_cls = widgets.FloatText
    return make_widget(obj, widget_class=w_cls, **kwargs)


def make_widget(obj:dict, widget_class, **kwargs):
    ro = obj['readOnly'] if 'readOnly' in obj else False

    name = kwargs.pop('name', obj['type'].title())
    description = name.replace('_', ' ').title()

    required = kwargs.pop('required', False)
    if required:
        description = F'<strong style="color:red">{description}</strong>'
    if ro:
        description = F'<i>{description}</i>'

    kwargs.update(dict(
        description = description, 
        description_allow_html = True,
        disabled = ro
    ))

    try:
        widget = widget_class(**kwargs)
    except:
        print(obj)
        raise 

    return widget


_handlers = {
    'string': _string,
    'number': _number,
    'array': _array,
    'object': _object,
}


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


OBJECT_BASECLASS = widgets.VBox
ITEMS_BASECLASS = widgets.VBox

@widgets.register
class Object(OBJECT_BASECLASS):
    def __init__(self, prop_widgets:dict):
        self._widgets = prop_widgets
        super().__init__(list(prop_widgets.values()))

    @property 
    def value(self):
        value = [w.value for w in self._widgets.values()]
        return value 

    @value.setter
    def value(self, value:dict):
        assert isinstance(value, dict), f"Expected a dictionary, instead got {type(value)}"
        for p,w in self._widgets.items():
            if p in value:
                w.value = value[p]
            else:
                w.value = ''


@widgets.register
class Items(ITEMS_BASECLASS):

    def __init__(self, obj:dict, description = "Text field", **kwargs):
        self._obj = obj
        self._wdgts = {}
        self.description = description
        add_btn = widgets.Button(icon="plus")
        add_btn.on_click(lambda btn: self.add_item())
        super().__init__([add_btn])

    def _make_widget(self, value=None):
        def generate_id():
            from random import randint
            id_ = randint(100,1000)
            while id_ in self._wdgts:
                id_ = randint(100,1000)
            return id_ 

        obj = self._obj
        prop_widgets = _handlers[obj['type']](obj)
        wdgt = Object(prop_widgets)
        wdgt.value = value
        # if isinstance(wdgt, dict):
        #     wdgt = widgets.VBox(list(wdgt.values()))

        id_ = generate_id()
        return wdgt, id_

    def del_item(self, id_):
        item_to_remove = self._wdgts.pop(id_)
        self.children = tuple([self.children[0]] + list(self._wdgts.values()))

    def add_item(self, value:Union[dict,str,None] = None):
        """Create new widget in items"""
        wdgt, id_ = self._make_widget(value=value)
        if value is not None:
            wdgt.value = value

        del_btn = widgets.Button(icon="trash")
        del_btn.on_click(lambda btn: self.del_item(id_))

        new_item = widgets.HBox([wdgt, del_btn])
        
        if all(item.children[0].value.strip() 
               for item in self.children if hasattr(item, 'children')):
            new_children = tuple(list(self.children) + [new_item])

        self._wdgts[id_] = new_item
        self.children = new_children

    def clear(self):
        """Remove all items (but the '+' button)"""
        self.children = (self.children[0], )

    @property 
    def value(self):
        value = [w.children[0].value for w in self.children[1:]]
        return value 

    @value.setter
    def value(self, value:Union[dict,list]):
        assert isinstance(value, (dict,list)), "Expected a list or dictionary."
        self.clear()
        if isinstance(value, list):
            for val in value:
                self.add_item(val)
        else:
            self.add_item(value)


