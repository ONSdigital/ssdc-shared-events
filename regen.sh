#!/bin/sh

cd event_dictionary/v0.3_DRAFT/
npx prettier --write ./*.json
generate-schema-doc event.schema.json --config template_name=md dictionary.md
../../generate_example_json.sh
cd ../..