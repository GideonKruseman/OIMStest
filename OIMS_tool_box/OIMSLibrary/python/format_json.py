#*<%REGION File header%>
#*=============================================================================
#* File      : format_json.py
#* Author    : Gideon Kruseman <g.kruseman@cgiar.org>
#* Version   : 1.0
#* Date      : 10/23/2023 9:41:58 AM
#* Changed   :
#* Changed by:
#* Remarks   :
#
"""
*! <%GTREE 0 tool documentation%>
This python code is intended to read a json file and make sure all the indentation is correct and then write it again. it should take an argument --json_file_path=<path to json file json file>

*! <%GTREE 0.1 technical information%>
language: python
version: 1.0.0
data: October 2023
author: Gideon Kruseman <g.kruseman@cgiar.org>
"""
#
#*=============================================================================
#*<%/REGION File header%>
#*! <%GTREE 1 initialization%>
#*! <%GTREE 1.1 import libraries%>
import argparse
import json

#*! <%GTREE 2 define functions%>
#*! <%GTREE 2.1 format json functions%>
def format_json(json_file_path, indent=4):
    try:
        # Read the JSON file
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        # Write the formatted JSON back to the file
        with open(json_file_path, 'w') as file:
            json.dump(data, file, indent=indent)

        print(f"JSON file '{json_file_path}' has been formatted with an indentation of {indent} spaces.")
    except FileNotFoundError:
        print(f"File '{json_file_path}' not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {str(e)}")

#*! <%GTREE 3 run code%>

if __name__ == "__main__":
    #*! <%GTREE 3.1  read command line arguments%>
    parser = argparse.ArgumentParser(description="Format a JSON file with proper indentation.")
    parser.add_argument("--json_file_path", required=True, help="Path to the JSON file.")
    parser.add_argument("--indent", type=int, default=4, help="Number of spaces for indentation (default is 4).")

    args = parser.parse_args()

    #*! <%GTREE 3.2  for,at json%>
    format_json(args.json_file_path, args.indent)



#*============================   End Of File   ================================