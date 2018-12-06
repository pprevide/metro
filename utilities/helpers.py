"""Provide useful academics-related functions for use by other modules.

This module contains functions relating to frequently-conducted manipulations,
    transformations, and conversions of academic data.
"""

from other_constants import *
import sys
import collections


# convenience function to convert a semester code like "F2010" to its corresponding academic year
def convert_term_code_to_academic_year(term_code, as_string=False):
    """Given a term code, such F2012, return the year in which the academic year
    to which that term code belongs started.

    Some columns of the CS query files indicate terms with an abbreviation such as "F2012" or "S2014".
    Academic years start in a Fall semester and end in the subsequent summer semester.  For example,
    the 2012-2013 academic year includes the Fall 2012, Winter 2013, Spring 2013, and Summer 2013
    semesters.  Given the term code F2012, this function returns 2012.  Given the term code
    S2013, this function likewise returns 2012 since the Spring 2013 semester is a part of
    the 2012-2013 academic year.

    Args:
        term_code (str): A string encoding the semester and year of a particular term.
        as_string (bool): If true, return the academic year as a string (e.g., "2012-2013");
            If false, return an integer representing the start of the year (e.g., 2012).

    Returns:
        The year in which the academic year containing term_code started, as a string.

    """
    year = int(term_code[-4:])
    if as_string == False:
        if term_code[0] == 'F':
            return year
        else:
            return year - 1
    else:
        if term_code[0] == 'F':
            return str(year) + '-' + str(year + 1)
        else:
            return str(year - 1) + '-' + str(year)


def parse_term_from_filename(filename):
    """Given a particular query file name, return the name of the term to which the query pertains.

    The SFSU CS query system emits csv files which are renamed to contain an abbreviation like "F2012"
    at the start of the filename.  More specifically, Fall semester file names start with F; winter,
    with WI; spring, with S, and summer, with SU.  To each of these abbreviations, the year is appended.
    All of the rows of a particular csv file apply to the same semester, so from the file name, the
    semester (e.g., Fall 2014) to which the csv files apply can be determined.

    This function converts the start of the filename, such as F2013, into a text representation of the relevant
    semester, such as "Fall 2013".

    Args:
        filename (str): The name of a csv file containing query results exported from CS.

    Returns:
        A string representation of the semester and year, such as "Fall 2013".

    """

    if filename[0] == 'F':
        return "Fall " + filename[1:5]
    else:
        if filename[0] == 'W':
            return "Winter " + filename[2:6]
        else:
            if filename[0] == 'S' and filename[1] == '2':
                return "Spring " + filename[1:5]
            else:
                if filename[0] == 'S' and filename[1] == 'U':
                    return "Summer " + filename[2:6]
                else:
                    print "ERROR: invalid filename prefix: ", filename
                    sys.exit(1)


def convert_semester_name_to_academic_year(semester_name):
    """Convert a semester name ("Fall 2011") into its corresponding academic year ("2011").

    Args:
        semester_name (str): Text representation of a particular semester.

    Returns:
        A string representing the year in which the applicable academic year started.

    """

    return semester_name[-4:] if semester_name[:2] in {"Fa"} \
        else str(int(semester_name[-4:]) - 1)


def create_numbers_semesters_dicts():
    """Create dictionaries that map semester numbers to semester names, and vice versa.

    Converting semester names (e.g., "Fall 2009") to an integer (e.g., 1) and vice versa is a frequent
    operation for this project.  This function creates dictionaries to hold lookups for faster
    conversions in either direction.

    See SEMESTERS_LIST in utilities/other_constants.py for the data structure containing
    the names of all relevant semesters.

    Returns:
        Dictionaries mapping semester names to numbers, and vice versa.

    """

    numbers_to_semesters_dict = dict()
    semesters_to_numbers_dict = dict()
    semester_no = 1
    for each_semester in SEMESTERS_LIST:
        semesters_to_numbers_dict[each_semester] = semester_no
        numbers_to_semesters_dict[semester_no] = each_semester
        semester_no += 1
    return numbers_to_semesters_dict, semesters_to_numbers_dict


def convert_semester_number_to_academic_year(semester_number):
    """Convert a semester number (9) to its corresponding academic year (2011).

    Args:
        semester_number (int): Numeric identifier of a particular semester.

    Returns:
        A string representation of the year in which the academic year started.

    """

    return convert_semester_name_to_academic_year(NUMBERS_TO_SEMESTERS_DICT[semester_number])


def show_counter_percentages(input_list, digits=3, print_output=False):
    """

    Args:
        input_list (list): List containing the elements to be counted.
        digits (int): Number of significant digits to use in the percentages.
        print_output (bool): If True, print output to the screen.

    Returns:
        A list of tuples in the form (list element, % of that element in the list).

    """

    counts = collections.Counter(input_list).most_common()
    results_list = []
    for each_tuple in counts:
        result_tuple = (each_tuple[0], round(float(each_tuple[1]) / len(input_list), digits))
        results_list.append(result_tuple)
        if print_output:
            print each_tuple[0], ": ", each_tuple[1], " total...", round(float(each_tuple[1]) / len(input_list), digits)
    return results_list


def convert_semester_name_to_semester_number(semester_name):
    """Convert a semester name ("Fall 2011") into its corresponding semester number (8).

    Refer to SEMESTERS_LIST in utilities/other_constants.py for a complete list of relevant semesters.

    Args:
        semester_name (str): A text representation of a particular semester.

    Returns:
        An integer identifier for that semester as used in this project.

    """

    return SEMESTERS_TO_NUMBERS_DICT[semester_name]
