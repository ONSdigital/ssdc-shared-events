# ssdc-shared-events

Shared Google Pub/Sub topics, subscriptions and JSON schemas, which form the event interface contract between different products in the Strategic Survey Data Collection universe.

## Where is the Event Dictionary?
[It's right here](event_dictionary/v0.3_DRAFT/dictionary.md)

## What's this all about then?
The schema which all events flowing between products must conform to, [lives here](event_dictionary/v0.3_DRAFT/event.schema.json)

The contract is **VERSIONED** so any changes should be made to the latest DRAFT version. Please do not modify a RELEASE version, because it would break a contract which our software complies with.

Naturally, any breaking change a version would be considered a major version increment. Ideally, contract changes are non-breaking and backwards compatible, initially: attributes should me marked as deprecated, and only retired after a couple of releases.

##  How to Validate the Schema and Re-Generate the Documentation & Example JSON
Install json-schema-for-humans by running: `pip install json-schema-for-humans`

Then, in the correct version directory, run: `generate-schema-doc event.schema.json --config template_name=md dictionary.md`

Install fake-schema-cli by running: `npm install -g fake-schema-cli`

Then, in the correct version directory, run: `../../generate_example_json.sh`