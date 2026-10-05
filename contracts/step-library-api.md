# Step Library API (Contract 3)

The reuse store. Written to only by the Verify & Promote Runner, on green.

- `search(intent: str, k: int) -> [{step_id, step, score, provenance}]`
  Returns candidate reusable steps/POM methods for a described intent.
- `promote(step, provenance) -> {step_id, created}`
  Embed a NEW, proven step (only called after its test passes). Idempotent/deduped.
- `stats() -> {counts by collection}`

Greenfield = `search` returns nothing → caller synthesizes → `promote` on green.
Transport TBD (HTTP/gRPC); must be language-agnostic.

## Step shape

`promote.step` (request) and every `search[].step` (response) are a **Step** as
defined by `qa_contracts/schemas/step.schema.json` (validate with
`qa_contracts.validate_step`): `kind` (`action`|`assertion`), `name`, `intent`,
`language` (`python`|`typescript`|`javascript`, the language of `body`),
`page_object`, optional `params`, and `body`. The same Step is what the
Synthesizer lists in `manifest.new` (Contract 4,
`qa_contracts/schemas/synthesis-result.schema.json`).

Wire shapes: `POST /search {intent, k}` -> `[{step_id, step, score, provenance}]`;
`POST /promote {step, provenance}` -> `{step_id, created}`.

## Healed-step memory

A locator-only fix that led to a clean green at `retries=0` (never a flaky pass) is
recorded so later synthesis and healing can prefer the known-good locator for a page and
intent. Append-only; written only by the Verify & Promote Runner.

- `record_heal(heal, provenance) -> {heal_id, created}`
- `lookup_heals(page_url: str, intent: str, k: int = 5) -> [{heal_id, heal, score, provenance}]`

**Heal** (request body `heal`, and each `lookup_heals[].heal`):

| Field | Type | Notes |
|---|---|---|
| `old_locator_expr` | string, required | the locator expression that broke |
| `new_locator_expr` | string, required | the replacement; must differ from `old_locator_expr` |
| `page_url` | string, required | page the locator lives on |
| `intent` | string, required | description of the step that uses the locator |
| `signature` | string, required | the failing locator (or snapshot) signature that was healed |
| `source_shas` | string[], optional | commit shas of the source the heal was made against |

Wire shapes:

- `POST /heals {heal, provenance}` -> `{heal_id, created}`. `heal_id` is a hash of
  `old_locator_expr`, `new_locator_expr`, normalized `page_url` and `intent`, so an exact
  repeat is a no-op (`created: false`) and the first record is kept. `422` when a required
  field is missing or empty, or when old equals new.
- `POST /heals/lookup {page_url, intent, k?}` -> `[{heal_id, heal, score, provenance}]`
  for that page only (query string, fragment and trailing slash of `page_url` are ignored),
  best intent match first. `score` is cosine similarity. `k` defaults to 5. A page with no
  heals returns `[]`.

Consumers must treat a remembered `new_locator_expr` as a candidate, not a guarantee: the
runner applies it first, re-runs the test, and falls back to normal healing if it fails.
Locators only; a heal never changes a step's intent or an assertion.
