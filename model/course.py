from utilities.constants import *


class Course:
    def __init__(self, semester, course, grade_number, grade, student_id):
        self.semester = semester
        self.course = course
        self.grade_number = grade_number
        self.grade = grade
        self.student_id = student_id
        self.is_math_course = False
        self.is_remediation_math_course = False
        if self.course in MATH_COURSES_SET:  self.is_math_course = True
        if self.course in MATH_REMEDIATION_COURSES_SET: self.is_remediation_math_course = True

    def to_dict(self):
        new_dict = {
            "semester": self.semester,
            "course": self.course,
            "grade_number": self.grade_number,
            "grade": self.grade,
            "is_math_course": self.is_math_course
        }
        return new_dict

    def to_string(self):
        return self.course  # + "(" + self.grade + ")"
