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
      with open(f'examples/{event_item["event"]}.example.json', 'w+') as example_file:
        json.dump(event, example_file, indent=2)