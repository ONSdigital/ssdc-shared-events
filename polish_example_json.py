import json
import random
import string
from functools import reduce
from pathlib import Path
from typing import Dict

CURRENT_DRAFT_VERSION = '0.6.0-DRAFT'
EXAMPLE_SURVEY_TYPES = [{'type': 'sis', 'shape': 'sis/0.1.0-DRAFT/sis.json'},
                        {'type': 'social', 'shape': 'social/0.1.0/social.json'},
                        {'type': 'business', 'shape': 'business/0.1.0-DRAFT/business.json'}]
SAMPLE_URL_PREFIX = 'https://raw.githubusercontent.com/ONSdigital/ssdc-shared-events/main/sample/'
PROJECT_ROOT = Path(__file__).parent
EVENT_DICTIONARY_PATH = PROJECT_ROOT.joinpath('event_dictionary')
CURRENT_DRAFT_PATH = EVENT_DICTIONARY_PATH.joinpath(CURRENT_DRAFT_VERSION)


def main():

    # First prepare the example events with examples they provide in their schemas
    # TODO - JSON Schema Faker can do this, but the CLI currently presents no way to config it.
    replace_random_data_with_schema_examples()

    # Then generate specifically tailored examples for each example survey type
    generate_survey_specific_example_events()


def generate_survey_specific_example_events():
    # Generate fully formed examples of each event type for each example survey
    # Also replace random/generic example data with specifically tailored, hardcoded examples where required

    event_header = json.loads(CURRENT_DRAFT_PATH.joinpath('eventHeader.schema.json').read_text())
    events = []
    for topic in event_header['properties']['topic']['enum']:
        events.append({
            'topic': topic,
            'event': to_camel_case(topic.replace("event_", ""))
        })

    event_template = json.loads(CURRENT_DRAFT_PATH.joinpath('event.example.json').read_text())
    event_template["header"]["version"] = CURRENT_DRAFT_VERSION
    event_template["header"]["originatingUser"] = 'foo.bar@ons.gov.uk'

    for survey_type in EXAMPLE_SURVEY_TYPES:
        survey_shape = json.loads(PROJECT_ROOT.joinpath('sample', survey_type['shape']).read_text())
        fake_sample, fake_sample_sensitive, fake_sample_sensitive_redacted = generate_fake_sample_data(survey_shape)

        for event_item in events:
            event_type = event_item["event"]
            event = event_template.copy()
            event["payload"] = json.loads(CURRENT_DRAFT_PATH.joinpath(f'{event_type}.example.json').read_text())
            event["header"]["topic"] = event_item["topic"]

            if event_type == 'caseUpdate':
                event["payload"]["caseUpdate"]["sample"] = fake_sample
                event["payload"]["caseUpdate"]["sampleSensitive"] = fake_sample_sensitive_redacted

            elif event_type == 'newCase':
                event["payload"]["newCase"]["sample"] = fake_sample
                event["payload"]["newCase"]["sampleSensitive"] = fake_sample_sensitive

            elif event_type == 'updateSample':
                event["payload"]["updateSample"]["sample"] = fake_sample

            elif event_type == 'updateSampleSensitive':
                event["payload"]["updateSampleSensitive"]["sampleSensitive"] = fake_sample_sensitive

            elif event_type == 'surveyUpdate':
                if survey_type["type"] == 'social':
                    event["payload"]["surveyUpdate"]["name"] = "LMS"
                else:
                    event["payload"]["surveyUpdate"]["name"] = survey_type["type"].upper()

                event["payload"]["surveyUpdate"]["sampleDefinition"] = survey_shape
                event["payload"]["surveyUpdate"]["sampleDefinitionUrl"] = f'{SAMPLE_URL_PREFIX}{survey_type["shape"]}'

            elif event_type == 'uacUpdate':

                if survey_type["type"] == 'social':
                    # For social surveys we intend to use UAC metadata for tracking waves
                    event["payload"]["uacUpdate"]["metadata"] = {"wave": 3}

            elif event_type == 'collectionExerciseUpdate':
                if survey_type["type"] == 'social':
                    event["payload"]["collectionExerciseUpdate"] = {
                        "collectionExerciseId": "ecd1e9c2-0e20-4b20-a214-f5b35457a664",
                        "surveyId": "3883af91-0052-4497-9805-3238544fcf8a",
                        "name": "velit",
                        "reference": "MVP012021",
                        "startDate": "2021-09-17T23:59:59.999Z",
                        "endDate": "2021-09-27T23:59:59.999Z",
                        "metadata": {
                            "numberOfWaves": "3",
                            "waveLength": "2",
                            "cohorts": "3",
                            "cohortSchedule": "7"
                        }
                    }
                elif survey_type["type"] == 'sis':
                    event["payload"]["collectionExerciseUpdate"]["metadata"] = None

            polished_example_file = CURRENT_DRAFT_PATH.joinpath('examples', survey_type["type"],
                                                                f'{event_item["event"]}.example.json')
            polished_example_file.write_text(json.dumps(event, indent=2))


