import json
from functools import reduce


def to_camel_case(snake_str):
    components = snake_str.split('-')
    return reduce(lambda x, y: x + y.title(), components[1:], components[0])


events = []

with open('eventHeader.schema.json', 'r') as event_header_file:
    event_header = json.load(event_header_file)
    for topic in event_header['properties']['topic']['enum']:
        events.append({
            'topic': topic,
            'event': to_camel_case(topic.replace("event_", ""))
        })

with open('event.example.json', 'r') as event_file:
    event = json.load(event_file)
    event["header"]["version"] = 'v0.3_DRAFT'
    event["header"]["originatingUser"] = 'foo.bar@ons.gov.uk'

    for event_item in events:
        with open(f'{event_item["event"]}.example.json', 'r') as specific_event_file:
            event["header"]["topic"] = event_item["topic"]
            event["payload"] = json.load(specific_event_file)

            if event_item["event"] == 'caseUpdate':
                event["payload"]["caseUpdate"]["sample"] = {
                    "addressLine1": "Flat 987, Magical Apartments",
                    "addressLine2": "123 Fake Street",
                    "addressLine3": "Some Suburb",
                    "townName": "Fake Town",
                    "postcode": "AB1 2ZX",
                    "region": "W",
                    "uprn": "123456789"
                }
                event["payload"]["caseUpdate"]["sampleSensitive"] = {
                    "phoneNumber": "REDACTED"
                }

            if event_item["event"] == 'newCase':
                event["payload"]["newCase"]["sample"] = {
                    "schoolId": "abc123",
                    "schoolName": "Chesterthorps High School",
                    "consentGivenTest": "true",
                    "consentGivenSurvey": "true"
                }
                event["payload"]["newCase"]["sampleSensitive"] = {
                    "firstName": "Fred",
                    "lastName": "Bloggs",
                    "childFirstName": "Jo",
                    "childMiddleNames": "Rose May",
                    "childLastName": "Pinker",
                    "childDob": "2001-12-31",
                    "additionalInfo": "Class 2A",
                    "childMobileNumber": "07123456789",
                    "childEmailAddress": "jo.rose.may.pinker@domain.com",
                    "parentMobileNumber": "07123456789",
                    "parentEmailAddress": "fred.bloggs@domain.com",
                }

            if event_item["event"] == 'collectionExerciseUpdate':
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

            with open(f'examples/{event_item["event"]}.example.json', 'w+') as example_file:
                json.dump(event, example_file, indent=2)
