"""
Translates a JSONSchema document (without $refs) into an equivalent Params model
"""
import param


# Parameters metadata:
# - https://param.holoviz.org/user_guide/Parameters.html#parameter-metadata
#

def _date(val, *args):
    """
    Return 'val' (and *args) as datetime.date object if not yet (eg, 'YYYY-MM-DD')
    """
    import datetime

    if val:
        assert isinstance(val, (str, datetime.date))
        val = datetime.date.fromisoformat(val) if isinstance(val, str) else val
    else:
        val = datetime.date.today()

    return (val, *args)


_format_args = {
    "date": _date
}

_param_classes = {
    "string": param.String,
    "date": param.CalendarDate
}

def _param(obj_type, *args, **kwargs):
    _class = _param_classes[obj_type]
    _format = _format_args.get(obj_type)
    args = _format(*args) if _format else args
    print(args)
    return _class(*args, **kwargs)


# def _string(obj, default, name, required=False, constant=False):
def _string(obj, *args, **kwargs):
    """
    Return a string/date "Param(*args, **kwargs)"

    >>> _string( {"type":"string"}, None )
    """
    print(obj)
    print(args)

    obj_type = obj['type'] if 'format' not in obj else obj['format']
    doc = obj.get('$comment', None)

    kwargs.update({ 'doc': doc })

    return _param(obj_type, *args, **kwargs)


def _const(obj):
    value = obj['const']
    value_type = type(value)
    return _handlers[value_type](obj, value, constant=True)


def _items(obj):
    """
    Process an 'items' element
    """
    pass


def _object(obj:str):
    """
    Process an 'object' element
    """
    # check mandatory fields
    assert all([ k in obj for k in ['type', 'properties'] ])
    pass


_handlers = {
    'items': _items,
    'object': _object,
    'string': _string,
    str: _string,
}


def main(obj):
    assert isinstance(obj, dict)
    _otype = obj['type']
    res = _handlers[obj['type']](obj)
