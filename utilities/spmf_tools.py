import os
import sys
from configuration import SPMF_DIR, BIN_DIR
from other_constants import SEASON_MODULO
from file_constants import SPMF_EXECUTABLE
from processing import preprocessing
import pandas as pd
import subprocess
from collections import Counter


def create_spmf_input_file(contacts_df, student_records_dict, roster_dict,
                           cohort_years, passing_only, seasons,
                           spmf_input_file_name, capture_gaps=False, comp_only=False):
    spmf_input_file = os.path.join(SPMF_DIR, spmf_input_file_name)
    labels_input_file = spmf_input_file.replace(".txt", "_labels.txt")
    if os.path.exists(spmf_input_file):
        os.remove(spmf_input_file)
    if os.path.exists(labels_input_file):
        os.remove(labels_input_file)
    with open(spmf_input_file, 'a') as output_file, open(labels_input_file, 'a') as labels_file:
        # Filter out students who don't satisfy the cohort_years argument
        students = contacts_df.loc[contacts_df["cohort_year"].isin(cohort_years), "student_id"].values
        # If comp_only, filter out students who aren't in category Comp
        #    Also remove those students who have no entry in student_records_dict
        if comp_only:
            students = contacts_df.loc[contacts_df["category"].isin(["Comp"]), "student_id"].values
            students = list(set(students).intersection(set(student_records_dict)))
        print "len of students: ", len(students)
        for student_id in students:
            term_course_group_dict = student_records_dict[student_id]
            sequence_string = ""
            if capture_gaps:
                terms_list = sorted(term_course_group_dict.keys())
                start_term, end_term = (terms_list[0], terms_list[len(terms_list)-1])
                for term in [x for x in range(start_term, end_term+1)
                             if x%4 in {SEASON_MODULO[s] for s in seasons}]:
                    try:
                        course_group = term_course_group_dict[term]
                        next_string = course_group.to_spmf_string(passing_only=passing_only)
                        if next_string!="-1 ":
                            sequence_string += next_string
                    except KeyError:
                        sequence_string += "GAP -1 "
                if sequence_string=="":
                    continue
                sequence_string += "-2"
            else:
                for term in sorted(term_course_group_dict.keys()):
                    course_group = term_course_group_dict[term]
                    next_string = course_group.to_spmf_string(passing_only=passing_only)
                    if next_string!="-1 ":
                        sequence_string += next_string
                if sequence_string=="":
                    continue
                sequence_string += "-2"
            output_file.write(sequence_string + '\n')
            labels_file.write(student_id + '\n')

def run_spmf(input_file_name, output_file_name, min_support, algorithm_name = "CM-SPADE", *args):
    command = ["java", "-jar", os.path.join(BIN_DIR, SPMF_EXECUTABLE), "run", algorithm_name,
               os.path.join(SPMF_DIR, input_file_name), os.path.join(SPMF_DIR, output_file_name),
               str(min_support)]
    command.extend(args)
    subprocess.Popen(command)

def determine_sequence_semester_lengths(sequence_list, input_file_name):
    lengths_list = []
    def loc(x, line):
        for idx, elem in enumerate(line):
            if x in set(elem.split()):
                return idx
        return -1000
    with open(os.path.join(SPMF_DIR, input_file_name), 'rU') as input_file:
        lines = [x.split(" -1 ") for x in input_file.readlines()]
        for idx, line in enumerate(lines):
            occurrences = map(loc, sequence_list, [line]*3)
            if occurrences[2]>occurrences[1] and occurrences[1]>occurrences[0] and sum(occurrences)>0:
                #print line
                #print occurrences
                lengths_list.append(occurrences[2]-occurrences[0]+1)
    return lengths_list


if __name__=='__main__':

    contacts_df, student_records_dict, roster_dict = preprocessing(metro_comp=True)
    create_spmf_input_file(contacts_df=contacts_df,
                           student_records_dict=student_records_dict,
                           roster_dict=roster_dict,
                           cohort_years=list(range(2009, 2017)),
                           passing_only=False,
                           seasons = ["Fall", "Spring", "Summer"],
                           spmf_input_file_name="spmfinput__comp_nopassing_nogaps_2009_16.txt",
                           capture_gaps=False,
                           comp_only=True)

