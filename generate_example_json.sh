#!/bin/bash

rm -rf tmp_for_json_generate/* || true
mkdir -p tmp_for_json_generate
cp ./*.schema.json tmp_for_json_generate
pushd tmp_for_json_generate || exit

for schema_file in ./*.schema.json
do
    sed -f ../../../replace_unknown_json_schema_types.sed < "$schema_file"  > "$schema_file".tmp
    mv "$schema_file".tmp "$schema_file"
    example_file_name=${schema_file/.schema.json/.example.json}
    fake-schema "$schema_file" > "$example_file_name"
done

# Have to do this again because it fails the first time, due to dependency having unexpected types
fake-schema event.schema.json > event.example.json

popd

cp tmp_for_json_generate/*.example.json .
rm -rf tmp_for_json_generate
