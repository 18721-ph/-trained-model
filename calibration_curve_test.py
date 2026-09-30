from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import (
    CalibratedClassifierCV,
    calibration_curve
)


# ==================================================
# PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "loan_data.csv"
)


# ==================================================
# LOAD DATA
# ==================================================

df = pd.read_csv(DATA_PATH)

df = df.dropna(
    subset=["Current_loan_status"]
)

df = df.drop(
    columns=[
        "customer_id",
        "historical_default"
    ]
)


# ==================================================
# CLEAN DATA
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


for column in [
    "loan_to_income",
    "interest_burden",
    "credit_history_ratio"
]:

    df[column] = (
        df[column]
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
    columns=["Current_loan_status"]
)

y = df["Current_loan_status"]


# ==================================================
# TRAIN / TEST SPLIT
# ==================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


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
# BASE MODEL
# ==================================================

base_model = Pipeline([
    (
        "preprocessor",
        preprocessor
    ),

    (
        "classifier",
        RandomForestClassifier(
            n_estimators=300,
            random_state=42,
            class_weight="balanced",
            n_jobs=-1
        )
    )
])


print(
    "Training uncalibrated model..."
)

base_model.fit(
    X_train,
    y_train
)

print(
    "Done."
)


# ==================================================
# CALIBRATED MODEL
# ==================================================

print(
    "\nTraining calibrated model..."
)

calibrated_model = CalibratedClassifierCV(
    estimator=base_model,
    method="sigmoid",
    cv=5
)

calibrated_model.fit(
    X_train,
    y_train
)

print(
    "Done."
)


# ==================================================
# GET PROBABILITIES
# ==================================================

base_default_index = list(
    base_model.classes_
).index(
    "DEFAULT"
)

calibrated_default_index = list(
    calibrated_model.classes_
).index(
    "DEFAULT"
)


base_probabilities = (
    base_model
    .predict_proba(
        X_test
    )[:, base_default_index]
)


calibrated_probabilities = (
    calibrated_model
    .predict_proba(
        X_test
    )[:, calibrated_default_index]
)


# ==================================================
# BINARY TARGET
# ==================================================

y_test_binary = (
    y_test == "DEFAULT"
).astype(int)


# ==================================================
# CALIBRATION CURVES
# ==================================================

base_true_rate, base_predicted_rate = (
    calibration_curve(
        y_test_binary,
        base_probabilities,
        n_bins=10,
        strategy="quantile"
    )
)


cal_true_rate, cal_predicted_rate = (
    calibration_curve(
        y_test_binary,
        calibrated_probabilities,
        n_bins=10,
        strategy="quantile"
    )
)


# ==================================================
# PRINT TABLES
# ==================================================

print(
    "\nUNCALIBRATED CALIBRATION BINS"
)

print(
    "Predicted probability -> "
    "Observed default rate"
)

for predicted, actual in zip(
    base_predicted_rate,
    base_true_rate
):

    print(
        f"{predicted * 100:6.2f}%"
        f" -> "
        f"{actual * 100:6.2f}%"
    )


print(
    "\nCALIBRATED CALIBRATION BINS"
)

print(
    "Predicted probability -> "
    "Observed default rate"
)

for predicted, actual in zip(
    cal_predicted_rate,
    cal_true_rate
):

    print(
        f"{predicted * 100:6.2f}%"
        f" -> "
        f"{actual * 100:6.2f}%"
    )


# ==================================================
# PLOT
# ==================================================

plt.figure(
    figsize=(8, 6)
)


# Perfect calibration line
plt.plot(
    [0, 1],
    [0, 1],
    linestyle="--",
    label="Perfect calibration"
)


# Uncalibrated
plt.plot(
    base_predicted_rate,
    base_true_rate,
    marker="o",
    label="Uncalibrated Random Forest"
)


# Calibrated
plt.plot(
    cal_predicted_rate,
    cal_true_rate,
    marker="o",
    label="Calibrated Random Forest"
)


plt.xlabel(
    "Mean predicted probability of DEFAULT"
)

plt.ylabel(
    "Observed fraction of DEFAULT"
)

plt.title(
    "Calibration Curve"
)

plt.legend()

plt.grid(True)

plt.tight_layout()

plt.show()