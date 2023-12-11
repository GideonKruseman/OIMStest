#<%REGION File header%>
#=============================================================================
# File      : JSON_schema_validator_4_OIMS.py
# Author    : Gideon Kruseman <g.kruseman@cgiar.org>
__version__ = "1.1.0"
# Date      : 10/23/2023 9:27:16 AM
# Changed   : 12/05/2023 3:27:27 PM
# Changed by: Gideon Kruseman <g.kruseman@cgiar.org>
# Remarks   :
"""
*! <%GTREE 0 documentation of OIMS consistency testing using JSON schema %>
*! <%GTREE 0.1 Introduction%>

"""
#=============================================================================
#<%/REGION File header%>
#*! <%GTREE 1 initialization%>
#*! <%GTREE 1.1 import libraries%>
#*! <%GTREE 1.1.1 basics  library%>
import os
import urllib.parse

#*! <%GTREE 1.1.2 json schema library%>
import jsonschema

#*! <%GTREE 1.1.3 command line parser linrary%>
import argparse

#*! <%GTREE 1.1.4 read external sources library%>
import json
import io
import requests


#*! <%GTREE 1.1.5 libraries to enhance reporting%>
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

#*! <%GTREE 1.1.6 enhanced error handling%>
import logging

#*! <%GTREE 1.2 define standard file locations e.g. at JSON Schema %>
json_schema_url = 'C:\json_schema_2020_12\schema'
# 'https://json-schema.org/draft/2020-12/schema'

#*! <%GTREE 1.3 standard text for reporting purposes%>
report_contents_boiler_text = "report on issues with json schema under development or review"
report_contents_title = "JSON_Schema_validation_report.pdf"
report_file_name = "JSON_Schema_validation_report.pdf"

#*! <%GTREE 2 function definitions%>
#*! <%GTREE 2.1 function to load local json files%>

