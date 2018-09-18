from utilities.other_constants import *


class Course:
    def __init__(self, semester_number, course, grade, grade_letter, student_id):
        self.semester_number = semester_number
        self.course = course
        self.grade = grade
        self.grade_letter = grade_letter
        self.student_id = student_id
        self.is_math_course = False
        self.is_remediation_math_course = False
        if self.course in MATH_COURSES_SET:  self.is_math_course = True
        if self.course in MATH_REMEDIATION_COURSES_SET: self.is_remediation_math_course = True

    def to_dict(self):
        new_dict = {
            "semester": self.semester_number,
            "course": self.course,
            "grade": self.grade,
            "grade_letter": self.grade_letter,
            "is_math_course": self.is_math_course
        }
        return new_dict

    def to_string(self):
        return self.course  # + "(" + self.grade + ")"
