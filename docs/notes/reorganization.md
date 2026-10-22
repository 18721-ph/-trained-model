# Repository organization report

## Audit before moves

The initial Git working tree was clean. A recursive inventory recorded 27,287 files, including dependency, Git, IDE, cache and generated files. `inventory-before.json` includes original paths/sizes and SHA-256 hashes for 537 files outside the main dependency/cache directories. No proposal PDFs, Word documents or notebooks were found.

Production code was already separated into `api/`, `src/`, `model/` and `frontend/`. The root contained ten research/utility scripts; four more experiments were in a flat `experiments/` directory. Backend tests were in `test/`; two datasets shared `data/`.

The dependency/path audit found:

- API imports `api.schemas`, `api.service`, `src.features` and `src.prediction`. Its model paths already resolve from `__file__` and needed no change.
- Model tests already resolve the project root from their file location; moving `test/` to `tests/` preserves that depth.
- Root cross-validation and feature-engineering scripts used working-directory-relative CSV paths. Other research scripts needed their project-root depth updated after moving.
- Correlation analysis uses the cleaned dataset, so it remains active and now loads `data/processed/cleaned_loan_data.csv`.
- The interactive prediction and persistence scripts import `src`; direct execution now adds their resolved project root to Python's import path.
- Frontend API configuration and Playwright's backend launch path do not depend on any moved files.
- The two cross-validation scripts are distinct: the original `experiments/` version adds a feature-importance block referencing undefined `model`. Both versions are retained. That pre-existing research issue is documented, not repaired in this organizational change.

## Moves and new folders

`moves.json` is the complete original-to-final mapping (17 entries, including the whole test directory and its caches).

| Original files | Destination |
| --- | --- |
| `calibration_test.py`, `calibration_curve_test.py`, `calibrated_threshold_test.py` | `experiments/calibration/` |
| `feature_engineering_test.py`, `feature_engineering_v2.py` | `experiments/feature_engineering/` |
| Root `cross_validate_models.py`; `experiments/random_forest_model.py`, `experiments/tune_random_forest.py` | `experiments/model_selection/` |
| `train_validation_test_threshold.py`, `experiments/random_forest_thresholds.py` | `experiments/threshold_tuning/` |
| Original `experiments/cross_validate_models.py` | `experiments/archived_experiments/` |
| `save_model.py` | `scripts/training/` |
| `predict_applicant.py` | `scripts/prediction/` |
| `loan_increase_data_audit.py` | `scripts/audits/` |
| `data/loan_data.csv` | `data/raw/` |
| `data/cleaned_loan_data.csv` | `data/processed/` |
| `test/` including caches | `tests/` |

New folders are the destinations above plus `docs/notes/`. Existing `analysis/`, `api/`, `src/`, `model/` and `frontend/` remain in place. No empty proposal folders were invented.

## Compatibility and documentation

Research scripts use `pathlib` and their resolved file location. Only import/path compatibility was edited; no feature engineering, training parameters, thresholds or inference logic changed. `src/` and the script packages have explicit `__init__.py` files. A shared path module was unnecessary for these independently executable historical scripts.

`pytest.ini` uses `testpaths = tests`, `python_files = test_*.py` and `pythonpath = .`. Experiments ending in `_test.py` are excluded from normal discovery. `.pytest_cache/` is now ignored, and existing caches are preserved.

README now explains the project goal, folder structure, artifact/data locations, historical experiments, Windows environment activation, backend/frontend startup, testing, script invocation and decision-support limitations. Previous architecture and UI usage guidance is retained.

All model artifacts, metadata, API code, existing shared feature/prediction code, frontend source, dependencies and datasets are preserved. No models were trained. Training scripts were inspected statically, not imported, because they execute training at module level. They still write artifacts when deliberately run by a future user.

## Verification

The frontend build used `--emptyOutDir=false` so Vite did not clear existing build files. Environment, IDE, Git and cache folders remain in place. No deletion or cleanup commands were used.

| Check | Result |
| --- | --- |
| Feature, prediction and API imports | Passed |
| Pytest collection | Exactly 17 tests, all under `tests/` |
| Targeted prediction/model/API tests | 17 passed (5 prediction, 6 model, 6 API) |
| Full `python -m pytest -v` | 17 passed, 4 existing dependency deprecation warnings |
| Frontend `npm.cmd run lint` | Passed |
| Frontend `npm.cmd run build -- --emptyOutDir=false` | Passed |
| Uvicorn with `--reload --port 8001` | Application startup complete; live `GET /` returned HTTP 200; verification server stopped afterward |
| File preservation | All 27,287 original files exist at their original or mapped destinations; zero missing |
| SHA-256 checks | Models, metadata, datasets, API, existing shared code, backend tests and frontend source/assets unchanged |
| Static Python/path verification from outside the repository | 30 Python files parsed; dataset/model paths resolve successfully without executing training |

`scripts/audits/verify_organization.py` can repeat the inventory, hash and path checks without training models. Detailed results are in `verification.json`. Frontend unit/browser tests were not rerun for this organization-only change; the older UI verification results in README are historical.

ZERO files were deleted. Git currently displays old paths as deleted and destinations as untracked because normal filesystem moves have not been staged; `moves.json` and the preservation check account for every moved file. No Git reset, cleanup, staging or commit was performed.

Remaining organizational issues: the pytest cache already contains tracked files, so adding an ignore rule does not untrack them. It is intentionally preserved and test execution updated its node list. Both cross-validation versions remain available, with the archived version's existing undefined-variable issue documented above. Existing generated/IDE/environment directories are intentionally retained.
