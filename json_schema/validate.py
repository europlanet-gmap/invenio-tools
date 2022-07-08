import os
import jsonschema

_curdir = os.path.dirname(os.path.abspath(__file__))


def read_schemas(basedir, pattern='*.schema.json'):
    """
    Return a dictionary with all schemas from 'basedir' matching 'pattern'
    """
    import json
    from glob import glob

    schemas = {}
    for fn in glob(os.path.join(basedir, pattern)):
        try:
            with open(fn) as f:
                js = json.load(f)
        except:
            print(f"Error loading JSON: '{fn}'")
            raise
        else:
            # If the schema has no "$id" key, we adhoc push one: the filename,
            # which is reasonable since this is the simplest, valid, and
            # normally the way schemas will cross-reference each other.
            _fn = os.path.basename(fn)
            if "$id" not in js:
                js["$id"] = _fn # +"#"
            schemas[js["$id"]] = js

    return schemas


schema_store = read_schemas(_curdir)


def validate(payload, schema='invenio_draft.schema.json'):
    # from jsonschema import Draft7Validator as Validator
    from jsonschema import RefResolver
    from jsonschema.validators import validator_for

    # If we had a simple schmea we could use jsonschema's 'validate' function
    # (as we did as first):
    # > import jsonschema
    # > res = jsonschema.validate(data, schema)
    #
    # But since the schema tree got a bit more complex,
    # > https://json-schema.org/understanding-json-schema/structuring.html,
    # we now have to creack open the components a little bit.
    #
    # One of the steps taken was to create a very simple "base" schema.
    # The "base" schema has two purposes: (1) to be used as the base
    # schema for jsonschema's RefResolver object, and (2) to define the
    # version of json-schema (currently draft-07) we're using in one single place.

    # Since we have "refs" in our schemas, we need a resolver to link them
    # resolver = RefResolver.from_schema(schema_store['base.schema.json'], store=schema_store)
    resolver = RefResolver.from_schema(schema_store[schema], store=schema_store)

    # Get the correct (or best) validator for our schema's version
    Validator = validator_for(schema_store['base.schema.json'])

    # Put them all together to define the validator/schema set to use
    validator = Validator(schema_store[schema], resolver=resolver)

    res = validator.validate(payload)
    # jsonschema.validate(data, schema_store[schema])
    return res
