"""Integration: every fixture under fixtures/ validates against its schema as expected."""
import pytest

from conftest import fixture_files, fixture_kind, load_json
from qa_contracts import (
    ContractError,
    validate_normalized_spec,
    validate_step,
    validate_synthesis_result,
    validate_test_cases,
)

pytestmark = pytest.mark.integration

# expected substring in the failure reason for each invalid fixture
REASONS = {
    "spec.missing-ticket-id.json": "'ticket_id' is a required property",
    "spec.bad-source-enum.json": "'slack' is not one of",
    "spec.wrong-schema-version.json": "at /schema_version:",
    "spec.bad-scenario-type.json": "'happy' is not one of",
    "spec.bad-test-data-shape.json": "at /test_data/valid_credentials:",
    "tc.missing-step-expected.json": "'expected' is a required property",
    "tc.wrong-schema-version.json": "at /schema_version:",
    "tc.empty-steps.json": "at /test_cases/0/steps:",
    "tc.covers-not-array.json": "is not of type 'array'",
    "step.bad-kind.json": "at /kind:",
    "step.missing-body.json": "'body' is a required property",
    "step.empty-body.json": "at /body:",
    "step.bad-name.json": "at /name:",
    "step.bad-page-object.json": "at /page_object:",
    "step.assertion-with-params.json": "at /params:",
    "step.duplicate-params.json": "at /params:",
    "step.missing-language.json": "'language' is a required property",
    "step.bad-language.json": "at /language:",
    "step.extra-field.json": "Additional properties",
    "sr.missing-manifest.json": "'manifest' is a required property",
    "sr.wrong-schema-version.json": "at /schema_version:",
    "sr.missing-schema-version.json": "'schema_version' is a required property",
    "sr.empty-test-file.json": "at /test_file:",
    "sr.new-bare-string.json": "at /manifest/new/0:",
    "sr.new-step-missing-body.json": "at /manifest/new/0:",
    "sr.reused-missing-step-id.json": "'step_id' is a required property",
    "sr.reused-missing-language.json": "'language' is a required property",
    "sr.reused-score-out-of-range.json": "at /manifest/reused/0/score:",
    "sr.warnings-not-strings.json": "at /warnings/0:",
}


_VALIDATORS = {
    "spec": validate_normalized_spec,
    "tc": validate_test_cases,
    "step": validate_step,
    "sr": validate_synthesis_result,
}


def _validator(path):
    return _VALIDATORS[fixture_kind(path)]


@pytest.mark.parametrize("path", fixture_files("valid"), ids=lambda p: p.name)
def test_valid_fixture_passes(path):
    _validator(path)(load_json(path))


@pytest.mark.parametrize("path", fixture_files("invalid"), ids=lambda p: p.name)
def test_invalid_fixture_fails_with_reason(path):
    assert path.name in REASONS, f"add expected reason for {path.name}"
    with pytest.raises(ContractError) as exc:
        _validator(path)(load_json(path))
    assert REASONS[path.name] in str(exc.value)


def test_valid_fixtures_cover_every_language_family():
    languages = set()
    for path in fixture_files("valid"):
        data = load_json(path)
        if fixture_kind(path) == "step":
            languages.add(data["language"])
        elif fixture_kind(path) == "sr":
            m = data["manifest"]
            languages |= {s["language"] for s in m["reused"] + m["new"]}
    assert {"python", "typescript"} <= languages


def test_every_reason_has_a_fixture():
    assert set(REASONS) == {p.name for p in fixture_files("invalid")}
