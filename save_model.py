from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# ==================================================
# PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "loan_data.csv"
)

MODEL_DIR = (
    BASE_DIR
    / "model"
)

MODEL_PATH = (
    MODEL_DIR
    / "loan_default_model.joblib"
)


# Create model directory if it does not exist
MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==================================================
# 1. LOAD DATA
# ==================================================

print("Loading loan dataset...")

df = pd.read_csv(DATA_PATH)

print(
    f"Rows loaded: {len(df)}"
)


# ==================================================
# 2. REMOVE ROWS WITHOUT TARGET
# ==================================================

df = df.dropna(
    subset=["Current_loan_status"]
)


# ==================================================
# 3. REMOVE UNUSED / SUSPICIOUS FEATURES
# ==================================================

df = df.drop(
    columns=[
        "customer_id",
        "historical_default"
    ]
)


# ==================================================
# 4. CLEAN NUMERIC COLUMNS
# ==================================================

df["customer_income"] = pd.to_numeric(
    df["customer_income"],
    errors="coerce"
)


# Convert loan amount such as:
#
# £35,000.00
#
# into:
#
# 35000.00

df["loan_amnt"] = (
    df["loan_amnt"]
    .astype(str)
    .str.replace(
        "£",
        "",
        regex=False
    )
    .str.replace(
        ",",
        "",
        regex=False
    )
)

df["loan_amnt"] = pd.to_numeric(
    df["loan_amnt"],
    errors="coerce"
)


# ==================================================
# 5. FEATURE ENGINEERING
# ==================================================

# ----------------------------------------------
# Feature 1:
# Loan amount relative to income
# ----------------------------------------------

df["loan_to_income"] = (
    df["loan_amnt"]
    / df["customer_income"]
)


# ----------------------------------------------
# Feature 2:
# Approximate annual interest amount
#
# Example:
#
# loan = 10,000
# rate = 10%
#
# interest_burden = 1,000
# ----------------------------------------------

df["interest_burden"] = (
    df["loan_amnt"]
    * (
        df["loan_int_rate"]
        / 100
    )
)


# ----------------------------------------------
# Feature 3:
# Credit history relative to age
#
# Example:
#
# age = 40
# credit history = 10 years
#
# ratio = 10 / 40 = 0.25
# ----------------------------------------------

df["credit_history_ratio"] = (
    df["cred_hist_length"]
    / df["customer_age"]
)


# Replace infinity caused by division by zero
engineered_features = [
    "loan_to_income",
    "interest_burden",
    "credit_history_ratio"
]

for feature in engineered_features:

    df[feature] = (
        df[feature]
        .replace(
            [
                np.inf,
                -np.inf
            ],
            np.nan
        )
    )


# ==================================================
# 6. FEATURES AND TARGET
# ==================================================

X = df.drop(
    columns=[
        "Current_loan_status"
    ]
)

y = df[
    "Current_loan_status"
]


# ==================================================
# 7. DEFINE NUMERIC FEATURES
# ==================================================

numeric_features = [
    "customer_age",
    "customer_income",
    "employment_duration",
    "loan_amnt",
    "loan_int_rate",
    "term_years",
    "cred_hist_length",

    # Engineered features
    "loan_to_income",
    "interest_burden",
    "credit_history_ratio"
]


# ==================================================
# 8. DEFINE CATEGORICAL FEATURES
# ==================================================

categorical_features = [
    "home_ownership",
    "loan_intent",
    "loan_grade"
]


# ==================================================
# 9. NUMERIC PREPROCESSING
# ==================================================

numeric_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(
            strategy="median"
        )
    )
])


# ==================================================
# 10. CATEGORICAL PREPROCESSING
# ==================================================

categorical_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(
            strategy="most_frequent"
        )
    ),

    (
        "encoder",
        OneHotEncoder(
            handle_unknown="ignore"
        )
    )
])


# ==================================================
# 11. COMBINE PREPROCESSING
# ==================================================

preprocessor = ColumnTransformer([
    (
        "numeric",
        numeric_pipeline,
        numeric_features
    ),

    (
        "categorical",
        categorical_pipeline,
        categorical_features
    )
])


# ==================================================
# 12. RANDOM FOREST
# ==================================================

classifier = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)


# ==================================================
# 13. FULL PIPELINE
# ==================================================

model = Pipeline([
    (
        "preprocessor",
        preprocessor
    ),

    (
        "classifier",
        classifier
    )
])


# ==================================================
# 14. TRAIN FINAL MODEL
# ==================================================

print(
    "\nTraining final Random Forest model..."
)

print(
    "Engineered features:"
)

for feature in engineered_features:
    print(
        f" - {feature}"
    )


model.fit(
    X,
    y
)


print(
    "\nTraining complete."
)


# ==================================================
# 15. SAVE MODEL
# ==================================================

joblib.dump(
    model,
    MODEL_PATH
)


print(
    f"\nModel saved to:"
)

print(
    MODEL_PATH
)


print(
    "\nFinal training rows:",
    len(X)
)

print(
    "Number of input columns:",
    len(X.columns)
)

print(
    "\nModel classes:",
    model["classifier"].classes_
)