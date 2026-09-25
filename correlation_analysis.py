import pandas as pd

df = pd.read_csv("cleaned_loan_data.csv")

# Create a temporary numeric version of the target
# ONLY for exploratory analysis.
df["default_numeric"] = df["Current_loan_status"].map({
    "NO DEFAULT": 0,
    "DEFAULT": 1
})

numeric_columns = [
    "customer_age",
    "customer_income",
    "employment_duration",
    "loan_amnt",
    "loan_int_rate",
    "term_years",
    "cred_hist_length",
    "default_numeric"
]

correlations = df[numeric_columns].corr()

print("\nCorrelation matrix:")
print(correlations)

print("\nCorrelation with loan default:")
print(
    correlations["default_numeric"]
    .sort_values(ascending=False)
)