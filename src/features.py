import numpy as np
import pandas as pd


def add_engineered_features(df):

    df = df.copy()

    df["loan_to_income"] = (
        df["loan_amnt"]
        / df["customer_income"]
    )

    df["interest_burden"] = (
        df["loan_amnt"]
        * (
            df["loan_int_rate"]
            / 100
        )
    )

    df["credit_history_ratio"] = (
        df["cred_hist_length"]
        / df["customer_age"]
    )


    engineered_features = [
        "loan_to_income",
        "interest_burden",
        "credit_history_ratio"
    ]


    for feature in engineered_features:

        df[feature] = (
            df[feature]
            .replace(
                [
                    np.inf,
                    -np.inf
                ],
                np.nan
            )
        )


    return df