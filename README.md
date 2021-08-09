# ssdc-shared-events

Shared Google Pub/Sub topics, subscriptions and JSON schemas, which form the event interface contract between different products in the Strategic Survey Data Collection universe.

##  How to Validate the Schema and Re-Generate the Documentation
Install json-schema-for-humans by running: `pip install json-schema-for-humans`

Then, run: `generate-schema-doc event.schema.json --config template_name=md dictionary.md`