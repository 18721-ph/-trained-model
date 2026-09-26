import pandas as pd

from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    make_scorer
)


# --------------------------------------------------
# 1. Load dataset
# --------------------------------------------------

df = pd.read_csv("loan_data.csv")


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
# 5. Separate features and target
# --------------------------------------------------

X = df.drop(
    columns=["Current_loan_status"]
)

y = df["Current_loan_status"]


print("Dataset rows:")
print(len(df))

print("\nTarget distribution:")
print(y.value_counts())


# --------------------------------------------------
# 6. Feature groups
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
# 7. Logistic Regression preprocessing
# --------------------------------------------------

logistic_numeric_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(strategy="median")
    ),
    (
        "scaler",
        StandardScaler()
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


logistic_preprocessor = ColumnTransformer([
    (
        "numeric",
        logistic_numeric_pipeline,
        numeric_features
    ),
    (
        "categorical",
        categorical_pipeline,
        categorical_features
    )
])


# --------------------------------------------------
# 8. Random Forest preprocessing
# --------------------------------------------------

forest_numeric_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(strategy="median")
    )
])


forest_preprocessor = ColumnTransformer([
    (
        "numeric",
        forest_numeric_pipeline,
        numeric_features
    ),
    (
        "categorical",
        categorical_pipeline,
        categorical_features
    )
])


# --------------------------------------------------
# 9. Models
# --------------------------------------------------

logistic_model = Pipeline([
    (
        "preprocessor",
        logistic_preprocessor
    ),
    (
        "classifier",
        LogisticRegression(
            max_iter=2000
        )
    )
])


random_forest_model = Pipeline([
    (
        "preprocessor",
        forest_preprocessor
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
# 10. Cross-validation setup
# --------------------------------------------------

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)


scoring = {
    "accuracy": "accuracy",

    "precision": make_scorer(
        precision_score,
        pos_label="DEFAULT"
    ),

    "recall": make_scorer(
        recall_score,
        pos_label="DEFAULT"
    ),

    "f1": make_scorer(
        f1_score,
        pos_label="DEFAULT"
    )
}


# --------------------------------------------------
# 11. Cross-validate Logistic Regression
# --------------------------------------------------

print("\nCross-validating Logistic Regression...")

logistic_results = cross_validate(
    logistic_model,
    X,
    y,
    cv=cv,
    scoring=scoring,
    n_jobs=-1
)


# --------------------------------------------------
# 12. Cross-validate Random Forest
# --------------------------------------------------

print("\nCross-validating Random Forest...")

forest_results = cross_validate(
    random_forest_model,
    X,
    y,
    cv=cv,
    scoring=scoring,
    n_jobs=-1
)


# --------------------------------------------------
# 13. Results
# --------------------------------------------------

print("\nLOGISTIC REGRESSION")

print(
    "Accuracy:",
    logistic_results["test_accuracy"].mean()
)

print(
    "Precision:",
    logistic_results["test_precision"].mean()
)

print(
    "Recall:",
    logistic_results["test_recall"].mean()
)

print(
    "F1:",
    logistic_results["test_f1"].mean()
)


print("\nRANDOM FOREST")

print(
    "Accuracy:",
    forest_results["test_accuracy"].mean()
)

print(
    "Precision:",
    forest_results["test_precision"].mean()
)

print(
    "Recall:",
    forest_results["test_recall"].mean()
)

print(
    "F1:",
    forest_results["test_f1"].mean()
)
# --------------------------------------------------
# 15. Random Forest feature importance
# --------------------------------------------------

feature_names = model[
    "preprocessor"
].get_feature_names_out()

importances = model[
    "classifier"
].feature_importances_

importance_df = pd.DataFrame({
    "feature": feature_names,
    "importance": importances
})

importance_df = importance_df.sort_values(
    "importance",
    ascending=False
)

print("\nTop Random Forest features:")

print(
    importance_df.head(20)
)