def replace_random_data_with_schema_examples():
    # Replace each event's random data with choices of examples in the schema where provided

    json_schema_files = {schema_file.name.split('.')[0]: schema_file
                         for schema_file in CURRENT_DRAFT_PATH.glob('*.schema.json')}
    json_example_files = CURRENT_DRAFT_PATH.glob('*.example.json')

    for json_example_file in json_example_files:
        schema_name = json_example_file.name.split('.')[0]
        schema = json.loads(json_schema_files[schema_name].read_text())
        json_example = json.loads(json_example_file.read_text())
        polished_json_example = polish_json_examples(json_example, schema)
        json_example_file.write_text(json.dumps(polished_json_example, indent=2))


def polish_json_examples(example_json: Dict, schema: Dict) -> Dict:
    """
    Recursively step through the example JSON, replacing random data with provided examples with schema examples. If
    the existing data already matches an example it will be left unchanged.

    When it comes to arrays and sub objects, if an entire example object is provided it will be used, otherwise we
    will recursively step through looking for examples within. It may be preferable to provide an example for an
    entire object or array to make sure the it conforms to restrictions such as uniqueness where randomly choosing
    individual examples may not.

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
            polished_example_json[key] = random.choice(schema_examples)

        elif key_schema.get('type') == 'array':
            # Recursively step through arrays.
            polished_example_json[key] = [polish_json_examples(i, key_schema.get('items', {})) for i in example_value]

        elif key_schema.get('type') == 'object':
            # Recursively step into sub objects.
            polished_example_json[key] = polish_json_examples(example_value, key_schema.get('properties', {}))

    return polished_example_json


def generate_fake_sample_data(survey_shape: Dict):
    # Generate fake sample data for a specific survey shape.
    # Note that the data may not conform to the sample spec, but the set of fields will at least be the correct shape
    column_names = []
    sensitive_column_names = []

    for shape_config in survey_shape:
        is_sensitive = shape_config.get('sensitive')
        column_name = shape_config['columnName']
        if is_sensitive:
            sensitive_column_names.append(column_name)
        else:
            column_names.append(column_name)

    fake_sample = {sample_key: f"dummy_{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}"
                   for sample_key in column_names}

    fake_sample_sensitive = {
        sample_key: f"dummy_{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}"
        for sample_key in sensitive_column_names}

    fake_sample_sensitive_redacted = {
        sample_key: "REDACTED" for sample_key in sensitive_column_names}
    return fake_sample, fake_sample_sensitive, fake_sample_sensitive_redacted


def to_camel_case(snake_str):
    components = snake_str.split('-')
    return reduce(lambda x, y: x + y.title(), components[1:], components[0])


if __name__ == '__main__':
    main()
