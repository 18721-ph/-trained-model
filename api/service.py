from pathlib import Path
import json

import joblib
import pandas as pd

from src.features import add_engineered_features
from src.prediction import classify_default


# ==================================================
# PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = BASE_DIR / "model"

CALIBRATED_MODEL_PATH = (
    MODEL_DIR
    / "calibrated_loan_default_model.joblib"
)

METADATA_PATH = (
    MODEL_DIR
    / "model_metadata.json"
)


# ==================================================
# LOAD MODEL
# ==================================================

calibrated_model = joblib.load(
    CALIBRATED_MODEL_PATH
)


with open(
    METADATA_PATH,
    "r"
) as file:

    metadata = json.load(file)


DECISION_THRESHOLD = metadata[
    "decision_threshold"
]


# ==================================================
# PREDICTION FUNCTION
# ==================================================

def predict_default(applicant_data: dict):

    applicant = pd.DataFrame([
        applicant_data
    ])


    # Feature engineering
    applicant = add_engineered_features(
        applicant
    )


    # Get model probabilities
    probabilities = (
        calibrated_model
        .predict_proba(
            applicant
        )[0]
    )


    classes = list(
        calibrated_model.classes_
    )


    default_index = classes.index(
        "DEFAULT"
    )

    no_default_index = classes.index(
        "NO DEFAULT"
    )


    default_probability = float(
        probabilities[
            default_index
        ]
    )


    no_default_probability = float(
        probabilities[
            no_default_index
        ]
    )


    # Apply our validated threshold
    prediction = classify_default(
        default_probability,
        DECISION_THRESHOLD
    )


    return {
        "default_probability":
            default_probability,

        "no_default_probability":
            no_default_probability,

        "decision_threshold":
            DECISION_THRESHOLD,

        "prediction":
            prediction
    }