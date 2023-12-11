#<%REGION File header%>
#=============================================================================
# File      : OIMS_schema_consistency_test_simple.py
# Author    : Gideon Kruseman <g.kruseman@cgiar.org>
__version__ = "1.1.0"
# Date      : 10/23/2023 9:27:16 AM
# Changed   : 12/05/2023 3:27:27 PM
# Changed by: Gideon Kruseman <g.kruseman@cgiar.org>
# Remarks   :
"""
*! <%GTREE 0 documentation of OIMS consistency testing using JSON schema %>
*! <%GTREE 0.1 Introduction%>
Tool to validate OIMS-compatible metadata schemas against a JSON schema validation file.
The Open Ontology-Based Interoperable Information Asset Metadata Schema (OIMS) is a flexible
and extensible metadata schema designed to standardize and organize metadata for various information
assets like datasets, documents, models, and publications, making them more accessible, transparent,
and reusable.

The script serves as a tool for ensuring consistency and correctness of metadata schemas in the context
of OIMS. By validating these schemas against predefined JSON schemas, it helps maintain data integrity
and standardization in a system or project that utilizes these metadata schemas.

*! <%GTREE 0.1 technical information%>
language: python
version: 1.1.0
date: December 2023
author: Gideon Kruseman <g.kruseman@cgiar.org>

*! <%GTREE 0.2 input%>
OIMS-compatible metadata file or metametadata file that needs to be validated
The high-level OIMS structure JSON Schema validator
A specific JSON schema validator relevant for the OIMS-compatible metadata file or metametadata file

*! <%GTREE 0.3  command line parameters%>
*! <%GTREE 0.3.1 required command line paremers%>
metadata_file_to_test_path     :  Path to the OIMS metadata JSON file
OIMS_structure_schema_path     :  Path to the OIMS structure JSON schema file
                                      [optional, default is the schema of the foresight initiative]
schema_path                    :  Path to the underlying JSON schema file
schema_name                    :  Name of the schema for reporting purposes


*! <%GTREE 0.4  description of the script%>
This Python script is designed for validating OIMS-compatible metadata against specific JSON schemas.
It starts by importing necessary libraries for JSON processing, schema validation, argument parsing,
and PDF report generation. The script defines functions to load JSON files, validate JSON data against
a given schema, and generate a PDF report with validation results. The main part of the script parses
command-line arguments to obtain file paths for the OIMS metadata file, the OIMS structure schema, and a
specific JSON schema, along with a name for the schema for reporting purposes. It then loads the metadata
and schema files, validates the metadata against these schemas, and handles any errors or validation
failures. If errors are encountered, they are printed to the terminal and also compiled into a PDF report.
If no errors are found, a success message is displayed and included in the PDF report. This script ensures
the integrity and standardization of metadata in systems or projects utilizing OIMS schemas.

*! <%GTREE 0.4.1  initialization (GTREE 1)%>
Import Libraries (GTREE 1.1): The script begins by importing necessary libraries. json for handling JSON
data, jsonschema for validating JSON against a schema, argparse for parsing command-line arguments, and
reportlab modules for generating PDF reports.
Import standard url locations of underlying files

*! <%GTREE 0.4.2 Function Definitions (GTREE 2)%>
Loading local JSON Files (GTREE 2.1):
A function load_json_file is defined to read JSON data from a specified file path. It handles potential
errors like file not found or JSON parsing issues.

Loading JSON files from URL (GTREE 2.2):
A function load_json_url is defined to read JSON data from a specified url. It handles potential
errors like file not found or JSON parsing issues.

Validating JSON Data (GTREE 2.3):
The validate_against_schema function is responsible for checking if the JSON data conforms to a given schema.
It reports validation success or details any errors encountered.

Generating PDF Report (GTREE 2.4):
The generate_pdf_report function creates a PDF document. This document lists all messages (errors or success)
generated during the validation process.

*! <%GTREE 0.4.3 Main Function Definition (GTREE 3)%>
Parsing Command Line Arguments (GTREE 3.1):
The main function starts by setting up a parser for command-line arguments to receive file paths and schema
names.

Error Container (GTREE 3.2):
An empty list is created to store any errors encountered during the script execution.

Loading Metadata and Schemas (GTREE 3.3):
The script loads the OIMS metadata, the OIMS structure schema, and the specific JSON schema, recording any
errors in the process.

Validating Metadata Against Schemas (GTREE 3.4):
Provided there are no loading errors, it proceeds to validate the metadata against the loaded schemas.
Validation failures are added to the error list.

Error Handling and Report Generation (GTREE 3.5):
The script checks for errors. If found, they are printed and compiled into a PDF report. If no errors are
found, a success message is printed and included in the PDF report.

*! <%GTREE 0.4.4 Execution (GTREE 4)%>
Run Tests:
Finally, the script execution is triggered using the if __name__ == "__main__": guard.
This ensures the main function is called only when the script is executed directly, not when imported as
a module.

*! <%GTREE 0.99  notes%>
optimized for viewing in GTREE. GTREE can be obtained free of charge through:
https://www.medictcare.nl/gamstools/
Note that GTREE can require GAMS to run without problems.
GTREE is used for tagging sections of the code and create an easily manageable tree structure.

"""
#=============================================================================
#<%/REGION File header%>
#*! <%GTREE 1 initialization%>
#*! <%GTREE 1.1 import libraries%>
import json
import requests
import io
import jsonschema
import argparse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


