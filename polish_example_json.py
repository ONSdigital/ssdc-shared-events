import json
import random
import string
from functools import reduce
from pathlib import Path

from example_json_polisher import polish_json_examples

CURRENT_DRAFT_VERSION = '0.6.0-DRAFT'
CWD = Path().cwd()


def to_camel_case(snake_str):
    components = snake_str.split('-')
    return reduce(lambda x, y: x + y.title(), components[1:], components[0])


json_schema_files = {schema_file.name.split('.')[0]: schema_file for schema_file in CWD.glob('*.schema.json')}
json_example_files = CWD.glob('*.example.json')

# Replace each event's random data with choices of examples in the schema where provided
for json_example_file in json_example_files:
    schema_name = json_example_file.name.split('.')[0]
    schema = json.loads(json_schema_files[schema_name].read_text())
    json_example = json.loads(json_example_file.read_text())
    polished_json_example = polish_json_examples(json_example, schema)
    json_example_file.write_text(json.dumps(polished_json_example, indent=2))

# Iterate over the examples, creating separate versions for different example survey types
# Also replace any random/generic example data with specifically tailored, hardcoded examples where required
sample_url_prefix = 'https://raw.githubusercontent.com/ONSdigital/ssdc-shared-events/main/sample/'
events = []
survey_types = [{'type': 'sis', 'shape': 'sis/0.1.0-DRAFT/sis.json'},
                {'type': 'social', 'shape': 'social/0.1.0/social.json'},
                {'type': 'business', 'shape': 'business/0.1.0-DRAFT/business.json'}]

event_header = json.loads(CWD.joinpath('eventHeader.schema.json').read_text())
for topic in event_header['properties']['topic']['enum']:
    events.append({
        'topic': topic,
        'event': to_camel_case(topic.replace("event_", ""))
    })

event = json.loads(CWD.joinpath('event.example.json').read_text())
event["header"]["version"] = CURRENT_DRAFT_VERSION
event["header"]["originatingUser"] = 'foo.bar@ons.gov.uk'

for survey_type in survey_types:
    survey_shape = json.loads(CWD.parents[1].joinpath('sample', survey_type['shape']).read_text())
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

    for event_item in events:
        event["payload"] = json.loads(CWD.joinpath(f'{event_item["event"]}.example.json').read_text())
        event["header"]["topic"] = event_item["topic"]

        if event_item["event"] == 'caseUpdate':
            event["payload"]["caseUpdate"]["sample"] = fake_sample
            event["payload"]["caseUpdate"]["sampleSensitive"] = fake_sample_sensitive_redacted

        if event_item["event"] == 'newCase':
            event["payload"]["newCase"]["sample"] = fake_sample
            event["payload"]["newCase"]["sampleSensitive"] = fake_sample_sensitive

        if event_item["event"] == 'updateSample':
            event["payload"]["updateSample"]["sample"] = fake_sample

        if event_item["event"] == 'updateSampleSensitive':
            event["payload"]["updateSampleSensitive"]["sampleSensitive"] = fake_sample_sensitive

        if event_item["event"] == 'surveyUpdate':
            if survey_type["type"] == 'social':
                event["payload"]["surveyUpdate"]["name"] = "LMS"
                # event["payload"]["surveyUpdate"]["allowedPrintFulfilments"] = [
                #     {
                #         "packCode": "replace-uac-en",
                #         "description": "Replacement UAC - English",
                #         "metadata": {
                #             "suitableRegions": ["E", "N"]
                #         }
                #     },
                #     {
                #         "packCode": "replace-uac-cy",
                #         "description": "Replacement UAC - English & Welsh",
                #         "metadata": {
                #             "suitableRegions": ["W"]
                #         }
                #     }
                # ]
                # event["payload"]["surveyUpdate"]["allowedSmsFulfilments"] = [
                #     {
                #         "packCode": "replace-uac-en",
                #         "description": "Replacement UAC - English",
                #         "metadata": {
                #             "suitableRegions": ["E", "N"]
                #         }
                #     },
                #     {
                #         "packCode": "replace-uac-cy",
                #         "description": "Replacement UAC - English & Welsh",
                #         "metadata": {
                #             "suitableRegions": ["W"]
                #         }
                #     }
                # ]
                # event["payload"]["surveyUpdate"]["allowedEmailFulfilments"] = []
            else:
                event["payload"]["surveyUpdate"]["name"] = survey_type["type"].upper()

            event["payload"]["surveyUpdate"]["sampleDefinition"] = survey_shape
            event["payload"]["surveyUpdate"]["sampleDefinitionUrl"] = f'{sample_url_prefix}{survey_type["shape"]}'

        if event_item["event"] == 'uacUpdate':

            if survey_type["type"] == 'social':
                # For social surveys we intend to use UAC metadata for tracking waves
                event["payload"]["uacUpdate"]["metadata"] = {"wave": 3}

        if event_item["event"] == 'collectionExerciseUpdate':
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

        polished_example_file = CWD.joinpath('examples', survey_type["type"], f'{event_item["event"]}.example.json')
        polished_example_file.write_text(json.dumps(event, indent=2))
