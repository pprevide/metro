# R script to convert a spss file into a separated-values file, with a specified delimiter.
# Invoke this script using the syntax spss_to_table.R spss_file_name, output_file_name, separator_char

library(foreign)
args = commandArgs(trailingOnly = TRUE)
converted_df = read.spss(args[1], to.data.frame = TRUE)
separator = args[3]
write.table(converted_df, file = args[2], quote = FALSE, sep = separator, row.names = FALSE)