# ssdc-shared-events

Shared Google Pub/Sub topics, subscriptions and JSON schemas, which form the event interface contract between different products in the Strategic Survey Data Collection universe.

## Where is the Event Dictionary?
[It's right here](event_dictionary/v0.3_DRAFT/dictionary.md)

## What's this all about then?
The schema which all events flowing between products must conform to, [lives here](event_dictionary/v0.3_DRAFT/event.schema.json)

It should be versioned, and products will implement a certain version of the schema, so edit with caution... you might break the interface contract!

##  How to Validate the Schema and Re-Generate the Documentation
Install json-schema-for-humans by running: `pip install json-schema-for-humans`

Then, in the correct version directory, run: `generate-schema-doc event.schema.json --config template_name=md dictionary.md`