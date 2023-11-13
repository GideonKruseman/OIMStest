#<%REGION File header%>
#=============================================================================
# File      : OIMS_snake_case_converter.py
# Author    : Gideon Kruseman <g.kruseman@cgiar.org>
__version__ = "1.0.0"
# Date      : 8/22/2023 9:27:16 AM
# Changed   : 8/22/2023 9:27:27 AM
# Changed by: Gideon Kruseman <g.kruseman@cgiar.org>
# Remarks   :
"""
*! <%GTREE 0 documentation of case converter%>
*! <%GTREE 0.1 Introduction%>
Tool to convert OIMS metadata file to to snake case
"""
#=============================================================================
#<%/REGION File header%>
#*! <%GTREE 1 initialization%>
#*! <%GTREE 1.1 import libraries%>
import json
import re
import argparse
#*! <%GTREE 1.2 Check command line arguments for settings file path%>
#
parser = argparse.ArgumentParser(description='Script to process data.')
parser.add_argument('--old_file_path', required=True, help='Path to the file where attributes need to be converted to snake-case')
parser.add_argument('--new_file_path', help='Path to the converted file')
parser.add_argument('--conversion_dict_path', default='conversion_dict.json', help='Path to conversion dictionary')

args = parser.parse_args()

# Check if new_file_path is provided, otherwise set it to old_file_path
if args.new_file_path is None:
    args.new_file_path = args.old_file_path

old_file_path = args.old_file_path
new_file_path = args.new_file_path
conversion_dict_path = args.conversion_dict_path

#*! <%GTREE 2 functions%>

def to_snake_case(s):
    """
    Convert a CamelCase string to snake_case while preserving OIMS intact.
    """
    if "OIMS" in s:
        s = s.replace("OIMS", "_OIMS_")  # Add underscores to isolate OIMS

    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    snake_cased_string = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    snake_cased_string = snake_cased_string.replace('__', '_')  # Remove any double underscores

    if "_oims_" in snake_cased_string:
        snake_cased_string = snake_cased_string.replace("_oims_", "OIMS")  # Correct the case for OIMS

    return snake_cased_string

def standardize_oims_properties(data):
    """
    Standardize the structure of OIMS_content_object_properties
    """
    if not isinstance(data, list):
        return [{"metadata": [data]}]

    for item in data:
        if "persistent_entity_id" in item and "entity_relationship" in item and "metadata" in item:
            continue
        elif "persistent_entity_id" in item and "metadata" in item:
            continue
        elif "metadata" in item:
            continue
        else:
            return [{"metadata": data}]
    return data

def convert_keys_recursive(data):
    """
    Recursively convert dictionary keys and build a conversion dictionary.
    Also, build a conversion dictionary and standardize OIMS_content_object_properties.
    """
    conversion_dict = {}

    if isinstance(data, list):
        new_list = []
        for item in data:
            new_item, item_conversion_dict = convert_keys_recursive(item)
            new_list.append(new_item)
            conversion_dict.update(item_conversion_dict)
        return new_list, conversion_dict

    if isinstance(data, dict):
        new_data = {}
        for k, v in data.items():
            new_key = to_snake_case(k)
            if new_key != k:
                conversion_dict[k] = {"new_item": new_key, "conversion_type": "CamelCase to snake_case"}

            # If the new key is "attribute_name", convert its value to snake_case
            if new_key == "attribute_name":
                v = to_snake_case(v)

            # If the new key is "attribute_value_elements", convert each value in the list to snake_case
            if new_key == "attribute_value_elements" and isinstance(v, list):
                v = [to_snake_case(item) for item in v]

            if new_key == "OIMS_content_object_properties":
                v = standardize_oims_properties(v)

            new_data[new_key], item_conversion_dict = convert_keys_recursive(v)
            conversion_dict.update(item_conversion_dict)
        return new_data, conversion_dict
    return data, conversion_dict

def check_consistency(data, conversion_dict):
    """
    Check consistency in the data based on the conversion dictionary.
    Log any discrepancies.
    """
    inconsistencies = []

    if isinstance(data, list):
        for item in data:
            inconsistencies.extend(check_consistency(item, conversion_dict))
            
    elif isinstance(data, dict):
        for key, value in data.items():
            if key in conversion_dict:
                converted_key = conversion_dict[key]['new_item']
                if converted_key != key:
                    inconsistencies.append(f"Inconsistency: {key} should be {converted_key}")

            # Continue the check on nested items
            inconsistencies.extend(check_consistency(value, conversion_dict))

    return inconsistencies

# Reading the JSON file
with open(old_file_path, 'r') as f:
    data = json.load(f)

converted_data, conversion_dict = convert_keys_recursive(data)

inconsistencies = check_consistency(converted_data, conversion_dict)

# Logging inconsistencies
for msg in inconsistencies:
    print(msg)

# Saving the modified data back to the JSON file
with open(new_file_path, 'w') as f:
    json.dump(converted_data, f, indent=4)

# If you want to save the conversion dictionary:
with open(conversion_dict_path, 'w') as f:
    json.dump(conversion_dict, f, indent=4)


#============================   End Of File   ================================