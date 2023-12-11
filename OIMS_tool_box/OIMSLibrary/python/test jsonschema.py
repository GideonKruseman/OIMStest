import jsonschema
import json

# Example schema using a Draft 2020-12 feature
schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "example": {
            "type": "string",
            "maxLength": 5
        }
    }
}

# Example JSON data
data = {"example": "test"}

# Validate the data
try:
    jsonschema.validate(instance=data, schema=schema)
    print("Validation successful. Draft 2020-12 might be supported.")
except jsonschema.exceptions.SchemaError as e:
    print(f"Schema error: {e}")
except jsonschema.exceptions.ValidationError as e:
    print(f"Validation error: {e}")
