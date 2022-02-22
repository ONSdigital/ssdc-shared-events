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

    for key, value in example_json.items():
        if key.startswith('$'):
            # $ prefix indicates a JSON schema parameter, ignore it
            continue

        key_schema = schema.get(key, {})
        if schema_examples := key_schema.get('examples'):
            # If the schema provides examples and the existing example JSON does not adhere,
            # then replace with a choice of schema example values
            if value not in schema_examples:
                polished_example_json[key] = random.choice(schema_examples)

        elif key_schema.get('type') == 'array':
            # Recursively step through arrays. Note that if an example for the entire array is supplied,
            # then examples for individual items will be ignored
            polished_example_json[key] = [polish_json_examples(i, key_schema.get('items', {})) for i in value]

        elif key_schema.get('type') == 'object':
            # Recursively step into sub objects
            polished_example_json[key] = polish_json_examples(value, key_schema['properties'])

    return polished_example_json
