import pandas as pd

df = pd.read_csv("cleaned_loan_data.csv")

categorical_columns = [
    "home_ownership",
    "loan_intent",
    "loan_grade",
    "historical_default",
    "Current_loan_status"
]

for column in categorical_columns:
    print(f"\n--- {column} ---")
    print(df[column].value_counts())
    