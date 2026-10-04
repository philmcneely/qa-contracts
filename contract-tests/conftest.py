"""Shared fixtures and helpers for the model-free contract tests."""
import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def load_json(path):
    return json.loads(Path(path).read_text("utf-8"))


def fixture_files(sub):
    return sorted((FIXTURES / sub).glob("*.json"))


def fixture_kind(path):
    """Fixture kind by name: step -> Step, synthesis-result/sr -> Contract 4, spec -> Contract 1, else Contract 2."""
    name = Path(path).name
    if name.startswith("step.") or ".step." in name:
        return "step"
    if name.startswith("sr.") or ".synthesis-result." in name:
        return "sr"
    return "spec" if "spec" in name else "tc"


@pytest.fixture
def minimal_spec():
    return load_json(FIXTURES / "valid" / "minimal.normalized-spec.json")


@pytest.fixture
def minimal_tcs():
    return load_json(FIXTURES / "valid" / "minimal.test-cases.json")


@pytest.fixture
def minimal_step():
    return load_json(FIXTURES / "valid" / "minimal.step.json")


@pytest.fixture
def login_step():
    return load_json(FIXTURES / "valid" / "login.step.json")


@pytest.fixture
def minimal_sr():
    return load_json(FIXTURES / "valid" / "minimal.synthesis-result.json")


@pytest.fixture
def login_sr():
    return load_json(FIXTURES / "valid" / "login.synthesis-result.json")
