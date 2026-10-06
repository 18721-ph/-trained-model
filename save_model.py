from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.calibration import CalibratedClassifierCV


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

BASE_MODEL_PATH = (
    MODEL_DIR
    / "base_random_forest.joblib"
)

CALIBRATED_MODEL_PATH = (
    MODEL_DIR
    / "calibrated_loan_default_model.joblib"
)


MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==================================================
# LOAD DATA
# ==================================================

print("Loading dataset...")

df = pd.read_csv(
    DATA_PATH
)

print(
    "Rows loaded:",
    len(df)
)


# ==================================================
# REMOVE MISSING TARGET
# ==================================================

df = df.dropna(
    subset=[
        "Current_loan_status"
    ]
)


# ==================================================
# REMOVE UNUSED FEATURES
# ==================================================

df = df.drop(
    columns=[
        "customer_id",
        "historical_default"
    ]
)


# ==================================================
# CLEAN NUMERIC COLUMNS
# ==================================================

df["customer_income"] = pd.to_numeric(
    df["customer_income"],
    errors="coerce"
)


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
# FEATURE ENGINEERING
# ==================================================

df["loan_to_income"] = (
    df["loan_amnt"]
    / df["customer_income"]
)


df["interest_burden"] = (
    df["loan_amnt"]
    * (
        df["loan_int_rate"]
        / 100
    )
)


df["credit_history_ratio"] = (
    df["cred_hist_length"]
    / df["customer_age"]
)


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
# FEATURES / TARGET
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
# FEATURE GROUPS
# ==================================================

numeric_features = [
    "customer_age",
    "customer_income",
    "employment_duration",
    "loan_amnt",
    "loan_int_rate",
    "term_years",
    "cred_hist_length",
    "loan_to_income",
    "interest_burden",
    "credit_history_ratio"
]


categorical_features = [
    "home_ownership",
    "loan_intent",
    "loan_grade"
]


# ==================================================
# PREPROCESSING
# ==================================================

numeric_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(
            strategy="median"
        )
    )
])


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
# FUNCTION TO CREATE RANDOM FOREST PIPELINE
# ==================================================

def create_base_model():

    classifier = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1
    )

    return Pipeline([
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
# TRAIN BASE MODEL
#
# This model will mainly be used for SHAP.
# ==================================================

print(
    "\nTraining base Random Forest..."
)

base_model = create_base_model()

base_model.fit(
    X,
    y
)

print(
    "Base Random Forest training complete."
)


# ==================================================
# TRAIN CALIBRATED MODEL
#
# Uses 5-fold calibration internally.
# ==================================================

print(
    "\nTraining calibrated Random Forest..."
)

calibration_base_model = create_base_model()


calibrated_model = CalibratedClassifierCV(
    estimator=calibration_base_model,
    method="sigmoid",
    cv=5
)


calibrated_model.fit(
    X,
    y
)


print(
    "Calibrated model training complete."
)


# ==================================================
# SAVE MODELS
# ==================================================

joblib.dump(
    base_model,
    BASE_MODEL_PATH
)


joblib.dump(
    calibrated_model,
    CALIBRATED_MODEL_PATH
)


# ==================================================
# OUTPUT
# ==================================================

print(
    "\n================================"
)

print(
    "MODELS SAVED"
)

print(
    "================================"
)


print(
    "\nBase Random Forest:"
)

print(
    BASE_MODEL_PATH
)


print(
    "\nCalibrated Random Forest:"
)

print(
    CALIBRATED_MODEL_PATH
)


print(
    "\nTraining rows:",
    len(X)
)


print(
    "Input columns:",
    len(X.columns)
)


print(
    "\nClasses:"
)

print(
    calibrated_model.classes_
)


print(
    "\nEngineered features:"
)

for feature in engineered_features:

    print(
        "-",
        feature
    )