# Loan default model

A scikit-learn Random Forest pipeline for predicting `DEFAULT` or `NO DEFAULT` from applicant information.

## Project structure

```text
loan-model/
├── data/
│   ├── loan_data.csv
│   └── cleaned_loan_data.csv
├── experiments/
│   ├── cross_validate_models.py
│   ├── random_forest_model.py
│   ├── random_forest_thresholds.py
│   └── tune_random_forest.py
├── analysis/
│   └── correlation_analysis.py
├── model/
│   └── loan_default_model.joblib
├── save_model.py
├── predict_applicant.py
├── requirements.txt
└── README.md
```

The checkout directory can have any name. Data and model paths are resolved relative to the scripts, so commands also work when launched from another directory using the script's full path.

## Setup

Use Python 3 and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Dependency versions match the existing project environment to preserve compatibility with the saved model.

## Train and predict

```powershell
.\.venv\Scripts\python.exe save_model.py
.\.venv\Scripts\python.exe predict_applicant.py
```

`save_model.py` reads `data/loan_data.csv`, removes rows without a target, excludes customer IDs and historical default, cleans numeric fields, and fits preprocessing and a 300-tree Random Forest on all available training data. It creates the model directory if needed and overwrites `model/loan_default_model.joblib`.

`predict_applicant.py` loads that pipeline, prompts for applicant details, and prints the predicted class and probabilities. The existing saved model is included locally; `.gitignore` excludes joblib files, so a fresh clone may need training first.

## Experiments and analysis

Run these from the project root:

```powershell
.\.venv\Scripts\python.exe experiments/cross_validate_models.py
.\.venv\Scripts\python.exe experiments/random_forest_model.py
.\.venv\Scripts\python.exe experiments/random_forest_thresholds.py
.\.venv\Scripts\python.exe experiments/tune_random_forest.py
.\.venv\Scripts\python.exe analysis/correlation_analysis.py
```

The experiments compare models, evaluate a Random Forest, explore classification thresholds, and tune hyperparameters. Use them to evaluate performance before fitting the final model on all data. Correlation analysis uses the separate `data/cleaned_loan_data.csv` dataset; the training and experiment scripts use `data/loan_data.csv`.
