# ssdc-shared-events

Shared Google Pub/Sub topics, subscriptions and JSON schemas, which form the event interface contract between different products in the Strategic Survey Data Collection universe.

## Where is the Event Dictionary?
[It's right here](event_dictionary/0.5.0/dictionary.md)

The _old_ event dictionary used to live in Confluence, and it was a little flawed because it didn't conform to a rigorous standard, like [JSON Schema](https://json-schema.org/).

If you're looking for example JSON, keep reading... it's in the section called [Where are JSON examples of messages?](#where-are-json-examples-of-messages)

## What's this all about then?
The schema which all events flowing between products must conform to, [lives here](event_dictionary/0.5.0/event.schema.json)

Because it's using the [JSON Schema](https://json-schema.org/) standard, it means that we are able to **GENERATE CODE** from it. So, you can feed the schema into your preferred language and it will spit out some useful code to allow you to manipulate events which are schema compliant. For example, take a look at [jsonschema2pojo](https://github.com/joelittlejohn/jsonschema2pojo) if Java floats your boat... but remember that we are language agnostic.

The contract is **VERSIONED** so any changes should be made to the latest DRAFT version. Please do not modify a RELEASE version, because it will break the contract which our software complies with.

Naturally, any breaking changes will require a major version increment. Ideally, contract changes are non-breaking and backwards compatible, initially: attributes should me marked as deprecated, and only retired after a couple of releases.

## Where are JSON examples of messages?
You'll find a JSON example of every event type with a `.example.json` suffix, in [this directory](https://github.com/ONSdigital/ssdc-shared-events/tree/main/event_dictionary/0.5.0/examples).

The examples are machine-generated, so the values might not make sense... they're just random placeholders, so that the message structure can be understood. You should refer to the [Event Dictionary](event_dictionary/0.5.0/dictionary.md) for the specifics on particular JSON properties.

##  How to Format, Validate the Schema and Re-Generate the Documentation & Example JSON
In a hurry? Just run `./regen.sh`

Formatting is done in the correct version directory by running (requires NPM installed): `npx prettier --write ./*.json`

Install python dependencies, including json-schema-for-humans by running  (requires Pipenv and Python >3.8 installed): `pipenv install`

Then, in the correct version directory, run: `generate-schema-doc event.schema.json --config template_name=md dictionary.md`

Install fake-schema-cli by running (requires NPM installed): `npm install -g fake-schema-cli`

Then, in the correct version directory, run: `../../generate_example_json.sh`

Final polishing is applied by running (requires Python 3): `pipenv run python ../../polish_example_json.py`