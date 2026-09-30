from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
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
    .str.replace("£", "", regex=False)
    .str.replace(",", "", regex=False)
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
# BASE RANDOM FOREST
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


# ==================================================
# CALIBRATED MODEL
# ==================================================

calibrated_model = CalibratedClassifierCV(
    estimator=base_model,
    method="sigmoid",
    cv=5
)


print(
    "Training calibrated Random Forest..."
)

calibrated_model.fit(
    X_train,
    y_train
)

print(
    "Training complete."
)


# ==================================================
# GET CALIBRATED DEFAULT PROBABILITIES
# ==================================================

classes = list(
    calibrated_model.classes_
)

default_index = classes.index(
    "DEFAULT"
)


default_probabilities = (
    calibrated_model.predict_proba(
        X_test
    )[:, default_index]
)


# ==================================================
# TEST DIFFERENT THRESHOLDS
# ==================================================

thresholds = [
    0.52,
    0.54,
    0.55,
    0.56,
    0.57,
    0.58,
    0.60
]

print(
    "\nCALIBRATED THRESHOLD COMPARISON"
)

print(
    "=" * 80
)


results = []


for threshold in thresholds:

    predictions = np.where(
        default_probabilities >= threshold,
        "DEFAULT",
        "NO DEFAULT"
    )


    accuracy = accuracy_score(
        y_test,
        predictions
    )


    precision = precision_score(
        y_test,
        predictions,
        pos_label="DEFAULT"
    )


    recall = recall_score(
        y_test,
        predictions,
        pos_label="DEFAULT"
    )


    f1 = f1_score(
        y_test,
        predictions,
        pos_label="DEFAULT"
    )


    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=[
            "NO DEFAULT",
            "DEFAULT"
        ]
    )


    tn, fp, fn, tp = (
        matrix.ravel()
    )


    results.append({
        "threshold": threshold,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "true_negative": tn,
        "false_positive": fp,
        "false_negative": fn,
        "true_positive": tp
    })


# ==================================================
# DISPLAY RESULTS
# ==================================================

results_df = pd.DataFrame(
    results
)


print(
    results_df.to_string(
        index=False,
        formatters={
            "threshold":
                lambda x:
                f"{x:.2f}",

            "accuracy":
                lambda x:
                f"{x:.4f}",

            "precision":
                lambda x:
                f"{x:.4f}",

            "recall":
                lambda x:
                f"{x:.4f}",

            "f1":
                lambda x:
                f"{x:.4f}"
        }
    )
)


# ==================================================
# FIND BEST F1
# ==================================================

best_row = results_df.loc[
    results_df["f1"].idxmax()
]


print(
    "\nBEST THRESHOLD BY F1"
)

print(
    "===================="
)


print(
    f"Threshold: "
    f"{best_row['threshold']:.2f}"
)


print(
    f"Accuracy: "
    f"{best_row['accuracy']:.4f}"
)


print(
    f"Precision: "
    f"{best_row['precision']:.4f}"
)


print(
    f"Recall: "
    f"{best_row['recall']:.4f}"
)


print(
    f"F1: "
    f"{best_row['f1']:.4f}"
)


print(
    "\nConfusion values:"
)


print(
    "True negatives:",
    int(
        best_row[
            "true_negative"
        ]
    )
)


print(
    "False positives:",
    int(
        best_row[
            "false_positive"
        ]
    )
)


print(
    "False negatives:",
    int(
        best_row[
            "false_negative"
        ]
    )
)


print(
    "True positives:",
    int(
        best_row[
            "true_positive"
        ]
    )
)