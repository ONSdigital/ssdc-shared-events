#!/bin/sh

cd event_dictionary/v0.3_DRAFT/
generate-schema-doc event.schema.json --config template_name=md dictionary.md
../../generate_example_json.sh
cd ../..