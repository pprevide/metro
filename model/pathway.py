import collections
from utilities.other_constants import *
from utilities.file_constants import PATHWAYS_FILE
from utilities.tables import Csv
from configuration import DATA_DIR
import os
import copy


class Pathway:
    def __init__(self,
                 name=None,
                 first_exp=None,
                 second_exp=None,
                 cap=None,
                 semester_courses_dict=None):
        self.name = name
        self.first_exp = first_exp
        self.second_exp = second_exp
        self.cap = cap
        self.semester_courses_dict = semester_courses_dict  # map semester number to sorted list of courses
        #self.core_sequence_list = self.get_core_sequence_list()
        self.math_courses_list = self.get_math_courses_list()
        self.first_math_course = self.get_first_math_course()
        self.first_math_semester = self.get_first_math_semester()

    @staticmethod
    def make_cohort_pathway_dict(pathway_file=os.path.join(DATA_DIR, PATHWAYS_FILE)):
        # Read a file of pathways formatted as explained below
        # Return a dictionary that maps cohort names to Pathway instances
        cohort_pathway_dict = dict()
        pathways_csv = Csv(pathway_file)
        header_row, rows = pathways_csv.read_csv()
        for row in rows:
            cohort_name = row["cohort"]+'-'+row["year"]
            assert(cohort_name not in cohort_pathway_dict), "Cohort was found twice in the pathways file"
            first_exp = set(row["first_exp"].split(';'))  #row["first_exp"]
            second_exp =  set(row["second_exp"].split(';'))  #row["second_exp"]
            cap = set(row["cap"].split(';'))   #row["cap"]
            semester_courses_dict = dict()  # Map semester numbers to list of optional courses in that semester
            # Use 0, 2, 4, 6 as keys in order to be consistent with four semesters in an academic year
            #   0 is fall of academic year 1; 1 is winter of year 1; 2 is spring of year 1; and so on
            semester_courses_dict[0] = row["semester_1"].split(';')
            semester_courses_dict[2] = row["semester_2"].split(';')
            semester_courses_dict[4] = row["semester_3"].split(';')
            semester_courses_dict[6] = row["semester_4"].split(';')
            cohort_pathway_dict[cohort_name] = Pathway(
                name = cohort_name,
                first_exp = first_exp,
                second_exp = second_exp,
                cap = cap,
                semester_courses_dict= semester_courses_dict
            )
        return cohort_pathway_dict

    # compute the progress of a student in their cohort's core-pathway
    def compute_pathway_progress(self, term_courseGroup_dict, passing_only=False):
        this_student_courses_set = set()
        for each_CourseGroup in term_courseGroup_dict.values():
            if passing_only:
                this_student_courses_set.update(each_CourseGroup.passing_course_names_set)
            else:
                this_student_courses_set.update(each_CourseGroup.course_names_set)
        progress = 0
        for each_attr in ["first_exp", "second_exp", "cap"]:
            if len(this_student_courses_set.intersection(getattr(self, each_attr))):
                progress+=1
        return progress

    def get_core_sequence_list(self):
        return list(self.first_exp | self.second_exp | self.cap)

    # Get the Metro math courses in this Pathway, as list of (course, semester) tuples
    #   semester refers to 0, 2, 4, or 6
    def get_math_courses_list(self):
        math_courses_list = []
        for each_key in sorted(self.semester_courses_dict):
            for each_course in self.semester_courses_dict[each_key]:
                if each_course in MATH_COURSES_SET:
                    math_courses_list.append( (each_course, each_key) )
        return math_courses_list

    # Return the name of the first Math course in this cohort, as a string
    #    Return None if there is no Math course in this pathway sequence
    def get_first_math_course(self):
        first_math_course = None
        try:
            first_course_tuple = self.math_courses_list[0]
            first_math_course = first_course_tuple[0]
        except:
            pass
        return first_math_course

    # Return the semester number of the first Math course in this cohort, as an int
    #    Return None if there is no Math course in this pathway sequence
    def get_first_math_semester(self):
        first_math_semester = None
        try:
            first_course_tuple = self.math_courses_list[0]
            first_math_semester = first_course_tuple[1]
        except:
            pass
        return first_math_semester

    # Did a student take a course early?
    def check_course_timing(self, student_id):
        pass
        #Not yet implemented
        # return number off semesters separating Pathway semester from student's semester for a course


