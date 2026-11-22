"""Validate a CreditSnapshot 1.0.0 document against the published JSON Schema."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schema" / "credit_snapshot.schema.json"


class SnapshotValidationError(ValueError):
    """Schema failed. Messages include only JSON paths, never document values (no PII)."""


def load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _path(err: Any) -> str:
    parts = [str(p) for p in err.absolute_path]
    return ".".join(parts) if parts else "<root>"


def iter_snapshot_errors(data: dict[str, Any]) -> list[str]:
    """Return safe, value-free error strings for a document."""
    validator = Draft202012Validator(load_schema())
    out: list[str] = []
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        kind = err.validator or "schema"
        out.append(f"{_path(err)}: {kind} constraint failed")
    return out


def validate_snapshot(data: dict[str, Any]) -> None:
    """Raise SnapshotValidationError if the document is not a valid CreditSnapshot 1.0.0."""
    if not isinstance(data, dict):
        raise SnapshotValidationError("<root>: object constraint failed")
    errors = iter_snapshot_errors(data)
    if errors:
        raise SnapshotValidationError("; ".join(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a CreditSnapshot 1.0.0 JSON file (errors omit document values)."
    )
    parser.add_argument("path", help="Path to a snapshot JSON file")
    args = parser.parse_args(argv)
    payload = json.loads(Path(args.path).read_text(encoding="utf-8"))
    try:
        validate_snapshot(payload)
    except SnapshotValidationError as exc:
        print(f"INVALID {args.path}: {exc}", file=sys.stderr)
        return 1
    print(f"VALID {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
