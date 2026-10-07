from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
import shap

from src.features import add_engineered_features


# ==================================================
# PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

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


# ==================================================
# LOAD METADATA
# ==================================================

with open(
    METADATA_PATH,
    "r"
) as metadata_file:

    metadata = json.load(
        metadata_file
    )


DECISION_THRESHOLD = metadata[
    "decision_threshold"
]


# ==================================================
# VALIDATION FUNCTIONS
# ==================================================

def get_int(
    prompt,
    min_value=None,
    max_value=None
):

    while True:

        try:
            value = int(
                input(prompt)
            )

        except ValueError:

            print(
                "Please enter a whole number."
            )

            continue


        if (
            min_value is not None
            and value < min_value
        ):

            print(
                f"Value must be at least {min_value}."
            )

            continue


        if (
            max_value is not None
            and value > max_value
        ):

            print(
                f"Value must not exceed {max_value}."
            )

            continue


        return value


def get_float(
    prompt,
    min_value=None,
    max_value=None
):

    while True:

        try:
            value = float(
                input(prompt)
            )

        except ValueError:

            print(
                "Please enter a valid number."
            )

            continue


        if (
            min_value is not None
            and value < min_value
        ):

            print(
                f"Value must be at least {min_value}."
            )

            continue


        if (
            max_value is not None
            and value > max_value
        ):

            print(
                f"Value must not exceed {max_value}."
            )

            continue


        return value


def get_choice(
    prompt,
    allowed_values
):

    while True:

        value = (
            input(prompt)
            .strip()
            .upper()
        )


        if value in allowed_values:
            return value


        print(
            "\nInvalid option."
        )

        print(
            "Allowed values:",
            ", ".join(
                allowed_values
            )
        )


# ==================================================
# MODEL INFORMATION
# ==================================================

print(
    "\nLoan Default Prediction"
)

print(
    "-----------------------"
)


print(
    "\nModel information"
)

print(
    "-----------------"
)

print(
    "Version:",
    metadata["model_version"]
)

print(
    "Algorithm:",
    metadata["algorithm"]
)

print(
    "Calibration:",
    metadata["calibration_method"]
)

print(
    "Decision threshold:",
    f"{DECISION_THRESHOLD * 100:.0f}%"
)


# ==================================================
# COLLECT APPLICANT DATA
# ==================================================

customer_age = get_int(
    "Customer age: ",
    min_value=18,
    max_value=100
)


customer_income = get_float(
    "Customer income: ",
    min_value=1
)


home_ownership = get_choice(
    "Home ownership "
    "(RENT / OWN / MORTGAGE / OTHER): ",
    [
        "RENT",
        "OWN",
        "MORTGAGE",
        "OTHER"
    ]
)


employment_duration = get_float(
    "Employment duration (years): ",
    min_value=0,
    max_value=70
)


loan_intent = get_choice(
    "Loan intent "
    "(EDUCATION / MEDICAL / VENTURE / PERSONAL / "
    "DEBTCONSOLIDATION / HOMEIMPROVEMENT): ",
    [
        "EDUCATION",
        "MEDICAL",
        "VENTURE",
        "PERSONAL",
        "DEBTCONSOLIDATION",
        "HOMEIMPROVEMENT"
    ]
)


loan_grade = get_choice(
    "Loan grade (A / B / C / D / E): ",
    [
        "A",
        "B",
        "C",
        "D",
        "E"
    ]
)


loan_amnt = get_float(
    "Loan amount: ",
    min_value=1
)


loan_int_rate = get_float(
    "Loan interest rate (%): ",
    min_value=0,
    max_value=50
)


term_years = get_int(
    "Loan term (years): ",
    min_value=1,
    max_value=30
)


cred_hist_length = get_int(
    "Credit history length (years): ",
    min_value=0,
    max_value=80
)


# ==================================================
# RELATIONSHIP VALIDATION
# ==================================================

while employment_duration > (
    customer_age - 14
):

    print(
        "\nEmployment duration appears inconsistent "
        "with customer age."
    )

    employment_duration = get_float(
        "Employment duration (years): ",
        min_value=0,
        max_value=70
    )


while cred_hist_length > customer_age:

    print(
        "\nCredit history cannot be longer "
        "than customer age."
    )

    cred_hist_length = get_int(
        "Credit history length (years): ",
        min_value=0,
        max_value=80
    )


# ==================================================
# CREATE RAW APPLICANT DATAFRAME
# ==================================================

