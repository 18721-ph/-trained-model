# Loan Default Risk Prediction System

An academic decision-support dashboard for lending staff. React submits borrower and loan details to a local FastAPI API. The existing sigmoid-calibrated Random Forest returns probabilities and a 0.56 decision threshold. SHAP explains the underlying base Random Forest; its impacts are neither causal effects nor percentage changes in calibrated probability.

## Architecture

- `frontend/src/components/layout`: shell and navigation.
- `frontend/src/components/assessment`: form, native constraints, relationship checks.
- `frontend/src/components/results`: probabilities, classification, threshold and SHAP groups.
- `frontend/src/pages`: assessment orchestration and model information.
- `frontend/src/services/predictionApi.ts`: typed fetch boundary, timeout, response validation and error handling.
- `frontend/src/types/prediction.ts`: request/response interfaces.
- `api/main.py`, `schemas.py`, `service.py`: HTTP API, authoritative validation, model loading and inference.
- `src/features.py`, `prediction.py`: existing feature engineering and classification.
- `model/`: saved base/calibrated models and metadata.
- `test/`: Python tests; `frontend/src/**/*.test.*`: mocked frontend tests.
- `frontend/e2e/`: real local browser integration test.

No submissions are persisted or sent to external services. Editing inputs clears the previous result. Dashboard, history and settings are marked as planned. Model information is a static reference to the current metadata, not a live health check.

## Backend setup: Windows PowerShell

From the project root, use the compatible existing Python environment (verified with Python 3.13):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8001
```

If activation is unavailable, invoke the interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8001
```

API: http://127.0.0.1:8001 ; interactive documentation: http://127.0.0.1:8001/docs . Predictions use `POST /predict`.

The files `model/base_random_forest.joblib`, `model/calibrated_loan_default_model.joblib`, and `model/model_metadata.json` must already be present. Joblib artifacts are excluded from Git; obtain the existing project artifacts if missing. Setup and tests do not retrain or replace the model. Keep the pinned Python dependencies for artifact compatibility.

## Frontend setup

In another PowerShell terminal, from the project root (verified with Node 24):

```powershell
cd frontend
npm.cmd ci
Copy-Item .env.example .env
npm.cmd run dev
```

Open http://localhost:5173 . The fixed Vite port matches the existing API CORS configuration.

`VITE_API_BASE_URL` defaults to `http://127.0.0.1:8001`; set it in `frontend/.env` and restart Vite to override it. Use only your local API for applicant data. Environment values are public configuration, not secrets. Enter income and loan amount in the same monetary unit consistent with the project dataset; no currency conversion is performed.

## Verification

From the project root:

```powershell
.\.venv\Scripts\python.exe -m pytest test/test_prediction.py -v
.\.venv\Scripts\python.exe -m pytest test/test_model.py -v
.\.venv\Scripts\python.exe -m pytest test/test_api.py -v
.\.venv\Scripts\python.exe -m pytest --collect-only -q
.\.venv\Scripts\python.exe -m pytest -v --durations=5
```

`pytest.ini` restricts automatic discovery to `test/test_*.py`. Old root and `experiments/` training scripts are preserved and not collected. Saved-model loading and SHAP imports still take several seconds.

From `frontend/`:

```powershell
npm.cmd run lint
npm.cmd run build
npm.cmd test
npm.cmd run test:e2e
```

Vitest tests mock the prediction service or fetch and do not require Python. Playwright uses installed Microsoft Edge and starts FastAPI and Vite if they are not running. It submits the known applicant, compares the displayed result with the API response, checks tablet/mobile overflow and saves screenshots in `frontend/test-results/`. The test does not assert an exact probability.

For a manual check, enter age 45, income 50000, RENT, employment 20 years, credit history 9 years, EDUCATION, grade B, amount 20000, interest 4%, and term 1 year. Click Assess Default Risk. The historical result is approximately 67.65% / DEFAULT; always use the actual API response.

Verified in this workspace: lint and production build passed; 17 frontend unit tests and 17 Python tests passed. The real browser assessment returned 0.676548282568419 / DEFAULT and displayed 67.65%. Desktop, tablet and mobile overflow checks passed.

## Limitations and interpretation

This is an academic prototype without authentication, customer storage, CRB integration or production infrastructure. Model Information shows approximate evaluation results on the held-out project test dataset, not guarantees for real bank customers. Independent validation, fairness assessment, access controls and monitoring would be needed before operational deployment.

This prediction is intended to support credit assessment and should not be used as the sole basis for approving or rejecting a loan.

Existing Python dependencies emit Starlette/httpx and SHAP/matplotlib deprecation warnings. The browser runner may emit a harmless NO_COLOR/FORCE_COLOR warning. These do not justify changing the model or its dependencies as part of the UI integration.
