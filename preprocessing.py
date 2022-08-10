import re
from datetime import date
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

twelve_point_gpa = [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
four_point_gpa = [4.0, 3.9, 3.7, 3.3, 3.0, 2.7, 2.3, 2.0, 1.7, 1.3, 1.0, 0.7, 0]

grade_interp = interp1d(twelve_point_gpa, four_point_gpa)


def normalize_gpa(gpa):
    try:
        gpa = float(gpa)
    except ValueError:
        print(gpa)
        return 0
    if 49 < gpa < 100:
        # GPA on percentage scale
        return gpa/100*4
    elif 4 < gpa < 12:
        # GPA on 12-point scale
        return grade_interp(gpa)
    else:
        # Dummy average GPA value
        return 0

def clean_funding(funding: str):
    if funding == "[]":
        return []
    funding = re.sub(r"\[\"", "", funding)
    funding = re.sub(r"\"]", "", funding)
    funding_sources = funding.split("\", \"")
    return funding_sources


def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


file = open("dateformat.txt", "w+")


def year_format(year: str):
    int_date = []
    str_date = re.split(r'[-/,.]', year)
    for i in str_date:
        int_date.append(int(i))

    if int_date[0] > 31:
        # 1st number is year
        if int_date[1] > 12:
            # Format is YY/DD/MM
            return date(int(str_date[0]), int(str_date[2]), int(str_date[1]))
        else:
            # Format is YY/MM/DD
            return date(int(str_date[0]), int(str_date[1]), int(str_date[2]))
    elif int_date[1] > 31:
        # 2nd number is year
        if int_date[0] > 12:
            # Format is DD/YY/MM
            return date(int(str_date[1]), int(str_date[2]), int(str_date[0]))
        else:
            # Format is MM/YY/DD
            return date(int(str_date[1]), int(str_date[0]), int(str_date[2]))
    else:
        # 3rd number is year
        if int_date[0] > 12:
            # Format is DD/MM/YY
            return date(int(str_date[2]), int(str_date[1]), int(str_date[0]))
        else:
            # Format is MM/DD/YY
            return date(int(str_date[2]), int(str_date[0]), int(str_date[1]))


df = pd.read_csv("anonymized_candidate_data.csv")
df = df[df['date_of_birth'].notna()]

df["paid_deposit"] = df["deposit_paid_date"].apply(lambda row: 1 if row == str else 0)
df["no_gpa"] = df["grade_point_average"].apply(lambda row: 1 if pd.isnull(row) else 0)
df["grade_point_average"] = df["grade_point_average"].apply(lambda row: 0 if pd.isnull(row) else row)
df["grade_point_average"] = df["grade_point_average"].apply(normalize_gpa)
df["payed_deposit"] = df["deposit_paid_date"].apply(lambda row: 0 if pd.isnull(row) else 1)
df["deadline_extension_approved"] = df["deadline_extension_status"].apply(lambda row: 0 if pd.isnull(row) else 1)
df["age"] = df['date_of_birth'].apply(lambda row: calculate_age(year_format(str(row))))
df["applied_for_scholarship"] = df['applied_for_scholarship'].apply(lambda row: 0 if pd.isnull(row) or row == "No" else 1)

df['funding_source_family'] = df["careerup_funding_sources"].apply(lambda row: 1 if 'Family' in clean_funding(row) else 0)
df['funding_source_scholarship'] = df["careerup_funding_sources"].apply(lambda row: 1 if 'Scholarship' in clean_funding(row) else 0)
df['funding_source_loans'] = df["careerup_funding_sources"].apply(lambda row: 1 if 'Loans' in clean_funding(row) else 0)
df['funding_source_careerup_financial_aid'] = df["careerup_funding_sources"].apply(lambda row: 1 if 'CareerUp Financial Aid' in clean_funding(row) else 0)
df['funding_source_university_financing'] = df["careerup_funding_sources"].apply(lambda row: 1 if 'University Financing' in clean_funding(row) else 0)
df['funding_source_myself'] = df["careerup_funding_sources"].apply(lambda row: 1 if 'Myself' in clean_funding(row) else 0)
df['funding_source_other'] = df["careerup_funding_sources"].apply(lambda row: 1 if 'Other' in clean_funding(row) else 0)
df["male"] = df['gender'].apply(lambda row: 1 if row == "Male" else 0)
df["female"] = df['gender'].apply(lambda row: 1 if row == "Female" else 0)
df["rather_not_disclose_gender"] = df['gender'].apply(lambda row: 1 if row == "Rather not disclose" else 0)
df["other_gender"] = df['gender'].apply(lambda row: 1 if row == "Other" else 0)


df.drop(["date_of_birth", "careerup_funding_sources", "application_stage", "payed_deposit", "deposit_paid_date",
         "graduation_date", "graduation_date", "balance_paid_date", "skills", "major", "leadscore", "next_steps_answer",
         "primary_industry", "program_type", "reapply_date", "reapply_previous_application_stage", "time_zone", "gender",
         "convicted_question"],
        axis=1, inplace=True)

df = df.query("age < 70")

df.to_csv("data.csv", index=False)