applicant = pd.DataFrame([
    {
        "customer_age":
            customer_age,

        "customer_income":
            customer_income,

        "home_ownership":
            home_ownership,

        "employment_duration":
            employment_duration,

        "loan_intent":
            loan_intent,

        "loan_grade":
            loan_grade,

        "loan_amnt":
            loan_amnt,

        "loan_int_rate":
            loan_int_rate,

        "term_years":
            term_years,

        "cred_hist_length":
            cred_hist_length
    }
])


# ==================================================
# FEATURE ENGINEERING
# ==================================================

applicant = add_engineered_features(
    applicant
)


loan_to_income = applicant.loc[
    0,
    "loan_to_income"
]

interest_burden = applicant.loc[
    0,
    "interest_burden"
]

credit_history_ratio = applicant.loc[
    0,
    "credit_history_ratio"
]


# ==================================================
# CALIBRATED PROBABILITY
# ==================================================

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


default_probability = probabilities[
    default_index
]

no_default_probability = probabilities[
    no_default_index
]


# ==================================================
# APPLY DECISION THRESHOLD
# ==================================================

if default_probability >= DECISION_THRESHOLD:

    prediction = "DEFAULT"

else:

    prediction = "NO DEFAULT"


# ==================================================
# PREDICTION RESULT
# ==================================================

print(
    "\n================================"
)

print(
    "PREDICTION RESULT"
)

print(
    "================================"
)


print(
    f"Calibrated probability of DEFAULT: "
    f"{default_probability * 100:.2f}%"
)


print(
    f"Calibrated probability of NO DEFAULT: "
    f"{no_default_probability * 100:.2f}%"
)


print(
    f"\nDecision threshold: "
    f"{DECISION_THRESHOLD * 100:.0f}%"
)


print(
    f"\nFinal Prediction: "
    f"{prediction}"
)


# ==================================================
# DERIVED FINANCIAL FEATURES
# ==================================================

print(
    "\n================================"
)

print(
    "DERIVED FINANCIAL FEATURES"
)

print(
    "================================"
)


print(
    f"Loan-to-income ratio: "
    f"{loan_to_income:.3f}"
)


print(
    f"Approx. annual interest amount: "
    f"{interest_burden:,.2f}"
)


print(
    f"Credit-history-to-age ratio: "
    f"{credit_history_ratio:.3f}"
)


# ==================================================
# SHAP EXPLANATION
# ==================================================

