"""Unit: each validator accepts valid objects and raises ContractError with the right path."""
import copy

import pytest

from qa_contracts import (
    ContractError,
    validate_normalized_spec,
    validate_step,
    validate_synthesis_result,
    validate_test_cases,
)

pytestmark = pytest.mark.unit


def _fails(validator, obj, *fragments):
    with pytest.raises(ContractError) as exc:
        validator(obj)
    for fragment in fragments:
        assert fragment in str(exc.value)


def test_spec_accepts_minimal(minimal_spec):
    validate_normalized_spec(minimal_spec)


def test_tcs_accept_minimal(minimal_tcs):
    validate_test_cases(minimal_tcs)


@pytest.mark.parametrize("field", ["schema_version", "ticket_id", "source", "acceptance_criteria"])
def test_spec_missing_required_field(minimal_spec, field):
    del minimal_spec[field]
    _fails(validate_normalized_spec, minimal_spec, f"'{field}' is a required property")


def test_spec_bad_source_enum(minimal_spec):
    minimal_spec["source"] = "slack"
    _fails(validate_normalized_spec, minimal_spec, "at /source:", "'slack' is not one of")


def test_spec_wrong_schema_version(minimal_spec):
    minimal_spec["schema_version"] = "9.9"
    _fails(validate_normalized_spec, minimal_spec, "at /schema_version:")


def test_spec_bad_scenario_type_path(minimal_spec):
    minimal_spec["acceptance_criteria"][0]["scenarios"][0]["type"] = "happy"
    _fails(
        validate_normalized_spec,
        minimal_spec,
        "at /acceptance_criteria/0/scenarios/0/type:",
        "'happy' is not one of",
    )


def test_spec_additional_properties_rejected(minimal_spec):
    minimal_spec["surprise"] = 1
    _fails(validate_normalized_spec, minimal_spec, "Additional properties")


def test_spec_rejects_non_object():
    _fails(validate_normalized_spec, [], "is not of type 'object'")


@pytest.mark.parametrize("field", ["schema_version", "ticket_id", "test_cases"])
def test_tcs_missing_required_field(minimal_tcs, field):
    del minimal_tcs[field]
    _fails(validate_test_cases, minimal_tcs, f"'{field}' is a required property")


def test_tcs_empty_steps_path(minimal_tcs):
    minimal_tcs["test_cases"][0]["steps"] = []
    _fails(validate_test_cases, minimal_tcs, "at /test_cases/0/steps:")


def test_tcs_step_missing_expected_path(minimal_tcs):
    del minimal_tcs["test_cases"][0]["steps"][0]["expected"]
    _fails(
        validate_test_cases,
        minimal_tcs,
        "at /test_cases/0/steps/0:",
        "'expected' is a required property",
    )


def test_tcs_covers_must_be_array(minimal_tcs):
    minimal_tcs["test_cases"][0]["covers"] = "ac-1"
    _fails(validate_test_cases, minimal_tcs, "at /test_cases/0/covers:", "is not of type 'array'")


def test_all_violations_reported_together(minimal_spec):
    minimal_spec["source"] = "slack"
    minimal_spec["schema_version"] = "9.9"
    _fails(validate_normalized_spec, minimal_spec, "at /source:", "at /schema_version:")


def test_validation_does_not_mutate_input(minimal_spec):
    before = copy.deepcopy(minimal_spec)
    validate_normalized_spec(minimal_spec)
    assert minimal_spec == before


def test_step_accepts_minimal_and_login(minimal_step, login_step):
    validate_step(minimal_step)
    validate_step(login_step)


@pytest.mark.parametrize("field", ["kind", "language", "name", "intent", "page_object", "body"])
def test_step_missing_required_field(login_step, field):
    del login_step[field]
    _fails(validate_step, login_step, f"'{field}' is a required property")


@pytest.mark.parametrize("language", ["python", "typescript", "javascript"])
def test_step_accepts_each_language(login_step, language):
    login_step["language"] = language
    validate_step(login_step)


@pytest.mark.parametrize("language", ["ruby", "Python", "", None, 3])
def test_step_bad_language(login_step, language):
    login_step["language"] = language
    _fails(validate_step, login_step, "at /language:")


def test_step_accepts_typescript_fixture(login_ts_step):
    validate_step(login_ts_step)
    assert login_ts_step["language"] == "typescript"


