"""Define a Course class.
"""

from utilities.other_constants import *


class Course:
    """This class defines attributes and functions associated with a single university course.

    Instances of this class are owned by a particular student and reflect the performance of that
    student in the indicated course.

    """
    def __init__(self, semester_number, course, grade, grade_letter, student_id):

        """Instantiate a Course object.

        Args:
            semester_number (int): Numeric identifier of the semester.
            course (str): Name of the course.
            grade (float): Numeric representation of grade obtained by the student in the course.
            grade_letter (str): Letter grade obtained by the student in the course.
            student_id (str): Nine-character identifier of the student

        """

        self.semester_number = semester_number
        self.course = course
        self.grade = grade
        self.grade_letter = grade_letter
        self.student_id = student_id
        # See utilities/other_constants.py for the lists of Math courses
        self.is_math_course = False
        self.is_remediation_math_course = False
        if self.course in MATH_COURSES_SET:  self.is_math_course = True
        if self.course in MATH_REMEDIATION_COURSES_SET: self.is_remediation_math_course = True

    def to_dict(self):
        """Create a dictionary of some of the fields of this class instance.

        Returns:
            Dictionary mapping relevant fields of an instance of this class.

        """

        new_dict = {
            "semester": self.semester_number,
            "course": self.course,
            "grade": self.grade,
            "grade_letter": self.grade_letter,
            "is_math_course": self.is_math_course
        }
        return new_dict

