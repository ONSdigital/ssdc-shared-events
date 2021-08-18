#!/bin/sh

mkdir -p tmp_for_json_generate
rm -r tmp_for_json_generate/* || true
cp *.schema.json tmp_for_json_generate
cd tmp_for_json_generate

for i in `ls *.schema.json`
do
    sed -f ../../../replace_unknown_json_schema_types.sed < $i  > $i.tmp
    mv $i.tmp $i
    example_file_name=${i/.schema.json/.example.json}
    fake-schema $i > $example_file_name
done

fake-schema event.schema.json > event.example.json

cd ..

cp tmp_for_json_generate/*.example.json .
rm -rf tmp_for_json_generate
