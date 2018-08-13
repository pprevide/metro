library(foreign)
args = commandArgs(trailingOnly = TRUE)
converted_df = read.spss(args[1], to.data.frame = TRUE)
separator = args[3]
write.table(converted_df, file = args[2], quote = FALSE, sep = separator, row.names = FALSE)

