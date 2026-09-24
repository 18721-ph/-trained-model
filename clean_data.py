import pandas as pd

# Load the original dataset
df = pd.read_csv("loan_data.csv")

print("Original shape:")
print(df.shape)


# --------------------------------------------------
# 1. Remove rows where our TARGET is missing
# --------------------------------------------------

df = df.dropna(subset=["Current_loan_status"])


# --------------------------------------------------
# 2. Drop customer_id
# --------------------------------------------------

df = df.drop(columns=["customer_id"])


# --------------------------------------------------
# 3. Convert customer_income into a number
# --------------------------------------------------

df["customer_income"] = pd.to_numeric(
    df["customer_income"],
    errors="coerce"
)


# --------------------------------------------------
# 4. Clean loan_amnt
# --------------------------------------------------

df["loan_amnt"] = (
    df["loan_amnt"]
    .str.replace("£", "", regex=False)
    .str.replace(",", "", regex=False)
)

df["loan_amnt"] = pd.to_numeric(
    df["loan_amnt"],
    errors="coerce"
)


# --------------------------------------------------
# 5. Handle historical_default
# --------------------------------------------------

df["historical_default"] = df["historical_default"].fillna("UNKNOWN")


# --------------------------------------------------
# 6. Fill missing numerical values
# --------------------------------------------------

df["employment_duration"] = df["employment_duration"].fillna(
    df["employment_duration"].median()
)

df["loan_int_rate"] = df["loan_int_rate"].fillna(
    df["loan_int_rate"].median()
)

df["customer_income"] = df["customer_income"].fillna(
    df["customer_income"].median()
)

df["loan_amnt"] = df["loan_amnt"].fillna(
    df["loan_amnt"].median()
)


# --------------------------------------------------
# Inspect the result
# --------------------------------------------------

print("\nCleaned shape:")
print(df.shape)

print("\nMissing values after cleaning:")
print(df.isnull().sum())

print("\nData types:")
print(df.dtypes)

print("\nFirst five rows:")
print(df.head())


# --------------------------------------------------
# Save our cleaned dataset
# --------------------------------------------------

df.to_csv("cleaned_loan_data.csv", index=False)

print("\nCleaned dataset saved as cleaned_loan_data.csv")