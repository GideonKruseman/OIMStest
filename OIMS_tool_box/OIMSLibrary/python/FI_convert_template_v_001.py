#*<%REGION File header%>
#*=============================================================================
#* File      : FI_convert_template_v_001.py
#* Author    : Gideon Kruseman <g.kruseman@cgiar.org>
#* Version   : 1.0
#* Date      : 10/25/2023 9:41:58 AM
#* Changed   :
#* Changed by:
#* Remarks   :
#
"""
*! <%GTREE 0 tool documentation%>
This tool is part of the toolbox that has been designed to convert the foresight initiative dataset metadata
template in EXCEL into an OIMS-compatible json metadata file.

The way it has been designed is to be as generic as possible to allow other templates
that contain metadata to be converted to OIMS

This component reads the filled in EXCEL template and converts it to a JSON file for further use.


*! <%GTREE 0.1 technical information%>
language: python
version: 1.0.0
data: October 2023
author: Gideon Kruseman <g.kruseman@cgiar.org>

*! <%GTREE 0.2 input%>
The filled in EXCEL template irrespective of the version or if it is for data and metrics or models and tools

a settings file that contains the information on the high level structure of the template with the following columns:
sheet_name        :   identifier of the sheet to read
format            :   indication of the orientation of the tabular data. valid values: vars_in_rows, vars_in_cols
skip_col        :   columns to skip when reading the data
skip_row        :   rows to skip when reading the data
data            :   range of the data
header_row  :   integer or empty if there is no header row

*! <%GTREE 0.3  command line parameters%>
*! <%GTREE 0.3.1 required command line paremers%>
--main_file_path      : Path to the main file the filled in EXCEL template

*! <%GTREE 0.3.2 optional command line parameters%>
--settings_file_pat   : Path to the settings file if settings not included in the template file already
--path_to_output_file : Path to the output file in json format

*! <%GTREE 0.4  description of the script%>
*_ Initialization:

The script starts by initializing necessary libraries and checking command-line arguments for the main file path,
settings file path, and output file path.

*_ Functions:

Defines helper functions to convert Excel column names to index, get the range from the settings, and convert a DataFrame
to a dictionary while removing NaNs.

*_ Settings Retrieval:

Attempts to read a settings sheet from the main workbook. If not found, it checks if an external settings file is provided.
The settings sheet provides details about each sheet in the main workbook, like the data format, columns/rows to skip, and
range of the data.

*_ Reading Metadata:

For each sheet mentioned in the settings, the script reads the sheet data based on the provided settings, removes unnecessary
rows and columns, and stores the processed data.

*_ Logging:

A detailed summary of each processed sheet, including its shape, column names, basic statistics, and the first few rows, is
written to a log file.

*_ Data Transformation:

For sheets where the data format is 'vars_in_rows', the script further transforms the data, converting rows to key-value pairs.

*_ Remove NaNs:

For each sheet's data, the script removes NaN values to ensure clean data for the final output.

*_ Output:

The processed and cleaned data for all sheets is written to a JSON file as the final output.
*! <%GTREE 0.99  notes%>

"""
#
#*=============================================================================
#*<%/REGION File header%>
#*! <%GTREE 1 initialization%>
#*! <%GTREE 1.1 import libraries%>
import pandas as pd
import sys
import json
import argparse
import os

#*! <%GTREE 1.2 Check command line arguments for settings file path%>
#
parser = argparse.ArgumentParser(description='Script to process Excel data.')
parser.add_argument('--main_file_path', required=True, help='Path to the main file')
parser.add_argument('--settings_file_path', help='Path to the settings file')
parser.add_argument('--path_to_output_file', help='Path to the output file in json format ')

args = parser.parse_args()

main_file_path = args.main_file_path
settings_file_path = args.settings_file_path

if not args.path_to_output_file:
    path_to_output_file = os.path.splitext(main_file_path)[0] + ".output.json"
else:
    path_to_output_file = args.path_to_output_file



#*! <%GTREE 2 define functions%>
def excel_column_to_index(column):
    index = 0
    for char in column:
        index = index * 26 + (ord(char.upper()) - ord('A') + 1)
    return index - 1

def get_range(value, data_format, max_value=10000):
    """Convert a range string to a list of values based on data format."""
    is_col = True if data_format == 'vars_in_rows' else False

    if ":" in value:
        start, end = value.split(":")
        if is_col:  # If the values are Excel-style column labels
            start = excel_column_to_index(start)
            end = max_value if end == 'end' else excel_column_to_index(end)
        else:
            start = int(start) - 1
            end = max_value if end == 'end' else int(end)
        return list(range(start, end))
    else:
        if is_col:  # This part is adjusted to handle single Excel column labels
            return [excel_column_to_index(value)]
        else:
            return [int(value) - 1]

def dataframe_to_dict_without_nans(df):
    return [
        {key: value for key, value in row.items() if pd.notna(value)}
        for _, row in df.iterrows()
    ]


#*! <%GTREE 3 get settings%>
# Try reading the settings sheet from the main workbook
try:
    settings_df = pd.read_excel(main_file_path, sheet_name="settings")
except Exception as e:
    # If it fails, check if an external settings file is provided
    if settings_file_path:
        try:
            settings_df = pd.read_excel(settings_file_path, sheet_name="settings")
        except Exception as e:
            print(f"Error reading the settings sheet from the external file: {e}")
            sys.exit()
    else:
        print("The main workbook doesn't contain a 'settings' sheet, and no external settings file was provided.")
        sys.exit()

