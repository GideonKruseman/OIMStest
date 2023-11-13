#<%REGION File header%>
#=============================================================================
# File      : json_schema_builder.py
# Author    : Gideon Kruseman <g.kruseman@cgiar.org>
# Version   : 1.0
# Date      : 10/23/2023 3:01:10 PM
# Changed   :
# Changed by:
# Remarks   :
# using this script would need to have the following packages installed:
#       json
#       jsonschema
#       argparse
#       os
#
#
#
#
#*=============================================================================
#*<%/REGION File header%>



import json
import jsonschema
import argparse
import os

def load_json_file(file_path, default=None):
    """Load a JSON file from a specified path. Return the default if not found."""
    if file_path is None:
        return default
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        if default is not None:
            return default
        print(f"Error: File '{file_path}' not found.")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred when reading '{file_path}': {e}")
        exit(1)

# Function to load metametadata from a separate file
def load_metametadata(file_path):
    try:
        with open(file_path, "r") as meta_file:
            metametadata = json.load(meta_file)
        return metametadata
    except FileNotFoundError:
        print(f"Metametadata file '{file_path}' not found.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding metametadata JSON: {e}")
        return {}

def generate_schema(json_data, metametadata_file, oims_content_object):
    # Load metametadata from the separate file
    metametadata = load_metametadata(metametadata_file)

    # Use the default schema as a base
    json_schema = default_schema()

    # Find the item in "OIMS_content" that matches the specified "OIMS_content_object"
    selected_item = None
    for item in json_data["OIMS"]["OIMS_content"]:
        if item.get("OIMS_content_object") == oims_content_object:
            selected_item = item
            break

    if selected_item:
        # Access the "metadata" list from the nested structure
        metadata_list = selected_item.get("OIMS_content_object_properties", [{}])[0].get("metadata", [])

        # Initialize the metadata properties dictionary
        metadata_properties = {}

        # Initialize the required properties dictionary
        required_metadata = []
        # Iterate over each metadata object in the list
        for metadata_obj in metadata_list:
            # Extract the attribute name from the metadata object
            attribute_name = metadata_obj.get("attribute_name")

            if attribute_name:
                # Create a nested dictionary to store attribute metadata
                attribute_metadata = {}

                # Add individual metadata properties to the attribute_metadata dictionary

                attribute_metadata["description"] = metadata_obj.get("attribute_description")

                if metadata_obj.get("multiple"):
                    # Handle the case when "multiple" is true
                    attribute_metadata["type"] = "array"

                    if metadata_obj.get("data_type") == "compound_object":
                        if metadata_obj.get("data_type_class") == "compound":
                            attribute_metadata["items"] = {
                            "type": "object",
                            "properties": {}
                            }
                            if metadata_obj.get("attribute_value_elements"):
                                # Create properties for attribute value elements
                                for value_element in metadata_obj.get("attribute_value_elements"):
                                    attribute_metadata["items"]["properties"][value_element] = {"type": "string"}
                            else:
                                # Raise an error if it doesn't meet the dependency
                                raise ValueError(f"evaluating {attribute_name} of data_type_class: {metadata_obj.get('data_type_class')} expecting values for 'attribute_value_elements'")
                        else:
                            # Raise an error if it doesn't meet the dependency
                            raise ValueError(f"evaluating {attribute_name} Invalid combination of data_type: {metadata_obj.get('data_type')} and data_type_class: {metadata_obj.get('data_type_class')}")

                    elif metadata_obj.get("data_type") == "boolean":
                        attribute_metadata["items"] = {
                            "type": "boolean"
                        }
                    elif metadata_obj.get("data_type") == "integer" or metadata_obj.get("data_type") == "float":
                        attribute_metadata["items"] = {
                            "type": "number"
                        }
                    elif metadata_obj.get("controlled_vocabulary"):
                        attribute_metadata["items"] = {
                            "type": "string"
                        }
                    else :
                        attribute_metadata["items"] = {
                            "type": "string"
                        }

                else:
                    if metadata_obj.get("data_type") == "compound_object":
                        if metadata_obj.get("data_type_class") == "compound":
                            attribute_metadata["type"] = "object"
                            attribute_metadata["properties"] = {}
                            if metadata_obj.get("attribute_value_elements"):
                                # Create properties for attribute value elements
                                for value_element in metadata_obj.get("attribute_value_elements"):
                                    attribute_metadata["properties"][value_element] = {"type": "string"}
                            else:
                                # Raise an error if it doesn't meet the dependency
                                raise ValueError(f"evaluating {attribute_name} of data_type_class: {metadata_obj.get('data_type_class')} expecting values for 'attribute_value_elements'")

                        else:
                            # Raise an error if it doesn't meet the dependency
                            raise ValueError(f"Invalid combination of data_type: {metadata_obj.get('data_type')} and data_type_class: {metadata_obj.get('data_type_class')}")


                    elif metadata_obj.get("data_type") == "boolean":
                        attribute_metadata["type"] = "boolean"
                    elif metadata_obj.get("data_type") == "integer" or metadata_obj.get("data_type") == "float":
                        attribute_metadata["type"] = "number"
                    elif metadata_obj.get("controlled_vocabulary"):
                        attribute_metadata["type"] = "string"
                    else :
                        attribute_metadata["type"] = "string"

                if metadata_obj.get("controlled_vocabulary"):
                    # Create an "enum" property and populate it with vocabulary_element_name values
                    attribute_metadata["enum"] = [element.get("vocabulary_element_name") for element in metadata_obj.get("controlled_vocabulary", [])]

                if metadata_obj.get("requirement_level") == "required":
                    # Set the property as required in the metadata schema
                    required_metadata.append(attribute_name)
                # Add the attribute_metadata to metadata_properties
                metadata_properties[attribute_name] = attribute_metadata

        # Update the schema with the populated metadata properties
        json_schema["properties"]["OIMS"]["properties"]["OIMS_content"]["items"]["properties"]["OIMS_content_object_properties"]["items"]["properties"]["metadata"]["items"]["properties"] = metadata_properties
        json_schema["properties"]["OIMS"]["properties"]["OIMS_content"]["items"]["properties"]["OIMS_content_object_properties"]["items"]["properties"]["metadata"]["items"]["required"] = required_metadata

    # Return the generated schema
    return json_schema


