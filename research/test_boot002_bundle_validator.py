from __future__ import annotations

import copy
import unittest

from boot002_bundle_validator import RunBundleRejected, validate_boot002_bundle


def manifest(variant, run_id):
    common = {
        "schema_version": "2.0-draft",
        "task_id": "BOOT-002",
        "experiment_id": "W0-H1STRUCT-MULTIAUDIT-FOUR-RUN",
        "run_id": run_id,
        "status": "COMPLETE",
        "variant": variant,
        "matched_control_group": "BOOT-002-A-B",
        "lookback_active": None,
        "source": {
            "repository": "afshinsaberone-a11y/wyckoff",
            "source_path": None,
            "source_git_blob_sha": "a" * 40,
            "tester_expert_name_expected": None,
            "source_property_version_expected": None,
            "source_ea_version_expected": None,
            "metaeditor_build": "MetaEditor 5 build 6230",
            "compile_result": "SUCCESS",
            "compile_log_path": "compile.log",
            "ex5_path": "expert.ex5",
            "ex5_sha256": ("1" if variant.startswith("H1STRUCT") else "2") * 64,
        },
        "set": {
            "path": None,
            "git_blob_sha": "b" * 40,
            "expected_strength_swing_lookback": None,
            "csv_input_name": "events.csv",
            "all_other_inputs_match_expected": True,
        },
        "tester": {
            "broker_server": "WMMarkets-Demo",
            "symbol": "XAUUSD",
            "period": "M5",
            "model": "Every tick based on real ticks",
            "start_server_time": "2024.01.02 00:00",
            "end_server_time": "2026.10.16 23:55",
            "common_window_frozen_before_run_A": True,
            "initial_deposit": 10000,
            "deposit_currency": "USD",
            "leverage": "1:200",
            "optimization": False,
            "forward_testing": False,
            "spread_setting": "Current",
            "commission_assumption": "Broker",
            "swap_assumption": "Broker",
            "slippage_assumption": "20 points",
            "history_coverage_notes": "Recorded in journal.",
        },
        "identity_checks": {
            "tester_expert_name": None,
            "csv_ea_version": None,
            "journal_lookback_value": None,
            "common_window_matches_all_runs": True,
            "journal_model_matches": True,
            "journal_deposit_leverage_match": True,
            "source_ex5_pair_matches_build_manifest": True,
            "run_valid": True,
            "invalidation_reason": None,
        },
        "outputs": {
            "tester_html_path": "tester.html",
            "tester_html_sha256": "c" * 64,
            "journal_path": "journal.log",
            "journal_sha256": "d" * 64,
            "event_csv_path": "events.csv",
            "event_csv_sha256": "e" * 64,
            "event_csv_rows": 100,
            "diagnostic_event_counts": {},
            "confirmed_structural_event_counts": {},
            "trading_event_counts": {},
            "trade_count": 1,
            "final_balance": 9990.0,
            "net_profit": -10.0,
        },
        "checks": {k: True for k in (
            "compile_no_errors", "tester_completed", "expected_ea_version_seen",
            "expected_expert_seen", "expected_lookback_seen",
            "only_permitted_set_fields_differ", "common_window_same_as_other_runs",
            "html_journal_csv_present", "history_warnings_recorded", "csv_not_overwritten"
        )},
        "limitations": [],
        "auditor_verdict": "CONDITIONAL",
    }
    expected = {
        "H1STRUCT_1083_CONTROL_LB5": ("A", 5, "Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_AUDIT", "1.083", "1.08-C2-H1STRUCT-AUDIT-SB050-T030", "src/Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_AUDIT.mq5", "sets/Wyckoff_C2_H1StructureAudit_2024_2026.set"),
        "MULTIAUDIT_1084_CONTROL_LB5": ("B", 5, "Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT", "1.084", "1.08-C2-H1STRUCT-ML-AUDIT-SB050-T030", "src/Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT.mq5", "sets/Wyckoff_C2_H1StructureMultiAudit_2024_2026.set"),
        "MULTIAUDIT_1084_SENSITIVITY_LB10": ("C", 10, "Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT", "1.084", "1.08-C2-H1STRUCT-ML-AUDIT-SB050-T030", "src/Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT.mq5", "sets/Wyckoff_C2_H1STRUCT_SL10_2024_2026.set"),
        "MULTIAUDIT_1084_SENSITIVITY_LB20": ("D", 20, "Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT", "1.084", "1.08-C2-H1STRUCT-ML-AUDIT-SB050-T030", "src/Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT.mq5", "sets/Wyckoff_C2_H1STRUCT_SL20_2024_2026.set"),
    }[variant]
    role, lb, expert, prop, ea, source_path, set_path = expected
    common["run_role"] = role
    common["lookback_active"] = lb
    common["source"].update({
        "source_path": source_path,
        "tester_expert_name_expected": expert,
        "source_property_version_expected": prop,
        "source_ea_version_expected": ea,
        "source_git_blob_sha": ("a" if role == "A" else "f") * 40,
    })
    common["set"].update({"path": set_path, "expected_strength_swing_lookback": lb})
    common["identity_checks"].update({
        "tester_expert_name": expert,
        "csv_ea_version": ea,
        "journal_lookback_value": lb,
    })
    return common


