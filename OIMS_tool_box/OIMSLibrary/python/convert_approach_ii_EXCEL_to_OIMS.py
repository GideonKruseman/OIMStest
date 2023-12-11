#*<%REGION File header%>
#*=============================================================================
#* File      : convert_approach_ii_EXCEL_to_OIMS.py
#* Author    : Gideon Kruseman <g.kruseman@cgiar.org>
#* Version   : 1.0
#* Date      : 11/07/2023 7:12:01 PM
#* Changed   :
#* Changed by:
#* Remarks   :
"""
*! <%GTREE 0 tool documentation%>
This tool is part of the toolbox that has been designed to convert the secong approach metadata
templates in EXCEL into an OIMS-compatible json metadata file.

The way it has been designed is to be as generic as possible to allow incorporation into workflows using alternate templates
that contain metadata to be converted to OIMS

This module parses the an excel file containing metadata in two separate sheets one containing the header information. The  second the content information
*! <%GTREE 0.1 technical information%>
language: python
version: 1.0.0
data: November 2023
author: Gideon Kruseman <g.kruseman@cgiar.org>

*! <%GTREE 0.2 input%>
an excel sheet with metadata

*! <%GTREE 0.3  command line parameters%>
*! <%GTREE 0.3.1 required command line paremers%>

"""
#*=============================================================================
#*<%/REGION File header%>
#*! <%GTREE 1 initialization%>
#*! <%GTREE 1.1 import libraries%>
import argparse
import pandas as pd
import json

#*! <%GTREE 1.2 Check command line arguments %>
# Parse command-line arguments
parser = argparse.ArgumentParser(description='Convert Excel to JSON for OIMS.')
parser.add_argument('--path_to_excel_file', type=str, required=True, help='Path to the input Excel file')
parser.add_argument('--path_to_json_file', type=str, required=True, help='Path to the output JSON file')
parser.add_argument('--OIMS_header_info_sheetname', type=str, required=True, help='The sheet name for OIMS header information')
parser.add_argument('--OIMS_content_info_sheetname', type=str, required=True, help='The sheet name for OIMS content information')
args = parser.parse_args()


#*! <%GTREE 2 define functions%>
#*! <%GTREE 2.1 get nested dictionary%>

def get_nested_dict(keys, value, compound=False):
    """ Create a nested dictionary from a list of keys and a value """
    if compound:
        # If the key represents a compound object, it should not overwrite but append to the list
        return_value = [value] if value else []
    else:
        return_value = value

    if keys:
        # Create a nested dictionary using recursion
        return {keys[0]: get_nested_dict(keys[1:], return_value)}
    else:
        return return_value

#*! <%GTREE 2.2 put information from sheet in dictionary%>
def excel_sheet_to_dict(sheet):
    data = {}
    for _, row in sheet.iterrows():
        # Retrieve keys only if 'parent_property' is not null, else use an empty list
        keys = str(row['parent_property']).split('.') if pd.notnull(row['parent_property']) else []
        compound = row.get('compound_object', False) == 'TRUE'
        multiple = row.get('multiple', 'FALSE')  # assuming default is 'FALSE' if not provided

        # If 'multiple' is 'local', we will split 'value' by '|' and convert it to a list
        if multiple == 'local' and pd.notnull(row['value']):
            value = row['value'].split('|')
        else:
            value = row['value'] if pd.notnull(row['value']) else None

        # Start at the root of the data dictionary and build the structure
        d = data
        for key in keys:
            if key not in d:
                d[key] = {}
            elif not isinstance(d[key], dict):  # Conflict if not a dictionary
                raise ValueError(f"Conflict at key '{key}'. Expected a dictionary but found {type(d[key]).__name__}.")
            d = d[key]  # Move to the next level

        # If there's a property, use it; otherwise, use the last key for assignment
        property_key = row['property'] if pd.notnull(row['property']) else keys[-1] if keys else None

        # If compound and no property key, create a nested structure or append to it
        if compound and property_key is None:
            nested_key = keys[-1] if keys else 'items'
            if nested_key not in d:
                d[nested_key] = []
            if isinstance(value, list):
                d[nested_key].extend(value)
            else:
                d[nested_key].append(value or {})
        elif property_key:  # Regular property assignment
            if property_key in d and isinstance(d[property_key], dict):
                raise ValueError(f"Cannot assign a value to key '{property_key}' because it is already a dictionary.")
            d[property_key] = value

    return data
    
#*! <%GTREE 2.3 remove nulls%>
def remove_none_values(d):
    if isinstance(d, dict):
        return {k: remove_none_values(v) for k, v in d.items() if v is not None and remove_none_values(v) != {}}
    elif isinstance(d, list):
        return [remove_none_values(v) for v in d if v is not None and remove_none_values(v) != []]
    else:
        return d


#*! <%GTREE 2.4 main process converting excel template to a json file%>
def excel_to_json(excel_path, json_path, header_sheet_name, content_sheet_name):
    # Read the sheets from the Excel file
    header_df = pd.read_excel(excel_path, sheet_name=header_sheet_name)
    content_df = pd.read_excel(excel_path, sheet_name=content_sheet_name)

    # Convert sheets to dictionaries
    header_data = excel_sheet_to_dict(header_df)
    content_data = excel_sheet_to_dict(content_df)

    # Now, clean the dictionary by removing all keys with None values
    cleaned_header_data = remove_none_values(header_data)
    cleaned_content_data = remove_none_values(content_data)

    # Function to safely extract nested data
    def safe_extract(data, key1, key2):
        return data.get(key1, {}).get(key2, data)

    # Extract "OIMS_header" and "OIMS_content" from the cleaned data if they exist, else keep the cleaned data
    final_header = safe_extract(cleaned_header_data, "OIMS", "OIMS_header")
    final_content = safe_extract(cleaned_content_data, "OIMS", "OIMS_content")

    # Combine header and content into the final JSON structure
    json_data = {
        "OIMS": {
            "OIMS_header": final_header,
            "OIMS_content": [final_content] if isinstance(final_content, dict) else final_content
        }
    }

    # Save to JSON
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)

#*! <%GTREE 3 Call the function with the provided command line arguments%>
#
#*! <%GTREE 3 run the process%>
excel_to_json(args.path_to_excel_file, args.path_to_json_file, args.OIMS_header_info_sheetname, args.OIMS_content_info_sheetname)

#*============================   End Of File   ================================