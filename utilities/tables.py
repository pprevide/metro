import csv
import subprocess
import pandas as pd
import os
import shutil

from constants import PERSONAL_INFO_COLUMN_NAMES_LIST


class Csv:
    def __init__(self, csv_file,
                 has_header_row = True,
                 provided_headers_list = None,
                 delimiter = ',',
                 is_spss = False):
        self.csv_file = csv_file
        self.has_header_row = has_header_row
        self.provided_headers_list = provided_headers_list
        self.delimiter = delimiter
        self.rows = self.read_csv()
        if is_spss:
            self.csv_file = self.convert_spss(csv_file)

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

    @staticmethod
    def convert_spss(spss_file_path, output_file_path, separator="\t"):
        conversion_script = "spss_to_table.R"
        cmd = ['Rscript', conversion_script] + [spss_file_path, output_file_path, separator]
        x = subprocess.check_output(cmd, universal_newlines= True)
        if x is not None:
            print x
            return output_file_path

    @staticmethod
    def remove_columns(path, columns=None, anonymize = True, make_backups = True):
        if columns is None: columns = []
        if anonymize: columns.extend(PERSONAL_INFO_COLUMN_NAMES_LIST)
        files = []
        if os.path.isfile(path):
            files.extend(path)
        elif os.path.isdir(path):
            files.extend([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
        else:
            raise TypeError("remove_columns() requires a file name or directory name")
        for file_name in files:
            if make_backups:
                shutil.copyfile(file_name, "_original_file_" + file_name)
            table_df = pd.read_csv(file_name)
            if isinstance(columns, basestring):
                columns = [columns]
            table_df.drop(labels=columns, axis=1, inplace=True)
            table_df.to_csv(file_name, index=False)
        return files











