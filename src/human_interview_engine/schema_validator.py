"""Pure-Python JSON Schema validator for HumanInterview Engine artifacts."""

from __future__ import annotations

from typing import Any


class SchemaValidationError(ValueError):
    """Raised when an artifact violates its JSON schema."""


def _matches_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return (isinstance(value, (int, float)) and not isinstance(value, bool))
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def validate_against_schema(data: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Validate `data` against a JSON Schema subset and return human-readable error strings."""
    errors: list[str] = []

    expected_type = schema.get("type")
    if expected_type is not None:
        allowed_types = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(_matches_type(data, t) for t in allowed_types):
            errors.append(f"{path}: expected type {allowed_types}, got {type(data).__name__}")
            return errors

    if "enum" in schema and data not in schema["enum"]:
        errors.append(f"{path}: value {data!r} not in enum {schema['enum']}")

    if isinstance(data, str):
        min_len = schema.get("minLength")
        if min_len is not None and len(data) < min_len:
            errors.append(f"{path}: string length {len(data)} < minLength {min_len}")

    if isinstance(data, (int, float)) and not isinstance(data, bool):
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if minimum is not None and data < minimum:
            errors.append(f"{path}: value {data} < minimum {minimum}")
        if maximum is not None and data > maximum:
            errors.append(f"{path}: value {data} > maximum {maximum}")

    if isinstance(data, dict):
        for req in schema.get("required", []):
            if req not in data:
                errors.append(f"{path}: missing required field '{req}'")
        props = schema.get("properties", {})
        for key, value in data.items():
            if key in props:
                errors.extend(validate_against_schema(value, props[key], f"{path}.{key}"))

    if isinstance(data, list):
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for idx, item in enumerate(data):
                errors.extend(validate_against_schema(item, item_schema, f"{path}[{idx}]"))

    return errors


def assert_valid_schema(data: Any, schema: dict[str, Any], label: str = "artifact") -> None:
    """Validate `data` and raise SchemaValidationError if any check fails."""
    errors = validate_against_schema(data, schema)
    if errors:
        raise SchemaValidationError(f"{label} failed schema validation:\n" + "\n".join(errors))
