# Tests

See [docs/TESTING.md](../docs/TESTING.md) for the TDD workflow, test layout, markers, fixtures, quality gates and how to add a resource type.

```bash
venv/bin/python -m pytest              # full suite
venv/bin/python -m pytest -m "not slow"
venv/bin/python -m pytest -k property
```
