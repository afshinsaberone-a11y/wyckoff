"""Fail-closed acceptance checks for the four BOOT-002 MT5 run manifests.

This validates recorded evidence only. It never compiles MQL5 or runs Strategy Tester.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
import re
from typing import Any


_VARIANTS = {
    "H1STRUCT_1083_CONTROL_LB5": {
        "role": "A",
        "lookback": 5,
        "expert": "Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_AUDIT",
        "property_version": "1.083",
        "ea_version": "1.08-C2-H1STRUCT-AUDIT-SB050-T030",
        "source_path": "src/Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_AUDIT.mq5",
        "set_path": "sets/Wyckoff_C2_H1StructureAudit_2024_2026.set",
    },
    "MULTIAUDIT_1084_CONTROL_LB5": {
        "role": "B",
        "lookback": 5,
        "expert": "Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT",
        "property_version": "1.084",
        "ea_version": "1.08-C2-H1STRUCT-ML-AUDIT-SB050-T030",
        "source_path": "src/Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT.mq5",
        "set_path": "sets/Wyckoff_C2_H1StructureMultiAudit_2024_2026.set",
    },
    "MULTIAUDIT_1084_SENSITIVITY_LB10": {
        "role": "C",
        "lookback": 10,
        "expert": "Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT",
        "property_version": "1.084",
        "ea_version": "1.08-C2-H1STRUCT-ML-AUDIT-SB050-T030",
        "source_path": "src/Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT.mq5",
        "set_path": "sets/Wyckoff_C2_H1STRUCT_SL10_2024_2026.set",
    },
    "MULTIAUDIT_1084_SENSITIVITY_LB20": {
        "role": "D",
        "lookback": 20,
        "expert": "Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT",
        "property_version": "1.084",
        "ea_version": "1.08-C2-H1STRUCT-ML-AUDIT-SB050-T030",
        "source_path": "src/Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT.mq5",
        "set_path": "sets/Wyckoff_C2_H1STRUCT_SL20_2024_2026.set",
    },
}

_HEX_64 = re.compile(r"^[0-9a-fA-F]{64}$")
_REQUIRED_CHECKS = (
    "compile_no_errors",
    "tester_completed",
    "expected_ea_version_seen",
    "expected_expert_seen",
    "expected_lookback_seen",
    "only_permitted_set_fields_differ",
    "common_window_same_as_other_runs",
    "html_journal_csv_present",
    "history_warnings_recorded",
    "csv_not_overwritten",
)
_SHARED_TESTER_FIELDS = (
    "broker_server",
    "symbol",
    "period",
    "model",
    "initial_deposit",
    "deposit_currency",
    "leverage",
    "optimization",
    "forward_testing",
    "spread_setting",
    "commission_assumption",
    "swap_assumption",
    "slippage_assumption",
)


class RunBundleRejected(ValueError):
    """Raised when a BOOT-002 run bundle cannot be accepted as complete."""


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RunBundleRejected(f"{name} must be an object/mapping.")
    return value


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RunBundleRejected(f"{name} must be a non-empty string.")
    return value


def _sha256(value: Any, name: str) -> str:
    text = _text(value, name)
    if not _HEX_64.fullmatch(text):
        raise RunBundleRejected(f"{name} must be a 64-character SHA-256 hex digest.")
    return text.lower()


def _strict_int(value: Any, name: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise RunBundleRejected(f"{name} must be an integer >= {minimum}.")
    return value


def _require_true(checks: Mapping[str, Any], key: str) -> None:
    if checks.get(key) is not True:
        raise RunBundleRejected(f"checks.{key} must be true.")


def validate_run_manifest(manifest: Mapping[str, Any]) -> None:
    """Validate one run against its exact A/B/C/D identity and evidence fields."""
    manifest = _mapping(manifest, "manifest")
    variant = _text(manifest.get("variant"), "variant")
    expected = _VARIANTS.get(variant)
    if expected is None:
        raise RunBundleRejected(f"Unsupported BOOT-002 variant: {variant}")

    if manifest.get("task_id") != "BOOT-002":
        raise RunBundleRejected("task_id must be BOOT-002.")
    if manifest.get("status") != "COMPLETE":
        raise RunBundleRejected("status must be COMPLETE.")
    if manifest.get("run_role") != expected["role"]:
        raise RunBundleRejected("run_role does not match variant.")
    _text(manifest.get("run_id"), "run_id")
    if manifest.get("lookback_active") != expected["lookback"]:
        raise RunBundleRejected("lookback_active does not match variant.")

    source = _mapping(manifest.get("source"), "source")
    for key in ("source_path", "tester_expert_name_expected", "source_property_version_expected", "source_ea_version_expected", "metaeditor_build", "compile_result", "compile_log_path", "ex5_path"):
        _text(source.get(key), f"source.{key}")
    if source["source_path"] != expected["source_path"]:
        raise RunBundleRejected("source_path does not match variant.")
    if source["tester_expert_name_expected"] != expected["expert"]:
        raise RunBundleRejected("tester_expert_name_expected does not match variant.")
    if source["source_property_version_expected"] != expected["property_version"]:
        raise RunBundleRejected("source_property_version_expected does not match variant.")
    if source["source_ea_version_expected"] != expected["ea_version"]:
        raise RunBundleRejected("source_ea_version_expected does not match variant.")
    if source["compile_result"].upper() not in {"SUCCESS", "0_ERRORS"}:
        raise RunBundleRejected("compile_result must indicate a successful compile.")
    _sha256(source.get("source_git_blob_sha"), "source.source_git_blob_sha")
    _sha256(source.get("ex5_sha256"), "source.ex5_sha256")

    settings = _mapping(manifest.get("set"), "set")
    _text(settings.get("path"), "set.path")
    if settings["path"] != expected["set_path"]:
        raise RunBundleRejected("set.path does not match variant.")
    _sha256(settings.get("git_blob_sha"), "set.git_blob_sha")
    if settings.get("expected_strength_swing_lookback") != expected["lookback"]:
        raise RunBundleRejected("SET Lookback does not match variant.")
    _text(settings.get("csv_input_name"), "set.csv_input_name")
    if settings.get("all_other_inputs_match_expected") is not True:
        raise RunBundleRejected("all_other_inputs_match_expected must be true.")

    tester = _mapping(manifest.get("tester"), "tester")
    for key in ("broker_server", "symbol", "period", "model", "start_server_time", "end_server_time", "spread_setting", "commission_assumption", "swap_assumption", "slippage_assumption"):
        _text(tester.get(key), f"tester.{key}")
    if tester["broker_server"] != "WMMarkets-Demo" or tester["symbol"] != "XAUUSD" or tester["period"] != "M5":
        raise RunBundleRejected("Tester broker/symbol/period does not match BOOT-002.")
    if tester["model"] != "Every tick based on real ticks":
        raise RunBundleRejected("Tester model must be Every tick based on real ticks.")
    _strict_int(tester.get("initial_deposit"), "tester.initial_deposit", 1)
    if tester["deposit_currency"] != "USD" or tester["leverage"] != "1:200":
        raise RunBundleRejected("Tester deposit currency/leverage mismatch.")
    if tester.get("optimization") is not False or tester.get("forward_testing") is not False:
        raise RunBundleRejected("Optimization and forward testing must both be false.")
    if tester.get("common_window_frozen_before_run_A") is not True:
        raise RunBundleRejected("Common test window must be frozen before Run A.")

    identity = _mapping(manifest.get("identity_checks"), "identity_checks")
    if identity.get("tester_expert_name") != expected["expert"]:
        raise RunBundleRejected("identity_checks.tester_expert_name mismatch.")
    if identity.get("csv_ea_version") != expected["ea_version"]:
        raise RunBundleRejected("identity_checks.csv_ea_version mismatch.")
    if identity.get("journal_lookback_value") != expected["lookback"]:
        raise RunBundleRejected("identity_checks.journal_lookback_value mismatch.")
    for key in ("common_window_matches_all_runs", "journal_model_matches", "journal_deposit_leverage_match", "source_ex5_pair_matches_build_manifest", "run_valid"):
        if identity.get(key) is not True:
            raise RunBundleRejected(f"identity_checks.{key} must be true.")
    if identity.get("invalidation_reason") not in (None, ""):
        raise RunBundleRejected("A valid Run cannot carry invalidation_reason.")

    outputs = _mapping(manifest.get("outputs"), "outputs")
    for key in ("tester_html_path", "journal_path", "event_csv_path"):
        _text(outputs.get(key), f"outputs.{key}")
    for key in ("tester_html_sha256", "journal_sha256", "event_csv_sha256"):
        _sha256(outputs.get(key), f"outputs.{key}")
    _strict_int(outputs.get("event_csv_rows"), "outputs.event_csv_rows", 1)
    _strict_int(outputs.get("trade_count"), "outputs.trade_count", 0)
    _mapping(outputs.get("diagnostic_event_counts"), "outputs.diagnostic_event_counts")
    _mapping(outputs.get("confirmed_structural_event_counts"), "outputs.confirmed_structural_event_counts")
    _mapping(outputs.get("trading_event_counts"), "outputs.trading_event_counts")

    checks = _mapping(manifest.get("checks"), "checks")
    for key in _REQUIRED_CHECKS:
        _require_true(checks, key)

    if manifest.get("auditor_verdict") not in {"PASS", "CONDITIONAL"}:
        raise RunBundleRejected("auditor_verdict must be PASS or CONDITIONAL.")


def validate_boot002_bundle(manifests: Sequence[Mapping[str, Any]]) -> None:
    """Validate exactly one valid A/B/C/D manifest with matched execution settings."""
    if not isinstance(manifests, Sequence) or isinstance(manifests, (str, bytes)) or len(manifests) != 4:
        raise RunBundleRejected("Exactly four BOOT-002 run manifests (A/B/C/D) are required.")

    by_role: dict[str, Mapping[str, Any]] = {}
    run_ids: set[str] = set()
    for manifest in manifests:
        validate_run_manifest(manifest)
        role = manifest["run_role"]
        if role in by_role:
            raise RunBundleRejected(f"Duplicate run role: {role}")
        by_role[role] = manifest
        run_id = manifest["run_id"]
        if run_id in run_ids:
            raise RunBundleRejected(f"Duplicate run_id: {run_id}")
        run_ids.add(run_id)

    if set(by_role) != {"A", "B", "C", "D"}:
        raise RunBundleRejected("Bundle must contain roles A, B, C and D exactly once.")

    roles = [by_role[x] for x in ("A", "B", "C", "D")]
    tester0 = roles[0]["tester"]
    shared_tester = tuple(tester0.get(key) for key in _SHARED_TESTER_FIELDS)
    common_window = (tester0["start_server_time"], tester0["end_server_time"])
    metaeditor_build = roles[0]["source"]["metaeditor_build"]

    for item in roles[1:]:
        tester = item["tester"]
        if tuple(tester.get(key) for key in _SHARED_TESTER_FIELDS) != shared_tester:
            raise RunBundleRejected("Tester execution settings differ across A/B/C/D.")
        if (tester["start_server_time"], tester["end_server_time"]) != common_window:
            raise RunBundleRejected("Start/end window differs across A/B/C/D.")
        if item["source"]["metaeditor_build"] != metaeditor_build:
            raise RunBundleRejected("MetaEditor build differs across the four runs.")

    # A and B are distinct Experts compiled by the same MetaEditor build.
    if roles[0]["source"]["ex5_sha256"] == roles[1]["source"]["ex5_sha256"]:
        raise RunBundleRejected("Run A and B must reference their separate EX5 binaries.")

    # B/C/D must use one and the same MultiAudit source and compiled EX5.
    b_source = roles[1]["source"]
    for item in roles[2:]:
        source = item["source"]
        if source["source_git_blob_sha"] != b_source["source_git_blob_sha"]:
            raise RunBundleRejected("Runs B/C/D must use the same MultiAudit source blob.")
        if source["ex5_sha256"] != b_source["ex5_sha256"]:
            raise RunBundleRejected("Runs B/C/D must use the same compiled MultiAudit EX5.")
