#!/usr/bin/env python
import os
import json

import validate


def resolve_references(obj, resolver, _id, refs=None):
    # print(f"Input (obj): {obj}")
    # print(f"Input (id): {_id}")
    # print(f"Input (refs): {refs}")
    refs = refs if refs is not None else []
    if isinstance(obj, list):
        out = [ resolve_references(item, resolver, _id, refs) for item in obj ]
    elif isinstance(obj, dict):
        _id = obj['$id'] if '$id' in obj else _id
        # print(f"Is dict (obj): {obj}")
        # print(f"Is dict (id): {_id}")
        out = {}
        for k,v in obj.items():
            if k == "$ref":
                # print(v)
                if v.startswith('#'):
                    v = _id + v
                else:
                    _id = v.split('#')[0]
                # print(v)
                res = resolver.resolve(v)[1]
                refs.append(v)
                out.update(resolve_references(res, resolver, _id, refs))
            else:
                out[k] = resolve_references(v, resolver, _id, refs)
    else:
        out = obj

    return out


def main(filename):
    from copy import deepcopy

    with open(filename) as fp:
        js = json.load(fp)

    schema_id = js['$id'] if '$id' in js else os.path.basename(filename)
    resolver = validate.create_resolver(schema_id)

    refs = []
    res = deepcopy(js)
    while len(refs) == 0 or len(refs) != len(refs_old):
        refs_old = refs[:]
        res = resolve_references(res, resolver, schema_id, refs)
    print(refs)
    return res


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Validate file (json) content against (invenio_draft) schema", file=sys.stderr)
        print(f"Usage: {sys.argv[0]} <filename.json>", file=sys.stderr)
        sys.exit(1)

    filename = sys.argv[1]
    assert os.path.exists(filename)

    res = main(filename)
    print(json.dumps(res, indent=2))

    sys.exit(0)
