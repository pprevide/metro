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
    SEMESTERS_TO_NUMBERS_DICT, VALID_GRADES, SEMESTERS_LIST


def preprocessing(metro_only=False, metro_comp=False, contacts_through_2016 = True):

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
    # Read pathway information associated with each Metro cohort
    #   Return a dictionary that maps cohort names to Pathway objects
    cohort_pathway_dict = pathway.Pathway.make_cohort_pathway_dict()
    contacts_df['Pathway'] = contacts_df['cohort'].map(cohort_pathway_dict)

    # Read the EnrollmentOpportunity csv
    enrollments_data_file = os.path.join(DATA_DIR, ENROLLMENTS_FILE)
    enrollments_df = pd.read_csv(enrollments_data_file,
                                 low_memory=False,
                                 usecols=ENROLLMENT_COLUMNS_DICT.keys())
    enrollments_df.rename(columns=ENROLLMENT_COLUMNS_DICT, inplace=True)
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
    for each_file in query_files:
        header_row, rows = Csv(csv_file=os.path.join(os.path.join(DATA_DIR, QUERY_DATA_DIR), each_file),
                               has_duplicate_column_names=True
                               ).read_csv()
        print "Reading ", each_file, ": ", len(rows)
        print header_row
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

