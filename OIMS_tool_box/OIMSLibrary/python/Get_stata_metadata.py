#*<%REGION File header%>
#*=============================================================================
#* File      : Get_stata_metadata.py
#* Author    : Gideon Kruseman <g.kruseman@cgiar.org>
#* Version   : 1.0
#* Date      : 11/07/2023 7:12:01 PM
#* Changed   :
#* Changed by:
#* Remarks   :
"""
*! <%GTREE 0 tool documentation%>
This tool is part of the toolbox that has been designed to convert the foresight initiative dataset metadata
template in EXCEL into an OIMS-compatible json metadata file.

The way it has been designed is to be as generic as possible to allow other templates
that contain metadata to be converted to OIMS

This module does a number of steps.
1. It reads a file location and gets names of all DTA files fpound there.
2. it generates the technical metadata for each file.
3. each file is sent to an R script [get_stata_metadata.R] to extract the structural metadata
4. it then parses the json files created by get_stata_metadata.R   and creates the OIMS-compatible structural metadata file
*! <%GTREE 0.1 technical information%>
language: python
version: 1.0.0
data: November 2023
author: Gideon Kruseman <g.kruseman@cgiar.org>

*! <%GTREE 0.2 input%>
an excel sheet with metadata

*! <%GTREE 0.3  command line parameters%>
*! <%GTREE 0.3.1 required command line paremers%>


*! <%GTREE 0.4  description of the script%>
*_ Initialization:


*_ Functions:

"""
#*=============================================================================
#*<%/REGION File header%>
#*! <%GTREE 1 initialization%>
#*! <%GTREE 1.1 import libraries%>
import sys
import json
import argparse
import os
import subprocess

#*! <%GTREE 1.2 Check command line arguments for settings file path%>
#
parser = argparse.ArgumentParser(description='Script to process dta file metadata.')
parser.add_argument('--dta_folder', required=True, help='Path to the folder containing the dta files')
parser.add_argument('--path_to_output_folder', help='Path to the output folder ')
parser.add_argument('--path_to_get_stata_metadata_R', help='Path to R script get_stata_metadata.R ')

args = parser.parse_args()

r_script_path =  args.path_to_get_stata_metadata_R
#*! <%GTREE 2 define functions%>
#*! <%GTREE 2.1 call R script%>
"""
the R script Get_stata_metadata.R takes the following command line arguments
--path_to_dta_file       :       path to the dta file to extract metadata
--path_to_output_folder  :       path to the folder where the output file needs to go

"""
def call_Get_stata_metadata_R(path_to_dta_file,path_to_output_folder):
    """
    1. call statement:
    Rscript.exe  location/of/R_script/get_stata_metadata.R   --path_to_dta_file=path_to_dta_file  --path_to_output_folder=path_to_output_folder
    """
    r_call = [
        "Rscript.exe", r_script_path,
        f"--path_to_dta_file={path_to_dta_file}",
        f"--path_to_output_folder={path_to_output_folder}"
    ]
    subprocess.run(r_call)  # Execute the R script

    """
    2. read the json files that were created:
        a. <dta filename without extension>_structural_metadata.json
    """
    dta_file_base = os.path.splitext(os.path.basename(path_to_dta_file))[0]  # Removing extension from file name
    variable_attributes_file = os.path.join(path_to_output_folder, f"{dta_file_base}_structural_metadata.json")
    with open(variable_attributes_file, 'r') as file:
        variable_attributes = json.load(file)

    """
    3. and add to dictionary first the general information:
    """
    oims_content =   {
        "OIMS_content":[
           {
               "OIMS_Content_Object":"technical_metadata_datafile",
               "OIMS_Content_Object_Properties":
                   {
                       "Persistent_Entity_ID":[
                           {
                           }
                       ],
                       "entity_relationship":[
                           {
                               "Entity_Relationship_type":"parent_of",
                               "Entity_List":[
                                   {
                                       "Persistent_Entity_ID":[
                                          {
                                          }
                                       ]
                                   }
                               ]
                           }
                       ],
                       "Metadata":[
                           {
                               "data_format":"text",
                               "file_format":"dta",
                               "file_type":"data_file",
                               "data_file_structure":"tabular"
                           }
                       ]
                   }
           },
           {
               "OIMS_Content_Object":"structural_metadata_datafile",
               "OIMS_Content_Object_Properties":
                   {
                       "Persistent_Entity_ID":[
                           {
                               "Entity_label":"<variable_name>"
                           }
                       ],
                       "entity_relationship":[
                           {
                               "Entity_Relationship_type":"child_of",
                               "Entity_List":[
                                   {
                                       "Persistent_Entity_ID":[
                                          {
                                              "Entity_label":"<dta filename with extension>"
                                          }
                                       ]
                                   }
                               ]
                           }
                       ],
                       "Metadata":[]
                   }
           }

        ]
       }
    oims_content["OIMS_content"].append({
        "OIMS_Content_Object": "technical_metadata_datafile",
        "OIMS_Content_Object_Properties": {
            "Entity_label":f"{dta_file_base}.dta")
        }
    })


    """
       and then the metadata cointents at variable level is already available through the R-script.
        "OIMS_content":[
           {
               "OIMS_Content_Object":"technical_metadata_datafile",
               "OIMS_Content_Object_Properties":
                   {
                       "Persistent_Entity_ID":[
                           {
                           }
                       ],
                       "entity_relationship":[
                           {
                               "Entity_Relationship_type":"parent_of",
                               "Entity_List":[
                                   {
                                       "Persistent_Entity_ID":[
                                          {
                                              "Entity_label":"<variable_name>"
                                          }

    """
    return oims_content

#*! <%GTREE 3 run%>


#*============================   End Of File   ================================