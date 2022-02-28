#!/bin/bash

if ! command -v npx &> /dev/null
then
    echo "command 'npx' could not be found. Did you forget to install NodeJS?"
    exit
fi

# This must be kept up to date with the current "work in progress" draft directory
pushd event_dictionary/0.6.0-DRAFT/ || exit

npx prettier --write ./*.json
pipenv run generate-schema-doc event.schema.json --config template_name=md dictionary.md
../../generate_example_json.sh

echo "Generating polished example events"
mkdir -p examples
mkdir -p examples/sis
mkdir -p examples/social
mkdir -p examples/business

pipenv run python ../../polish_example_json.py
rm ./*.example.json

popd || exit
