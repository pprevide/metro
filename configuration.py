import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")
HOME_DIR = os.path.expanduser("~")
SPMF_DIR = os.path.join(DATA_DIR, "spmf")
BIN_DIR = os.path.join(ROOT_DIR, "bin")
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")
RSTCMP2_QUERY_DIR = os.path.join(DATA_DIR, "Rstcmp2_queries")