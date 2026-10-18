from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
import shap

from src.features import (
    add_engineered_features
)

from src.prediction import (
    classify_default
)


# ==================================================
# PATHS
# ==================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
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

METADATA_PATH = (
    MODEL_DIR
    / "model_metadata.json"
)


# ==================================================
# LOAD MODELS
# ==================================================

base_model = joblib.load(
    BASE_MODEL_PATH
)

calibrated_model = joblib.load(
    CALIBRATED_MODEL_PATH
)


with open(
    METADATA_PATH,
    "r"
) as file:

    metadata = json.load(file)


DECISION_THRESHOLD = (
    metadata[
        "decision_threshold"
    ]
)


# ==================================================
# FRIENDLY FEATURE NAMES
# ==================================================

FRIENDLY_NAMES = {

    "customer_age":
        "Customer age",

    "customer_income":
        "Customer income",

    "employment_duration":
        "Employment duration",

    "loan_amnt":
        "Loan amount",

    "loan_int_rate":
        "Interest rate",

    "term_years":
        "Loan term",

    "cred_hist_length":
        "Credit history length",

    "loan_to_income":
        "Loan-to-income ratio",

    "interest_burden":
        "Interest-related exposure",

    "credit_history_ratio":
        "Credit-history ratio",

    "home_ownership":
        "Home ownership",

    "loan_intent":
        "Loan purpose",

    "loan_grade":
        "Loan grade"
}


# ==================================================
# GROUP ONE-HOT FEATURES
# ==================================================

def get_original_feature_name(
    transformed_name
):

    name = transformed_name


    if "__" in name:

        name = name.split(
            "__",
            1
        )[1]


    categorical_prefixes = [
        "home_ownership_",
        "loan_intent_",
        "loan_grade_"
    ]


    for prefix in categorical_prefixes:

        if name.startswith(prefix):

            return prefix.rstrip("_")


    return name


# ==================================================
# SHAP EXPLANATION
# ==================================================

def explain_prediction(
    applicant
):

    preprocessor = base_model[
        "preprocessor"
    ]

    classifier = base_model[
        "classifier"
    ]


    transformed = (
        preprocessor
        .transform(
            applicant
        )
    )


    feature_names = (
        preprocessor
        .get_feature_names_out()
    )


    explainer = shap.TreeExplainer(
        classifier
    )


    shap_values = (
        explainer
        .shap_values(
            transformed
        )
    )


    default_index = list(
        classifier.classes_
    ).index(
        "DEFAULT"
    )


    # SHAP versions can return
    # different structures.

    if isinstance(
        shap_values,
        list
    ):

        default_shap = (
            shap_values[
                default_index
            ][0]
        )

    else:

        shap_array = np.array(
            shap_values
        )

        if shap_array.ndim == 3:

            default_shap = (
                shap_array[
                    0,
                    :,
                    default_index
                ]
            )

        else:

            default_shap = (
                shap_array[0]
            )


    grouped_impacts = {}


    for (
        feature_name,
        impact
    ) in zip(
        feature_names,
        default_shap
    ):

        original_feature = (
            get_original_feature_name(
                feature_name
            )
        )


        grouped_impacts[
            original_feature
        ] = (
            grouped_impacts.get(
                original_feature,
                0
            )
            + float(impact)
        )


    risk_factors = []

    protective_factors = []


    for (
        feature,
        impact
    ) in grouped_impacts.items():

        display_name = (
            FRIENDLY_NAMES.get(
                feature,
                feature
            )
        )


        factor = {
            "feature":
                display_name,

            "impact":
                float(impact)
        }


        if impact > 0:

            risk_factors.append(
                factor
            )

        elif impact < 0:

            protective_factors.append(
                factor
            )


    risk_factors.sort(
        key=lambda x: x["impact"],
        reverse=True
    )


    protective_factors.sort(
        key=lambda x: x["impact"]
    )


    return (
        risk_factors[:5],
        protective_factors[:5]
    )


# ==================================================
# PREDICTION FUNCTION
# ==================================================

def predict_default(
    applicant_data
):

    applicant = pd.DataFrame([
        applicant_data
    ])


    # Feature engineering
    applicant = (
        add_engineered_features(
            applicant
        )
    )


    # Calibrated probabilities
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


    prediction = classify_default(
        default_probability,
        DECISION_THRESHOLD
    )


    # SHAP explanation
    (
        risk_factors,
        protective_factors
    ) = explain_prediction(
        applicant
    )


    return {

        "default_probability":
            default_probability,

        "no_default_probability":
            no_default_probability,

        "decision_threshold":
            DECISION_THRESHOLD,

        "prediction":
            prediction,

        "top_risk_factors":
            risk_factors,

        "top_protective_factors":
            protective_factors
    }