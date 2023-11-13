#*<%REGION File header%>
#*=============================================================================
#* File      : get_stata_metadata.R
#* Author    : Gideon Kruseman <g.kruseman@cgiar.org>
#* Version   : 1.0.0
#* Date      : 11/13/2023 10:08:34 AM
#* Changed   :
#* Changed by:
#* Remarks   :
#! using the if(FALSE statement to emulate a multi-line comment)
#if(FALSE) {
#"""
#*! <%GTREE 0 tool documentation%>
#This tool is part of the toolbox that has been designed to convert the foresight initiative dataset metadata
#into an OIMS-compatible json metadata file.
#
#This component is for extracting stata metadata
#
#It can be combined with data from templates and other sources.
#
#*! <%GTREE 0.1 technical information%>
#language: R
#version: 1.0.0
#data: October 2023
#author: Gideon Kruseman <g.kruseman@cgiar.org>
#
#*! <%GTREE 0.2 input%>
#
#*! <%GTREE 0.3  command line parameters%>
#*! <%GTREE 0.3.1 required command line paremers%>
#--path_to_dta_file       :       path to the dta file to extract metadata
#--path_to_output_folder  :       path to the folder where the output file needs to go
#
#*! <%GTREE 0.4  description of the script%>
#*_ Initialization:
#
#The script starts by initializing necessary libraries and checking command-line arguments for the main file path,
#settings file path, and output file path. If the libraries are not yet installed they should be installed prior to running the R script.
#
#"""
#}
#! end of multi-line comment
#*=============================================================================
#*<%/REGION File header%>
#! <%GTREE 1 initialization%>
#! <%GTREE 1.1 get libraries%>
library('readstata13')
library('optparse')
library('jsonlite')

#! <%GTREE 1.2 get command line arguments%>
option_list <- list(
  make_option(c("--path_to_dta_file"), type="character", default=NULL,
              help="path to the dta file to extract metadata", metavar="character"),
  make_option(c("--path_to_output_folder"), type="character", default=NULL,
              help="path to output folder", metavar="character")
)

# Parse the options
parser <- OptionParser(option_list=option_list)
args <- parse_args(parser)

#! <%GTREE 1.3 append note function%>
append_note <- function(var_info, note) {
  if (!is.null(var_info$notes) && nzchar(var_info$notes)) {
    var_info$notes <- paste(var_info$notes, note, sep = "; ")
  } else {
    var_info$notes <- note
  }
  return(var_info)
}
#! <%GTREE 2 read data using ReadStata13 %>
df_rs13 <-as.data.frame(read.dta13(args$path_to_dta_file, generate.factors=TRUE))

#! <%GTREE 3 get factor info%>
factors <- get.label.tables(df_rs13)
factors <- factors[vapply(factors, Negate(is.null),NA)]
#! <%GTREE 3.1 store factor information in a dataframe%>
# Initialize an empty list to store results
results_list <- list()

# Loop through each item in the factors list
# Loop through each item in the factors list
for (varname in names(factors)) {

  # Extract labels and codes for the current variable
  labels <- names(factors[[varname]])
  codes <- as.integer(factors[[varname]])

  # Create a controlled vocabulary list for the current variable
  cv_entries <- lapply(seq_along(codes), function(i) {
    list(
      controlled_vocabulary_term_id = codes[i],
      controlled_vocabulary_term_description = labels[i]
    )
  })

  # Add this list to the results list with the variable name as the key
  results_list[[varname]] <- list(
    variable_name = varname,
    controlled_vocabulary = cv_entries
  )
}

#! <%GTREE 4 get other structural metadata at variable level%>
# Determine target length
target_length <- length(names(df_rs13))

# Filter attributes with the target length
matching_attributes <- sapply(attributes(df_rs13), function(attr) length(attr) == target_length)

# Extract the attributes that match the target length
filtered_attributes <- attributes(df_rs13)[names(matching_attributes[matching_attributes])]

# Convert the list of filtered attributes to a dataframe
variable_metadata <- as.data.frame(filtered_attributes, stringsAsFactors = FALSE)

