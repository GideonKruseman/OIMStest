


import json
import jsonschema
import argparse
import os

# Function to generate JSON schema from JSON data
def generate_json_schema(json_data):
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {},
        "required": []
    }

    for key, value in json_data.items():
        schema["properties"][key] = infer_schema(value)
        schema["required"].append(key)

    return schema

def infer_schema(data):
    if isinstance(data, dict):
        properties = {}
        required = []
        for key, value in data.items():
            properties[key] = infer_schema(value)
            required.append(key)
        return {
            "type": "object",
            "properties": properties,
            "required": required
        }
    elif isinstance(data, list):
        if len(data) == 0:
            return {
                "type": "array"
            }
        else:
            items_schema = infer_schema(data[0])
            return {
                "type": "array",
                "items": items_schema
            }
    elif isinstance(data, int):
        return {
            "type": "integer"
        }
    elif isinstance(data, float):
        return {
            "type": "number"
        }
    elif isinstance(data, str):
        return {
            "type": "string"
        }
    elif isinstance(data, bool):
        return {
            "type": "boolean"
        }
    elif data is None:
        return {
            "type": "null"
        }
    else:
        # If the data type is not recognized, simply treat it as "any"
        return {}

# Create an argument parser
parser = argparse.ArgumentParser(description="Generate JSON schema from a JSON file")

# Add an argument for the JSON file path
parser.add_argument("--json_file_path", required=True, help="Path to the JSON file")

# Parse the command-line arguments
args = parser.parse_args()

# Read the JSON file specified in the command-line argument
try:
    with open(args.json_file_path, "r") as json_file:
        json_data = json.load(json_file)
except FileNotFoundError:
    print(f"Error: File '{args.json_file_path}' not found.")
    exit(1)
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
    exit(1)

# Generate the JSON schema
schema = generate_json_schema(json_data)

# Derive the output file path
output_file_path = os.path.splitext(args.json_file_path)[0] + ".schema.json"

# Write the generated schema to a JSON file
with open(output_file_path, "w") as output_file_path:
    json.dump(schema, output_file_path, indent=2)

print(f"JSON schema has been written to '{output_file_path}'")

# Optionally, you can validate your JSON data against the generated schema using jsonschema.validate()
try:
    jsonschema.validate(json_data, schema)
    print("JSON data is valid against the schema.")
except jsonschema.exceptions.ValidationError as e:
    print(f"JSON data is not valid against the schema: {e}")