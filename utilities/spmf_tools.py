import os
import sys
from configuration import SPMF_DIR
from other_constants import SEASON_MODULO
from processing import preprocessing
import pandas as pd

def create_spmf_input_file(contacts_df, student_records_dict, roster_dict,
                           cohort_years, passing_only, seasons,
                           spmf_input_file_name, capture_gaps=False):
    spmf_input_file = os.path.join(SPMF_DIR, spmf_input_file_name)
    if os.path.exists(spmf_input_file):
        os.remove(spmf_input_file)
    with open(spmf_input_file, 'a') as output_file:
        # Filter out students who don't satisfy the cohort_years argument
        students = contacts_df.loc[contacts_df["cohort_year"].isin(cohort_years), "student_id"].values
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
            output_file.write(sequence_string)
            output_file.write('\n')


if __name__=='__main__':
    contacts_df, student_records_dict, roster_dict = preprocessing(metro_only=True)
    print "Got here"
    create_spmf_input_file(contacts_df=contacts_df,
                           student_records_dict=student_records_dict,
                           roster_dict=roster_dict,
                           cohort_years=[2014, 2015, 2016],
                           passing_only=True,
                           seasons = ["Fall", "Spring", "Summer"],
                           spmf_input_file_name="practicespmffile.txt",
                           capture_gaps=True)