# Rename the attributes in the dataframe
names(variable_metadata) <- c("variable_name", "variable_format", "variable_length", "variable_label", "variable_description")

# Convert the dataframe to a list to prepare for JSON conversion
variable_metadata_list <- split(variable_metadata, seq(nrow(variable_metadata)))



# Initialize an empty list to hold the combined information
combined_info_list <- list()

# Loop over the variable names
for (index in names(variable_metadata_list)) {
  # Retrieve the variable name from the metadata
  var_name_in_metadata <- variable_metadata_list[[index]]$variable_name
  # Retrieve the row as a list
  var_metadata <- variable_metadata_list[[index]]
  # Find the controlled vocabulary list by matching the variable_name

  controlled_vocab <- NULL
  if (!is.null(results_list[[var_name_in_metadata]]$controlled_vocabulary)) {
    controlled_vocab <- results_list[[var_name_in_metadata]]$controlled_vocabulary
  }

  # Create a list that includes both the controlled vocabulary and the variable metadata
  # Initialize an empty list for the combined information
  combined_info <- list(
    variable_name = var_metadata$variable_name,
    variable_format = var_metadata$variable_format,
    variable_length = var_metadata$variable_length,
    variable_label = var_metadata$variable_label,
    variable_description = var_metadata$variable_description
  )

  # Only add controlled_vocabulary if it's not NULL
  if (!is.null(controlled_vocab)) {
    combined_info$controlled_vocabulary <- controlled_vocab
  }

  # Add the combined info to the combined_info_list
  combined_info_list[[index]] <- combined_info
}