def default_schema():
    json_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "<uri to the github repository of the schema>",
        "title": "<e.g. schema build on OIMS_basis.json>",
        "description": "<e.g. Basic structure of an OIMS compatible metadata file>",
        "type": "object",
        "properties": {
            "OIMS": {
                "type": "object",
                "properties": {
                    "\\": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "OIMS_header": {
                        "type": "object",
                        "properties": {
                            "mapping_info": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "mapper_tool_name": {
                                            "type": "string"
                                        }
                                    }
                                }
                            },
                            "metadata_schema": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "OIMS_content_object": {},
                                        "schema_properties": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "schema_name": {},
                                                    "schema_description": {},
                                                    "schema_type": {},
                                                    "schema_version": {},
                                                    "schema_url": {},
                                                    "OIMS_content_object": {}
                                                }
                                            }
                                        }
                                    }
                                }
                            },
                            "file_descriptors": {
                                "type": "object",
                                "properties": {
                                    "metadata_name": {},
                                    "meta_data_description": {},
                                    "metadata_version": {
                                        "type": "object",
                                        "properties": {
                                            "current_version": {},
                                            "metadata_version_status": {}
                                        }
                                    },
                                    "contact": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "contact_name": {},
                                                "contact_affiliation": {
                                                    "type": "object",
                                                    "properties": {
                                                        "contact_affiliation_name": {},
                                                        "contact_affiliation_acronym": {}
                                                    }
                                                },
                                                "contact_identifier": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "identifier_scheme": {},
                                                            "identifier": {}
                                                        }
                                                    }
                                                },
                                                "contact_email": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "string"
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "required": ["mapping_info", "metadata_schema", "file_descriptors"]
                    },
                    "OIMS_content": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "\\": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                },
                                "OIMS_content_object": {},
                                "OIMS_content_object_properties": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "metadata": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {},
                                                    "required":[],
                                                    "if": {
                                                        "properties": {}
                                                    },
                                                    "then": {
                                                        "properties": {}
                                                    },
                                                    "else": {
                                                        "if": {
                                                            "properties": {}
                                                        },
                                                        "then": {
                                                            "properties": {}
                                                        },
                                                        "else": {
                                                            "if": {
                                                                "properties": {}
                                                            },
                                                            "then": {
                                                                "properties": {}
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        },
                                        "required": ["metadata"]
                                    }
                                }
                            },
                            "required": ["OIMS_content_object_properties", "OIMS_content_object"]
                        }
                    }
                },
                "required": ["\\", "OIMS_header", "OIMS_content"]
            }
        },
        "required": ["OIMS"]
    }
    return json_schema

def validate_against_schema(data, schema, schema_name):
    """Validate data against a provided schema."""
    try:
        jsonschema.validate(data, schema)
        print(f"JSON data is valid against the {schema_name}.")
    except jsonschema.exceptions.ValidationError as e:
        print(f"JSON data is not valid against the {schema_name}: {e}")
        exit(1)
    except jsonschema.exceptions.SchemaError as e:
        print(f"Error in the schema itself: {e}")
        exit(1)


def main():
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Generate JSON schema from a JSON file")

    # Add an argument for the JSON file path
    parser.add_argument("--json_file_path", required=True, help="Path to the JSON file")
    parser.add_argument("--json_schema_file_path", required=False, help="Path to a higher level JSON schema file")
    parser.add_argument("--OIMS_metametadata_file_path", required=True, help="Path to the underlying metametadata file")
    parser.add_argument("--OIMS_content_object", required=True, help="OIMS")

    # Parse the command-line arguments
    args = parser.parse_args()

    json_data = load_json_file(args.json_file_path)
    json_schema = load_json_file(args.json_schema_file_path, default=default_schema()) if args.json_schema_file_path else default_schema()
    metametadata_file = args.OIMS_metametadata_file_path
    OIMS_content_object = args.OIMS_content_object

    # Derive the output file path
    output_file_path = os.path.splitext(args.json_file_path)[0] + ".schema.json"

    validate_against_schema(json_data, json_schema, "higher level schema")

    schema = generate_schema(json_data, metametadata_file, OIMS_content_object)

    # Write the generated schema to a JSON file
    try:
        with open(output_file_path, "w") as output_file:
            json.dump(schema, output_file, indent=2)
    except IOError as e:
        print(f"File writing error: {e}")
        exit(1)

    print(f"JSON schema has been written to '{output_file_path}'")

    validate_against_schema(json_data, schema, "generated schema")


# Generate the JSON schema
if __name__ == "__main__":
    main()

#*============================   End Of File   ================================