try:

    preprocessor = base_model[
        "preprocessor"
    ]

    classifier = base_model[
        "classifier"
    ]


    transformed_applicant = (
        preprocessor.transform(
            applicant
        )
    )


    if hasattr(
        transformed_applicant,
        "toarray"
    ):

        transformed_applicant = (
            transformed_applicant
            .toarray()
        )


    feature_names = (
        preprocessor
        .get_feature_names_out()
    )


    explainer = shap.TreeExplainer(
        classifier
    )


    shap_values = (
        explainer.shap_values(
            transformed_applicant
        )
    )


    # ==================================================
    # HANDLE SHAP OUTPUT FORMAT
    # ==================================================

    if isinstance(
        shap_values,
        list
    ):

        base_classes = list(
            classifier.classes_
        )

        base_default_index = (
            base_classes.index(
                "DEFAULT"
            )
        )

        local_values = (
            shap_values[
                base_default_index
            ][0]
        )

    else:

        shap_array = np.asarray(
            shap_values
        )

        base_classes = list(
            classifier.classes_
        )

        base_default_index = (
            base_classes.index(
                "DEFAULT"
            )
        )


        if shap_array.ndim == 3:

            local_values = (
                shap_array[
                    0,
                    :,
                    base_default_index
                ]
            )

        elif shap_array.ndim == 2:

            local_values = (
                shap_array[0]
            )

        else:

            raise ValueError(
                "Unexpected SHAP output shape."
            )


    # ==================================================
    # GROUP TRANSFORMED FEATURES
    # ==================================================

    original_features = [
        "customer_age",
        "customer_income",
        "home_ownership",
        "employment_duration",
        "loan_intent",
        "loan_grade",
        "loan_amnt",
        "loan_int_rate",
        "term_years",
        "cred_hist_length",
        "loan_to_income",
        "interest_burden",
        "credit_history_ratio"
    ]


    grouped_impacts = {
        feature: 0.0
        for feature
        in original_features
    }


    for (
        transformed_feature,
        shap_value
    ) in zip(
        feature_names,
        local_values
    ):

        clean_name = (
            transformed_feature
            .replace(
                "numeric__",
                ""
            )
            .replace(
                "categorical__",
                ""
            )
        )


        if clean_name in grouped_impacts:

            grouped_impacts[
                clean_name
            ] += float(
                shap_value
            )

            continue


        for original in [
            "home_ownership",
            "loan_intent",
            "loan_grade"
        ]:

            if clean_name.startswith(
                original + "_"
            ):

                grouped_impacts[
                    original
                ] += float(
                    shap_value
                )

                break


    # ==================================================
    # FRIENDLY NAMES
    # ==================================================

    friendly_names = {

        "customer_age":
            "Customer age",

        "customer_income":
            "Customer income",

        "home_ownership":
            "Home ownership",

        "employment_duration":
            "Employment duration",

        "loan_intent":
            "Loan purpose",

        "loan_grade":
            "Loan grade",

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
            "Approx. annual interest amount",

        "credit_history_ratio":
            "Credit-history-to-age ratio"
    }


    display_values = {

        "customer_age":
            f"{customer_age} years",

        "customer_income":
            f"{customer_income:,.2f}",

        "home_ownership":
            home_ownership,

        "employment_duration":
            f"{employment_duration:g} years",

        "loan_intent":
            loan_intent,

        "loan_grade":
            loan_grade,

        "loan_amnt":
            f"{loan_amnt:,.2f}",

        "loan_int_rate":
            f"{loan_int_rate:g}%",

        "term_years":
            f"{term_years} years",

        "cred_hist_length":
            f"{cred_hist_length} years",

        "loan_to_income":
            f"{loan_to_income:.3f}",

        "interest_burden":
            f"{interest_burden:,.2f}",

        "credit_history_ratio":
            f"{credit_history_ratio:.3f}"
    }


    # ==================================================
    # SORT LOCAL IMPACTS
    # ==================================================

    sorted_impacts = sorted(
        grouped_impacts.items(),
        key=lambda item: abs(
            item[1]
        ),
        reverse=True
    )


    risk_increasing = [
        item
        for item
        in sorted_impacts
        if item[1] > 0
    ]


    risk_reducing = [
        item
        for item
        in sorted_impacts
        if item[1] < 0
    ]


    # ==================================================
    # PRINT SHAP EXPLANATION
    # ==================================================

    print(
        "\n================================"
    )

    print(
        "WHY THE MODEL MADE THIS DECISION"
    )

    print(
        "================================"
    )


    if risk_increasing:

        print(
            "\nFactors that pushed the model "
            "toward DEFAULT:"
        )


        for (
            feature,
            impact
        ) in risk_increasing[:5]:

            print(
                f"- "
                f"{friendly_names[feature]} "
                f"({display_values[feature]}) "
                f"increased the model's estimated "
                f"default risk "
                f"(impact: {impact:+.4f})."
            )


    if risk_reducing:

        print(
            "\nFactors that pushed the model "
            "toward NO DEFAULT:"
        )


        for (
            feature,
            impact
        ) in risk_reducing[:5]:

            print(
                f"- "
                f"{friendly_names[feature]} "
                f"({display_values[feature]}) "
                f"reduced the model's estimated "
                f"default risk "
                f"(impact: {impact:+.4f})."
            )


except Exception as error:

    print(
        "\nPrediction succeeded, "
        "but the SHAP explanation "
        "could not be generated."
    )

    print(
        "Explanation error:",
        error
    )


# ==================================================
# FINAL MODEL EXPLANATION
# ==================================================

print(
    "\n================================"
)

print(
    "MODEL EXPLANATION"
)

print(
    "================================"
)


print(
    f"\nThe model classified this "
    f"applicant as {prediction}."
)


print(
    "\nThe model considered the applicant's "
    "income, loan characteristics, employment, "
    "credit history, home ownership, loan grade "
    "and engineered financial relationships."
)


print(
    f"\nCalibrated estimated probability "
    f"of default: "
    f"{default_probability * 100:.2f}%"
)


if default_probability >= DECISION_THRESHOLD:

    print(
        f"\nBecause the calibrated probability "
        f"of default is at or above the "
        f"{DECISION_THRESHOLD * 100:.0f}% "
        f"decision threshold, "
        f"the final prediction is DEFAULT."
    )

else:

    print(
        f"\nBecause the calibrated probability "
        f"of default is below the "
        f"{DECISION_THRESHOLD * 100:.0f}% "
        f"decision threshold, "
        f"the final prediction is NO DEFAULT."
    )


print(
    "\nNote: SHAP explains how the base "
    "Random Forest used the input features. "
    "It does not mean any individual feature "
    "causes default."
)