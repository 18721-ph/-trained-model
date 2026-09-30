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
    brier_score_loss,
    log_loss,
    roc_auc_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
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
# TRAIN BASE MODEL
# ==================================================

print("Training uncalibrated Random Forest...")

base_model.fit(
    X_train,
    y_train
)

print("Done.")


# ==================================================
# CALIBRATED MODEL
# ==================================================

print(
    "\nTraining calibrated Random Forest..."
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

print("Done.")


# ==================================================
# GET PROBABILITIES
# ==================================================

base_classes = list(
    base_model.classes_
)

base_default_index = (
    base_classes.index("DEFAULT")
)

base_probabilities = (
    base_model.predict_proba(
        X_test
    )[:, base_default_index]
)


calibrated_classes = list(
    calibrated_model.classes_
)

calibrated_default_index = (
    calibrated_classes.index("DEFAULT")
)

calibrated_probabilities = (
    calibrated_model.predict_proba(
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
# PREDICTIONS
# ==================================================

base_predictions = (
    base_model.predict(
        X_test
    )
)

calibrated_predictions = (
    calibrated_model.predict(
        X_test
    )
)


# ==================================================
# EVALUATION FUNCTION
# ==================================================

def evaluate_model(
    name,
    predictions,
    probabilities
):

    print(
        f"\n{name}"
    )

    print(
        "=" * len(name)
    )


    print(
        "Accuracy:",
        accuracy_score(
            y_test,
            predictions
        )
    )


    print(
        "Precision:",
        precision_score(
            y_test,
            predictions,
            pos_label="DEFAULT"
        )
    )


    print(
        "Recall:",
        recall_score(
            y_test,
            predictions,
            pos_label="DEFAULT"
        )
    )


    print(
        "F1:",
        f1_score(
            y_test,
            predictions,
            pos_label="DEFAULT"
        )
    )


    print(
        "ROC-AUC:",
        roc_auc_score(
            y_test_binary,
            probabilities
        )
    )


    print(
        "Brier score:",
        brier_score_loss(
            y_test_binary,
            probabilities
        )
    )


    print(
        "Log loss:",
        log_loss(
            y_test_binary,
            probabilities
        )
    )


# ==================================================
# SHOW RESULTS
# ==================================================

evaluate_model(
    "UNCALIBRATED RANDOM FOREST",
    base_predictions,
    base_probabilities
)

evaluate_model(
    "CALIBRATED RANDOM FOREST",
    calibrated_predictions,
    calibrated_probabilities
)


# ==================================================
# PROBABILITY COMPARISON
# ==================================================

comparison = pd.DataFrame({

    "actual":
        y_test.values,

    "uncalibrated_probability":
        base_probabilities,

    "calibrated_probability":
        calibrated_probabilities

})


comparison[
    "difference"
] = (
    comparison[
        "calibrated_probability"
    ]
    -
    comparison[
        "uncalibrated_probability"
    ]
)


print(
    "\nExamples where calibration "
    "changed the probability most:"
)

print(
    comparison
    .assign(
        abs_difference=lambda x:
            x["difference"].abs()
    )
    .sort_values(
        "abs_difference",
        ascending=False
    )
    .head(20)
    [
        [
            "actual",
            "uncalibrated_probability",
            "calibrated_probability",
            "difference"
        ]
    ]
)