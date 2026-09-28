import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)


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
# 3. Remove unused / suspicious columns
# --------------------------------------------------

df = df.drop(
    columns=[
        "customer_id",
        "historical_default"
    ]
)


# --------------------------------------------------
# 4. Clean numeric-looking columns
# --------------------------------------------------

df["customer_income"] = pd.to_numeric(
    df["customer_income"],
    errors="coerce"
)

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
# 5. FEATURE ENGINEERING
# --------------------------------------------------

df["loan_to_income"] = (
    df["loan_amnt"]
    / df["customer_income"]
)


# Protect against impossible division results
df["loan_to_income"] = (
    df["loan_to_income"]
    .replace([float("inf"), -float("inf")], pd.NA)
)


# --------------------------------------------------
# 6. Features and target
# --------------------------------------------------

X = df.drop(
    columns=["Current_loan_status"]
)

y = df["Current_loan_status"]


# --------------------------------------------------
# 7. Train/test split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# --------------------------------------------------
# 8. Feature groups
# --------------------------------------------------

numeric_features = [
    "customer_age",
    "customer_income",
    "employment_duration",
    "loan_amnt",
    "loan_int_rate",
    "term_years",
    "cred_hist_length",
    "loan_to_income"
]


categorical_features = [
    "home_ownership",
    "loan_intent",
    "loan_grade"
]


# --------------------------------------------------
# 9. Numeric preprocessing
# --------------------------------------------------

numeric_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(strategy="median")
    )
])


# --------------------------------------------------
# 10. Categorical preprocessing
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
# 11. Combine preprocessing
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
# 12. Random Forest model
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
# 13. Train
# --------------------------------------------------

print("Training Random Forest with loan_to_income...")

model.fit(
    X_train,
    y_train
)

print("Training complete.")


# --------------------------------------------------
# 14. Predictions
# --------------------------------------------------

predictions = model.predict(
    X_test
)

probabilities = model.predict_proba(
    X_test
)

default_index = list(
    model.classes_
).index("DEFAULT")

default_probabilities = probabilities[
    :,
    default_index
]


# --------------------------------------------------
# 15. Evaluation
# --------------------------------------------------

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

roc_auc = roc_auc_score(
    (y_test == "DEFAULT").astype(int),
    default_probabilities
)


print("\nRESULTS WITH loan_to_income")

print("\nAccuracy:")
print(accuracy)

print("\nPrecision:")
print(precision)

print("\nRecall:")
print(recall)

print("\nF1:")
print(f1)

print("\nROC-AUC:")
print(roc_auc)

print("\nConfusion Matrix:")
print(
    confusion_matrix(
        y_test,
        predictions,
        labels=[
            "NO DEFAULT",
            "DEFAULT"
        ]
    )
)


# --------------------------------------------------
# 16. Feature importance
# --------------------------------------------------

feature_names = (
    model["preprocessor"]
    .get_feature_names_out()
)

importances = (
    model["classifier"]
    .feature_importances_
)

importance_df = pd.DataFrame({
    "feature": feature_names,
    "importance": importances
})

importance_df = (
    importance_df
    .sort_values(
        "importance",
        ascending=False
    )
)


print("\nTop features:")

print(
    importance_df.head(20)
)