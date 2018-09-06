from utilities import *

class StudentSequence:
    # course_groups holds  ordered list of course groups
    def __init__(self, course_groups=None, student_id=None):
        self.course_sequence = [] if course_groups is None else course_groups
        self.student_id = 0 if student_id == None else student_id

    def add_CourseGroup(self, next_group):
        self.course_sequence.append(next_group)
        self.course_sequence = sorted(self.course_sequence, key=lambda x: x.semester_number)

    def get_student_sequence(self):
        ordered_sequence = sorted(self.course_sequence, key=lambda x: x.semester_number)
        sequence_string = ""
        for each_group in ordered_sequence:
            sequence_string += each_group.to_string() + " "
        return sequence_string[:-1]
