#!/usr/bin/env python3
"""Static preflight checks for Financial ML Core+ / Wyckoff MultiAudit.

This script does not compile MQL5 or execute MT5 Strategy Tester.
It validates repository contracts and the diagnostic-only source delta.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
PASSES: list[str] = []


def read_text(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        ERRORS.append(f"Missing required file: {relative}")
        return ""
    return path.read_text(encoding="utf-8-sig")


def check(condition: bool, ok: str, error: str) -> None:
    if condition:
        PASSES.append(ok)
    else:
        ERRORS.append(error)


def parse_set(relative: str) -> dict[str, str]:
    text = read_text(relative)
    values: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(";") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def parse_mql_inputs(source: str) -> set[str]:
    pattern = re.compile(r"^\s*(?:input|sinput)\s+\S+\s+([A-Za-z_]\w*)\s*=", re.MULTILINE)
    return set(pattern.findall(source))


def is_known_metadata_line(line: str) -> bool:
    stripped = line.strip()
    if stripped.startswith("//|") and "C2_H1STRUCT_AUDIT.mq5" in stripped:
        return True
    if stripped.startswith("#property version") and '"1.083"' in stripped:
        return True
    if stripped.startswith("#property description") and "C2 H1 structure audit" in stripped:
        return True
    if stripped.startswith("#define EA_VERSION") and "1.08-C2-H1STRUCT-AUDIT-SB050-T030" in stripped:
        return True
    return False


def baseline_is_preserved(base: str, multi: str) -> tuple[bool, list[str]]:
    """Every non-metadata line of v1.083 must remain in order in v1.084."""
    expected = [line for line in base.splitlines() if not is_known_metadata_line(line)]
    actual = multi.splitlines()
    cursor = 0
    missing: list[str] = []
    for line in expected:
        while cursor < len(actual) and actual[cursor] != line:
            cursor += 1
        if cursor >= len(actual):
            missing.append(line)
            if len(missing) >= 8:
                break
        else:
            cursor += 1
    return not missing, missing


def main() -> int:
    base_path = "src/Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_AUDIT.mq5"
    multi_path = "src/Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT.mq5"
    base = read_text(base_path)
    multi = read_text(multi_path)

    check(bool(base and multi), "Both H1STRUCT source files are present.", "Could not read both source files.")
    if not base or not multi:
        return 1

    version = re.search(r'^\s*#property\s+version\s+"([^"]+)"', multi, re.MULTILINE)
    ea_version = re.search(r'^\s*#define\s+EA_VERSION\s+"([^"]+)"', multi, re.MULTILINE)
    check(bool(version and version.group(1) == "1.084"),
          "MultiAudit property version is 1.084.",
          "MultiAudit #property version is not 1.084.")
    check(bool(ea_version and ea_version.group(1) == "1.08-C2-H1STRUCT-ML-AUDIT-SB050-T030"),
          "MultiAudit EA_VERSION matches the registered identifier.",
          "MultiAudit EA_VERSION does not match the registered identifier.")

    preserved, missing = baseline_is_preserved(base, multi)
    check(preserved,
          "All non-metadata v1.083 source lines are preserved in order.",
          "One or more baseline source lines are missing/changed: " + repr(missing))

    function_start = multi.find("void LogStrengthStructureAudit(")
    function_end = multi.find("//------------------------------ SOS / SOW", function_start)
    diagnostic_function = multi[function_start:function_end] if function_start >= 0 and function_end > function_start else ""
    check(bool(diagnostic_function),
          "Diagnostic-only LogStrengthStructureAudit function is present.",
          "Could not locate complete LogStrengthStructureAudit function.")
    if diagnostic_function:
        forbidden = ("PlaceTrade(", "OrderSend(", "trade.Buy(", "trade.Sell(", "PositionOpen(")
        found = [token for token in forbidden if token in diagnostic_function]
        check(not found,
              "Diagnostic function contains no order/position execution calls.",
              "Order/position execution token found inside diagnostic function: " + ", ".join(found))

    check('SOS_STRENGTH_BAR_AUDIT' in diagnostic_function and
          'SOW_STRENGTH_BAR_AUDIT' in diagnostic_function,
          "Both SOS/SOW diagnostic event labels are present.",
          "One or both SOS/SOW diagnostic event labels are missing.")
    check(multi.count("LogStrengthStructureAudit(true,") == 1 and
          multi.count("LogStrengthStructureAudit(false,") == 1,
          "Diagnostic function is called once for each directional Strength branch.",
          "Unexpected number of diagnostic calls for Buy/Sell Strength.")

    multi_inputs = parse_mql_inputs(multi)
    set_paths = [
        "sets/Wyckoff_C2_H1StructureMultiAudit_2024_2026.set",
        "sets/Wyckoff_C2_H1STRUCT_SL10_2024_2026.set",
        "sets/Wyckoff_C2_H1STRUCT_SL20_2024_2026.set",
    ]
    sets = [parse_set(path) for path in set_paths]
    check(all(bool(item) for item in sets), "All three MultiAudit SET files are present.", "One or more MultiAudit SET files are missing.")
    if all(sets):
        key_sets = [set(item) for item in sets]
        check(all(keys == key_sets[0] for keys in key_sets[1:]),
              "All three SET files contain the same keys.",
              "SET key sets differ across lookback variants.")
        check(set(sets[0]) == multi_inputs,
              f"MultiAudit inputs and SET keys match ({len(multi_inputs)} inputs).",
              f"Input/SET mismatch: inputs={len(multi_inputs)}, set_keys={len(sets[0])}, missing={sorted(multi_inputs-set(sets[0]))}, extra={sorted(set(sets[0])-multi_inputs)}")

        lookbacks = [item.get("InpStrengthSwingLookback") for item in sets]
        check(lookbacks == ["5", "10", "20"],
              "SET lookbacks are exactly 5, 10, and 20 in the expected order.",
              f"Unexpected lookback sequence: {lookbacks}")

        reference = sets[0]
        allowed = {"InpStrengthSwingLookback", "InpCSVFileName"}
        diffs: set[str] = set()
        for item in sets[1:]:
            diffs.update(key for key in reference if reference.get(key) != item.get(key))
        check(diffs == allowed,
              "Only Lookback and CSV output filename differ among SET files.",
              f"Unexpected SET differences: {sorted(diffs)}")
        csv_names = [item.get("InpCSVFileName") for item in sets]
        check(len(set(csv_names)) == 3 and all(csv_names),
              "Each SET has a distinct non-empty CSV input filename.",
              f"CSV input filenames are not unique: {csv_names}")

    # Reconstructed C2 baseline: every SET value must equal the archived Tester Journal.
    c2_source = read_text("src/Wyckoff_XAUUSD_W0_v1_08_C2_T030_SB050.mq5")
    c2_source_inputs = parse_mql_inputs(c2_source)
    c2_ea_version = re.search(r'^\\s*#define\\s+EA_VERSION\\s+"([^"]+)"', c2_source, re.MULTILINE)
    check(bool(c2_ea_version and c2_ea_version.group(1) == "1.08-C2-TIMING-SB050-T030"),
          "C2 baseline source EA_VERSION is the registered 1.08 timing build.",
          "C2 baseline source EA_VERSION mismatch.")

    c2_set = parse_set("sets/Wyckoff_C2_T030_SB050_RECONSTRUCTED_FROM_20261103_JOURNAL.set")
    c2_journal = read_text("events/20261103.log")
    journal_lines = c2_journal.splitlines()
    c2_start = next((i for i, line in enumerate(journal_lines)
                     if r"testing of Experts\Wyckoff_XAUUSD_W0_v1_08_C2_T030_SB050.ex5" in line), -1)
    c2_end = next((i for i, line in enumerate(journal_lines)
                   if i > c2_start and "XAUUSD,H1: history cache allocated" in line), -1)
    c2_journal_inputs: dict[str, str] = {}
    if c2_start >= 0:
        section = journal_lines[c2_start:c2_end if c2_end > c2_start else c2_start + 180]
        for line in section:
            match = re.search(r"Tester\s+(Inp[A-Za-z0-9_]+)=(.*)$", line)
            if match:
                c2_journal_inputs[match.group(1)] = match.group(2)

    check(bool(c2_set and c2_journal_inputs),
          "Reconstructed C2 SET and archived Tester Journal are present.",
          "Could not read reconstructed C2 SET or archived Tester Journal inputs.")
    if c2_set and c2_journal_inputs:
        check(set(c2_set) == c2_source_inputs == set(c2_journal_inputs),
              "C2 source, reconstructed SET, and Journal have identical 67 input keys.",
              f"C2 input-key mismatch: source={len(c2_source_inputs)}, set={len(c2_set)}, journal={len(c2_journal_inputs)}")
        value_diffs = {key: (c2_set.get(key), c2_journal_inputs.get(key))
                       for key in set(c2_set) | set(c2_journal_inputs)
                       if c2_set.get(key) != c2_journal_inputs.get(key)}
        check(not value_diffs,
              "All reconstructed C2 SET values exactly match the archived Journal.",
              "C2 reconstructed SET value mismatch: " + repr(value_diffs))

    h1struct_set = parse_set("sets/Wyckoff_C2_H1StructureAudit_2024_2026.set")
    if h1struct_set and sets:
        h1_multi_diffs = {key for key in h1struct_set
                          if h1struct_set.get(key) != sets[0].get(key)}
        check(set(h1struct_set) == set(sets[0]) and h1_multi_diffs == {"InpCSVFileName"},
              "H1STRUCT v1.083 SET and MultiAudit lookback-5 SET match except CSV filename.",
              f"H1STRUCT/MultiAudit lookback-5 SET differences: {sorted(h1_multi_diffs)}")
        check(h1struct_set.get("InpStrengthSwingLookback") == "5" and
              sets[0].get("InpStrengthSwingLookback") == "5",
              "H1STRUCT and MultiAudit control SETs both use Strength Lookback 5.",
              "H1STRUCT/MultiAudit control Lookback is not 5.")

    process_start = multi.find("void ProcessWaitStrength(")
    process_end = multi.find("//------------------------------ LPS / LPSY", process_start)
    process_strength = multi[process_start:process_end] if process_start >= 0 and process_end > process_start else ""
    active_lookback = ("for(int i=1;i<=lookback;i++) priorHigh=" in process_strength and
                       "for(int i=1;i<=lookback;i++) priorLow=" in process_strength)
    check(active_lookback,
          "InpStrengthSwingLookback controls the active SOS/SOW prior-swing break levels.",
          "Could not verify active SOS/SOW use of Strength Lookback.")

    manifest_path = "experiments/BOOT_002_RUN_MANIFEST_TEMPLATE.json"
    manifest_text = read_text(manifest_path)
    try:
        manifest = json.loads(manifest_text)
        json_ok = True
    except json.JSONDecodeError as exc:
        manifest = {}
        json_ok = False
        ERRORS.append(f"Run manifest template is invalid JSON: {exc}")
    if json_ok:
        check(manifest.get("task_id") == "BOOT-002" and manifest.get("status") == "PLANNED",
              "BOOT-002 manifest is a valid unexecuted template.",
              "Manifest task_id/status is unexpected.")
        check(manifest.get("identity_checks", {}).get("run_valid") is False,
              "Manifest template does not pre-claim a valid test run.",
              "Manifest template must not mark a run as valid before execution.")

    run_card = read_text("docs/BOOT_002_MULTIAUDIT_RUN_CARD_FA.md")
    check("Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT" in run_card and
          "1.08-C2-H1STRUCT-ML-AUDIT-SB050-T030" in run_card,
          "BOOT-002 run card identifies the correct Expert and EA_VERSION.",
          "BOOT-002 run card does not contain the expected Expert/EA_VERSION.")

    print("Financial ML Core+ static preflight")
    for item in PASSES:
        print(f"PASS: {item}")
    for item in ERRORS:
        print(f"FAIL: {item}")
    print(f"Summary: {len(PASSES)} passed, {len(ERRORS)} failed.")
    print("NOTE: This is repository/static validation only; it does not compile MQL5 or run MT5 Strategy Tester.")
    return 1 if ERRORS else 0


if __name__ == "__main__":
    sys.exit(main())
