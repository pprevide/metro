"""Define a CourseGroup class."""
from utilities.other_constants import *

duplicate_courses_set = set()
students_with_duplicate_courses_set = set()


class CourseGroup:
    """This class defines attributes and functions for a student's courses in one semester.

    Instances of this class are owned by a particular student and contain Course objects associated
    with all the courses that the student took in the indicated semester number.

    Instances of this class are the values in the dictionary student_records_dict, which is created by
    the processing.py module.
    """
    def __init__(self,
                 course_list=None, semester_number=None,
                 major=None, major_second=None,
                 term_gpa=None, term_units=None,
                 cumulative_gpa=None, cumulative_units=None,
                 student_id=None):
        """Instantiate a CourseGroup object.

        Args:
            course_list (List of Course instances): The courses taken by the student in a particular semester.
            semester_number (int): the semester represented as an integer (see SEMESTERS_TO_NUMBERS_DICT in
                utilities/other_constants.py for the derivation of these integers).
            major (str): The student's major, if included in the data.
            major_second (str): The student's second major, if included.
            term_gpa (float): The student's GPA for the semester.
            term_units (int): The student's number of units for the semester.
            cumulative_gpa (float): The student's cumulative GPA up to and including the semester.
            cumulative_units (int): The student's cumulative units up to and including the semester.
            student_id (str): Nine-character student identifier.

        """

        self.course_list = [] if course_list is None else course_list
        self.semester_number = semester_number  # 0 if semester_number is None else semester_number
        self.major = major
        self.major_second = major_second
        self.term_gpa = term_gpa
        self.term_units = term_units
        self.cumulative_gpa = cumulative_gpa
        self.cumulative_units = cumulative_units
        self.student_id = student_id
        self.course_names_set = set()
        self.passing_course_names_set = set()

    def get_numbered_course_group(self):
        """
        Create a representation of the semester number and courses taken by a student.

        This function is similar to a to_string function, with the format of the resulting
        string as, for example, [3: {MATH110, MATH120, PSY171}]

        The 3 refers to self.semester_number.

        Returns:
            The semester number followeed by a list of course names separated by commas.

        """

        course_string = "[" + str(self.semester_number) + ": {"
        for idx, each in enumerate(list(self.course_list)):
            if idx > 0: course_string += ", "
            course_string += each.to_string()
        course_string += "}]"
        return course_string

    def get_number_of_courses(self):
        """Convenience function to return the number of courses the student took in a certain semester.

        Returns:
            Number of courses taken in a semester by a certain student.

        """

        return len(self.course_list)

    def add_Course(self, new_course):
        """Append a Course instance to the course_list of the CourseGroup.

        Args:
            new_course (Course): The Course object to add.

        Returns:
            None

        """

        if new_course.course not in self.course_names_set:
            self.course_list.append(new_course)
            self.course_names_set.add(new_course.course)
            if new_course.grade_letter in PASSING_GRADES:
                self.passing_course_names_set.add(new_course.course)
        else:
            new_grade = new_course.grade
            for each_course in self.course_list:
                if each_course.course == new_course.course:
                    old_grade = each_course.grade
                    old_course = each_course
                    if old_grade!=new_grade:
                        duplicate_courses_set.add(new_course.course)
                        students_with_duplicate_courses_set.add(self.student_id)

    def get_math_courses(self):
        """Get the Math courses taken by a student this semester.

        See Course.py and utilities/other_constants.py for the Math courses and how the Course
        objects account for them.  Only those Math courses listed in utilities/other_constants.py
        will be accounted for.

        Returns:
            List of Math Course objects taken by a student in this semester.

        """

        math_courses = []
        for each_Course in self.course_list:
            if each_Course.is_math_course == True:
                math_courses.append(each_Course)
        return math_courses

    #
    def get_remediation_math_courses(self):
        """Get the remedial Math courses taken by a student in this semester.

        See Course.py and utilities/other_constants.py for the remediation Math courses and how the Course
        objects account for them.  Only those remediation Math courses listed in utilities/other_constants.py
        will be accounted for.

        Returns:
            List of remedial Math Course objects taken by a student in this semester.

        """
        remediation_math_courses = []
        for each_Course in self.course_list:
            if each_Course.is_remediation_math_course == True:
                remediation_math_courses.append(each_Course)
        return remediation_math_courses

    def to_string(self):
        """Create a string representation of the calling CourseGroup object.

        The string consists of the course names, separated by '+' characters.

        Returns:
            String representation of the courses in the calling CourseGroup object.

        """
        stlist = []
        st = ""
        for each_course_object in self.course_list:
            stlist.append(each_course_object.course)
        for idx, each_course in enumerate(sorted(stlist)):
            nextst = each_course
            if idx < len(stlist) - 1: nextst += "+"
            st += nextst
        return st

    def to_spmf_string(self, passing_only=False):
        """Create a string represention of the calling CourseGroup object for SPMF.

        The SPMF sequential pattern mining framework requires a specific input file format.
        Courses in a particular semester must be separated by a space.
        Semesters must be separated by "-1".

        For example, one semester in a SPMF input file could be "MATH110 MATH120 -1" (not
        including the quotation marks).  Each student's entire record would be one line in the
        SPMF input file.

        Args:
            passing_only (bool):  Add only those courses which a student passed to the string.

        Returns:
            SPMF-ready string representation of the courses of the calling CourseGroup object.

        """
        stlist = []
        st = ""
        for each_course_object in self.course_list:
            if passing_only:
                if each_course_object.grade_letter in PASSING_GRADES:
                    stlist.append(each_course_object.course)
            else:
                stlist.append(each_course_object.course)
        for idx, each_course in enumerate(sorted(stlist)):
            nextst = each_course
            nextst += " "
            st += nextst
        st += "-1 "
        return st
