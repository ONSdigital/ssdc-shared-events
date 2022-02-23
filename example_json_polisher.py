import random

from typing import Dict


def polish_json_examples(example_json: Dict, schema: Dict) -> Dict:
    """
    Recursively step through the example JSON, replacing random data with provided examples with schema examples. If
    the existing data already matches an example it will be left unchanged.

    :param example_json: Dictionary parsed example JSON with dummy data to be replaced
    :param schema: Dictionary parsed JSON schema
    :return: Dictionary format polished example JSON
    """
    polished_example_json = example_json

    if schema.get('type') == 'object':
        # If given an object then recursively step into the properties
        return polish_json_examples(example_json, schema['properties'])

    for key, example_value in example_json.items():
        if key.startswith('$') or not (key_schema := schema.get(key)):
            # $ prefix indicates a JSON schema parameter or no reference to this key in the schema, ignore it
            continue

        if (schema_examples := key_schema.get('examples')) and (example_value not in schema_examples):
            # If the schema provides examples and the existing example JSON does not adhere,
            # then replace with a choice of schema example values
            # if value not in schema_examples:
            polished_example_json[key] = random.choice(schema_examples)

        elif key_schema.get('type') == 'array':
            # Recursively step through arrays. Note that if an example for the entire array is supplied,
            # then examples for individual items will be ignored. It may be preferable to provide an entire example
            # array instead as building examples for individual example items may not respect restrictions on the
            # array as a whole such as uniqueness of elements
            polished_example_json[key] = [polish_json_examples(i, key_schema.get('items', {})) for i in example_value]

        elif key_schema.get('type') == 'object':
            # Recursively step into sub objects. Note that if an example for the entire sub object is provided then
            # that will be used and examples within the sub object will be ignored.
            polished_example_json[key] = polish_json_examples(example_value, key_schema.get('properties', {}))

    return polished_example_json
