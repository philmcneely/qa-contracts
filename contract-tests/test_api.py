"""API: the public surface as a consuming repo uses it, including the ContractError shape."""
import pytest

import qa_contracts
from qa_contracts import (
    ContractError,
    validate_normalized_spec,
    validate_step,
    validate_synthesis_result,
    validate_test_cases,
)

pytestmark = pytest.mark.api


def test_public_names_exported():
    assert set(qa_contracts.__all__) == {
        "ContractError",
        "validate_normalized_spec",
        "validate_step",
        "validate_synthesis_result",
        "validate_test_cases",
    }
    for name in qa_contracts.__all__:
        assert hasattr(qa_contracts, name)


def test_validators_return_none_on_success(minimal_spec, minimal_tcs):
    assert validate_normalized_spec(minimal_spec) is None
    assert validate_test_cases(minimal_tcs) is None


def test_contract_error_is_a_value_error():
    assert issubclass(ContractError, ValueError)


def test_error_message_shape_for_spec(minimal_spec):
    del minimal_spec["ticket_id"]
    with pytest.raises(ValueError) as exc:  # consumers may catch the base class
        validate_normalized_spec(minimal_spec)
    lines = str(exc.value).splitlines()
    assert lines[0] == "invalid Normalized Spec:"
    assert all(line.startswith("  at /") for line in lines[1:])


def test_error_message_shape_for_test_cases(minimal_tcs):
    minimal_tcs["test_cases"][0]["steps"] = []
    with pytest.raises(ContractError) as exc:
        validate_test_cases(minimal_tcs)
    lines = str(exc.value).splitlines()
    assert lines[0] == "invalid Test Cases:"
    assert any(line.startswith("  at /test_cases/0/steps:") for line in lines[1:])


def test_one_line_per_violation(minimal_spec):
    minimal_spec["source"] = "slack"
    minimal_spec["schema_version"] = "9.9"
    with pytest.raises(ContractError) as exc:
        validate_normalized_spec(minimal_spec)
    assert len(str(exc.value).splitlines()) == 3


def test_cross_contract_payload_rejected(minimal_spec, minimal_tcs):
    with pytest.raises(ContractError):
        validate_test_cases(minimal_spec)
    with pytest.raises(ContractError):
        validate_normalized_spec(minimal_tcs)


def test_new_validators_return_none_on_success(minimal_step, minimal_sr):
    assert validate_step(minimal_step) is None
    assert validate_synthesis_result(minimal_sr) is None


def test_error_message_shape_for_step(minimal_step):
    minimal_step["kind"] = "click"
    with pytest.raises(ValueError) as exc:
        validate_step(minimal_step)
    lines = str(exc.value).splitlines()
    assert lines[0] == "invalid Step:"
    assert any(line.startswith("  at /kind:") for line in lines[1:])


def test_error_message_shape_for_synthesis_result(minimal_sr):
    del minimal_sr["manifest"]
    with pytest.raises(ContractError) as exc:
        validate_synthesis_result(minimal_sr)
    lines = str(exc.value).splitlines()
    assert lines[0] == "invalid Synthesis Result:"
    assert all(line.startswith("  at /") for line in lines[1:])


def test_synthesis_result_rejects_cross_contract_payloads(minimal_spec, minimal_tcs, minimal_step, minimal_sr):
    for other in (minimal_spec, minimal_tcs, minimal_step):
        with pytest.raises(ContractError):
            validate_synthesis_result(other)
    with pytest.raises(ContractError):
        validate_step(minimal_sr)


def test_language_is_required_on_step_and_reused_ref(minimal_step, minimal_sr):
    del minimal_step["language"]
    with pytest.raises(ContractError) as exc:
        validate_step(minimal_step)
    assert "'language' is a required property" in str(exc.value)
    minimal_sr["manifest"]["reused"] = [{
        "step_id": "s1", "kind": "action", "name": "go",
        "page_object": "P", "intent": "go", "score": 0.5,
    }]
    with pytest.raises(ContractError) as exc:
        validate_synthesis_result(minimal_sr)
    assert "at /manifest/reused/0:" in str(exc.value)
