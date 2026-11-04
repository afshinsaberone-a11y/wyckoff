"""CLI for validating a complete BOOT-002 A/B/C/D evidence bundle."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence

from boot002_bundle_validator import RunBundleRejected, validate_boot002_bundle


def _read_manifest(path: str) -> dict:
    file_path = Path(path)
    try:
        with file_path.open("r", encoding="utf-8-sig") as handle:
            value = json.load(handle)
    except FileNotFoundError as exc:
        raise RunBundleRejected(f"Manifest file not found: {file_path}") from exc
    except json.JSONDecodeError as exc:
        raise RunBundleRejected(
            f"Invalid JSON in {file_path} at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    if not isinstance(value, dict):
        raise RunBundleRejected(f"Manifest root must be a JSON object: {file_path}")
    return value


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the evidence package for MT5 BOOT-002 runs A/B/C/D."
    )
    parser.add_argument("--run-a", required=True, help="JSON manifest for H1STRUCT v1.083 / Lookback 5.")
    parser.add_argument("--run-b", required=True, help="JSON manifest for MultiAudit v1.084 / Lookback 5.")
    parser.add_argument("--run-c", required=True, help="JSON manifest for MultiAudit v1.084 / Lookback 10.")
    parser.add_argument("--run-d", required=True, help="JSON manifest for MultiAudit v1.084 / Lookback 20.")
    parser.add_argument("--output-json", help="Optional path for a machine-readable validation result.")
    args = parser.parse_args(argv)

    paths = [args.run_a, args.run_b, args.run_c, args.run_d]
    try:
        manifests = [_read_manifest(path) for path in paths]
        validate_boot002_bundle(manifests)
        result = {
            "status": "VALID",
            "task_id": "BOOT-002",
            "run_ids": [item["run_id"] for item in manifests],
            "roles": [item["run_role"] for item in manifests],
            "message": "All four manifests passed identity, common-settings and artifact-evidence checks.",
        }
        exit_code = 0
    except (RunBundleRejected, OSError) as exc:
        result = {
            "status": "REJECTED",
            "task_id": "BOOT-002",
            "error": str(exc),
        }
        exit_code = 2

    encoded = json.dumps(result, ensure_ascii=False, indent=2)
    print(encoded)
    if args.output_json:
        try:
            Path(args.output_json).write_text(encoded + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"Could not write result JSON: {exc}", file=sys.stderr)
            return 3
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
