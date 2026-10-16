from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_root_endpoint():

    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "message":
            "Loan Default Prediction API is running"
    }


def test_predict_endpoint():

    applicant = {
        "customer_age": 45,
        "customer_income": 50000,
        "home_ownership": "RENT",
        "employment_duration": 20,
        "loan_intent": "EDUCATION",
        "loan_grade": "B",
        "loan_amnt": 20000,
        "loan_int_rate": 4,
        "term_years": 1,
        "cred_hist_length": 9
    }

    response = client.post(
        "/predict",
        json=applicant
    )

    assert response.status_code == 200

    data = response.json()

    assert "default_probability" in data
    assert "no_default_probability" in data
    assert "decision_threshold" in data
    assert "prediction" in data

    assert 0 <= data["default_probability"] <= 1
    assert 0 <= data["no_default_probability"] <= 1

    assert abs(
        data["default_probability"]
        + data["no_default_probability"]
        - 1
    ) < 1e-6

    assert data["decision_threshold"] == 0.56

    assert data["prediction"] in [
        "DEFAULT",
        "NO DEFAULT"
    ]


def test_invalid_age_is_rejected():

    applicant = {
        "customer_age": 10,
        "customer_income": 50000,
        "home_ownership": "RENT",
        "employment_duration": 5,
        "loan_intent": "PERSONAL",
        "loan_grade": "B",
        "loan_amnt": 10000,
        "loan_int_rate": 8,
        "term_years": 2,
        "cred_hist_length": 3
    }

    response = client.post(
        "/predict",
        json=applicant
    )

    assert response.status_code == 422
    

def test_invalid_home_ownership_is_rejected():

    applicant = {
        "customer_age": 35,
        "customer_income": 50000,
        "home_ownership": "INVALID",
        "employment_duration": 5,
        "loan_intent": "PERSONAL",
        "loan_grade": "B",
        "loan_amnt": 10000,
        "loan_int_rate": 8,
        "term_years": 2,
        "cred_hist_length": 3
    }

    response = client.post(
        "/predict",
        json=applicant
    )

    assert response.status_code == 422

def test_unrealistic_employment_duration_is_rejected():

    applicant = {
        "customer_age": 20,
        "customer_income": 50000,
        "home_ownership": "RENT",
        "employment_duration": 15,
        "loan_intent": "PERSONAL",
        "loan_grade": "B",
        "loan_amnt": 10000,
        "loan_int_rate": 8,
        "term_years": 2,
        "cred_hist_length": 3
    }

    response = client.post(
        "/predict",
        json=applicant
    )

    assert response.status_code == 422


def test_credit_history_longer_than_age_is_rejected():

    applicant = {
        "customer_age": 25,
        "customer_income": 50000,
        "home_ownership": "RENT",
        "employment_duration": 5,
        "loan_intent": "PERSONAL",
        "loan_grade": "B",
        "loan_amnt": 10000,
        "loan_int_rate": 8,
        "term_years": 2,
        "cred_hist_length": 30
    }

    response = client.post(
        "/predict",
        json=applicant
    )

    assert response.status_code == 422