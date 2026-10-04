# qa-contracts

Versioned, model-free contracts for a QA / test-generation pipeline — the shared
schemas and validators that let independent components interoperate. Each component
depends only on these contracts, so any one of them can be swapped or run on its own.

## Contracts

- `contracts/normalized-spec.schema.json` — a spec normalized to canonical BDD
- `contracts/test-cases.schema.json` — structured test cases derived from a spec
- `contracts/step.schema.json` — a reusable, executable test step
- `contracts/synthesis-result.schema.json` — a generated test plus its reuse manifest
- `contracts/step-library-api.md` — the step-library search/promote interface

## Validators

```bash
pip install .
```

```python
from qa_contracts import (
    validate_normalized_spec,
    validate_test_cases,
    validate_step,
    validate_synthesis_result,
)
```

Each validator raises `ContractError` (a `ValueError`) listing every violation with
its JSON path. No model or network is involved.

## Tests

Model-free contract tests, organized into `unit` / `integration` / `api` / `e2e` markers:

```bash
pip install -r requirements.txt -e .
pytest              # full suite
pytest -m unit      # one level
```

See `docs/USAGE.md` for how a consuming component installs and uses the validators.
