"""Provide services for using the sequential pattern mining framework ("SPMF").

SPMF is an open-source data mining library implemented in Java.  Its focus is on pattern mining,
and it implements many algorithms: mining of itemsets, association rules, sequential patterns, and
many others: <http://www.philippe-fournier-viger.com/spmf>.

SPMF has particular requirements for the format of its input files, and it produces output files
that also have a unique format.  The functions in this module help to create the input files
and provide a wrapper so that the SPMF executable can be called from within a Python script.

In this project, the utility of SPMF is to analyze sequences of courses taken by students.
The resulting output files can then be parsed and explored using a Python script.
"""
import os
from configuration import SPMF_DIR, BIN_DIR
from other_constants import SEASON_MODULO
from file_constants import SPMF_EXECUTABLE
from processing import preprocessing
import subprocess


def create_spmf_input_file(contacts_df, student_records_dict,
                           cohort_years, passing_only, seasons,
                           spmf_input_file_name, capture_gaps=False, comp_only=False):
    """Create a correctly-formatted SPMF input file from the course performance data.

    See the SPMF web site for a complete description of the required format.

    :param contacts_df: Pandas dataframe of student records.
    :param student_records_dict: Python dictionary mapping semester numbers to CourseGroup objects.
    :param cohort_years: The cohort years of students for whom to generate course sequences.
    :param passing_only: Include a course only if the student passed it.
    :param seasons: Consider only these semesters (e.g., fall, winter, spring or summer).
    :param spmf_input_file_name: Specify the name of the input file.
    :param capture_gaps: Include semesters in which a student took no classes.
    :param comp_only: Consider only Comparison students.
    :return: None.
    """

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
    """Run the SPMF executable and provide all the required parameters.

    The SPMF executable can be downloaded as a jar file.  The subprocess module is used to create a new
    subprocess and execute the appropriate command that includes the required parameters.

    Use the SPMF_DIR directory, specified in configuration.py, for the input and output files.
    Use the BIN_DIR directory, also specified in configuration.py, to store the executable itself.

    :param input_file_name: The name of the input file.
    :param output_file_name: The name of the output file.
    :param min_support: The minimum support, as a percentage or a floating-point proportion.
    :param algorithm_name: The SPMF algorithm to run.  "CM-SPADE", the default, is a sequential pattern
    mining algorithm that will find all sequences of length 1 or greater, as well as the number of
    records (students) that exhibit that sequence.
    :param args: Any additional arguments required by the chosen algorithm (none, if the default
    algorithm is chosen).
    :return: None.
    """
    command = ["java", "-jar", os.path.join(BIN_DIR, SPMF_EXECUTABLE), "run", algorithm_name,
               os.path.join(SPMF_DIR, input_file_name), os.path.join(SPMF_DIR, output_file_name),
               str(min_support)]
    command.extend(args)
    subprocess.Popen(command)

def determine_sequence_semester_lengths(sequence_list, spmf_file_name):
    """Determine the length of each sequence, in semesters.

    SPMF's sequential pattern mining algorithms return text files that indicate sequences and the number of
    students who had that sequence.  Longer sequences are of more interest, while sequences of length 1 are not
    that interesting.  For example, any student who took MATH60 will have the one-item sequence [MATH60].  This
    function determines the number of semesters captured in each sequence (to continue the MATH60 example, the length
    would be 1).

    As another example, in the sequence [MATH60; MATH70; MATH110] the semicolons separate different semesters, so this
    sequence has length 3.  On the other hand, SPMF can also indicate when multiple courses occur in the same semester,
    such that [MATH60 MATH70; MATH110] has MATH60 and MATH70 taken concurrently.  In this example, the length of the
    sequence is 2.

    :param sequence_list: A course sequence indicated in an SPMF output file for a sequential pattern mining
    algorithm such as CM-SPADE.
    :param spmf_file_name: The name of the SPMF output file containing the sequences.
    :return: Integer number of semesters encompassed by the sequence.
    """
    lengths_list = []
    def loc(x, line):
        for idx, elem in enumerate(line):
            if x in set(elem.split()):
                return idx
        return -1000
    with open(os.path.join(SPMF_DIR, spmf_file_name), 'rU') as input_file:
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