#*! <%GTREE 4 read the metadata from the template%>
# Read other sheets based on the settings
all_data = {}
for _, row in settings_df.iterrows():
    sheet = row['sheet_name']
    skip_col = str(row['skip_col'])
    skip_row = str(row['skip_row'])
    data_format = row['format']
    header_row = row['header_row']

    data_range = get_range(row['data'], row['format'])

    # Read the entire sheet
    # Read the sheet using the specified header row
    try:
        if not pd.isna(header_row):
            full_df = pd.read_excel(main_file_path, sheet_name=sheet, header=int(header_row)-1)
        else:
            full_df = pd.read_excel(main_file_path, sheet_name=sheet, header=None)
        print(f"full_df.shape of sheet {sheet}:")
        print(full_df.shape)
    except Exception as e:
        print(f"Error reading sheet {sheet}: {e}")
        continue

    if full_df.shape[0] == 0:
       print(f"Sheet {sheet} is empty. Skipping...")
       continue

    # Drop ignored rows
    if not pd.isna(skip_row):
        ignore_rows = [int(float(x)) - 1 for x in skip_row.split(',') if x.strip().lower() != "nan"]  # Assuming 1-indexed rows
        full_df = full_df.drop(ignore_rows).reset_index(drop=True)

    # Drop ignored columns
    if not pd.isna(skip_col):
        ignore_cols = [excel_column_to_index(x.strip()) for x in skip_col.split(',') if x.strip().lower() != "nan"]
        for idx, col in enumerate(ignore_cols):
            if col >= len(full_df.columns):
                print(f"Skipping invalid column index: {col} from input: {skip_col.split(',')[idx]}")
                ignore_cols[idx] = -1  # set to an invalid value
        col_names_to_drop = [full_df.columns[i] for i in ignore_cols if i != -1]  # filter out the invalid value
        full_df = full_df.drop(columns=col_names_to_drop)

    # Filter out invalid column indices:
    data_range = [idx for idx in data_range if idx < full_df.shape[1]]

    if not data_range:
        print(f"No valid column indices for sheet {sheet}. Skipping...")
        continue

    if data_format == 'vars_in_cols':
        valid_columns = full_df.columns.dropna().tolist()
        data_df = full_df[valid_columns]

    elif data_format == 'vars_in_rows':
        print("Shape of full_df:", full_df.shape)
        print("Head of full_df:", full_df.head())
        valid_rows_mask = ~full_df[full_df.columns[1]].isna()
        print("valid_rows_mask: ", valid_rows_mask)
        print("Shape of valid_rows_mask:", valid_rows_mask.shape)
        print("Head of valid_rows_mask:", valid_rows_mask.head())
        data_df = full_df[valid_rows_mask]

    all_data[sheet] = data_df

#*! <%GTREE 5 write log%>

# Define the log file path
log_file_path = "summary.log"

# Open the log file for writing
with open(log_file_path, 'w') as log_file:

    # Redirect standard output to log file
    original_stdout = sys.stdout  # Store the original standard output
    sys.stdout = log_file

    # Now print the summaries (these will go to the log file instead of terminal)
    for sheet_name, df in all_data.items():
        print(f"Sheet: {sheet_name}")
        print('- . ' * 10, '\n')  # Separator line for better readability
        print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        print(f"Columns: {', '.join(map(str, df.columns))}")

        print('- . ' * 10)  # Separator line for better readability
        # Display basic statistics for numerical columns
        print("Basic Statistics:")
        print(df.describe())

        print('- . ' * 10)  # Separator line for better readability
        # Display first few rows
        print("First 5 rows:")
        print(df.head())

        print('-' * 80, '\n')  # Separator line for better readability

    # Restore standard output back to terminal
    sys.stdout = original_stdout

#*! <%GTREE 6 Transform data for sheets where data_format == 'vars_in_rows' %>

for sheet, df in all_data.items():
    print(f"Checking sheet: {sheet}")

    if isinstance(df, pd.DataFrame):
        print(f"Sheet {sheet} is a DataFrame.")

        if 0 in df.columns:
            print(f"Sheet {sheet} has a column named '0'.")

            transformed_data = {}
            for _, row in df.iterrows():
                key = row[0]
                values = row.iloc[1:].dropna().tolist()
                transformed_data[key] = values

            print(f"Transformed data for sheet {sheet}:")  # Debug statement
            print(transformed_data)  # Debug statement

            all_data[sheet] = transformed_data
        else:
            print(f"Sheet {sheet} does not have a column named '0'. Column names are: {df.columns}")
    else:
        print(f"Sheet {sheet} is not a DataFrame.")


#*! <%GTREE 7 remove the instances with no 'nans'' %>

for key, value in all_data.items():
    if isinstance(value, pd.DataFrame):
        all_data[key] = dataframe_to_dict_without_nans(value)

#*! <%GTREE 8 write json output file%>
# Convert all DataFrame objects inside the dictionary to records

print("All Data before writing to JSON:")

for sheet, data in all_data.items():
    if isinstance(data, list):  # If data is a list
        print(f"{sheet} (data is a list):", data[:2])  # Print the first two items
    elif isinstance(data, dict):  # If data is a dictionary
        first_two_keys = list(data.keys())[:2]
        print(f"{sheet} (data is a dictionary):", {key: data[key] for key in first_two_keys})  # Print the data for the first two keys


with open(path_to_output_file, 'w') as outfile:
    json.dump(all_data, outfile, indent=4)
#*============================   End Of File   ================================