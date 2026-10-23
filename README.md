# Loan Default Risk Prediction System

An academic decision-support dashboard for lending staff. React submits borrower and loan details to a local FastAPI API. The existing sigmoid-calibrated Random Forest returns probabilities and a 0.56 decision threshold. SHAP explains the underlying base Random Forest; its impacts are neither causal effects nor percentage changes in calibrated probability.

## Project goal and repository structure

This final-year project helps lending institutions assess loan default risk with calibrated probabilities and supporting explanations. Historical experiments are preserved for academic traceability.

```text
loan model/
|-- api/                         FastAPI endpoints, validation and inference
|-- src/                         Shared features and classification
|-- model/                       Saved models and metadata
|-- data/raw/loan_data.csv
|-- data/processed/cleaned_loan_data.csv
|-- analysis/                    Correlation analysis
|-- experiments/
|   |-- model_selection/
|   |-- calibration/
|   |-- threshold_tuning/
|   |-- feature_engineering/
|   `-- archived_experiments/    Alternate cross-validation version
|-- scripts/
|   |-- training/save_model.py
|   |-- prediction/predict_applicant.py
|   `-- audits/loan_increase_data_audit.py
|-- tests/                       Automated backend tests
|-- frontend/                    Existing React/Vite app and frontend tests
|-- docs/notes/                  Inventory, move map and organization report
|-- requirements.txt
|-- pytest.ini
`-- README.md
```

Both datasets and both cross-validation versions are preserved. The archived cross-validation version has an existing undefined `model` reference in its final feature-importance block. No proposal documents or notebooks were found. Virtual environment, IDE files, caches and generated frontend files remain in place.

From the project root, after activating the environment:

```powershell
python -m scripts.prediction.predict_applicant
python -m scripts.audits.loan_increase_data_audit
python analysis/correlation_analysis.py
```

Scripts resolve file paths from their own location; direct execution by absolute script path also supports other working directories. Experiments train models when executed. `scripts/training/save_model.py` retrains and writes model artifacts when deliberately run; it is not part of setup or verification.

See the [organization report](docs/notes/reorganization.md), [original inventory](docs/notes/inventory-before.json) and [complete move map](docs/notes/moves.json).

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
- `tests/`: Python tests; `frontend/src/**/*.test.*`: mocked frontend tests.
- `frontend/e2e/`: real local browser integration test.

Submissions go to the configured prediction API. Successful assessments are retained in browser memory for the current session by default; no records are written to browser storage or a database. Refreshing or closing the page clears history and resets preferences. Editing inputs clears the current result but preserves completed history entries.

- Dashboard summarizes retained assessments, predicted classes and mean default probability. These are session statistics, not model performance metrics.
- Assessment History filters results by prediction and shows original inputs, probabilities, thresholds and SHAP explanations.
- Settings enables/disables future history collection, clears existing history after confirmation, and checks the configured API connection. Clearing history leaves the current assessment form/result intact.
- Model Information remains a static reference to the current metadata. Workspace settings do not change the model or its decision threshold.

## Backend setup: Windows PowerShell

From the project root, use the compatible existing Python environment (verified with Python 3.13):

```powershell
if (-not (Test-Path .venv)) { python -m venv .venv }
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
.\.venv\Scripts\python.exe -m pytest tests/test_prediction.py -v
.\.venv\Scripts\python.exe -m pytest tests/test_model.py -v
.\.venv\Scripts\python.exe -m pytest tests/test_api.py -v
.\.venv\Scripts\python.exe -m pytest --collect-only -q
.\.venv\Scripts\python.exe -m pytest -v --durations=5
```

`pytest.ini` restricts automatic discovery to `tests/test_*.py` and adds the project root to the import path. Historical `experiments/` training scripts are preserved and not collected. Saved-model loading and SHAP imports still take several seconds.

From `frontend/`:

```powershell
npm.cmd run lint
npm.cmd run build -- --emptyOutDir=false
npm.cmd test
npm.cmd run test:e2e
```

The build flag preserves existing files in `frontend/dist/` instead of clearing the directory. Vitest tests mock the prediction service or fetch and do not require Python. Playwright uses installed Microsoft Edge and starts FastAPI and Vite if they are not running. It submits the known applicant, compares the displayed result with the API response, checks tablet/mobile overflow and saves screenshots in `frontend/test-results/`. The test does not assert an exact probability.

For a manual check, enter age 45, income 50000, RENT, employment 20 years, credit history 9 years, EDUCATION, grade B, amount 20000, interest 4%, and term 1 year. Click Assess Default Risk. The historical result is approximately 67.65% / DEFAULT; always use the actual API response.

Verified in this workspace: lint and production build passed; 17 frontend unit tests and 17 Python tests passed. The real browser assessment returned 0.676548282568419 / DEFAULT and displayed 67.65%. Desktop, tablet and mobile overflow checks passed.

## Limitations and interpretation

This is an academic prototype without authentication, customer storage, CRB integration or production infrastructure. Model Information shows approximate evaluation results on the held-out project test dataset, not guarantees for real bank customers. Independent validation, fairness assessment, access controls and monitoring would be needed before operational deployment.

This prediction is intended to support credit assessment and should not be used as the sole basis for approving or rejecting a loan.

Existing Python dependencies emit Starlette/httpx and SHAP/matplotlib deprecation warnings. The browser runner may emit a harmless NO_COLOR/FORCE_COLOR warning. These do not justify changing the model or its dependencies as part of the UI integration.
