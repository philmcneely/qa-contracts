"""
===============================================================================
Model-Free Contract Validation for the QA / Test-Generation Platform
===============================================================================

This module validates the artifacts that cross component boundaries of the QA
platform against their versioned JSON Schemas (draft-07). Producers and
consumers call the same validators, so a component can be swapped without
breaking its neighbors. No LLM and no network are involved.

Features:
    ✓ Contract 1: Normalized Spec validation (validate_normalized_spec)
    ✓ Contract 2: Test Cases validation (validate_test_cases)
    ✓ Contract 4: Synthesis Result validation (validate_synthesis_result)
    ✓ Step validation (validate_step): the Step used by Contracts 3 and 4
    ✓ Schemas ship inside the package (qa_contracts/schemas/*.json)
    ✓ Every violation is reported at once, sorted, with its JSON path
    ✓ Single ContractError type (a ValueError) for all failures
    ✓ Compiled validators are cached per schema

Error Format:
    invalid <label>:
      at /<json/path>: <jsonschema message>

Usage Examples:
    from qa_contracts import validate_normalized_spec, ContractError

    try:
        validate_normalized_spec(spec_dict)
    except ContractError as err:
        print(err)

Dependencies:
    - jsonschema, referencing: Draft7Validator and cross-schema $ref resolution

Author: PMAC
Date: [2026-10-03]
===============================================================================
"""
import json
from functools import lru_cache
from importlib import resources

from jsonschema import Draft7Validator
from referencing import Registry, Resource


class ContractError(ValueError):
    """Raised when a payload does not conform to its contract."""


@lru_cache(maxsize=None)
def _registry():
    """Registry of the packaged schemas by $id, so cross-schema $refs resolve."""
    registry = Registry()
    for entry in (resources.files("qa_contracts") / "schemas").iterdir():
        if entry.name.endswith(".json"):
            schema = json.loads(entry.read_text("utf-8"))
            registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    return registry


@lru_cache(maxsize=None)
def _validator(name):
    text = (resources.files("qa_contracts") / "schemas" / name).read_text("utf-8")
    schema = json.loads(text)
    Draft7Validator.check_schema(schema)
    return Draft7Validator(schema, registry=_registry())


def _validate(obj, name, label):
    errors = sorted(_validator(name).iter_errors(obj), key=lambda e: list(e.absolute_path))
    if errors:
        lines = [
            f"  at /{'/'.join(str(p) for p in e.absolute_path)}: {e.message}" for e in errors
        ]
        raise ContractError(f"invalid {label}:\n" + "\n".join(lines))


def validate_normalized_spec(obj):
    """Raise ContractError unless obj is a valid Normalized Spec (Contract 1)."""
    _validate(obj, "normalized-spec.schema.json", "Normalized Spec")


def validate_test_cases(obj):
    """Raise ContractError unless obj is valid Test Cases (Contract 2)."""
    _validate(obj, "test-cases.schema.json", "Test Cases")


def validate_synthesis_result(obj):
    """Raise ContractError unless obj is a valid Synthesis Result (Contract 4)."""
    _validate(obj, "synthesis-result.schema.json", "Synthesis Result")


def validate_step(obj):
    """Raise ContractError unless obj is a valid Step (step.schema.json)."""
    _validate(obj, "step.schema.json", "Step")
