#*<%REGION File header%>
#*=============================================================================
#* File      : get_stata_metadata.R
#* Author    : Gideon Kruseman <g.kruseman@cgiar.org>
#* Version   : 1.0.0
#* Date      : 10/4/2023 10:08:34 AM
#* Changed   :
#* Changed by:
#* Remarks   :
#! using the if(FALSE statement to emulate a multi-line comment)
if(FALSE) {
"""
*! <%GTREE 0 tool documentation%>
This tool is part of the toolbox that has been designed to convert the foresight initiative dataset metadata
into an OIMS-compatible json metadata file.

This component is for extracting stata metadata

It can be combined with data from templates and other sources.

*! <%GTREE 0.1 technical information%>
language: R
version: 1.0.0
data: October 2023
author: Gideon Kruseman <g.kruseman@cgiar.org>

*! <%GTREE 0.2 input%>

*! <%GTREE 0.3  command line parameters%>
*! <%GTREE 0.3.1 required command line paremers%>
--path_to_dta_file       :       path to the dta file to extract metadata
--path_to_output_file    :       path to the folder where the output file needs to go

*! <%GTREE 0.4  description of the script%>
*_ Initialization:

The script starts by initializing necessary libraries and checking command-line arguments for the main file path,
settings file path, and output file path. If the libraries are not yet installed they should be installed prior to running the R script.

"""
}
#! end of multi-line comment
#*=============================================================================
#*<%/REGION File header%>
#! <%GTREE 1 initialization%>
#! <%GTREE 1.1 get libraries%>
library('readstata13')
library(optparse)

#! <%GTREE 1.2 get command line arguments%>
option_list <- list(
  make_option(c("--path_to_dta_file"), type="character", default=NULL,
              help="path to the dta file to extract metadata", metavar="character"),
  make_option(c("--path_to_output_file"), type="character", default=NULL,
              help="path to output file", metavar="character")
)

# Parse the options
parser <- OptionParser(option_list=option_list)
args <- parse_args(parser)
#! <%GTREE 2 read data using ReadStata13 %>
df_rs13 <-as.data.frame(read.dta13(args$path_to_dta_file, generate.factors=TRUE))

#! <%GTREE 3 get factor info%>
factors <- get.label.tables(df_rs13)
factors <- factors[vapply(factors, Negate(is.null),NA)]
#! <%GTREE 3.1 store factor information in a dataframe%>
# Initialize an empty dataframe to store results
results_df <- data.frame(Variable = character(),
                         Code = integer(),
                         Label = character(),
                         stringsAsFactors = FALSE)

# Loop through each item in the factors list
for (varname in names(factors)) {

  # Extract labels and codes for the current variable
  labels <- names(factors[[varname]])
  codes <- as.integer(factors[[varname]])

  # Create a dataframe for the current variable
  temp_df <- data.frame(Variable = rep(varname, length(codes)),
                        Code = codes,
                        Label = labels,
                        stringsAsFactors = FALSE)

  # Append the dataframe to the results dataframe
  results_df <- rbind(results_df, temp_df)
}

# View the results
head(results_df)

#! <%GTREE 3.2 export to json%>
# Export to a json
# Extract file name without extension
file_name_sans_ext <- tools::file_path_sans_ext(basename(args$path_to_dta_file))

# Combine the file name with the new ending
new_file_name <- paste0(file_name_sans_ext, "_factor_labels.json")

# Combine with the output directory path
full_output_path <- file.path(args$path_to_output_file, new_file_name)

# Write to JSON
write_json(results_df, full_output_path)

#! <%GTREE 4 get other structural metadata at variable level%>

# Determine target length
target_length <- length(names(df_rs13))

# Filter attributes with the target length
matching_attributes <- sapply(attributes(df_rs13), function(attr) length(attr) == target_length)

# Extract the attributes that match the target length
filtered_attributes <- attributes(df_rs13)[names(matching_attributes[matching_attributes])]

# Convert the list of filtered attributes to a dataframe
variable_metadata <- as.data.frame(filtered_attributes, stringsAsFactors = FALSE)

# View the results
head(variable_metadata)

# Export to a json
# Extract file name without extension
file_name_sans_ext <- tools::file_path_sans_ext(basename(args$path_to_dta_file))

# Combine the file name with the new ending
new_file_name <- paste0(file_name_sans_ext, "_variable_attributes.json")

# Combine with the output directory path
full_output_path <- file.path(args$path_to_output_file, new_file_name)

# Write to JSON
write_json(variable_metadata, full_output_path)
#! <%GTREE 5 identify possible factors hidden as numbers%>

# Find variable names where the conditions are met
candidates <- which(grepl("=", attributes(df_rs13)$var.labels) & !is.na(attributes(df_rs13)$val.labels))

# Extract the labels for these variables
candidate_labels <- attributes(df_rs13)$var.labels[candidates]

