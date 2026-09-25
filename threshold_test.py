import pandas as pd

from sklearn.model_selection import train_test_split

from sklearn.compose import ColumnTransformer

from sklearn.pipeline import Pipeline

from sklearn.preprocessing import OneHotEncoder, StandardScaler

from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression

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
# 2. Remove rows without a target
# --------------------------------------------------

df = df.dropna(subset=[
    "Current_loan_status"
])


# --------------------------------------------------
# 3. Remove ID
# --------------------------------------------------

df = df.drop(
    columns=[
    "customer_id" ,
    "historical_default"
    ]
)


# --------------------------------------------------
# 4. Clean numeric-looking text
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

X = df.drop(columns=["Current_loan_status"])

y = df["Current_loan_status"]


# --------------------------------------------------
# 6. Train/test split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)
print("\nRows before split:")
print(len(df))

print("\nTraining rows:")
print(len(X_train))

print("\nTesting rows:")
print(len(X_test))

print("\nTesting target distribution:")
print(y_test.value_counts())


# --------------------------------------------------
# 7. Define columns
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
    "loan_grade",
]


# --------------------------------------------------
# 8. Numeric preprocessing
# --------------------------------------------------

numeric_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(strategy="median")
    ),

    (
        "scaler",
        StandardScaler()
    )
])


# --------------------------------------------------
# 9. Categorical preprocessing
# --------------------------------------------------

categorical_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(
            strategy="constant",
            fill_value="UNKNOWN"
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
# 11. Create complete ML pipeline
# --------------------------------------------------

model = Pipeline([
    (
        "preprocessor",
        preprocessor
    ),

    (
        "classifier",
        LogisticRegression(
            max_iter=1000
        )
    )
])


# --------------------------------------------------
# 12. Train
# --------------------------------------------------

print("Training model...")

model.fit(
    X_train,
    y_train
)

print("Training complete.")


# --------------------------------------------------
# 13. Predictions
# --------------------------------------------------

predictions = model.predict(X_test)


# Probability of DEFAULT
probabilities = model.predict_proba(X_test)

default_index = list(
    model.classes_
).index("DEFAULT")

default_probabilities = probabilities[:, default_index]

from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

thresholds = [
    0.50,
    0.45,
    0.40,
    0.35,
    0.30
]

print("\nThreshold comparison:")

for threshold in thresholds:

    threshold_predictions = [
        "DEFAULT" if probability >= threshold else "NO DEFAULT"
        for probability in default_probabilities
    ]

    precision = precision_score(
        y_test,
        threshold_predictions,
        pos_label="DEFAULT"
    )

    recall = recall_score(
        y_test,
        threshold_predictions,
        pos_label="DEFAULT"
    )

    f1 = f1_score(
        y_test,
        threshold_predictions,
        pos_label="DEFAULT"
    )

    matrix = confusion_matrix(
        y_test,
        threshold_predictions,
        labels=["NO DEFAULT", "DEFAULT"]
    )

    print(f"\nThreshold: {threshold}")

    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")

    print("Confusion Matrix:")
    print(matrix)
# --------------------------------------------------
# 14. Evaluation
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
# --------------------------------------------------
# 15. Inspect feature importance / coefficients
# --------------------------------------------------

feature_names = model[
    "preprocessor"
].get_feature_names_out()

coefficients = model[
    "classifier"
].coef_[0]

coef_df = pd.DataFrame({
    "feature": feature_names,
    "coefficient": coefficients
})

coef_df["absolute_coefficient"] = (
    coef_df["coefficient"].abs()
)

coef_df = coef_df.sort_values(
    "absolute_coefficient",
    ascending=False
)

print("\nTop features influencing the model:")
print(
    coef_df[
        ["feature", "coefficient"]
    ].head(20)
)
print("\nModel classes:")
print(model["classifier"].classes_)