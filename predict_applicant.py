import joblib
import pandas as pd
import numpy as np
import shap

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH =(
    BASE_DIR
    / "model"
    / "loan_default_model.joblib"
)
# --------------------------------------------------
# 1. Load trained model
# --------------------------------------------------

model = joblib.load(MODEL_PATH)

print("\nLoan Default Prediction")
print("-----------------------")

def get_int(prompt, min_value=None, max_value=None):
    while True:
        try:
            value = int(input(prompt))

            if min_value is not None and value < min_value:
                print(
                    f"Value must be at least {min_value}."
                )
                continue

            if max_value is not None and value > max_value:
                print(
                    f"Value must not be more than {max_value}."
                )
                continue

            return value

        except ValueError:
            print(
                "Please enter a whole number."
            )


def get_float(prompt, min_value=None, max_value=None):
    while True:
        try:
            value = float(input(prompt))

            if min_value is not None and value < min_value:
                print(
                    f"Value must be at least {min_value}."
                )
                continue

            if max_value is not None and value > max_value:
                print(
                    f"Value must not be more than {max_value}."
                )
                continue

            return value

        except ValueError:
            print(
                "Please enter a valid number."
            )


def get_choice(prompt, allowed_values):
    while True:
        value = input(prompt).strip().upper()

        if value in allowed_values:
            return value

        print(
            "Invalid option."
        )

        print(
            "Allowed values:",
            ", ".join(allowed_values)
        )
# --------------------------------------------------
# 2. Collect applicant information
# --------------------------------------------------

customer_age = get_int(
    "Customer age: ",
    min_value=18,
    max_value=100
)
customer_income = get_float(
    "Customer income: ",
    min_value=0
)

home_ownership = get_choice(
    "Home ownership" 
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
    max_value=60
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
).strip().upper()

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

while cred_hist_length > customer_age:
    print(
        "Credit history length cannot be greater "
        "than customer age."
    )

    cred_hist_length = get_int(
        "Credit history length (years): ",
        min_value=0,
        max_value=80
    )

# --------------------------------------------------
# 3. Applicant dataframe
# --------------------------------------------------

applicant = pd.DataFrame([
    {
        "customer_age": customer_age,
        "customer_income": customer_income,
        "home_ownership": home_ownership,
        "employment_duration": employment_duration,
        "loan_intent": loan_intent,
        "loan_grade": loan_grade,
        "loan_amnt": loan_amnt,
        "loan_int_rate": loan_int_rate,
        "term_years": term_years,
        "cred_hist_length": cred_hist_length
    }
])


# --------------------------------------------------
# 4. Prediction
# --------------------------------------------------

prediction = model.predict(applicant)[0]

probabilities = model.predict_proba(applicant)[0]

classes = list(
    model["classifier"].classes_
)

default_index = classes.index("DEFAULT")
no_default_index = classes.index("NO DEFAULT")

default_probability = probabilities[
    default_index
]

no_default_probability = probabilities[
    no_default_index
]


# --------------------------------------------------
# 5. Display prediction
# --------------------------------------------------

print("\n================================")
print("PREDICTION RESULT")
print("================================")

print(
    f"Probability of DEFAULT: "
    f"{default_probability * 100:.2f}%"
)

print(
    f"Probability of NO DEFAULT: "
    f"{no_default_probability * 100:.2f}%"
)

print(
    f"\nFinal Prediction: {prediction}"
)


# --------------------------------------------------
# 6. Prepare data for explanation
# --------------------------------------------------

preprocessor = model[
    "preprocessor"
]

classifier = model[
    "classifier"
]

transformed_applicant = preprocessor.transform(
    applicant
)

# SHAP works more reliably with dense input
if hasattr(
    transformed_applicant,
    "toarray"
):
    transformed_applicant = (
        transformed_applicant.toarray()
    )


feature_names = (
    preprocessor
    .get_feature_names_out()
)


# --------------------------------------------------
# 7. Build SHAP explanation
# --------------------------------------------------

explainer = shap.TreeExplainer(
    classifier
)

shap_result = explainer(
    transformed_applicant
)


# --------------------------------------------------
# 8. Extract SHAP values for DEFAULT class
# --------------------------------------------------

values = shap_result.values

# Newer SHAP versions may return:
# (samples, features, classes)
if values.ndim == 3:

    default_shap_values = values[
        0,
        :,
        default_index
    ]

