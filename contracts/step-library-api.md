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
`page_object`, optional `params`, and `body`. The same Step is what the
Synthesizer lists in `manifest.new` (Contract 4,
`qa_contracts/schemas/synthesis-result.schema.json`).

Wire shapes: `POST /search {intent, k}` -> `[{step_id, step, score, provenance}]`;
`POST /promote {step, provenance}` -> `{step_id, created}`.
