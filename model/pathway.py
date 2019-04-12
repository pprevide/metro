"""Define a Pathway class.

"""
from utilities.other_constants import *
from utilities.file_constants import PATHWAYS_FILE
from utilities.tables import Csv
from configuration import DATA_DIR
import os


class Pathway:
    """This class defines attributes and functions associated with a Metro program course pathway.

    The Metro program consists of different academies.  Each academy has its own course pathway.  The
    students in an academy will have the same pathway.

    Instances of this class are associated with each Metro student's attributes, as stored in a Pandas
    DataFrame created in the preprocessing() function of processing.py.

    Each Pathway consists of three carefully-designed courses in which the Metro program invests significant
    resources and effort.  These three courses comprise a "core pathway".
    The courses are designed to be taken in sequence, as the later ones build on earlier ones.
    Metro requires its students to participate in this sequence.  The three courses are as follows:
    (1) the first-year experience course, taken in either fall or spring semester of the student's first year.
    (2) the second-year experience course, taken in the fall of the student's second year.
    (3) the capstone course, taken in the spring of the student's second year.
    In some instances, one of the above required courses can be chosen from a set of possible options.

    Each Pathway can also include some optional courses that Metro suggests students take at certain times.
    For example, the core-pathway courses listed above are generally not Math courses.  Metro's optional courses
    do include suggested Math courses and suggested semesters when to take them.

    University students who do not participate in Metro do not take the carefully-designed
    core-pathway courses listed above.  It is possible that non-Metro students can take a course by the same
    name as a core-pathway course, but it will not be the Metro version of the course.  In other words,
    it will not include the services and additional features that Metro puts in its core-pathway courses.

    """

    def __init__(self,
                 name=None,
                 first_exp=None,
                 second_exp=None,
                 cap=None,
                 semester_courses_dict=None):
        """Instantiate a Pathway object.

        Args:
            name (str): The name and year of the academy that has this pathway (e.g., Health1-2012).
            first_exp (set of strings): The first year experience course(s).
            second_exp (set of strings): The second year experience course(s).
            cap (set of strings): The capstone course(s).
            semester_courses_dict (dict): Mapping of semester numbers to the courses in which they are taken.

        """

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
        """Read a file of pathways and return a dictionary mapping cohort names to Pathway objects.

        Args:
            pathway_file (str): Name of the csv file that holds Pathway information.

        Returns:
            Dictionary mapping cohort names (HLTH-2014) to Pathway objects.

        """

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

    def compute_pathway_progress(self, term_courseGroup_dict, passing_only=False):
        """Compute the progress of a student in their cohort's core-pathway

        Args:
            term_courseGroup_dict (dict): Mapping of term numbers to CourseGroup instances.
            passing_only (bool): Consider only courses that the student passed.

        Returns:
            An integer representing the number of core-pathway courses taken by the student
            (or passed, if passing_only is true).

        """

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
        """Get the core-pathway sequence of courses.

        Returns:
            List of sets of strings representing the core pathway courses.

        """

        return list(self.first_exp | self.second_exp | self.cap)

    def get_math_courses_list(self):
        """Get the Metro Math courses and their timing.

        Semester numbers in the returned tuples are 0, 2, 4 and 6, since winter and summer
        semesters come between fall and spring semesters.

        Returns:
            List of (course, semester number) tuples for the Math courses in this Pathway.

        """
        math_courses_list = []
        for each_key in sorted(self.semester_courses_dict):
            for each_course in self.semester_courses_dict[each_key]:
                if each_course in MATH_COURSES_SET:
                    math_courses_list.append( (each_course, each_key) )
        return math_courses_list

    def get_first_math_course(self):
        """Get the name of the first Math course in this Pathway.

        Returns:
            String name of the first Math course, or None if there is no Math course in this Pathway.

        """
        first_math_course = None
        try:
            first_course_tuple = self.math_courses_list[0]
            first_math_course = first_course_tuple[0]
        except:
            pass
        return first_math_course

    def get_first_math_semester(self):
        """Get the semester number of the first Math course in this Pathway.

        Returns:
            Integer semester number, or None if there is no Math course in this Pathway.

        """

        first_math_semester = None
        try:
            first_course_tuple = self.math_courses_list[0]
            first_math_semester = first_course_tuple[1]
        except:
            pass
        return first_math_semester


