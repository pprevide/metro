from other_constants import *
import sys
import collections

# convenience function to convert a semester code like "F2010" to its corresponding academic year
def convert_term_code_to_academic_year(term_code, as_string=False):
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


# convenience function to convert a semester ("Fall 2011") into its corresponding academic year ("2011")
def convert_semester_name_to_academic_year(semester_name):
    return semester_name[-4:] if semester_name[:2] in {"Su", "Fa"} \
        else str(int(semester_name[-4:])-1)

def create_numbers_semesters_dicts():
    numbers_to_semesters_dict = dict()
    semesters_to_numbers_dict = dict()
    semester_no = 1
    for each_semester in SEMESTERS_LIST:
        semesters_to_numbers_dict[each_semester] = semester_no
        numbers_to_semesters_dict[semester_no] = each_semester
        semester_no += 1
    return numbers_to_semesters_dict, semesters_to_numbers_dict

# convenience function to convert a semester number (9) to its corresponding academic year (2011)
def convert_semester_number_to_academic_year(semester_number):
    return convert_semester_name_to_academic_year(NUMBERS_TO_SEMESTERS_DICT[semester_number])

# Convenience function to print out the percentages of each item in a list
def show_counter_percentages(input_list, digits=3):
    counts = collections.Counter(input_list).most_common()
    for each_tuple in counts:
        print each_tuple[0], ": ", each_tuple[1], " total...", round(float(each_tuple[1]) / len(input_list), digits)

# Convenience function to convert a semester name ("Fall 2011") into its corresponding semester number (8)
def convert_semester_name_to_semester_number(semester_name):
    return SEMESTERS_TO_NUMBERS_DICT[semester_name]



