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
    roc_auc_score,
    brier_score_loss,
    log_loss,
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
# 1. LOAD DATA
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
# 2. CLEAN DATA
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
# 3. FEATURE ENGINEERING
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
# 4. FEATURES AND TARGET
# ==================================================

X = df.drop(
    columns=["Current_loan_status"]
)

y = df["Current_loan_status"]


# ==================================================
# 5. FIRST SPLIT:
#    80% DEVELOPMENT
#    20% TEST
# ==================================================

X_dev, X_test, y_dev, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ==================================================
# 6. SECOND SPLIT:
#    DEVELOPMENT → TRAIN + VALIDATION
#
#    75% of development = TRAIN
#    25% of development = VALIDATION
#
#    Overall:
#
#    TRAIN       = 60%
#    VALIDATION  = 20%
#    TEST        = 20%
# ==================================================

X_train, X_val, y_train, y_val = train_test_split(
    X_dev,
    y_dev,
    test_size=0.25,
    random_state=42,
    stratify=y_dev
)


print("\nDATA SPLIT")
print("=" * 40)

print(
    "Training rows:",
    len(X_train)
)

print(
    "Validation rows:",
    len(X_val)
)

print(
    "Test rows:",
    len(X_test)
)


# ==================================================
# 7. FEATURE GROUPS
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
# 8. PREPROCESSING
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
# 9. BASE RANDOM FOREST
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
# 10. CALIBRATED MODEL
# ==================================================

calibrated_model = CalibratedClassifierCV(
    estimator=base_model,
    method="sigmoid",
    cv=5
)


print(
    "\nTraining calibrated Random Forest..."
)

calibrated_model.fit(
    X_train,
    y_train
)

print(
    "Training complete."
)


# ==================================================
# 11. VALIDATION PROBABILITIES
# ==================================================

classes = list(
    calibrated_model.classes_
)

default_index = classes.index(
    "DEFAULT"
)


val_probabilities = (
    calibrated_model
    .predict_proba(
        X_val
    )[:, default_index]
)


# ==================================================
# 12. SEARCH THRESHOLDS ON VALIDATION SET
# ==================================================

thresholds = np.arange(
    0.30,
    0.71,
    0.01
)


validation_results = []


for threshold in thresholds:

    predictions = np.where(
        val_probabilities >= threshold,
        "DEFAULT",
        "NO DEFAULT"
    )


    precision = precision_score(
        y_val,
        predictions,
        pos_label="DEFAULT"
    )


    recall = recall_score(
        y_val,
        predictions,
        pos_label="DEFAULT"
    )


    f1 = f1_score(
        y_val,
        predictions,
        pos_label="DEFAULT"
    )


    accuracy = accuracy_score(
        y_val,
        predictions
    )


    validation_results.append({
        "threshold": threshold,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1
    })


validation_df = pd.DataFrame(
    validation_results
)


# ==================================================
# 13. FIND BEST VALIDATION THRESHOLD
# ==================================================

best_validation_row = (
    validation_df
    .loc[
        validation_df["f1"].idxmax()
    ]
)


best_threshold = float(
    best_validation_row[
        "threshold"
    ]
)


print(
    "\nBEST THRESHOLD ON VALIDATION SET"
)

print(
    "=" * 40
)


print(
    f"Threshold: "
    f"{best_threshold:.2f}"
)

print(
    f"Accuracy: "
    f"{best_validation_row['accuracy']:.4f}"
)

print(
    f"Precision: "
    f"{best_validation_row['precision']:.4f}"
)

print(
    f"Recall: "
    f"{best_validation_row['recall']:.4f}"
)

print(
    f"F1: "
    f"{best_validation_row['f1']:.4f}"
)


# ==================================================
# 14. SHOW TOP VALIDATION THRESHOLDS
# ==================================================

print(
    "\nTOP 10 VALIDATION THRESHOLDS BY F1"
)

print(
    "=" * 60
)


top_thresholds = (
    validation_df
    .sort_values(
        "f1",
        ascending=False
    )
    .head(10)
)


print(
    top_thresholds.to_string(
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
# 15. FINAL TEST SET PROBABILITIES
# ==================================================

test_probabilities = (
    calibrated_model
    .predict_proba(
        X_test
    )[:, default_index]
)


# ==================================================
# 16. APPLY ONLY THE CHOSEN THRESHOLD
#     TO THE UNTOUCHED TEST SET
# ==================================================

test_predictions = np.where(
    test_probabilities >= best_threshold,
    "DEFAULT",
    "NO DEFAULT"
)


# ==================================================
# 17. FINAL TEST METRICS
# ==================================================

test_accuracy = accuracy_score(
    y_test,
    test_predictions
)

test_precision = precision_score(
    y_test,
    test_predictions,
    pos_label="DEFAULT"
)

test_recall = recall_score(
    y_test,
    test_predictions,
    pos_label="DEFAULT"
)

test_f1 = f1_score(
    y_test,
    test_predictions,
    pos_label="DEFAULT"
)


y_test_binary = (
    y_test == "DEFAULT"
).astype(int)


test_roc_auc = roc_auc_score(
    y_test_binary,
    test_probabilities
)

test_brier = brier_score_loss(
    y_test_binary,
    test_probabilities
)

test_log_loss = log_loss(
    y_test_binary,
    test_probabilities
)


matrix = confusion_matrix(
    y_test,
    test_predictions,
    labels=[
        "NO DEFAULT",
        "DEFAULT"
    ]
)


tn, fp, fn, tp = (
    matrix.ravel()
)


# ==================================================
# 18. FINAL UNTOUCHED TEST RESULTS
# ==================================================

print(
    "\nFINAL UNTOUCHED TEST RESULTS"
)

print(
    "=" * 40
)


print(
    f"Chosen threshold: "
    f"{best_threshold:.2f}"
)


print(
    f"\nAccuracy: "
    f"{test_accuracy:.4f}"
)

print(
    f"Precision: "
    f"{test_precision:.4f}"
)

print(
    f"Recall: "
    f"{test_recall:.4f}"
)

print(
    f"F1: "
    f"{test_f1:.4f}"
)

print(
    f"ROC-AUC: "
    f"{test_roc_auc:.4f}"
)

print(
    f"Brier score: "
    f"{test_brier:.4f}"
)

print(
    f"Log loss: "
    f"{test_log_loss:.4f}"
)


print(
    "\nConfusion Matrix:"
)

print(
    matrix
)


print(
    "\nDetailed counts:"
)

print(
    "True negatives:",
    tn
)

print(
    "False positives:",
    fp
)

print(
    "False negatives:",
    fn
)

print(
    "True positives:",
    tp
)