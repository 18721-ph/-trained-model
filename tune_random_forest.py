import pandas as pd

from sklearn.model_selection import (
    train_test_split,
    RandomizedSearchCV
)

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
    confusion_matrix,
    classification_report,
    roc_auc_score
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
# 7. Train/test split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print("Training rows:")
print(len(X_train))

print("\nTesting rows:")
print(len(X_test))


# --------------------------------------------------
# 8. Define feature groups
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
# 12. Base Random Forest
# --------------------------------------------------

forest = RandomForestClassifier(
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)


# --------------------------------------------------
# 13. Complete pipeline
# --------------------------------------------------

model = Pipeline([
    (
        "preprocessor",
        preprocessor
    ),

    (
        "classifier",
        forest
    )
])


# --------------------------------------------------
# 14. Parameters to search
# --------------------------------------------------

parameter_grid = {

    "classifier__n_estimators": [
        200,
        300,
        500,
        700
    ],

    "classifier__max_depth": [
        None,
        10,
        20,
        30,
        40
    ],

    "classifier__min_samples_split": [
        2,
        5,
        10
    ],

    "classifier__min_samples_leaf": [
        1,
        2,
        4
    ],

    "classifier__max_features": [
        "sqrt",
        "log2",
        None
    ]
}


# --------------------------------------------------
# 15. Randomized search
# --------------------------------------------------

search = RandomizedSearchCV(
    estimator=model,
    param_distributions=parameter_grid,
    n_iter=20,
    scoring="f1_macro",
    cv=5,
    verbose=2,
    random_state=42,
    n_jobs=-1
)


print("\nStarting Random Forest tuning...")

search.fit(
    X_train,
    y_train
)

print("\nTuning complete.")


# --------------------------------------------------
# 16. Best parameters
# --------------------------------------------------

print("\nBest parameters:")

for key, value in search.best_params_.items():
    print(
        key,
        "=",
        value
    )


print("\nBest cross-validation score:")
print(
    search.best_score_
)


# --------------------------------------------------
# 17. Get best model
# --------------------------------------------------

best_model = search.best_estimator_


# --------------------------------------------------
# 18. Test predictions
# --------------------------------------------------

predictions = best_model.predict(
    X_test
)

probabilities = best_model.predict_proba(
    X_test
)


default_index = list(
    best_model.classes_
).index("DEFAULT")


default_probabilities = probabilities[
    :,
    default_index
]


# --------------------------------------------------
# 19. Evaluation
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


print("\nFINAL TEST RESULTS")

print("\nAccuracy:")
print(accuracy)

print("\nPrecision:")
print(precision)

print("\nRecall:")
print(recall)

print("\nF1 Score:")
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


print("\nClassification Report:")

print(
    classification_report(
        y_test,
        predictions
    )
)