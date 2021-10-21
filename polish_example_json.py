import json
import random
import string
from functools import reduce


def to_camel_case(snake_str):
    components = snake_str.split('-')
    return reduce(lambda x, y: x + y.title(), components[1:], components[0])


URL_PREFIX = 'https://raw.githubusercontent.com/ONSdigital/ssdc-shared-events/main/sample/'
events = []
survey_types = [{'type': 'sis', 'shape': 'sis/0.1.0-DRAFT/sis.json'},
                {'type': 'social', 'shape': 'social/0.1.0-DRAFT/social.json'},
                {'type': 'business', 'shape': 'business/0.1.0-DRAFT/business.json'}]

with open('eventHeader.schema.json', 'r') as event_header_file:
    event_header = json.load(event_header_file)
    for topic in event_header['properties']['topic']['enum']:
        events.append({
            'topic': topic,
            'event': to_camel_case(topic.replace("event_", ""))
        })

with open('event.example.json', 'r') as event_file:
    event = json.load(event_file)
    event["header"]["version"] = '0.4.0'
    event["header"]["originatingUser"] = 'foo.bar@ons.gov.uk'

    for survey_type in survey_types:
        with open(f"../../sample/{survey_type['shape']}", 'r') as shape_file:
            shape_file = json.load(shape_file)
            column_names = []
            sensitive_column_names = []

            for shape_config in shape_file:
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
            with open(f'{event_item["event"]}.example.json', 'r') as specific_event_file:
                event["header"]["topic"] = event_item["topic"]
                event["payload"] = json.load(specific_event_file)

                if event_item["event"] == 'caseUpdate':
                    event["payload"]["caseUpdate"]["sample"] = fake_sample
                    event["payload"]["caseUpdate"]["sampleSensitive"] = fake_sample_sensitive_redacted

                if event_item["event"] == 'newCase':
                    event["payload"]["newCase"]["sample"] = fake_sample
                    event["payload"]["newCase"]["sampleSensitive"] = fake_sample_sensitive

                if event_item["event"] == 'updateSampleSensitive':
                    event["payload"]["updateSampleSensitive"]["sampleSensitive"] = fake_sample_sensitive

                if event_item["event"] == 'surveyUpdate':
                    if survey_type["type"] == 'social':
                        event["payload"]["surveyUpdate"]["name"] = "LMS"
                    else:
                        event["payload"]["surveyUpdate"]["name"] = survey_type["type"].upper()

                    event["payload"]["surveyUpdate"]["sampleDefinition"] = shape_file
                    event["payload"]["surveyUpdate"][
                        "sampleDefinitionUrl"] = f'{URL_PREFIX}{survey_type["shape"]}'

                if event_item["event"] == 'uacUpdate':
                    if survey_type["type"] == 'social':
                        event["payload"]["uacUpdate"]["metadata"] = {"wave": 3}

                if event_item["event"] == 'collectionExerciseUpdate':
                    if survey_type["type"] == 'social':
                        event["payload"]["collectionExerciseUpdate"] = {
                            "collectionExerciseId": "3883af91-0052-4497-9805-3238544fcf8a",
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

                with open(f'examples/{survey_type["type"]}/{event_item["event"]}.example.json', 'w+') as example_file:
                    json.dump(event, example_file, indent=2)