def test_step_params_optional(login_step):
    del login_step["params"]
    validate_step(login_step)


def test_step_bad_kind(login_step):
    login_step["kind"] = "click"
    _fails(validate_step, login_step, "at /kind:", "'click' is not one of")


@pytest.mark.parametrize("name", ["SubmitCreds", "1go", "go-now", ""])
def test_step_bad_name(login_step, name):
    login_step["name"] = name
    _fails(validate_step, login_step, "at /name:")


def test_step_bad_page_object(login_step):
    login_step["page_object"] = "login_page"
    _fails(validate_step, login_step, "at /page_object:")


def test_step_blank_intent(login_step):
    login_step["intent"] = "   "
    _fails(validate_step, login_step, "at /intent:")


def test_step_param_must_be_identifier(login_step):
    login_step["params"] = ["email", "1bad"]
    _fails(validate_step, login_step, "at /params/1:")


def test_step_params_unique(login_step):
    login_step["params"] = ["email", "email"]
    _fails(validate_step, login_step, "at /params:")


def test_step_body_must_be_non_empty_lines(login_step):
    login_step["body"] = []
    _fails(validate_step, login_step, "at /body:")
    login_step["body"] = ["  "]
    _fails(validate_step, login_step, "at /body/0:")


def test_assertion_step_takes_no_params(minimal_step):
    minimal_step["params"] = ["email"]
    _fails(validate_step, minimal_step, "at /params:")


def test_step_additional_properties_rejected(login_step):
    login_step["code"] = "x"
    _fails(validate_step, login_step, "Additional properties")


def test_sr_accepts_minimal_and_login(minimal_sr, login_sr):
    validate_synthesis_result(minimal_sr)
    validate_synthesis_result(login_sr)


@pytest.mark.parametrize("field", ["schema_version", "test_file", "manifest", "warnings"])
def test_sr_missing_required_field(login_sr, field):
    del login_sr[field]
    _fails(validate_synthesis_result, login_sr, f"'{field}' is a required property")


def test_sr_ticket_id_optional_but_non_empty(login_sr):
    del login_sr["ticket_id"]
    validate_synthesis_result(login_sr)
    login_sr["ticket_id"] = ""
    _fails(validate_synthesis_result, login_sr, "at /ticket_id:")


@pytest.mark.parametrize("key", ["reused", "new"])
def test_sr_manifest_requires_both_lists(login_sr, key):
    del login_sr["manifest"][key]
    _fails(validate_synthesis_result, login_sr, f"'{key}' is a required property")


def test_sr_new_items_are_validated_as_steps(login_sr):
    login_sr["manifest"]["new"][0]["kind"] = "click"
    _fails(validate_synthesis_result, login_sr, "at /manifest/new/0/kind:")


def test_sr_new_assertion_with_params_rejected(login_sr):
    login_sr["manifest"]["new"][0]["params"] = ["email"]
    _fails(validate_synthesis_result, login_sr, "at /manifest/new/0/params:")


def test_sr_reused_item_path(login_sr):
    del login_sr["manifest"]["reused"][0]["step_id"]
    _fails(validate_synthesis_result, login_sr, "at /manifest/reused/0:", "'step_id' is a required property")


def test_sr_reused_requires_language(login_sr):
    del login_sr["manifest"]["reused"][0]["language"]
    _fails(validate_synthesis_result, login_sr, "at /manifest/reused/0:", "'language' is a required property")


def test_sr_reused_bad_language(login_sr):
    login_sr["manifest"]["reused"][0]["language"] = "ruby"
    _fails(validate_synthesis_result, login_sr, "at /manifest/reused/0/language:")


def test_sr_new_step_requires_language(login_sr):
    del login_sr["manifest"]["new"][0]["language"]
    _fails(validate_synthesis_result, login_sr, "at /manifest/new/0:", "'language' is a required property")


def test_sr_reused_score_range(login_sr):
    login_sr["manifest"]["reused"][0]["score"] = -0.1
    _fails(validate_synthesis_result, login_sr, "at /manifest/reused/0/score:")


def test_sr_additional_properties_rejected(login_sr):
    login_sr["surprise"] = 1
    _fails(validate_synthesis_result, login_sr, "Additional properties")
