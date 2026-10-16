from fastapi import FastAPI

from api.schemas import (
    ApplicantRequest,
    PredictionResponse
)

from api.service import predict_default


app = FastAPI(
    title="Loan Default Prediction API",
    description=(
        "API for estimating the probability "
        "that a borrower may default."
    ),
    version="1.0.0"
)


# ==================================================
# HEALTH CHECK
# ==================================================

@app.get("/")
def root():

    return {
        "message":
            "Loan Default Prediction API is running"
    }


# ==================================================
# PREDICTION ENDPOINT
# ==================================================

@app.post(
    "/predict",
    response_model=PredictionResponse
)
def predict(
    applicant: ApplicantRequest
):

    result = predict_default(
        applicant.model_dump()
    )

    return result