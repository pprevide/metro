from utilities.other_constants import *


duplicate_courses_set = set()
students_with_duplicate_courses_set = set()

class CourseGroup:
    # course_list holds a list of Course objects
    def __init__(self,
                 course_list=None, term_number=None, semester_number=None,
                 major=None, major_second=None, level=None,
                 term_gpa=None, term_units=None,
                 cumulative_gpa=None, cumulative_units=None,
                 student_id=None):
        self.course_list = [] if course_list is None else course_list
        self.term_number = term_number  # 0 if term_number is None else term_number
        self.semester_number = semester_number  # 0 if semester_number is None else semester_number
        self.major = major
        self.major_second = major_second
        self.level = level
        self.term_gpa = term_gpa
        self.term_units = term_units
        self.cumulative_gpa = cumulative_gpa
        self.cumulative_units = cumulative_units
        self.student_id = student_id
        self.course_names_set = set()

    def get_numbered_course_group(self):
        course_string = "[" + str(self.semester_number) + ": {"
        for idx, each in enumerate(list(self.course_list)):
            if idx > 0: course_string += ", "
            course_string += each.to_string()
        course_string += "}]"
        return course_string

    def get_number_of_courses(self):
        return len(self.course_list)

    def add_Course(self, new_course):  # takes a Course object as argument
        if new_course.course not in self.course_names_set:
            self.course_list.append(new_course)
            self.course_names_set.add(new_course.course)
        else:
            new_grade = new_course.grade
            old_grade = None
            old_course = None
            for each_course in self.course_list:
                if each_course.course == new_course.course:
                    old_grade = each_course.grade
                    old_course = each_course
                    if old_grade!=new_grade:
                        duplicate_courses_set.add(new_course.course)
                        students_with_duplicate_courses_set.add(self.student_id)

    def get_math_courses(self):  # return list, possibly empty, of Math Course objects in this CourseGroup
        math_courses = []
        for each_Course in self.course_list:
            if each_Course.is_math_course == True:
                math_courses.append(each_Course)
        return math_courses

    # return list, possibly empty, of remedial Math Course objects in this CourseGroup
    def get_remediation_math_courses(self):
        remediation_math_courses = []
        for each_Course in self.course_list:
            if each_Course.is_remediation_math_course == True:
                remediation_math_courses.append(each_Course)
        return remediation_math_courses

    def to_string(self):
        stlist = []
        st = ""
        for each_course_object in self.course_list:
            stlist.append(each_course_object.course)
        for idx, each_course in enumerate(sorted(stlist)):
            nextst = each_course
            if idx < len(stlist) - 1: nextst += "+"
            st += nextst
        return st

    def to_spmf_string(self):
        stlist = []
        st = ""
        for each_course_object in self.course_list:
            stlist.append(each_course_object.course)
        for idx, each_course in enumerate(sorted(stlist)):
            nextst = each_course
            nextst += " "
            st += nextst
        st += "-1 "
        return st
