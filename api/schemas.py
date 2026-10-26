from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    model_validator
)


class ApplicantRequest(BaseModel):

    customer_age: int = Field(
        ge=18,
        le=100
    )

    customer_income: float = Field(
        gt=0
    )

    home_ownership: Literal[
        "RENT",
        "OWN",
        "MORTGAGE",
        "OTHER"
    ]

    employment_duration: float = Field(
        ge=0,
        le=70
    )

    loan_intent: Literal[
        "EDUCATION",
        "MEDICAL",
        "VENTURE",
        "PERSONAL",
        "DEBTCONSOLIDATION",
        "HOMEIMPROVEMENT"
    ]

    loan_grade: Literal[
        "A",
        "B",
        "C",
        "D",
        "E"
    ]

    loan_amnt: float = Field(
        gt=0
    )

    loan_int_rate: float = Field(
        ge=0,
        le=50
    )

    term_years: int = Field(
        ge=1,
        le=30
    )

    cred_hist_length: int = Field(
        ge=0,
        le=80
    )


    @model_validator(mode="after")
    def validate_relationships(self):

        max_possible_employment = (
            self.customer_age - 14
        )

        if (
            self.employment_duration
            > max_possible_employment
        ):
            raise ValueError(
                "Employment duration is not "
                "realistic for the applicant's age."
            )


        if (
            self.cred_hist_length
            > self.customer_age
        ):
            raise ValueError(
                "Credit history length cannot "
                "exceed customer age."
            )


        return self


class ExplanationFactor(BaseModel):

    feature: str

    impact: float


class PredictionResponse(BaseModel):

    default_probability: float

    no_default_probability: float

    decision_threshold: float

    prediction: Literal[
        "DEFAULT",
        "NO DEFAULT"
    ]

    top_risk_factors: list[
        ExplanationFactor
    ]

    top_protective_factors: list[
        ExplanationFactor
    ]


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=1024)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=1024)
    new_password: str = Field(min_length=1, max_length=1024)


class UserResponse(BaseModel):
    username: str
    display_name: str
    role: str
