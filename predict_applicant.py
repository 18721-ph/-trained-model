from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent


# --------------------------------------------------
# 1. Load the trained model
# --------------------------------------------------

model = joblib.load(PROJECT_ROOT / "model" / "loan_default_model.joblib")

print("\nLoan Default Prediction")
print("-----------------------")


# --------------------------------------------------
# 2. Collect applicant information
# --------------------------------------------------

customer_age = int(
    input("Customer age: ")
)

customer_income = float(
    input("Customer income: ")
)

home_ownership = input(
    "Home ownership (RENT / OWN / MORTGAGE / OTHER): "
).strip().upper()

employment_duration = float(
    input("Employment duration (years): ")
)

loan_intent = input(
    "Loan intent "
    "(EDUCATION / MEDICAL / VENTURE / PERSONAL / "
    "DEBTCONSOLIDATION / HOMEIMPROVEMENT): "
).strip().upper()

loan_grade = input(
    "Loan grade (A / B / C / D / E): "
).strip().upper()

loan_amnt = float(
    input("Loan amount: ")
)

loan_int_rate = float(
    input("Loan interest rate: ")
)

term_years = int(
    input("Loan term (years): ")
)

cred_hist_length = int(
    input("Credit history length (years): ")
)


# --------------------------------------------------
# 3. Create applicant dataframe
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
# 4. Predict class
# --------------------------------------------------

prediction = model.predict(
    applicant
)[0]


# --------------------------------------------------
# 5. Predict probabilities
# --------------------------------------------------

probabilities = model.predict_proba(
    applicant
)[0]

classes = model.classes_

default_index = list(
    classes
).index("DEFAULT")

no_default_index = list(
    classes
).index("NO DEFAULT")

default_probability = probabilities[
    default_index
]

no_default_probability = probabilities[
    no_default_index
]


# --------------------------------------------------
# 6. Display result
# --------------------------------------------------

print("\n-----------------------")
print("PREDICTION RESULT")
print("-----------------------")

print(
    f"Probability of DEFAULT: "
    f"{default_probability * 100:.2f}%"
)

print(
    f"Probability of NO DEFAULT: "
    f"{no_default_probability * 100:.2f}%"
)

print(
    f"\nPrediction: {prediction}"
)
