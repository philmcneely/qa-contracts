# Using qa-contracts

`qa-contracts` is a small Python package holding the versioned contracts for the
QA / test-generation platform plus **model-free validators** for them. Components
import the validators instead of re-implementing checks, so any one can be swapped
without breaking its neighbors. No LLM, no network.

## The contracts

| Contract | Boundary | Artifact | Validator |
|---|---|---|---|
| 1 | Spec Normalizer -> Test-Case Designer | Normalized Spec (`schemas/normalized-spec.schema.json`) | `validate_normalized_spec(obj)` |
| 2 | Test-Case Designer -> Automation Synthesizer | Test Cases (`schemas/test-cases.schema.json`) | `validate_test_cases(obj)` |
| 3 | Synthesizer / Runner <-> Step Library | `search` / `promote` / `stats` API (`contracts/step-library-api.md`); its `step` payloads are Steps | `validate_step(obj)` for the Step |
| 4 | Automation Synthesizer -> Verify & Promote Runner | Synthesis Result `{schema_version, ticket_id?, test_file, manifest{reused,new}, warnings}` (`schemas/synthesis-result.schema.json`) | `validate_synthesis_result(obj)` |
| - | shared by 3 and 4 | Step: `{kind, language, name, intent, page_object, params?, body}` (`schemas/step.schema.json`) | `validate_step(obj)` |

`manifest.new` holds full Steps (the Runner promotes them on green);
`manifest.reused` holds references `{step_id, kind, language, name, page_object, intent, score}`
to steps already in the library. An assertion Step takes no `params`.

`language` is required on every Step and every reused reference, one of
`python`, `typescript`, `javascript`. A Step's `body` lines are written in that
language (for example `await self.page.get_by_role(...).click()` for `python`,
`await this.page.getByRole(...).click();` for `typescript`/`javascript`), so a
reuse is only valid when the reference's `language` matches the test being
generated. Use the same value in `manifest.new` and `manifest.reused` for a
given target.

## Test data in the Normalized Spec

`test_data` is an optional object on the Normalized Spec for concrete data the
spec provides (credentials, paths, identifiers). The Synthesizer should use
these values in generated tests instead of inventing placeholders. Each value is
a string or a string-to-string object; omit the field when the spec has no data.

```json
"test_data": {
  "valid_credentials": {"username": "user@example.com", "password": "correct-password"},
  "invalid_credentials": {"username": "user@example.com", "password": "wrong-password"},
  "login_path": "/login"
}
```

## Install in a component repo

```bash
pip install git+https://github.com/<owner>/qa-contracts.git
```

For local development of this repo:

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt -e .
```

## Consume the validators

```python
from qa_contracts import (
    validate_normalized_spec, validate_test_cases,
    validate_synthesis_result, validate_step, ContractError,
)

try:
    validate_normalized_spec(spec_dict)
    validate_test_cases(test_cases_dict)
    validate_synthesis_result(synthesis_result_dict)
    validate_step(step_dict)
except ContractError as err:
    print(err)
```

Validators return `None` on success and raise `ContractError` (a `ValueError`)
listing every violation, one per line:

```
invalid Test Cases:
  at /test_cases/0/steps: [] should be non-empty
```

| Part | Meaning |
|---|---|
| First line | `invalid <Normalized Spec \| Test Cases \| Synthesis Result \| Step>:` |
| `at /<path>` | JSON path of the offending value (`/` = document root) |
| Remainder | the `jsonschema` message for that violation |

Match on the path, not on exact message wording.

## Running the tests

Tests live in `contract-tests/`. Each level is a pytest marker and runs alone.

| Level | Command | What it checks |
|---|---|---|
| Unit | `pytest -m unit` | validators accept valid objects and raise `ContractError` with correct paths per invalid case |
| Integration | `pytest -m integration` | every file under `fixtures/valid/` passes and every `fixtures/invalid/` file fails for its stated reason |
| API | `pytest -m api` | public exports and the `ContractError` shape, as a consuming repo sees them |
| E2E | `pytest -m e2e` | login Normalized Spec -> Test Cases both validate; `covers` ids are a subset of AC ids and every AC is covered |
| All | `pytest` | the full suite (what CI runs) |

Adding an invalid fixture: drop the file in `contract-tests/fixtures/invalid/`
(`spec.*` Contract 1, `tc.*` Contract 2, `sr.*` Contract 4, `step.*` Step) and add its expected reason to
`REASONS` in `contract-tests/test_integration.py`; a test fails if they drift apart.
