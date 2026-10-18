from fastapi import FastAPI

from api.schemas import (
    ApplicantRequest,
    PredictionResponse
)

from api.service import predict_default
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Loan Default Prediction API",
    description=(
        "API for estimating the probability "
        "that a borrower may default."
    ),
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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