def bundle():
    variants = [
        "H1STRUCT_1083_CONTROL_LB5",
        "MULTIAUDIT_1084_CONTROL_LB5",
        "MULTIAUDIT_1084_SENSITIVITY_LB10",
        "MULTIAUDIT_1084_SENSITIVITY_LB20",
    ]
    result = [manifest(v, f"RUN-{i}") for i, v in enumerate(variants, 1)]
    # B/C/D share the same MultiAudit EX5.
    for item in result[2:]:
        item["source"]["ex5_sha256"] = result[1]["source"]["ex5_sha256"]
    return result


class Boot002BundleValidatorTests(unittest.TestCase):
    def test_accepts_complete_matched_abcd_bundle(self):
        validate_boot002_bundle(bundle())

    def test_rejects_missing_run(self):
        with self.assertRaises(RunBundleRejected):
            validate_boot002_bundle(bundle()[:3])

    def test_rejects_duplicate_role(self):
        runs = bundle()
        runs[3] = copy.deepcopy(runs[2])
        runs[3]["run_id"] = "RUN-D"
        with self.assertRaises(RunBundleRejected):
            validate_boot002_bundle(runs)

    def test_rejects_wrong_expert_identity(self):
        runs = bundle()
        runs[0]["identity_checks"]["tester_expert_name"] = "WrongExpert"
        with self.assertRaises(RunBundleRejected):
            validate_boot002_bundle(runs)

    def test_rejects_wrong_ea_version(self):
        runs = bundle()
        runs[2]["identity_checks"]["csv_ea_version"] = "1.08-C2"
        with self.assertRaises(RunBundleRejected):
            validate_boot002_bundle(runs)

    def test_rejects_wrong_lookback(self):
        runs = bundle()
        runs[3]["set"]["expected_strength_swing_lookback"] = 10
        with self.assertRaises(RunBundleRejected):
            validate_boot002_bundle(runs)

    def test_rejects_missing_output_hash(self):
        runs = bundle()
        runs[1]["outputs"]["event_csv_sha256"] = None
        with self.assertRaises(RunBundleRejected):
            validate_boot002_bundle(runs)

    def test_rejects_missing_compile_success(self):
        runs = bundle()
        runs[0]["source"]["compile_result"] = "FAILED"
        with self.assertRaises(RunBundleRejected):
            validate_boot002_bundle(runs)

    def test_rejects_different_common_window(self):
        runs = bundle()
        runs[3]["tester"]["end_server_time"] = "2026.10.17 00:00"
        with self.assertRaises(RunBundleRejected):
            validate_boot002_bundle(runs)

    def test_rejects_execution_cost_mismatch(self):
        runs = bundle()
        runs[2]["tester"]["commission_assumption"] = "Zero"
        with self.assertRaises(RunBundleRejected):
            validate_boot002_bundle(runs)

    def test_rejects_different_metaeditor_build(self):
        runs = bundle()
        runs[3]["source"]["metaeditor_build"] = "MetaEditor 5 build 6300"
        with self.assertRaises(RunBundleRejected):
            validate_boot002_bundle(runs)

    def test_rejects_different_multiaudit_binary_for_c_d(self):
        runs = bundle()
        runs[3]["source"]["ex5_sha256"] = "3" * 64
        with self.assertRaises(RunBundleRejected):
            validate_boot002_bundle(runs)

    def test_rejects_same_binary_for_a_and_b(self):
        runs = bundle()
        runs[0]["source"]["ex5_sha256"] = runs[1]["source"]["ex5_sha256"]
        with self.assertRaises(RunBundleRejected):
            validate_boot002_bundle(runs)

    def test_rejects_unfrozen_common_window(self):
        runs = bundle()
        runs[0]["tester"]["common_window_frozen_before_run_A"] = False
        with self.assertRaises(RunBundleRejected):
            validate_boot002_bundle(runs)

    def test_rejects_false_acceptance_check(self):
        runs = bundle()
        runs[2]["checks"]["csv_not_overwritten"] = False
        with self.assertRaises(RunBundleRejected):
            validate_boot002_bundle(runs)

    def test_rejects_invalid_run_even_if_artifacts_exist(self):
        runs = bundle()
        runs[1]["identity_checks"]["run_valid"] = False
        runs[1]["identity_checks"]["invalidation_reason"] = "EA_VERSION mismatch"
        with self.assertRaises(RunBundleRejected):
            validate_boot002_bundle(runs)


if __name__ == "__main__":
    unittest.main()
