"""Define the paths to directories used by the processing and analysis modules.

The constants defined in this file represent the system path to a root project directory, and a
collection of relative paths for directories that hold the student data, the Sequential Pattern Mining
Framework files and associated executable; output files from the create_tableau_file and spmf_tools modules;
and csv files exported by San Francisco State University's Campus Solutions (CS) querying system.

When any new data directories are created or the paths to existing ones are modified, those changes should be made
in this file.
"""

import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")
HOME_DIR = os.path.expanduser("~")
SPMF_DIR = os.path.join(DATA_DIR, "spmf")
BIN_DIR = os.path.join(ROOT_DIR, "bin")
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")
RSTCMP2_QUERY_DIR = os.path.join(DATA_DIR, "Rstcmp2_queries")