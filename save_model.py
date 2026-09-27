from pathlib import Path

import pandas as pd
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier


PROJECT_ROOT = Path(__file__).resolve().parent


# --------------------------------------------------
# 1. Load dataset
# --------------------------------------------------

df = pd.read_csv("data/loan_data.csv")


# --------------------------------------------------
# 2. Remove rows without target
# --------------------------------------------------

df = df.dropna(
    subset=["Current_loan_status"]
)


# --------------------------------------------------
# 3. Remove ID and suspicious history feature
# --------------------------------------------------

df = df.drop(
    columns=[
        "customer_id",
        "historical_default"
    ]
)


# --------------------------------------------------
# 4. Clean customer_income
# --------------------------------------------------

df["customer_income"] = pd.to_numeric(
    df["customer_income"],
    errors="coerce"
)


# --------------------------------------------------
# 5. Clean loan amount
# --------------------------------------------------

df["loan_amnt"] = (
    df["loan_amnt"]
    .str.replace("£", "", regex=False)
    .str.replace(",", "", regex=False)
)

df["loan_amnt"] = pd.to_numeric(
    df["loan_amnt"],
    errors="coerce"
)


# --------------------------------------------------
# 6. Features and target
# --------------------------------------------------

X = df.drop(
    columns=["Current_loan_status"]
)

y = df["Current_loan_status"]


# --------------------------------------------------
# 7. Feature groups
# --------------------------------------------------

numeric_features = [
    "customer_age",
    "customer_income",
    "employment_duration",
    "loan_amnt",
    "loan_int_rate",
    "term_years",
    "cred_hist_length"
]


categorical_features = [
    "home_ownership",
    "loan_intent",
    "loan_grade"
]


# --------------------------------------------------
# 8. Numeric preprocessing
# --------------------------------------------------

numeric_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(strategy="median")
    )
])


# --------------------------------------------------
# 9. Categorical preprocessing
# --------------------------------------------------

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


# --------------------------------------------------
# 10. Combine preprocessing
# --------------------------------------------------

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


# --------------------------------------------------
# 11. Random Forest
# --------------------------------------------------

model = Pipeline([
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


# --------------------------------------------------
# 12. Train on ALL available data
# --------------------------------------------------

print("Training final Random Forest model...")

model.fit(
    X,
    y
)

print("Training complete.")


# --------------------------------------------------
# 13. Save model
# --------------------------------------------------

model_path = PROJECT_ROOT / "model" / "loan_default_model.joblib"
model_path.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(model, model_path)

print(
    f"\nModel saved to {model_path}"
)
