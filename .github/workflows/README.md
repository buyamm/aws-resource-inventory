# CI pipeline

`tdd-pipeline.yml` runs on pushes to `main`, `develop` and `feature/**`, and on pull requests to `main` and `develop`. Every job uses Python 3.11 and installs `requirements-dev.txt` (plus `pip install -e .` where tests or mypy need the package). The commands are the ones in [CLAUDE.md](../../CLAUDE.md); `tests/unit/test_ci_workflow.py` checks that they stay in sync and point at files that exist.

| Job | Command | Gate |
|---|---|---|
| `type-check` | `mypy src` (settings in `pyproject.toml`) | no errors |
| `lint` | `ruff check src tests`, `black --check src tests` | no violations |
| `unit-tests` | `pytest tests/unit --cov=src`, then `coverage report` | ≥ 80 % overall; 100 % for `src/parser.py` and `src/sanitizer.py` |
| `property-tests` | `pytest tests -k property --hypothesis-seed=0` | 100 examples per property (profile in `tests/conftest.py`) |
| `integration-tests` | `pytest tests/integration` | all pass (moto 4.x mocks) |
| `e2e-tests` | `pytest tests/e2e` | all pass; live AWS tests are skipped |
| `security-scan` | `bandit -r src -ll` | no medium or high severity issue |
| `test-summary` | - | fails unless every job above succeeded |

Artifacts: `coverage-report` (HTML), `integration-test-results` and `e2e-test-results` (JUnit XML), `security-scan-results` (full bandit JSON report, including low-severity notes).

Run the same gates locally:

```bash
venv/bin/python -m pytest tests/unit --cov=src
venv/bin/coverage report --include="src/parser.py" --fail-under=100
venv/bin/coverage report --include="src/sanitizer.py" --fail-under=100
venv/bin/python -m pytest tests -k property
venv/bin/python -m pytest tests/integration tests/e2e
venv/bin/ruff check src tests && venv/bin/black --check src tests && venv/bin/mypy src
venv/bin/bandit -r src -ll
```
