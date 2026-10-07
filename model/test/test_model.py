from pathlib import Path

import joblib
import json
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent.parent

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

METADATA_PATH = (
    MODEL_DIR
    / "model_metadata.json"
)


# ==================================================
# TEST 1
# Model files exist
# ==================================================

def test_model_files_exist():

    assert BASE_MODEL_PATH.exists()

    assert CALIBRATED_MODEL_PATH.exists()

    assert METADATA_PATH.exists()


# ==================================================
# TEST 2
# Models can be loaded
# ==================================================

def test_models_load():

    base_model = joblib.load(
        BASE_MODEL_PATH
    )

    calibrated_model = joblib.load(
        CALIBRATED_MODEL_PATH
    )

    assert base_model is not None

    assert calibrated_model is not None


# ==================================================
# TEST 3
# Metadata loads correctly
# ==================================================

def test_metadata_loads():

    with open(
        METADATA_PATH,
        "r"
    ) as file:

        metadata = json.load(
            file
        )

    assert "model_version" in metadata

    assert "decision_threshold" in metadata

    assert "engineered_features" in metadata


# ==================================================
# TEST 4
# Threshold is valid
# ==================================================

def test_threshold_valid():

    with open(
        METADATA_PATH,
        "r"
    ) as file:

        metadata = json.load(
            file
        )

    threshold = metadata[
        "decision_threshold"
    ]

    assert 0 <= threshold <= 1


# ==================================================
# TEST 5
# Feature engineering calculations
# ==================================================

def test_feature_engineering():

    income = 50000

    loan_amount = 20000

    interest_rate = 10

    age = 40

    credit_history = 5


    loan_to_income = (
        loan_amount
        / income
    )

    interest_burden = (
        loan_amount
        * (
            interest_rate
            / 100
        )
    )

    credit_history_ratio = (
        credit_history
        / age
    )


    assert loan_to_income == 0.4

    assert interest_burden == 2000

    assert credit_history_ratio == 0.125


# ==================================================
# TEST 6
# Prediction probabilities are valid
# ==================================================

def test_prediction_probability():

    calibrated_model = joblib.load(
        CALIBRATED_MODEL_PATH
    )


    applicant = pd.DataFrame([
        {
            "customer_age": 40,

            "customer_income": 75000,

            "home_ownership": "RENT",

            "employment_duration": 20,

            "loan_intent": "VENTURE",

            "loan_grade": "B",

            "loan_amnt": 20000,

            "loan_int_rate": 10,

            "term_years": 1,

            "cred_hist_length": 5,

            "loan_to_income":
                20000 / 75000,

            "interest_burden":
                20000 * 0.10,

            "credit_history_ratio":
                5 / 40
        }
    ])


    probabilities = (
        calibrated_model
        .predict_proba(
            applicant
        )[0]
    )


    assert len(probabilities) == 2

    assert all(
        0 <= probability <= 1
        for probability
        in probabilities
    )


    assert abs(
        sum(probabilities) - 1
    ) < 0.000001