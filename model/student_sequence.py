"""Define a Student Sequence class.

"""

class StudentSequence:
    """This class describes an entire record of the academic career of a student.

    It consists of the CourseGroup objects representing the courses, grades, and other information
    for that student for every semester where the student took one or more classes.

    """
    # course_groups holds  ordered list of course groups
    def __init__(self, course_groups=None, student_id=None):
        """Instantiate a StudentSequence object.

        Args:
            course_groups (list): The CourseGroup objects, sorted by semester.
            student_id (str): The student's identifier.
        """

        self.course_sequence = [] if course_groups is None else course_groups
        self.student_id = 0 if student_id == None else student_id

    def add_CourseGroup(self, next_group):
        """Add a CourseGroup instance to this StudentSequence instance.

        Args:
            next_group (CourseGroup): The CourseGroup to add.

        Returns:
            None

        """

        self.course_sequence.append(next_group)
        self.course_sequence = sorted(self.course_sequence, key=lambda x: x.semester_number)

    def get_student_sequence(self):
        """Create a string representation of this StudentSequence.

        Each semester's string representation is that returned by the CourseGroup instance.
        The string representation is ordered by semester.

        Returns:
            String representation of the courses in this StudentSequence, sorted by semester.

        """

        ordered_sequence = sorted(self.course_sequence, key=lambda x: x.semester_number)
        sequence_string = ""
        for each_group in ordered_sequence:
            sequence_string += each_group.to_string() + " "
        return sequence_string[:-1]