else:

    default_shap_values = values[0]


# --------------------------------------------------
# 9. Group encoded columns back into original fields
# --------------------------------------------------

feature_groups = {
    "customer_age": 0.0,
    "customer_income": 0.0,
    "home_ownership": 0.0,
    "employment_duration": 0.0,
    "loan_intent": 0.0,
    "loan_grade": 0.0,
    "loan_amnt": 0.0,
    "loan_int_rate": 0.0,
    "term_years": 0.0,
    "cred_hist_length": 0.0
}


for feature_name, shap_value in zip(
    feature_names,
    default_shap_values
):

    clean_name = feature_name.replace(
        "numeric__",
        ""
    )

    clean_name = clean_name.replace(
        "categorical__",
        ""
    )

    matched = False

    for original_feature in feature_groups:

        if (
            clean_name == original_feature
            or
            clean_name.startswith(
                original_feature + "_"
            )
        ):

            feature_groups[
                original_feature
            ] += float(shap_value)

            matched = True
            break


# --------------------------------------------------
# 10. Values for human-readable explanation
# --------------------------------------------------

display_values = {

    "customer_age":
        f"{customer_age} years",

    "customer_income":
        f"{customer_income:,.0f}",

    "home_ownership":
        home_ownership,

    "employment_duration":
        f"{employment_duration:g} years",

    "loan_intent":
        loan_intent,

    "loan_grade":
        loan_grade,

    "loan_amnt":
        f"{loan_amnt:,.0f}",

    "loan_int_rate":
        f"{loan_int_rate:g}%",

    "term_years":
        f"{term_years} years",

    "cred_hist_length":
        f"{cred_hist_length} years"
}


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
        "Credit history length"
}


# --------------------------------------------------
# 11. Sort features by strength
# --------------------------------------------------

sorted_features = sorted(
    feature_groups.items(),
    key=lambda item: abs(item[1]),
    reverse=True
)


risk_increasing = []

risk_reducing = []


for feature, contribution in sorted_features:

    information = {
        "feature": feature,
        "name": friendly_names[feature],
        "value": display_values[feature],
        "contribution": contribution
    }

    if contribution > 0:

        risk_increasing.append(
            information
        )

    elif contribution < 0:

        risk_reducing.append(
            information
        )


# --------------------------------------------------
# 12. Explanation
# --------------------------------------------------

print("\n================================")
print("WHY THE MODEL MADE THIS DECISION")
print("================================")


print(
    "\nFactors that pushed the prediction "
    "toward DEFAULT:"
)

if len(risk_increasing) == 0:

    print(
        "- No major features strongly pushed "
        "the prediction toward default."
    )

else:

    for item in risk_increasing[:5]:

        print(
            f"- {item['name']} "
            f"({item['value']}) "
            f"increased the model's estimated "
            f"default risk "
            f"(impact: {item['contribution']:+.4f})."
        )


print(
    "\nFactors that pushed the prediction "
    "toward NO DEFAULT:"
)

if len(risk_reducing) == 0:

    print(
        "- No major features strongly pushed "
        "the prediction toward no default."
    )

else:

    for item in risk_reducing[:5]:

        print(
            f"- {item['name']} "
            f"({item['value']}) "
            f"reduced the model's estimated "
            f"default risk "
            f"(impact: {item['contribution']:+.4f})."
        )


# --------------------------------------------------
# 13. Final plain-English conclusion
# --------------------------------------------------

print("\n================================")
print("MODEL EXPLANATION")
print("================================")


if prediction == "DEFAULT":

    print(
        f"""
The model classified this applicant as DEFAULT.

After analysing the applicant's income,
loan characteristics, employment history,
credit history, home ownership and loan grade,
the combination of risk-increasing factors
was strong enough to produce a
{default_probability * 100:.2f}% estimated
probability of default.

Because this probability is above the current
50% classification threshold, the final
prediction is DEFAULT.
"""
    )

else:

    print(
        f"""
The model classified this applicant as NO DEFAULT.

The model found some factors that increased
default risk and others that reduced it.
When all of these effects were combined,
the estimated probability of default was
{default_probability * 100:.2f}%.

Because this is below the current 50%
classification threshold, the final
prediction is NO DEFAULT.

The strongest factors shown above explain
which applicant characteristics moved the
prediction toward or away from default.
"""
    )