# View the results
#head(variable_metadata)
if (FALSE) {
#! 15 lines of code disabled
# Export to a json
# Extract file name without extension
file_name_sans_ext <- tools::file_path_sans_ext(basename(args$path_to_dta_file))

# Combine the file name with the new ending
new_file_name <- paste0(file_name_sans_ext, "_variable_attributes.json")

# Combine with the output directory path
full_output_path <- file.path(args$path_to_output_folder, new_file_name)

# Write to JSON
write_json(variable_metadata, full_output_path, pretty = TRUE)
}
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
  #!print(paste("Matches for pattern1: ", matches1))  # Debug print

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
    #!print(paste("Matches for pattern2: ", matches2))  # Debug print
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
    #!print(paste("Matches for pattern3: ", matches3))  # Debug print
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
      #!print(paste("Matches for pattern4: ", matches4))  # Debug print

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
  #!print(paste("examining candidate label :",label))
  # Find which variable this label belongs to
  var_indices <- which(all_labels == label)
  for (var_index in var_indices) {
    varname <- colnames(df_rs13)[var_index]
    #!print(paste("Working on variable:", varname))

    # Use the extract_pairs function to get the codes and descriptions
    mypairs <- extract_pairs(label)

    # Print out what was extracted
    #!print(paste("extracted pairs: ",mypairs))

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

print("line 312")
# Initialize the array with the same length as combined_info_list
true_or_false_array <- rep(FALSE, length(combined_info_list))

# Populate the array with FALSE values
for (j in 1:length(combined_info_list)) {
  true_or_false_array[j]<-FALSE
  }
print("line 320")

# Iterate over each row in the combined_results
for (i in 1:nrow(combined_results)) {
  variable_name <- combined_results$variable[i]
  code <- combined_results$code[i]
  description <- combined_results$description[i]

  # Variable to track if we found the variable_name in combined_info_list
  found_variable <- FALSE

  # Iterate over combined_info_list to find the matching variable_name
  for (j in 1:length(combined_info_list)) {
    if (combined_info_list[[j]]$variable_name == variable_name) {
      print(paste("variable_name found in combined_info_list:", variable_name))
      found_variable <- TRUE
      # Access the variable's info in combined_info_list
      var_info <- combined_info_list[[j]]

      # Check if controlled_vocabulary exists, if not, initialize it as a list
      if (is.null(var_info$controlled_vocabulary)) {
        var_info$controlled_vocabulary <- vector("list", 0)
      }

      # Create a new entry for the controlled vocabulary
      new_cv_entry <- list(
        controlled_vocabulary_term_id = code,
        controlled_vocabulary_term_description = description
      )

      # Append the new controlled vocabulary entry to the list
      var_info$controlled_vocabulary <- append(var_info$controlled_vocabulary, list(new_cv_entry))
      true_or_false_array[j]<-TRUE
      # Update the variable's info back into combined_info_list
      combined_info_list[[j]] <- var_info

      # No need to continue the inner loop once we found the match
      break
    }
  }

  if (!found_variable) {
    print(paste("variable_name NOT found in combined_info_list:", variable_name))
  }
}

for (j in 1:length(combined_info_list)) {
    true_or_false <- TRUE
    if (true_or_false_array[j]) {
        var_info <- combined_info_list[[j]]
        if (true_or_false==TRUE) {
          true_or_false <- FALSE
          var_info <- append_note(var_info, "Updated controlled vocabulary generated by section 5 of get_stata_metadata.R")
          }
        combined_info_list[[j]] <- var_info
       }
  }

# Now combined_info_list is updated with the new controlled vocabulary terms



#! <%GTREE 6 identify the data type of each variable%>
# Identify data types for each variable
data_types <- sapply(df_rs13, class)

# Combine the unique values count and data types into a single dataframe
variable_info <- data.frame(
  variable_name = names(df_rs13),
  data_type = data_types,
  unique_value_count = sapply(df_rs13, function(col) length(unique(col))),
  stringsAsFactors = FALSE
)

for (i in 1:length(combined_info_list)) {
  var_name <- combined_info_list[[i]]$variable_name

  # Find the corresponding entry in variable_info
  var_info_match <- variable_info[variable_info$variable_name == var_name, ]

  # Check if there is a matching entry
  if (nrow(var_info_match) == 1) {
    # Add data_type and unique_value_count to the combined_info_list entry
    combined_info_list[[i]]$data_type <- var_info_match$data_type
    combined_info_list[[i]]$unique_value_count <- var_info_match$unique_value_count
  } else {
    # Handle the case where no matching entry is found
    print(paste("No matching information found for variable", var_name))
  }
}

print("line 293")
#! <%GTREE 7 Count and check unique values for each variable%>

# Initialize a data frame to store discrepancies
discrepancies_df <- data.frame(Variable = character(),
                              MissingInData = I(list()),
                              ExtraInData = I(list()),
                              stringsAsFactors = FALSE)

# Function to create a mapping from labels to codes
create_label_to_code_mapping <- function(labels, codes) {
  return(setNames(codes, labels))
}

# Check if the factor codes match the unique values in the data
for (varname in names(factors)) {
  if (!is.null(factors[[varname]])) {
    # Extract labels and codes for the current variable
    labels <- names(factors[[varname]])
    codes <- as.integer(factors[[varname]])

    # Create the mapping for the current variable
    label_to_code_mapping <- create_label_to_code_mapping(labels, codes)

    # Get unique data values
    data_values <- unique(df_rs13[[varname]])

    # Convert labels to codes (if the data values are in the labels list)
    data_codes <- ifelse(data_values %in% names(label_to_code_mapping), label_to_code_mapping[data_values], data_values)

    # Identify mismatches
    missing_in_data <- setdiff(codes, data_codes)
    extra_in_data <- setdiff(data_codes, codes)

    # Report discrepancies
    if (length(missing_in_data) > 0) {
      warning(paste("Not all factor codes for variable", varname, "are present in the data."))
      print(paste("Factor codes not in data for", varname, ":", toString(missing_in_data)))
    }

    if (length(extra_in_data) > 0) {
      warning(paste("There are values in the data for variable", varname, "that are not consistent with the factor codes."))
      print(paste("Data values not in factor codes for", varname, ":", toString(extra_in_data)))
    }
    # Add discrepancies to the data frame
    if (length(missing_in_data) > 0 || length(extra_in_data) > 0) {
      new_row <- data.frame(Variable = varname,
                            MissingInData = I(list(missing_in_data)),
                            ExtraInData = I(list(extra_in_data)),
                            stringsAsFactors = FALSE)
      discrepancies_df <- rbind(discrepancies_df, new_row)
    }
  }
}

for (j in 1:length(combined_info_list)) {
  varname <- combined_info_list[[j]]$variable_name
  var_info <- combined_info_list[[j]]
  if (varname %in% discrepancies_df$Variable) {
    controlled_vocabulary_list <- combined_info_list[[j]]$controlled_vocabulary
    # Extract discrepancies for this variable
    missing_in_data <- discrepancies_df$MissingInData[discrepancies_df$Variable == varname][[1]]
    extra_in_data <- discrepancies_df$ExtraInData[discrepancies_df$Variable == varname][[1]]

    # Now iterate through each controlled vocabulary item
    for (cv_item_index  in seq_along(controlled_vocabulary_list)) {
      cv_item <- controlled_vocabulary_list[[cv_item_index]]
      controlled_vocabulary_term_id <- cv_item$controlled_vocabulary_term_id

      # Check if this code is in the missing or extra lists
      codemissing <- controlled_vocabulary_term_id %in% missing_in_data
      codeextra <- controlled_vocabulary_term_id %in% extra_in_data

      #update cv_item if needed
      if (codemissing ) {
        print(paste("Updating controlled vocabulary for", varname, "with term ID", controlled_vocabulary_term_id))
        # Create a new entry for the controlled vocabulary
        var_info$controlled_vocabulary[[cv_item_index]]$code_missing_in_data <- TRUE
        # Update the variable's info back into combined_info_list
        var_info <- append_note(var_info, "Updated controlled vocabulary generated by section 7 of get_stata_metadata.R")

      }
    }
    combined_info_list[[j]] <- var_info
  }
}

print("line 481")
# ... [code for checking factors in section 5] ...

# Flag text variables with limited unique values
print("line 380")
text_variables <- variable_info[variable_info$Variable %in% names(df_rs13[sapply(df_rs13, is.character)]),]
#print("line 382")
# Set your threshold for what you consider to be a controlled vocabulary
threshold <- 20  # For example, you might consider 10 or fewer unique values to indicate a controlled vocabulary

controlled_vocab_candidates <- text_variables[text_variables$UniqueValueCount <= threshold,] # Set your threshold

# ... [rest of the script] ...


#! <%GTREE 8 identify potential primary keys%>
# Function to check for primary key candidates
print("test to determine number of rows")
nrow(df_rs13)
check_primary_key <- function(df) {
  number_of_rows <- nrow(df)
  primary_key_candidates <- sapply(df, function(column) length(unique(column)) == number_of_rows)

  # If there is any variable that has the same number of unique values as there are rows, it could be a primary key
  potential_primary_keys <- names(which(primary_key_candidates))

  if (length(potential_primary_keys) > 0) {
    return(potential_primary_keys)
  } else {
    # If no single primary key candidate is found, look for combinations
    for (i in 2:length(df)) {
      combinations <- combn(names(df), i)
      for (j in 1:ncol(combinations)) {
        combination <- as.data.frame(df[,combinations[, j]])
        if (nrow(unique(combination)) == number_of_rows) {
          return(combinations[, j])
        }
      }
    }
    # If no combination is found, return NULL
    return(NULL)
  }
}

# Call the function to check for primary key candidates
primary_key <- check_primary_key(df_rs13)
str(primary_key)
# Check if a primary key or a combination of keys is found
if (!is.null(primary_key)) {
  if (length(primary_key) == 1) {
    message("Potential primary key found: ", primary_key)
    for (j in 1:length(combined_info_list)) {
      varname <- combined_info_list[[j]]$variable_name
      var_info <- combined_info_list[[j]]
      if (varname %in% primary_key) {
        combined_info_list[[j]]$key <- "primary key"
      }
    }

  } else {
    message("No single primary key found. A combination of variables could serve as a primary key: ", paste(primary_key, collapse = ", "))
    for (j in 1:length(combined_info_list)) {
      varname <- combined_info_list[[j]]$variable_name
      var_info <- combined_info_list[[j]]
      if (varname %in% primary_key) {
        combined_info_list[[j]]$key <- "potential primary key"
      }
    }
  }
} else {
  message("No primary key or combination of keys found that uniquely identifies each record.")
}

#! <%GTREE 9 identify dummy variables%>
# if data_type is integer and unique_value_count == 2
# test if the unique values are 0 and 1
# in that case  change data_type to "dummy"   in combined_info_list

for (i in 1:length(combined_info_list)) {
  var_info <- combined_info_list[[i]]
  var_name <- var_info$variable_name

  # Check if the data type is integer, unique value count is 2, and controlled vocabulary does not exist
  if (var_info$data_type == "integer" && var_info$unique_value_count == 2 && is.null(var_info$controlled_vocabulary)) {
    # Get unique values from the dataset
    unique_values <- unique(df_rs13[[var_name]])

    # Check if the unique values are 0 and 1
    if (all(sort(unique_values) == c(0, 1))) {
      # Update the data type to 'dummy'
      combined_info_list[[i]]$data_type <- "dummy"
    }
  }
}


#! <%GTREE 10 identify potential controlled vocaularies%>
#given:
#variable_info <- data.frame(
#  variable_name = names(df_rs13),
#  data_type = data_types,
#  unique_value_count = sapply(df_rs13, function(col) length(unique(col))),
#  stringsAsFactors = FALSE
#)
#
# if data_type is "character" and unique_value <= 30
# create a "controlled_vocabulary":[] list with objects
# {
#    "controlled_vocabulary_term_id":value
#    "controlled_vocabulary_term_description":value
# }
# this information should be updated in combined_info_list
# moreover, combined_info_list[[i]]$data_type <- "controlled_vocabulary"

for (i in 1:length(combined_info_list)) {
  var_info <- combined_info_list[[i]]
  var_name <- var_info$variable_name

  # Identify character variables with unique values <= 30
  if (var_info$data_type == "character" && var_info$unique_value_count <= 30) {
    # Get unique values from the dataset
    unique_values <- unique(df_rs13[[var_name]])
    print(paste("found controlled vocabulary candidates in: ", var_info$variable_name ))
    # Create controlled vocabulary
    controlled_vocabulary <- vector("list", length(unique_values))
    for (j in 1:length(unique_values)) {
      x = as.character(unique_values[j])
      print(paste(j,": ",x))
      controlled_vocabulary[[j]] <- list(
        controlled_vocabulary_term_id = j,
        controlled_vocabulary_term_description = as.character(unique_values[j])
      )
    }

    # Update combined_info_list
    combined_info_list[[i]]$controlled_vocabulary <- controlled_vocabulary
    combined_info_list[[i]]$data_type <- "controlled_vocabulary"
  }
}

#! <%GTREE 32 clean upo the list of lists%>
remove_duplicate_cv_entries <- function(cv_list) {
  # Check if the list is empty
  if (length(cv_list) == 0) {
    return(list())
  }

  # Create an empty list to store unique entries
  unique_entries <- list()

  # Iterate over each entry in the list
  for (entry in cv_list) {
    # Convert the entry to a character vector for comparison
    entry_char <- sapply(entry, as.character)

    # Check if this entry is unique
    is_unique <- TRUE
    for (unique_entry in unique_entries) {
      if (identical(sapply(unique_entry, as.character), entry_char)) {
        is_unique <- FALSE
        break
      }
    }

    # If unique, add to the list of unique entries
    if (is_unique) {
      unique_entries <- append(unique_entries, list(entry))
    }
  }

  return(unique_entries)
}

# Apply function to combined_info_list
for (i in 1:length(combined_info_list)) {
  var_info <- combined_info_list[[i]]
  true_or_false=FALSE
  if (!is.null(var_info$controlled_vocabulary)) {
    combined_info_list[[i]]$controlled_vocabulary <- remove_duplicate_cv_entries(var_info$controlled_vocabulary)

  }
  if (true_or_false) {
    var_info <- combined_info_list[[i]]
    var_info <- append_note(var_info, "Updated controlled vocabulary generated by section 32 of get_stata_metadata.R")
    combined_info_list[[i]] <- var_info

  }
}

#! <%GTREE 11 supplement missing controlled vocabulary terms with code 0 when there are only two options%>
for (i in 1:length(combined_info_list)) {
  var_info <- combined_info_list[[i]]

  # Check if the variable has a controlled vocabulary with only one term and unique_value_count is 2
  if (!is.null(var_info$controlled_vocabulary) &&
      length(var_info$controlled_vocabulary) == 1 &&
      var_info$unique_value_count == 2) {
      x=var_info$variable_name
    print(paste("candidate to supplement CVs: ",x) )

    # Extract the existing controlled vocabulary term
    existing_term <- var_info$controlled_vocabulary[[1]]

    # Check if the existing term ID is 1
    if (existing_term$controlled_vocabulary_term_id == 1) {
      # Generate the new term description
      new_term_description <- paste("not", existing_term$controlled_vocabulary_term_description)

      # Create the new controlled vocabulary term
      new_term <- list(controlled_vocabulary_term_id = 0,
                       controlled_vocabulary_term_description = new_term_description)

      # Append the new term to the controlled vocabulary
      var_info$controlled_vocabulary <- append(var_info$controlled_vocabulary, list(new_term))
      var_info <- append_note(var_info, "Updated controlled vocabulary generated by section 11 of get_stata_metadata.R")
    }
  }

  # Update the combined_info_list
  combined_info_list[[i]] <- var_info
}


#! <%GTREE 12 identify potential units of measurement%>
# in combined_info_list for each object in the list of lists:
# if data_type = numeric or integer check variable_description if it contains the sub-string "in ha" or "(ha)" or "(has)" then add
# unit_of_measurement with value "ha"
# if data_type = numeric or integer check variable_description if it contains the sub-string "in days" or "(days)" then add
# unit_of_measurement with value "days"
# if data_type = numeric or integer check variable_description if it contains the sub-string "in %" or "(%)" or "in percentage" then add
# unit_of_measurement with value "%"

for (i in 1:length(combined_info_list)) {
  var_info <- combined_info_list[[i]]

  # Check if the data type is numeric or integer
  if (var_info$data_type == "numeric" || var_info$data_type == "integer") {

    # Check for "ha" related units in variable_description
    if (grepl("in ha|\\(ha\\)|\\(has\\)", var_info$variable_description, ignore.case = TRUE)) {
      var_info$unit_of_measurement <- "ha"
      var_info <- append_note(var_info, "unit of measurement generated by section 12 of get_stata_metadata.R")
    }

    # Check for "days" related units in variable_description
    if (grepl("in days|\\(days\\)", var_info$variable_description, ignore.case = TRUE)) {
      var_info$unit_of_measurement <- "days"
      var_info <- append_note(var_info, "unit of measurement generated by section 12 of get_stata_metadata.R")
    }

    # Check for "%" or "percentage" related units in variable_description
    if (grepl("in %|\\(%)|in percentage", var_info$variable_description, ignore.case = TRUE)) {
      var_info$unit_of_measurement <- "%"
      var_info <- append_note(var_info, "unit of measurement generated by section 12 of get_stata_metadata.R")
    }
  }

  # Update the combined_info_list
  combined_info_list[[i]] <- var_info
}



#! <%GTREE 33 create json file%>
#! <%GTREE 33.1 flatten list%>
# Flatten the results list into a single list of variables with their vocabularies
final_list <- unname(lapply(combined_info_list, function(x) x))

#! <%GTREE 33.2 Convert the list to JSON structure%>
# Convert the list to JSON
json_output <- jsonlite::toJSON(final_list, pretty = TRUE, auto_unbox = TRUE)

#! <%GTREE 33.3 export to json%>
# Export to a json
# Extract file name without extension
file_name_sans_ext <- tools::file_path_sans_ext(basename(args$path_to_dta_file))

# Combine the file name with the new ending
new_file_name <- paste0(file_name_sans_ext, "_structural_metadata.json")

# Combine with the output directory path
full_output_path <- file.path(args$path_to_output_folder, new_file_name)

# Write to JSON
# Write the JSON output to file
writeLines(json_output, full_output_path)


#*============================   End Of File   ================================