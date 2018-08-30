import csv
import subprocess
from helpers import *

MATH_COURSES_SET = {"MATH124", "ISED160", "PSY171", "MATH110", "MATH199", "MATH226"}
MATH_REMEDIATION_COURSES_SET = {"MATH60", "MATH70"}

SEMESTERS_LIST = [
    "Fall 2009", "Winter 2010", "Spring 2010", "Summer 2010",
    "Fall 2010", "Winter 2011", "Spring 2011", "Summer 2011",
    "Fall 2011", "Winter 2012", "Spring 2012", "Summer 2012",
    "Fall 2012", "Winter 2013", "Spring 2013", "Summer 2013",
    "Fall 2013", "Winter 2014", "Spring 2014", "Summer 2014",
    "Fall 2014", "Winter 2015", "Spring 2015", "Summer 2015",
    "Fall 2015", "Winter 2016", "Spring 2016", "Summer 2016",
    "Fall 2016", "Winter 2017", "Spring 2017", "Summer 2017",
    "Fall 2017"
]

VALID_GRADES = [
    'A', 'A+', 'A-',
    'B', 'B+', 'B-',
    'C', 'C+', 'C-',
    'D', 'D+', 'D-',
    'F', 'I', 'IC',
    'CR', 'NC', 'RD',
    'RP', 'W', 'WU'
]
GRADE_POINT_DICT = {
    "A+": 4.0,
    "A": 4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B": 3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C": 2.0,
    "C-": 1.7,
    "D+": 1.3,
    "D": 1.0,
    "D-": 0.7,
    "F": 0.0,
    "NC": 0.0,
    "CR": None,
    "W": None,
    "WU": None,
    "I": None,
    "IC": None,
    "RD": None,
    "RP": None
}
GRADE_OUTCOME_DICT = {
    "A+": "High",
    "A": "High",
    "A-": "High",
    "B+": "High",
    "B": "High",
    "B-": "Medium",
    "C+": "Medium",
    "C": "Medium",
    "C-": "Medium",
    "D+": "Low",
    "D": "Low",
    "D-": "Low",
    "F": "Low",
    "NC": "Low",
    "CR": "Medium",
    "W": None,
    "WU": None,
    "I": None,
    "IC": "Low",
    "RD": None,
    "RP": None
}

VALID_LEVELS_SET = {"Freshman", "Sophomore", "Junior", "Senior"}



