import pandas as pd
import numpy as np 
from src.prediction import classify_default
from src.features import add_engineered_features


def test_zero_income_does_not_create_infinity():

    df = pd.DataFrame([
        {
            "customer_income": 0,
            "loan_amnt": 20000,
            "loan_int_rate": 10,
            "customer_age": 40,
            "cred_hist_length": 5
        }
    ])

    result = add_engineered_features(df)

    value = result.loc[
        0,
        "loan_to_income"
    ]

    assert pd.isna(value)

def test_probability_below_threshold():

    result = classify_default(
        0.55,
        0.56
    )

    assert result == "NO DEFAULT"


def test_probability_equal_to_threshold():

    result = classify_default(
        0.56,
        0.56
    )

    assert result == "DEFAULT"


def test_probability_above_threshold():

    result = classify_default(
        0.80,
        0.56
    )

    assert result == "DEFAULT"


def test_low_probability():

    result = classify_default(
        0.05,
        0.56
    )

    assert result == "NO DEFAULT"
