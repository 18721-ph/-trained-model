from pathlib import Path

import pandas as pd


# ==================================================
# PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "loan_data.csv"
)


# ==================================================
# LOAD DATA
# ==================================================

df = pd.read_csv(
    DATA_PATH
)


# ==================================================
# BASIC INFORMATION
# ==================================================

print(
    "\n================================"
)

print(
    "LOAN INCREASE DATA AUDIT"
)

print(
    "================================"
)


print(
    "\nRows:"
)

print(
    len(df)
)


print(
    "\nColumns:"
)

for column in df.columns:

    print(
        "-",
        column
    )


# ==================================================
# DATA TYPES
# ==================================================

print(
    "\n================================"
)

print(
    "DATA TYPES"
)

print(
    "================================"
)


print(
    df.dtypes
)


# ==================================================
# MISSING VALUES
# ==================================================

print(
    "\n================================"
)

print(
    "MISSING VALUES"
)

print(
    "================================"
)


print(
    df.isna().sum()
)


# ==================================================
# LOOK FOR POSSIBLE LOAN-AMOUNT TARGETS
# ==================================================

possible_keywords = [
    "approve",
    "approved",
    "request",
    "requested",
    "increase",
    "limit",
    "eligible",
    "maximum",
    "max",
    "amount"
]


candidate_columns = []


for column in df.columns:

    lower_column = column.lower()

    for keyword in possible_keywords:

        if keyword in lower_column:

            candidate_columns.append(
                column
            )

            break


print(
    "\n================================"
)

print(
    "POSSIBLE AMOUNT-TARGET COLUMNS"
)

print(
    "================================"
)


if candidate_columns:

    for column in candidate_columns:

        print(
            "-",
            column
        )

else:

    print(
        "No obvious approved/requested increase "
        "target found."
    )


# ==================================================
# CURRENT LOAN AMOUNT
# ==================================================

print(
    "\n================================"
)

print(
    "CURRENT LOAN AMOUNT SAMPLE"
)

print(
    "================================"
)


print(
    df[
        [
            "customer_income",
            "loan_amnt",
            "loan_grade",
            "Current_loan_status"
        ]
    ].head(20)
)


# ==================================================
# TARGET QUESTION
# ==================================================

print(
    "\n================================"
)

print(
    "TARGET DESIGN CHECK"
)

print(
    "================================"
)


required_targets = [
    "approved_increase_amount",
    "approved_total_amount",
    "requested_increase_amount"
]


found_required_target = False


for column in required_targets:

    if column in df.columns:

        found_required_target = True

        print(
            "Potential supervised target found:",
            column
        )


if not found_required_target:

    print(
        "\nThe current dataset does not contain "
        "a clear historical target showing how "
        "much additional credit was approved."
    )

    print(
        "\nTherefore, loan_amnt should NOT simply "
        "be treated as the answer to the loan "
        "increase problem without further analysis."
    )