#*<%REGION File header%>
#*=============================================================================
#* File      : convert_dataverse_to_OIMS.py
#* Author    : Gideon Kruseman <g.kruseman@cgiar.org>
#* Version   : 1.0
#* Date      : 10/31/2023 7:12:01 PM
#* Changed   :
#* Changed by:
#* Remarks   :
"""
*! <%GTREE 0 tool documentation%>
This tool is part of the toolbox that has been designed to convert the foresight initiative dataset metadata
template in EXCEL into an OIMS-compatible json metadata file.

The way it has been designed is to be as generic as possible to allow other templates
that contain metadata to be converted to OIMS

This module parses the json metadata file of a dataset from a dataverse instance
*! <%GTREE 0.1 technical information%>
language: python
version: 1.0.0
data: October 2023
author: Gideon Kruseman <g.kruseman@cgiar.org>

*! <%GTREE 0.2 input%>
a dataverse metadata file in json format
"""
#*=============================================================================
#*<%/REGION File header%>
import re
import json
import argparse

def quote_properties(input_str):
    # Use regex to identify unquoted property names and add quotes
    cleaned_str = re.sub(r'(?<=\{|, )([a-zA-Z_][a-zA-Z_0-9]*)(?=\s*:)', r'"\1"', input_str)
    return cleaned_str

def main():
    parser = argparse.ArgumentParser(description="Clean up JSON file with unquoted properties.")
    parser.add_argument("--input_filepath", required=True, help="Path to the JSON file with dataverse metadata.")
    parser.add_argument("--do_clean", required=True, choices=['no', 'harvard_dataverse'], help="should the data be cleaned: valid values: no|harvard_dataverse")
    args = parser.parse_args()

    with open(args.input_filepath, 'r') as f:
        data = f.read()

    cleaned_data = quote_properties(data)

    # Optional: Load to verify that the cleaned JSON is valid
    json.loads(cleaned_data)

    # Overwrite the file with the cleaned JSON data
    with open(args.input, 'w') as f:
        f.write(cleaned_data)

    print(f"Cleaned JSON saved to {args.input}")

if __name__ == "__main__":
    main()

#*============================   End Of File   ================================