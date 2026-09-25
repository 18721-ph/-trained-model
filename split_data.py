import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv("cleaned_loan_data.csv")

# Features
X = df.drop(columns=["Current_loan_status"])

# Target
y = df["Current_loan_status"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Full dataset:")
print(X.shape)

print("\nTraining features:")
print(X_train.shape)

print("\nTesting features:")
print(X_test.shape)

print("\nTraining target distribution:")
print(y_train.value_counts())

print("\nTesting target distribution:")
print(y_test.value_counts())