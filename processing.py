"""Collect and organize data from all sources.

This module pulls together all the student data, performs transformations
and some feature engineering, and populates certain data structures.  These
structures are made available to other modules and can be used for
analysis of student performance and demographics data.

Functions exported by this module include:
    preprocessing(): collect, transform, and return structures for student data

"""

import os, sys
import pandas as pd
import numpy as np
import time
from configuration import DATA_DIR, HOME_DIR
from model import course, course_group, pathway
from utilities.helpers import parse_term_from_filename
from utilities.tables import Csv
from utilities.file_constants import *
from utilities.other_constants import GRADE_POINT_DICT, GRADE_OUTCOME_DICT, NUMBERS_TO_SEMESTERS_DICT, \
    SEMESTERS_TO_NUMBERS_DICT, VALID_GRADES, SEMESTERS_LIST, RACE_RENAMING_DICT, INCOME_CATEGORIES_DICT,\
    INCOMPLETE_GRADES


def preprocessing(metro_only=False, metro_comp=False, contacts_through_2016=True,
                  attributes_only=False):
    """Collect, transform, feature-engineer, and return student data for analysis by callers.

    The student data exists as a collection of csv files, which are stored in the /data directory.
    This function reads those files and processes the data.
    These csv files are exported from different sources:
        1. The Salesforce org for the Metro program: these files are created using Salesforce's Data
            Export feature.  Each table corresponds to one of the Salesforce record types.
        2. The SFSU Campus Solutions (CS) querying system: these files represent the output of a particular
            query for a particular term.
        3. The SFSU Institutional Research (IR) department has made some student demographic data available
            that is not otherwise available from Salesforce or from CS queries.
    Students fall into three exclusive groups: Metro students; Comparison students, and
        everyone else.  Some data studies will be concerned with only Metro students, while others
        may want to compare Metro and Comparison student outcomes or properties.  The parameters listed
        below enable these different types of studies.

    Args:
        metro_only (bool): Consider and return information for Metro students only.
        metro_comp (bool): Consider and return for Metro and Comparison students only.
        contacts_through_2016 (bool): If true, only students in 2009-2016 cohort years are considered.
        attributes_only (bool): If true, consider and return only the demographic and personal attributes of
        students.  If false, the semester-by-semester academic performance of the students is also
        collected, engineered, and returned.

    Returns: The tuple (contacts_df, student_record_dict, roster_dict).
        contacts_df is a pandas dataframe containing student demographic and personal attributes.
        student_record_dict is a Python dictionary whose keys are student id's and whose values are
            Python dictionaries, which in turn map semester numbers (i.e., Fall 2009 is 1, Winter 2009
                is 2, etc.) to CourseGroup objects (see the model/course_group.py file).
                If attributes_only, the student_record_dict is None.
        roster_dict is a Python dictionary that maps the strings "metro", "comp", and "combined" to
            Python sets containing the student id's for Metro, Comparison and Metro plus Comparison students
            respectively.

    """

    ##########################################
    ##### Information Specific to Metro ######
    ##########################################

    # Read Contacts file
    contact_data_file = os.path.join(DATA_DIR, CONTACTS_FILE)
    contacts_df = pd.read_csv(contact_data_file,
                              low_memory=False,
                              usecols=CONTACT_COLUMNS_DICT.keys(),
                              dtype=CONTACT_DTYPE_CONVERSIONS_DICT
                              )
    contacts_df.rename(columns=CONTACT_COLUMNS_DICT, inplace=True)
    # if desired, limit the Contact records to those from 2009-2016 start terms
    if contacts_through_2016:
        contacts_df = contacts_df[~contacts_df['applicant_pool_year'].isin(['2017-2018', '2016-2017', np.nan])]
    contacts_df = contacts_df[~contacts_df['applicant_pool_year'].isnull()]


    # Read Accounts file
    account_data_file = os.path.join(DATA_DIR, ACCOUNTS_FILE)
    accounts_df = pd.read_csv(account_data_file,
                              low_memory=False,
                              usecols=ACCOUNT_COLUMNS_DICT.keys())
    accounts_df.rename(columns=ACCOUNT_COLUMNS_DICT, inplace=True)

    # In Contacts df, replace Account Id with Account name
    contacts_df['category'].replace(accounts_df
                        .set_index("account_id", verify_integrity=True)
                        .to_dict()["account_name"],
                        inplace=True)
    contacts_df['category'].replace(CONTACT_STUDENT_TYPES_DICT, inplace=True)
    # remove rows of Contacts that are not SFSU Students or SFSU Comparison Students
    contacts_df = contacts_df[contacts_df["category"].isin(CONTACT_STUDENT_TYPES_DICT.values())]

    # Add the students' cohorts
    cohort_data_file = os.path.join(DATA_DIR, COHORTS_FILE)
    cohorts_df = pd.read_csv(cohort_data_file,
                             low_memory=False,
                             usecols=COHORT_COLUMNS_DICT.keys())
    cohorts_df.rename(columns=COHORT_COLUMNS_DICT, inplace=True)
    # In contacts_df, replace Cohort identifier with Cohort name
    contacts_df.replace(cohorts_df
                        .set_index("cohort_id", verify_integrity=True)
                        .to_dict()["cohort_name"],
                        inplace=True)
    contacts_df['cohort_year'] = contacts_df['cohort'].str[-4:].astype('int32')
    contacts_df['cohort_name'] = contacts_df['cohort'].str[:-5]
    contacts_df = contacts_df[~contacts_df['cohort_year'].isin([2017])]

    # Create pools for Metro students, comparison students, and both
    combined_students_set = set(contacts_df.loc[contacts_df["category"]
                             .isin(["Metro", "Comp"]), "student_id"]
                             .values)
    metro_students_set = set(contacts_df.loc[contacts_df["category"]
                           .isin(["Metro"]), "student_id"]
                           .values)
    comp_students_set = set(contacts_df.loc[contacts_df["category"]
                             .isin(["Comp"]), "student_id"]
                             .values)

    #################################
    #####  Pathways Processing  #####
    #################################
    # Each Metro student is assigned to a cohort, which in turn follows a specific pathway, or sequence,
    #   of 3 foundational Metro courses.  See the model/pathway.py file for more information.

    # Read pathway information associated with each Metro cohort
    #   Return a dictionary that maps cohort names to Pathway objects
    cohort_pathway_dict = pathway.Pathway.make_cohort_pathway_dict()
    contacts_df['Pathway'] = contacts_df['cohort'].map(cohort_pathway_dict)

    # Read the Terms csv so that EnrollmentOpportunity terms can be determined
    terms_data_file = os.path.join(DATA_DIR, TERMS_FILE)
    terms_df = pd.read_csv(terms_data_file,
                           low_memory=False,
                           usecols=TERM_COLUMNS_DICT.keys())
    terms_df.rename(columns=TERM_COLUMNS_DICT, inplace=True)
    # remove unneeded term objects
    terms_df = terms_df[(terms_df["term_name"].str.contains("SFSU")) \
        & (~terms_df["term_name"].str.contains("COMP"))]
    # remove leading unwanted characters in the term names
    terms_df["term_name"] = terms_df["term_name"].map(lambda x : x[5:])
    terms_df.set_index("term_id", verify_integrity=True, inplace=True)


    # Read the EnrollmentOpportunity csv
    enrollments_data_file = os.path.join(DATA_DIR, ENROLLMENTS_FILE)
    enrollments_df = pd.read_csv(enrollments_data_file,
                                 low_memory=False,
                                 usecols=ENROLLMENT_COLUMNS_DICT.keys())
    enrollments_df.rename(columns=ENROLLMENT_COLUMNS_DICT, inplace=True)
    # replace the Term ID with the term number from the Terms csv
    contacts_df.replace(cohorts_df
                        .set_index("cohort_id", verify_integrity=True)
                        .to_dict()["cohort_name"],
                        inplace=True)
    enrollments_df.replace(terms_df.to_dict()["term_name"], inplace=True)
    enrollments_df.set_index("enrollment_id", verify_integrity=True, inplace=True)
    graduates_df = enrollments_df.drop_duplicates(subset=["student_id", "stage"], keep="first")[['student_id', "stage"]]
    graduates_df["student_id"].replace(contacts_df
                           .set_index("contact_id", verify_integrity=True)
                           .to_dict()['student_id'],
                            inplace=True)
    grouped = graduates_df.groupby("student_id")
    def get_result(df):
        stages_set = set(df["stage"].values)
        if 'Graduated' in stages_set:
            return 'Graduated'
        else:
            if 'Left Institution' in stages_set:
                return "Left"
            else:
                return "Open"
    aggregated = grouped.apply(get_result)
    contacts_df['result'] = contacts_df['student_id'].map(aggregated.to_dict())

    ##########################################
    #####   Information for all FTFTF   ######
    ##########################################

    # Read and create a data frame for IR data
    ir_df = pd.DataFrame()
    for f in sorted([x for x in os.listdir(os.path.join(DATA_DIR, "IR_data"))
                     if "FTFTF_Fall" in x and x[0]!='~']):
        df = pd.read_csv(os.path.join((os.path.join(DATA_DIR, "IR_data")), f),
                         usecols=IR_DATA_DICT.keys(),
                         dtype=str)
        ir_df = pd.concat([ir_df, df], ignore_index=True)
    ir_df.rename(columns=IR_DATA_DICT, inplace=True)
    # Students who withdrew, then started again, appear in the IR data twice
    # Keep the latter record for those students
    ir_df.set_index(keys='student_id', inplace=True, drop=False)
    ir_df.drop_duplicates(subset='student_id', keep='last', inplace=True)
    if len(ir_df.index.get_duplicates())>0:
        raise ValueError("The IR dataframe has duplicated indexes before merging with parents' education.")

    # Add parents' education levels from remaining IR file
    parents_df = pd.read_csv(os.path.join(os.path.join(DATA_DIR, "IR_data"), IR_PARENT_EDUC_FILE),
                             usecols=IR_PARENT_EDUC_DICT.keys(),
                             dtype=IR_PARENT_EDUC_DTYPE_CONVERSIONS_DICT
                             )
    parents_df.rename(columns=IR_PARENT_EDUC_DICT, inplace=True)
    # remove rows whose terms are prior to 2009
    parents_df = parents_df[parents_df["start_term"]>2090]
    parents_df.set_index(keys='student_id', inplace=True, verify_integrity=True, drop=False)


    # Combine parents' education levels into the ir_df data frame
    ir_df = ir_df.merge(parents_df, on='student_id', how='outer')
    ir_df.set_index(keys="student_id", inplace=True, verify_integrity=True, drop=False)
    if len(ir_df.index.get_duplicates())>0:
        raise ValueError("The IR dataframe has duplicated indexes before merging with contacts.")
    # Now combine the attributes data contained in ir_df into contacts_df
    contacts_df.set_index(keys='student_id', inplace=True, verify_integrity=True, drop=False)
    contacts_df = contacts_df.combine_first(ir_df)

    # Transform race and household-income values into more readable labels
    contacts_df["race"].replace(RACE_RENAMING_DICT, inplace=True)
    contacts_df.loc[~contacts_df["race"].isin(RACE_RENAMING_DICT.values()), "race"] = "Other"
    contacts_df["household_income"].replace(INCOME_CATEGORIES_DICT, inplace=True)
    contacts_df.loc[~contacts_df["household_income"].isin(INCOME_CATEGORIES_DICT.values()),
                    "household_income"] = np.nan

    if attributes_only:
        if metro_only:
            contacts_df = contacts_df[contacts_df["category"] == "Metro"]
        else:
            if metro_comp:
                contacts_df = contacts_df[contacts_df["category"].isin(["Metro", "Comp"])]
        roster_dict = {"metro": metro_students_set,
                       "comp": comp_students_set,
                       "combined": combined_students_set}
        return contacts_df, None, roster_dict

    #################################
    ##### Enrollment Processing #####
    #################################

    semesters_to_numbers_dict = dict()  # maps semester names ("Fall 2009") to semester numbers (1)
    numbers_to_semesters_dict = dict()  # maps semester numbers (1) to semester names ("Fall 2009")

    semester_no = 1
    for each_semester in SEMESTERS_LIST:
        semesters_to_numbers_dict[each_semester] = semester_no
        numbers_to_semesters_dict[semester_no] = each_semester
        semester_no += 1

    student_record_dict = dict()   # map each student id to a dictionary of term->CourseGroup key-value pairs
    # Incorporate term-by-term enrollment data in a dict
    query_files = sorted(os.listdir(os.path.join(DATA_DIR, QUERY_DATA_DIR)))
    total_rows_read = 0
    for idx, each_file in enumerate(query_files):
        header_row, rows = Csv(csv_file=os.path.join(os.path.join(DATA_DIR, QUERY_DATA_DIR), each_file),
                               has_duplicate_column_names=True
                               ).read_csv()
        print "Reading file", idx+1, "of", len(query_files), "...", each_file, "# rows:", len(rows)
        for idx, row in enumerate(rows):
            total_rows_read+=1
            student_id = row["SF State ID"]
            status = row["Status"]
            grade_letter = row["Grade"]
            # Skip this row of the csv file if conditions warrant
            if status != "Enrolled" or grade_letter not in VALID_GRADES: continue
            if metro_only and student_id not in metro_students_set : continue
            else:
                if metro_comp and student_id not in combined_students_set: continue
            grade = GRADE_POINT_DICT[grade_letter]
            #admit_term = row["Admit Term"]
            semester = SEMESTERS_TO_NUMBERS_DICT[parse_term_from_filename(each_file)]
            semester_number = semester
            course_name = row["Class"].replace(" ", "")
            this_course_object = course.Course(semester_number=semester_number,
                                               course=course_name,
                                               grade=grade,
                                               grade_letter=grade_letter,
                                               student_id=student_id)
            # Add it to this student's CourseGroup for that term
            #     First check if student exists in the outer dict yet:
            try:
                term_CourseGroup_dict = student_record_dict[student_id]
                # If student has a CourseGroup for this semester, add this Course to it
                try:
                    current_CourseGroup = term_CourseGroup_dict[semester_number]
                    current_CourseGroup.add_Course(this_course_object)
                    term_CourseGroup_dict[semester_number] = current_CourseGroup
                # if a student has no CourseGroup yet for this semester, create it
                except:
                    new_CourseGroup = course_group.CourseGroup(semester_number=semester_number,
                                                               student_id=student_id)
                    new_CourseGroup.add_Course(this_course_object)
                    term_CourseGroup_dict[semester_number] = new_CourseGroup
                student_record_dict[student_id] = term_CourseGroup_dict
            # If a student doesn't exist in the outer dict yet, create a dictionary
            #     and add the first term->CourseGroup key-value pair to it
            except KeyError:
                term_CourseGroup_dict = dict()
                new_CourseGroup = course_group.CourseGroup(semester_number=semester_number,
                                                           student_id=student_id)
                new_CourseGroup.add_Course(this_course_object)
                term_CourseGroup_dict[semester_number] = new_CourseGroup
                student_record_dict[student_id] = term_CourseGroup_dict

    # need the student_records_dict to be limited only to its comp students
    comp_students_full_set = set(contacts_df["student_id"].values).intersection(student_record_dict)
    contacts_df = contacts_df[contacts_df["student_id"].isin(comp_students_full_set)]

    # Use this student_records_dict to compute
    #     (1) core-pathway progress (0 for Comp students) and
    #     (2) 4th-term completion
    # Add these fields to each student record

    progress_df = pd.DataFrame(columns=["student_id", "core_progress"])
    fourth_term_completion_df = pd.DataFrame(columns=["student_id", "fourth_completion"])
    for idx, student_id in enumerate(student_record_dict):
        this_student_records_dict = student_record_dict[student_id]
        cohort_year = str(int(contacts_df.loc[contacts_df["student_id"] == student_id, "cohort_year"].item()))
        first_term_numeric = SEMESTERS_TO_NUMBERS_DICT["Fall "+cohort_year]
        first_4_terms_set = set(range(first_term_numeric, first_term_numeric+7, 2))
        if first_term_numeric+6 not in this_student_records_dict.keys()\
                or len(first_4_terms_set.intersection(this_student_records_dict.keys()))<3:
            fourth_completion = False
        else:
            try:
                fourthcoursegroup = this_student_records_dict[first_term_numeric+6]
                incomplete = True
                courses = []
                for this_course in fourthcoursegroup.course_list:
                    courses.append( (this_course.course, this_course.grade_letter))
                    if this_course.grade_letter not in INCOMPLETE_GRADES:
                        incomplete = False
                        fourth_completion = True
                        break
                if incomplete:
                    fourth_completion = False
            except KeyError:
                fourth_completion = False
        fourth_term_completion_df = fourth_term_completion_df\
            .append(pd.DataFrame({"student_id":[student_id],
                                  "fourth_completion": [fourth_completion]}),
                    ignore_index=True)
        # Now populate the progress data frame
        # Metro students have a Pathway - compute how many courses from it were taken
        # Comp students do not have a Pathway: core progress is 0
        try:
            pathway_obj = contacts_df.loc[contacts_df["student_id"] == student_id, "Pathway"].item()
            core_courses_list = pathway_obj.get_core_sequence_list()
            this_student_courses_set = set()
            for each_CourseGroup in this_student_records_dict.values():
                this_student_courses_set.update(each_CourseGroup.passing_course_names_set)
            this_student_progress = len(list(set(core_courses_list).intersection(this_student_courses_set)))
        except AttributeError:
            this_student_progress = 0
        progress_df = progress_df.append(
            pd.DataFrame(
                {"student_id": [student_id], "core_progress": [this_student_progress]}
            ), ignore_index=True)
    progress_df["core_progress"] = progress_df["core_progress"].astype('int8')
    contacts_df = contacts_df.merge(progress_df, how="outer", on="student_id") \
        .merge(fourth_term_completion_df, how = "outer", on="student_id")

    # Prepare the data structures to be returned to the caller

    roster_dict = {"metro": metro_students_set,
                   "comp": comp_students_set,
                   "combined": combined_students_set}

    if metro_only:
        contacts_df = contacts_df[contacts_df["category"]=="Metro"]
    else:
        if metro_comp:
            contacts_df = contacts_df[contacts_df["category"].isin(["Metro", "Comp"])]
    print "total rows read: ", total_rows_read

    return contacts_df, student_record_dict, roster_dict


if __name__ == '__main__':
    contacts_df, student_record_dict, roster_dict = preprocessing(metro_comp=True)

