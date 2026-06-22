"""Small JSON Schema subset validator for emitted artifacts.

The project is dependency-free for the seed repo, so tests use this focused
validator for the simple committed schemas instead of pulling in jsonschema.
"""

from __future__ import annotations

from typing import Any, Dict, List


def validate_schema(data: Any, schema: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    _validate_node(data, schema, "$", errors)
    return errors


def _validate_node(data: Any, schema: Dict[str, Any], path: str, errors: List[str]) -> None:
    if "const" in schema and data != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}")
    if "enum" in schema and data not in schema["enum"]:
        errors.append(f"{path}: expected one of {schema['enum']!r}")

    expected_type = schema.get("type")
    if expected_type and not _matches_type(data, expected_type):
        errors.append(f"{path}: expected {expected_type}")
        return

    if expected_type == "object" or isinstance(data, dict):
        _validate_object(data, schema, path, errors)
    elif expected_type == "array" or isinstance(data, list):
        _validate_array(data, schema, path, errors)


def _validate_object(data: Any, schema: Dict[str, Any], path: str, errors: List[str]) -> None:
    if not isinstance(data, dict):
        return
    for key in schema.get("required", []):
        if key not in data:
            errors.append(f"{path}: missing required key {key!r}")
    properties = schema.get("properties", {})
    for key, child_schema in properties.items():
        if key in data:
            _validate_node(data[key], child_schema, f"{path}.{key}", errors)
    if schema.get("additionalProperties") is False:
        allowed = set(properties)
        for key in data:
            if key not in allowed:
                errors.append(f"{path}: unexpected key {key!r}")


def _validate_array(data: Any, schema: Dict[str, Any], path: str, errors: List[str]) -> None:
    if not isinstance(data, list):
        return
    min_items = schema.get("minItems")
    if min_items is not None and len(data) < int(min_items):
        errors.append(f"{path}: expected at least {min_items} items")
    item_schema = schema.get("items")
    if item_schema:
        for index, item in enumerate(data):
            _validate_node(item, item_schema, f"{path}[{index}]", errors)


def _matches_type(data: Any, expected_type: str) -> bool:
    if expected_type == "object":
        return isinstance(data, dict)
    if expected_type == "array":
        return isinstance(data, list)
    if expected_type == "string":
        return isinstance(data, str)
    if expected_type == "number":
        return isinstance(data, (int, float)) and not isinstance(data, bool)
    if expected_type == "integer":
        return isinstance(data, int) and not isinstance(data, bool)
    if expected_type == "boolean":
        return isinstance(data, bool)
    if expected_type == "null":
        return data is None
    return True