def load_json_file(file_path):
    """Load and return the JSON data from a file, handling potential errors."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file), None
    except FileNotFoundError as e:
        logging.error(f"File not found: {file_path}. Please check the file path.")
        return None, str(e)
    except json.JSONDecodeError as e:
        return None, f"Error parsing JSON file {file_path}: {e}"

#*! <%GTREE 2.2 function to load json files from GitHub%>
def load_json_url(url):
    try:
        response = requests.get(url, timeout=10)  # Set a reasonable timeout
        if response.status_code == 200:
            return response.json(), None
        else:
            logging.error(f"Failed to retrieve data from {url}. Status code: {response.status_code}")
            return None, f"Failed to retrieve data from {url}. Status code: {response.status_code}"
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP Error occurred while retrieving data from {url}: {e}")
        return None, str(e)
    except requests.exceptions.ConnectionError as e:
        logging.error(f"Connection Error occurred while retrieving data from {url}: {e}")
        return None, str(e)
    except requests.exceptions.Timeout as e:
        logging.error(f"Timeout occurred while retrieving data from {url}: {e}")
        return None, str(e)
    except requests.exceptions.RequestException as e:
        logging.error(f"General Request Exception occurred while retrieving data from {url}: {e}")
        return None, str(e)


#*! <%GTREE 2.3 function to validate a json file against a json schema%>
def validate_against_schema(data, schema, schema_name):
    """Validate data against a provided schema, returning status and message."""
    try:
        jsonschema.validate(data, schema)
        return True, "JSON data is valid against the {}.".format(schema_name)
    except jsonschema.exceptions.ValidationError as e:
        logging.error("Validation error occurred", exc_info=True)
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


#*! <%GTREE 2.4 function to va;lidate parts %>
def validate_schema_part(data, schema_part, path=''):
    """Validate a part of the schema."""
    try:
        jsonschema.validate(data, schema_part)
        logging.info(f"Schema part at '{path}' is valid.")
        return True, None
    except jsonschema.exceptions.ValidationError as e:
        logging.error(f"Validation error in schema part at '{path}': {e}")
        return False, str(e)

#*! <%GTREE 2.5 function to va;lidate parts %>
def traverse_and_validate(data, schema, path=''):
    """Recursively traverse and validate each part of the schema."""
    if isinstance(schema, dict):
        if 'properties' in schema:
            for key, value in schema['properties'].items():
                new_path = f"{path}/{key}" if path else key
                part_valid, error = validate_schema_part(data.get(key, {}), value, path=new_path)
                if not part_valid:
                    return False, error
                # If the property is an object, recurse into it
                if value.get('type') == 'object':
                    deeper_valid, deeper_error = traverse_and_validate(data.get(key, {}), value, path=new_path)
                    if not deeper_valid:
                        return False, deeper_error
        return True, None
    return False, "Invalid schema structure"

#*! <%GTREE 2.6 function to check locations%>
def check_location_type(location):
    """Check if the given location is a local file path or a URL."""
    # Check if it's a URL
    parsed = urllib.parse.urlparse(location)
    if parsed.scheme in ('http', 'https'):
        return "URL"

    # Check if it's a local file path
    if os.path.exists(location):
        return "Local file path"

    return "Unknown"

#*! <%GTREE 2.7 function to generate a pdf report with provided messages%>
def generate_pdf_report(messages, report_contents_title, boiler_text, filename):
    """Generate a PDF report with the provided messages."""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []

    # Add the report title
    styles = getSampleStyleSheet()
    story.append(Paragraph(report_contents_title, styles['Title']))

    # Add a spacer
    story.append(Spacer(1, 0.2*inch))

    # Boilerplate text
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
#*! <%GTREE 3.1.1 basic command line parsing%>
    parser = argparse.ArgumentParser(description='Script to validate OIMS-compatible metadata schemas.')
    parser.add_argument('--json_schema_file_to_test_path',
                        required=True,
                        help='Absolute or relative path to the JSON Schema file to be tested. Example: /path/to/validator.schema.json.')
    parser.add_argument('--debug_logging_mode',
                        default='w',
                        help='logging mode for debugging: w= write; a=append')

    args = parser.parse_args()

    #*! <%GTREE 3.1.2 test if deug_logging_mode is set to a or w else generate an error%>
    if not (args.debug_logging_mode=="a" or args.debug_logging_mode=="w"):
        args.debug_logging_mode = "w"


    #*! <%GTREE 3.2 configure logging%>
    logging.basicConfig(
        filename='app.log',
        filemode=args.debug_logging_mode,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    #*! <%GTREE 3.3 create container list for errors%>
    errors = []

    #*! <%GTREE 3.3 load metadata and schemas%>
    #*! <%GTREE 3.3.1 load json schema file to be tested and validated against JSON Schema version draft/2020-12/%>
    schema_to_validate, err = load_json_file(args.json_schema_file_to_test_path)
    if err: errors.append(err)

    #*! <%GTREE 3.3.2 load JSON Schema version draft/2020-12/%>
    if check_location_type(json_schema_url)=="URL":
        json_schema, err = load_json_url(json_schema_url)
        if err: errors.append(err)
    else:
        json_schema, err = load_json_file(json_schema_url)
        if err: errors.append(err)


#*! <%GTREE 3.4 validate schema against base json schemas%>
    if not errors:
        valid, msg = validate_against_schema(schema_to_validate, json_schema, "JSON Schema version draft/2020-12")
        if not valid: errors.append(msg)


#*! <%GTREE 3.5 validate schema step by step%>
    if errors:
        valid, msg = traverse_and_validate(schema_to_validate, json_schema)
        if not valid:
            errors.append(msg)

#*! <%GTREE 3.6 error handling%>
    if errors:
        print("\n".join(errors))
        generate_pdf_report(errors, report_contents_title, report_contents_boiler_text,  report_file_name)
    else:
        success_message = "All validations passed successfully."
        print("All validations passed successfully.")
        generate_pdf_report([success_message], report_contents_title, report_contents_boiler_text, report_file_name)

#*! <%GTREE 4 run tests%>
if __name__ == "__main__":
    main()

#*============================   End Of File   ================================        