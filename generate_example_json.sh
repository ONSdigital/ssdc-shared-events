#!/bin/bash
shopt -s nullglob

if [ $# -ge 1 ]; then
  TARGET_SCHEMA_FILES=( "$@" )
else
  # If not passed a list of targets, target them all
  echo "Regenerating all examples"
  TARGET_SCHEMA_FILES=(./*.schema.json)
fi

rm -rf tmp_for_json_generate/* || true
mkdir -p tmp_for_json_generate

# Due to dependencies in the schemas, we must regenerate them all at this stage, even if we are targeting specific schemas
for schema_file in ./*.schema.json; do

  # The "event" schema will surely fail if we try it here due to interdependencies, we will come back and run it last
  if [[ "$schema_file" == "./event.schema.json" ]]; then
    continue
  fi

  sed -f ../../replace_unknown_json_schema_types.sed < "$schema_file" > "tmp_for_json_generate/$schema_file"
  example_file_name=${schema_file/.schema.json/.example.json}
  fake-schema "tmp_for_json_generate/$schema_file" > "tmp_for_json_generate/$example_file_name"
done

# The "event" schema depends on the other schemas it contains so it must be generated last, after all the other
# temporary schemas have had any unsupported types replaced
# Run in the tmp directory so that the dependencies are resolved to the temporary, amended versions we just generated
sed -f ../../replace_unknown_json_schema_types.sed < "event.schema.json" > "tmp_for_json_generate/event.schema.json"
pushd tmp_for_json_generate || exit
fake-schema "./event.schema.json" > "./event.example.json"
popd || exit

# Finally, copy out only the targeted example files, plus the "event" schema
for schema_file in "${TARGET_SCHEMA_FILES[@]}"; do
  example_file_name=${schema_file/.schema.json/.example.json}
  cp "tmp_for_json_generate/$example_file_name" .
done

cp tmp_for_json_generate/event.example.json .

rm -rf tmp_for_json_generate