# Extract the value labels for these variables
candidate_val_labels <- attributes(df_rs13)$val.labels[candidates]
#
extract_pairs <- function(label) {
  output <- data.frame(code = integer(0), description = character(0))

  # Check for unwanted pattern "text==integer"
  unwanted_pattern <- "\\w+==[0-9]+"
  if (grepl(unwanted_pattern, label)) {
    return(output) # Return an empty data frame
  }

  # Pattern for cases like "0= non adopter 1= adopter"
  pattern1 <- "([0-9A-Za-z]+)\\s?=\\s?([^0-9,=]+?)(?= [0-9A-Za-z]=|,|$)"
  matches1 <- regmatches(label, gregexpr(pattern1, label, perl = TRUE))
  print(paste("Matches for pattern1: ", matches1))  # Debug print

  # Only enter the loop if there's an actual match
  if (length(matches1[[1]]) > 0 && (matches1 != "character(0)" || matches1[[1]] != "character(0)")) {
    for (i in 1:length(matches1[[1]])) {
      code <- as.integer(gsub(pattern1, "\\1", matches1[[1]][i], perl = TRUE))
      desc <- gsub(pattern1, "\\2", matches1[[1]][i], perl = TRUE)
      output <- rbind(output, data.frame(code = code, description = desc))
    }
  }

  # If nothing captured so far, try the next pattern
  if (nrow(output) == 0) {
    # Pattern for cases like "Received=1 (2015)"
    pattern2 <- "([^0-9=]+)\\s?=\\s?([0-9]+)\\s?\\(.*\\)"
    matches2 <- regmatches(label, gregexpr(pattern2, label, perl = TRUE))
    print(paste("Matches for pattern2: ", matches2))  # Debug print
    # Only enter the loop if there's an actual match
    if (length(matches2[[1]]) > 0 && (matches2 != "character(0)" || matches2[[1]] != "character(0)")) {
      for (i in 1:length(matches2[[1]])) {
        code <- as.integer(gsub(pattern2, "\\2", matches2[[1]][i], perl = TRUE))
        desc <- gsub(pattern2, "\\1", matches2[[1]][i], perl = TRUE)
        output <- rbind(output, data.frame(code = code, description = desc))
      }
    }
  }

  # If still nothing captured, try the next pattern
  if (nrow(output) == 0) {
    # Pattern for cases like "yes=1"
    pattern3 <- "([a-zA-Z]+)\\s?=\\s?([0-9]+)\\b"
    matches3 <- regmatches(label, gregexpr(pattern3, label, perl = TRUE))
    print(paste("Matches for pattern3: ", matches3))  # Debug print
    # Only enter the loop if there's an actual match
    if (length(matches3[[1]]) > 0 && (matches3 != "character(0)" || matches3[[1]] != "character(0)")) {
      for (i in 1:length(matches3[[1]])) {
        code <- as.integer(gsub(pattern3, "\\2", matches3[[1]][i], perl = TRUE))
        desc <- gsub(pattern3, "\\1", matches3[[1]][i], perl = TRUE)
        output <- rbind(output, data.frame(code = code, description = desc))
      }
    }
  }

  # If still nothing captured, try the next pattern
  if (nrow(output) == 0) {
      # Pattern for cases like "adopted=1" or "1= adopted"
      pattern4 <- "(\\w+)\\s?=\\s?(\\d)|\\s?(\\d)\\s?=\\s?(\\w+)"
      matches4 <- regmatches(label, gregexpr(pattern4, label, perl = TRUE))
      print(paste("Matches for pattern4: ", matches4))  # Debug print

      # Only enter the loop if there's an actual match
      if (matches4 != "character(0)" && matches4[[1]] != "character(0)") {
          for (i in 1:length(matches4[[1]])) {
              desc <- gsub(pattern4, "\\1", matches4[[1]][i], perl = TRUE)
              code <- as.integer(gsub(pattern4, "\\2", matches4[[1]][i], perl = TRUE))

              # If the above didn't capture because the regex matched the second possibility
              if(desc == matches4[[1]][i] || is.na(code)) {
                  desc <- gsub(pattern4, "\\4", matches4[[1]][i], perl = TRUE)
                  code <- as.integer(gsub(pattern4, "\\3", matches4[[1]][i], perl = TRUE))
              }

              output <- rbind(output, data.frame(code = code, description = desc))
          }
      }
  }
  #return(output)
  return(data.frame(codes = output$code, descriptions = output$description))
}




# First, get all variable labels
all_labels <- attributes(df_rs13)$var.labels

parsed_results <- list()
combined_results <- NULL

for (label in candidate_labels) {
  print(paste("examining candidate label :",label))
  # Find which variable this label belongs to
  var_indices <- which(all_labels == label)
  for (var_index in var_indices) {
    varname <- colnames(df_rs13)[var_index]
    print(paste("Working on variable:", varname))

    # Use the extract_pairs function to get the codes and descriptions
    mypairs <- extract_pairs(label)

    # Print out what was extracted
    print(paste("extracted pairs: ",mypairs))

    data_values <- unique(df_rs13[[varname]])
    match_indices <- which(mypairs$codes %in% data_values)

    if (length(match_indices) > 0) {
      matched_descriptions <- mypairs$descriptions[match_indices]
      matched_codes <- mypairs$codes[match_indices]

      # Combine all results into a single dataframe
      df <- data.frame(variable = varname, code = matched_codes, description = matched_descriptions, stringsAsFactors = FALSE)
      combined_results <- rbind(combined_results, df)
    }
  }
}

# Save the combined results to a single file
# Export to a json
# Extract file name without extension
file_name_sans_ext <- tools::file_path_sans_ext(basename(args$path_to_dta_file))

# Combine the file name with the new ending
new_file_name <- paste0(file_name_sans_ext, "_parsed_results.csv".json")

# Combine with the output directory path
full_output_path <- file.path(args$path_to_output_file, new_file_name)

# Write to JSON
write_json(combined_results, full_output_path)


#*============================   End Of File   ================================