#*! <%GTREE 1.2 define standard file locations in the Foresight Initiative GitHub Repository%>
oims_structure_url = 'https://raw.githubusercontent.com/ForesightInitiative/OIMS/main/BasicSchemas/OIMS_structure.schema.json'
logo_url = 'https://raw.githubusercontent.com/ForesightInitiative/OIMS/main/CGIAR%20Initiative%20-%20Foresight%20and%20Metrics-03.jpg'
logo_path = "foresight_logo.png"
#*! <%GTREE 1.3 boiler text for reporting purposes%>
boiler_text_report = "This report is generated by the OIMS schema validation tool. OIMS stands for Open Ontology-Based Interoperable Information Asset Metadata Schema. The Python script OIMS_schema_consistency_test_simple.py uses the JSON Schema approach to validate if metadata files are OIMS-compatible amnd meet the requirements of the underlying schema."

#*! <%GTREE 2 function definitions%>
#*! <%GTREE 2.1 function to load local json files%>

def load_json_file(file_path):
    """Load and return the JSON data from a file, handling potential errors."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file), None
    except FileNotFoundError:
        return None, f"File not found: {file_path}. Please check the file path."
    except json.JSONDecodeError as e:
        return None, f"Error parsing JSON file {file_path}: {e}"

#*! <%GTREE 2.2 function to load json files from GitHub%>
def load_json_github(url):
    response = requests.get(url)
    # Check if the request was successful
    if response.status_code == 200:
        return response.json(), None  # This will directly parse the JSON content
    else:
        return None, f"Failed to retrieve data from {url}"

#*! <%GTREE 2.3 function to validate a json file against a json schema%>
def validate_against_schema(data, schema, schema_name):
    """Validate data against a provided schema, returning status and message."""
    try:
        jsonschema.validate(data, schema)
        return True, "JSON data is valid against the {}.".format(schema_name)
    except jsonschema.exceptions.ValidationError as e:
        error_details = {
            'message': e.message,
            'error_path': list(e.path),
            'error_instance': e.instance,
            'schema_path': list(e.schema_path)
        }
        error_message = "JSON data is not valid against the {}: {}. Error details: {}".format(schema_name, e.message, error_details)
        return False, error_message
    except jsonschema.exceptions.SchemaError as e:
        return False, "Error in the schema itself: {}".format(e)


#*! <%GTREE 2.4 function to generate a pdf report with provided messages%>
def generate_pdf_report(messages, logo_url, boiler_text, filename="OIMS_validation_report.pdf", logo_path=logo_path):
    """Generate a PDF report with the provided messages."""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []

    """
    # Add the logo

    # download and add a logo
    try:
        logo_image = ImageReader(logo_url)
        logo = Image(logo_image, 2*inch, inch)  # Adjust size as needed
        story.append(logo)
    except Exception as e:
        logo_size = 50
        logo = Image(logo_path, 72*inch, inch)
        print(f"Failed to retrieve logo from {logo_url}: {e}")
    """

    # Add the report title
    story.append(Paragraph("OIMS Schema Validation Report", styles['Title']))

    # Add a spacer
    story.append(Spacer(1, 0.2*inch))

    # Boilerplate text
    styles = getSampleStyleSheet()
    boiler_paragraph = Paragraph(boiler_text, styles['Normal'])
    story.append(boiler_paragraph)

    # Add a spacer
    story.append(Spacer(1, 0.2*inch))

    # Add messages
    for message in messages:
        message_paragraph = Paragraph(message, styles['Normal'])
        story.append(message_paragraph)
        story.append(Spacer(1, 0.1*inch))

    # Add a spacer
    story.append(Spacer(1, 0.2*inch))

    # Add messages
    for message in messages:
        message_paragraph = Paragraph(message, styles['Normal'])
        story.append(message_paragraph)
        story.append(Spacer(1, 0.1*inch))

    # Build the PDF
    doc.build(story)

#*! <%GTREE 3 main definition%>
def main():
#*! <%GTREE 3.1 Check command line arguments for settings file path%>
    parser = argparse.ArgumentParser(description='Script to validate OIMS-compatible metadata schemas.')
    parser.add_argument('--metadata_file_to_test_path',
                        required=True,
                        help='Absolute or relative path to the OIMS metadata JSON file to be tested. Example: /path/to/metadata.json.')
    parser.add_argument('--OIMS_structure_schema_path',
                        default='GitHub_foresight_initiative_OIMS',
                        help='Path to the OIMS structure JSON schema file. default is the foresight initiative GitHub repo')
    parser.add_argument('--schema_path',
                        required=True,
                        help='Path to the underlying JSON schema file.')
    parser.add_argument('--schema_name',
                        required=True,
                        help='Name of the schema for reporting purposes.')

    args = parser.parse_args()

    #*! <%GTREE 3.2 create container list for errors%>
    errors = []

    #*! <%GTREE 3.3 load metadata and schemas%>
    #*! <%GTREE 3.3.1 load oims metadata file to be validated%>
    oims_metadata, err = load_json_file(args.metadata_file_to_test_path)
    if err: errors.append(err)

    #*! <%GTREE 3.3.2 load high-level OIMS structure JSON Schema validator file%>
    if args.OIMS_structure_schema_path == 'GitHub_foresight_initiative_OIMS':
        oims_structure_schema, err = load_json_github(oims_structure_url)
        if err: errors.append(err)

    else:
        oims_structure_schema, err = load_json_file(args.OIMS_structure_schema_path)
        if err: errors.append(err)

    #*! <%GTREE 3.3.3 load the specific JSON Schema validator file%>
    schema, err = load_json_file(args.schema_path)
    if err: errors.append(err)

#*! <%GTREE 3.4 validate metadata against schemas%>
    if not errors:
        valid, msg = validate_against_schema(oims_metadata, oims_structure_schema, "high-level OIMS structure schema")
        if not valid: errors.append(msg)

        valid, msg = validate_against_schema(oims_metadata, schema, args.schema_name)
        if not valid: errors.append(msg)

#*! <%GTREE 3.5 error handling%>
    if errors:
        print("\n".join(errors))
        generate_pdf_report(errors, logo_url, boiler_text_report)
    else:
        success_message = "All validations passed successfully."
        print("All validations passed successfully.")
        generate_pdf_report([success_message], logo_url, boiler_text_report)

#*! <%GTREE 4 run tests%>
if __name__ == "__main__":
    main()

#*============================   End Of File   ================================