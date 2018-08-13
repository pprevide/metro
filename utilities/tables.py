import csv
import subprocess

class Csv:
    def __init__(self, csv_file,
                 has_header_row = True,
                 provided_headers_list = None,
                 delimiter = ','):
        self.csv_file = csv_file
        self.has_header_row = has_header_row
        self.provided_headers_list = provided_headers_list
        self.delimiter = delimiter
        self.rows = self.read_csv()

    def read_csv(self):
        with open(self.csv_file, 'rU') as file_object:
            reader = csv.reader(file_object, delimiter=self.delimiter)
            if self.has_header_row:
                header_row = next(reader, None)
                header_source = header_row
            else:
                header_row = []
                header_source = self.provided_headers_list
            rows = [
                { header: value for header, value in zip(header_source, next_row)}
                for next_row in reader ]
        return header_row, rows


def convert_spss(spss_file_path, output_file_path, separator="\t"):
    conversion_script = "spss_to_table.R"
    cmd = ['Rscript', conversion_script] + [spss_file_path, output_file_path, separator]
    x = subprocess.check_output(cmd, universal_newlines= True)
    if x is not None: print x





