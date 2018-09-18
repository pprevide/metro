import os, sys
import pandas as pd
import numpy as np

from configuration import DATA_DIR, HOME_DIR
from utilities.helpers import *
from utilities.tables import *
from utilities.file_constants import *



def preprocessing(metro_only=False, attributes_only=False, contacts_through_2016 = True):

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
    contacts_df['cohort_year'] = contacts_df['cohort'].str[-4:]
    contacts_df['cohort'] = contacts_df['cohort'].str[:-5]

    # Read the EnrollmentOpportunity csv 
    enrollments_data_file = os.path.join(DATA_DIR, ENROLLMENTS_FILE)
    enrollments_df = pd.read_csv(enrollments_data_file,
                                 low_memory=False,
                                 usecols=ENROLLMENT_COLUMNS_DICT.keys())
    enrollments_df.rename(columns=ENROLLMENT_COLUMNS_DICT, inplace=True)
    enrollments_df.set_index("enrollment_id", verify_integrity=True, inplace=True)


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
    print "metro students: ", len(metro_students_set.intersection(set(contacts_df['student_id'].values)))
    print "comp students: ",  len(comp_students_set.intersection(set(contacts_df['student_id'].values)))
    print contacts_df.loc[ list(metro_students_set)[0]]
    print contacts_df[contacts_df['father_edu']==5].head()
    contacts_df[contacts_df["category"]=="Metro"].to_csv(os.path.join(HOME_DIR, "outputcsv"), index=False)


   # print contacts_df['student_id'].head()












if __name__ == '__main__':
    preprocessing()
