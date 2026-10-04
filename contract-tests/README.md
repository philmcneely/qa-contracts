# Contract tests (model-free)

Validate that artifacts crossing each boundary conform to the schema in
`../contracts/` — NO LLM involved. Every producer/consumer runs these in CI so a
component can be swapped without breaking its neighbors.

- validate sample Normalized Spec payloads against normalized-spec.schema.json
- validate sample Test Cases payloads against test-cases.schema.json
- round-trip fixtures live in `fixtures/`

Layout (pytest markers, each runnable alone: `pytest -m unit`, etc.):

| File | Marker | Covers |
|---|---|---|
| `test_unit.py` | `unit` | validators accept/reject with correct paths |
| `test_integration.py` | `integration` | every fixture validates as expected |
| `test_api.py` | `api` | public surface + `ContractError` shape |
| `test_e2e.py` | `e2e` | login spec -> test cases, traceability |
