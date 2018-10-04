CONTACTS_FILE = "Contact.csv"
CONTACTS_2016_FILE = "Contact_2016.csv"
# Dictionary of Contacts.csv column names and their new, more convenient names
CONTACT_COLUMNS_DICT = {
    "SFSU_student_ID__c" : "student_id",
    "CurrentCohort__c": "cohort",
    "Race_or_ethnicity_iped_ir__c": "race",
    "AccountId": "category",
    "Applicant_pool_year__c": "applicant_pool_year",
    "First_Generation__c": "first_gen",
    "Household_income__c": "household_income",
    "What_language_at_home__c": "language",
    "Sex_Gender__c": "gender",
    "Country_of_Origin__c": "national_origin",
    "Third_term_persistence__c": "third_persistence",
    "Fifth_term_persistence__c": "fifth_persistence",
    "Seventh_term_persistence__c": "seventh_persistence",
    "Pell_eligible__c": "pell_eligible",
    "Student_Origin__c": "regional_origin",
    "Education_level_mother_or_guardian1_IR__c": "mother_edu",
    "Education_level_father_or_guardian2_IR__c": "father_edu",
    "Current_Metro_Enrollment__c": "current_metro_enrollment",
    "Current_Institution_Enrollment__c": "current_institutional_enrollment",
    "Id": "contact_id"
}
CONTACT_DTYPE_CONVERSIONS_DICT = {
    "SFSU_student_ID__c" : str,
    "UD_Student_ID__c": str,
    "mother_edu": int,
    "father_edu": int
}

CONTACT_STUDENT_TYPES_DICT = {
    "SFSU Students": "Metro",
    "SFSU Comparison Students": "Comp"
}
ACCOUNTS_FILE = "Account.csv"
ACCOUNT_COLUMNS_DICT = {
    "Id": "account_id",
    "Name": "account_name"
}
COHORTS_FILE = "Cohorts__c.csv"
COHORT_COLUMNS_DICT = {
    "Id": "cohort_id",
    "Name": "cohort_name"
}

ENROLLMENTS_FILE = "EnrollmentOpportunity__c.csv"
ENROLLMENT_COLUMNS_DICT = {
    "Id": "enrollment_id",
    "MetroPersistence__c": "metro_persistence",
    "Stage__c": "stage",
    "Contact__c": "student_id",
    "TermNumber__c": "term_number"
}

IR_DATA_DICT = {
    "cohort_sid": "student_id",
    "cohort_year_term": "cohort_year_term",
    "sex": "gender",
    "pell_eligible": "pell_eligible",
    "lst_dept_long": "department",
    "cohort_acad_plan_desc1": "major",
    "ethnic_desc1": "race",
    "rtn_yr1": "third_persistence",
    "rtn_yr2": "fifth_persistence",
    "rtn_yr3": "seventh_persistence",
    "deg_yr4": "fourth_year_graduated",
    "deg_yr5": "fifth_year_graduated",
    "deg_yr6": "sixth_year_graduated",
    "deg_cnt": "graduated",
    "deg_year_term": "graduation_term"
}

IR_PARENT_EDUC_FILE = "parent_educ.csv"
IR_PARENT_EDUC_DICT = {
    "student_id": "student_id",
    "mother_edu": "mother_edu",
    "father_edu": "father_edu",
    "strm": "start_term"
}
IR_PARENT_EDUC_DTYPE_CONVERSIONS_DICT = {
    "strm": int,
    "student_id": str,
    "mother_edu": str,
    "father_edu": str
}

PATHWAYS_FILE = "Pathways.csv"
QUERY_DATA_DIR = "query_data"

SPMF_EXECUTABLE = "spmf.jar"
