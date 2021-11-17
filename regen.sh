#!/bin/bash

if ! command -v npx &> /dev/null
then
    echo "command 'npx' could not be found. Did you forget to install NodeJS?"
    exit
fi

if ! command -v generate-schema-doc &> /dev/null
then
    echo "command 'generate-schema-doc' could not be found. Did you forget to install it?"
    exit
fi

if ! command -v python3 &> /dev/null
then
    echo "command 'python3' could not be found. Did you forget to install it?"
    exit
fi

cd event_dictionary/0.6.0-DRAFT/
npx prettier --write ./*.json
generate-schema-doc event.schema.json --config template_name=md dictionary.md
../../generate_example_json.sh
mkdir -p examples
mkdir -p examples/sis
mkdir -p examples/social
mkdir -p examples/business
python ../../polish_example_json.py
rm *.example.json
cd ../..