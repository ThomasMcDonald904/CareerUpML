import math

import numpy
import pandas as pd
import numpy as np

df = pd.read_csv("anonymized_candidate_data.csv")

df["paid_deposit"] = df["deposit_paid_date"].apply(lambda row: 1 if row == str else 0)
df["no_gpa"] = df["grade_point_average"].apply(lambda row: 1 if pd.isnull(row) else 0)
df["grade_point_average"] = df["grade_point_average"].apply(lambda row: 0 if pd.isnull(row) else row)



