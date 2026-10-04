"""E2E: login Normalized Spec -> Test Cases flow validates and traces end to end."""
import pytest

from conftest import FIXTURES, load_json
from qa_contracts import (
    validate_normalized_spec,
    validate_step,
    validate_synthesis_result,
    validate_test_cases,
)

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def login():
    spec = load_json(FIXTURES / "valid" / "login.normalized-spec.json")
    tcs = load_json(FIXTURES / "valid" / "login.test-cases.json")
    return spec, tcs


def test_both_contracts_validate(login):
    spec, tcs = login
    validate_normalized_spec(spec)
    validate_test_cases(tcs)


def test_same_ticket(login):
    spec, tcs = login
    assert spec["ticket_id"] == tcs["ticket_id"]


def test_covers_ids_are_known_acs(login):
    spec, tcs = login
    ac_ids = {ac["id"] for ac in spec["acceptance_criteria"]}
    covered = {c for tc in tcs["test_cases"] for c in tc.get("covers", [])}
    assert covered <= ac_ids, f"unknown ACs: {covered - ac_ids}"


def test_every_ac_is_covered(login):
    spec, tcs = login
    ac_ids = {ac["id"] for ac in spec["acceptance_criteria"]}
    covered = {c for tc in tcs["test_cases"] for c in tc.get("covers", [])}
    assert ac_ids <= covered, f"uncovered ACs: {ac_ids - covered}"


@pytest.fixture(scope="module")
def synthesis():
    return load_json(FIXTURES / "valid" / "login.synthesis-result.json")


def test_synthesis_result_validates_and_matches_ticket(login, synthesis):
    _, tcs = login
    validate_synthesis_result(synthesis)
    assert synthesis["ticket_id"] == tcs["ticket_id"]


def test_new_steps_are_valid_steps_for_promote(synthesis):
    """What the Runner forwards to /promote is each manifest.new item, unchanged."""
    for step in synthesis["manifest"]["new"]:
        validate_step(step)


def test_reused_and_new_do_not_overlap(synthesis):
    reused = {(r["page_object"], r["name"]) for r in synthesis["manifest"]["reused"]}
    new = {(s["page_object"], s["name"]) for s in synthesis["manifest"]["new"]}
    assert not reused & new


@pytest.fixture(scope="module")
def ts_synthesis():
    return load_json(FIXTURES / "valid" / "login-ts.synthesis-result.json")


def test_typescript_login_synthesis_result_validates(login, ts_synthesis):
    _, tcs = login
    validate_synthesis_result(ts_synthesis)
    assert ts_synthesis["ticket_id"] == tcs["ticket_id"]
    for step in ts_synthesis["manifest"]["new"]:
        validate_step(step)
        assert step["language"] == "typescript"
    assert all(r["language"] == "typescript" for r in ts_synthesis["manifest"]["reused"])
