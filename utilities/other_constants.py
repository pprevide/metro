"""Define constants relating to courses, semester identifiers, grades, and other non-file topics.

This file defines constants associated with pre-defined collections of information, such as grades,
courses, semester identifiers, and so on.

Constants relating to csv file headers and filenames are defined in other_constants.py.  All other
constants should be defined in this file.
"""

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

SEMESTERS_TO_NUMBERS_DICT = {x: SEMESTERS_LIST.index(x) + 1 for x in SEMESTERS_LIST}
NUMBERS_TO_SEMESTERS_DICT = {SEMESTERS_LIST.index(x) + 1: x for x in SEMESTERS_LIST}
SEASON_MODULO = {
    "Fall": 1, "Winter": 2, "Spring": 3, "Summer": 0
}
VALID_GRADES = [
    'A', 'A+', 'A-',
    'B', 'B+', 'B-',
    'C', 'C+', 'C-',
    'D', 'D+', 'D-',
    'F', 'I', 'IC',
    'CR', 'NC', 'RD',
    'RP', 'W', 'WU'
]
PASSING_GRADES = {
    'A', 'A+', 'A-',
    'B', 'B+', 'B-',
    'C', 'C+', 'C-',
    'D', 'D+', 'CR'
}
INCOMPLETE_GRADES = {
    'W', 'WU', 'I', 'IC'
}
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
PERSONAL_INFO_COLUMN_NAMES_LIST = {"First Name", "Last Name", "Address", "Phone Number"}
RACE_RENAMING_DICT = {
    "Hispanic/Latino (any race)": "Hispanic/Latino",
    "Asian Only (Asian) - Non-Hispanic": "Asian",
    "Black or African American Only (Black) - Non-Hispanic": "Black",
    "White Only (White) - Non-Hispanic": "White"
}
INCOME_CATEGORIES_DICT = {
    "Less than or equal to $30,000": 0,
    "$30,001 - $50,000": 1,
    "50,001 - $70,000": 2,
    "$70,001 or higher": 3
}
EDUCATION_CATEGORIES_DICT = {
    "No High School": 0,
    "Some High School": 1,
    "High School Grad": 2,
    "Some College": 3,
    "2-Yr College Grad": 4,
    "4-Yr College Grad": 5,
    "Postgraduate": 6
}
