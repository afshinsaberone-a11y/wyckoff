import csv
import tempfile
import unittest
from pathlib import Path

from event_ledger_v2_validator import SCHEMA_COLUMNS, validate_rows


RUN = "WM20261104A001"
RANGE = RUN + ":R1"
CYCLE = RANGE + ":C1"
ATTEMPT = CYCLE + ":A1"
CANDIDATE = ATTEMPT + ":E1"


def make_row(sequence, event, **overrides):
    row = {column: "" for column in SCHEMA_COLUMNS}
    row.update({
        "SchemaVersion": "2",
        "RunID": RUN,
        "EventID": f"{RUN}:EV{sequence}",
        "EventSequence": str(sequence),
        "EventTimeServer": "2026.11.04 10:15:00",
        "ObservedAtServer": "2026.11.04 10:15:00",
        "TimeBasis": "BROKER_SERVER_RAW",
        "SourceTimeframe": "PERIOD_M5",
        "SourceBarOpenServer": "2026.11.04 10:10:00",
        "Symbol": "XAUUSD",
        "EA_Version": "1.083-C2-TIMING-SB050-T030-LEDGER-V2",
        "RangeID": RANGE,
        "LegacySetupID": "1",
        "Direction": "BUY",
        "Event": event,
        "InitialBalance": "1000.00",
    })
    row.update(overrides)
    return row


def valid_candidate_rows():
    return [
        make_row(1, "RANGE_FOUND", SourceTimeframe="PERIOD_H1",
                 SourceBarOpenServer="2026.11.04 10:00:00"),
        make_row(2, "CANDIDATE_CREATED", CycleID=CYCLE, AttemptID=ATTEMPT,
                 CandidateID=CANDIDATE),
        make_row(3, "REJECT_SPREAD_TOO_HIGH", CycleID=CYCLE, AttemptID=ATTEMPT,
                 CandidateID=CANDIDATE, DecisionID=CANDIDATE + ":D1",
                 DecisionStatus="REJECTED", ReasonCode="REJECT_SPREAD_TOO_HIGH"),
        make_row(4, "M5_ENTRY_EVALUATION", CycleID=CYCLE, AttemptID=ATTEMPT,
                 CandidateID=CANDIDATE),
    ]


class EventLedgerV2ValidatorTests(unittest.TestCase):
    def test_valid_candidate_and_rejection_chain(self):
        report = validate_rows(SCHEMA_COLUMNS, valid_candidate_rows(), RUN)
        self.assertTrue(report["valid"], report["errors"])
        self.assertEqual(report["stats"]["unique_candidates"], 1)
        self.assertEqual(report["stats"]["decisions"], 1)

    def test_schema_order_is_strict(self):
        changed = SCHEMA_COLUMNS.copy()
        changed[0], changed[1] = changed[1], changed[0]
        report = validate_rows(changed, valid_candidate_rows())
        self.assertFalse(report["valid"])
        self.assertIn("exact 28-column", report["errors"][0])

    def test_reject_requires_candidate_and_decision(self):
        rows = [make_row(1, "REJECT_SPREAD_TOO_HIGH",
                         DecisionStatus="REJECTED",
                         ReasonCode="REJECT_SPREAD_TOO_HIGH",
                         DecisionID="missing:D1")]
        report = validate_rows(SCHEMA_COLUMNS, rows)
        self.assertFalse(report["valid"])
        self.assertTrue(any("without CandidateID" in error for error in report["errors"]))

    def test_candidate_cannot_precede_created_event(self):
        rows = [make_row(1, "M5_ENTRY_EVALUATION", CycleID=CYCLE,
                         AttemptID=ATTEMPT, CandidateID=CANDIDATE)]
        report = validate_rows(SCHEMA_COLUMNS, rows)
        self.assertFalse(report["valid"])
        self.assertTrue(any("before its CANDIDATE_CREATED" in error for error in report["errors"]))

    def test_candidate_must_have_exactly_one_creation_event(self):
        rows = valid_candidate_rows()
        rows.append(make_row(5, "CANDIDATE_CREATED", CycleID=CYCLE,
                             AttemptID=ATTEMPT, CandidateID=CANDIDATE))
        report = validate_rows(SCHEMA_COLUMNS, rows)
        self.assertFalse(report["valid"])
        self.assertTrue(any("has 2 CANDIDATE_CREATED rows" in error for error in report["errors"]))

    def test_event_sequence_must_be_strictly_increasing(self):
        rows = valid_candidate_rows()
        rows[2]["EventSequence"] = "2"
        rows[2]["EventID"] = f"{RUN}:EV2"
        report = validate_rows(SCHEMA_COLUMNS, rows)
        self.assertFalse(report["valid"])
        self.assertTrue(any("not strictly increasing" in error for error in report["errors"]))

    def test_time_basis_and_timestamp_format_are_checked(self):
        rows = valid_candidate_rows()
        rows[0]["TimeBasis"] = "UTC"
        rows[1]["ObservedAtServer"] = "not-a-time"
        report = validate_rows(SCHEMA_COLUMNS, rows)
        self.assertFalse(report["valid"])
        self.assertTrue(any("TimeBasis" in error for error in report["errors"]))
        self.assertTrue(any("ObservedAtServer" in error for error in report["errors"]))

    def test_decision_id_must_belong_to_candidate(self):
        rows = valid_candidate_rows()
        rows[2]["DecisionID"] = "OTHER-CANDIDATE:D1"
        report = validate_rows(SCHEMA_COLUMNS, rows)
        self.assertFalse(report["valid"])
        self.assertTrue(any("DecisionID is not nested" in error for error in report["errors"]))

    def test_deal_event_requires_deal_and_position_ids(self):
        rows = valid_candidate_rows()
        rows.append(make_row(5, "TRADE_ENTRY_DEAL", CycleID=CYCLE,
                             AttemptID=ATTEMPT, CandidateID=CANDIDATE,
                             OrderID="50001", DealID="", PositionID="70001"))
        report = validate_rows(SCHEMA_COLUMNS, rows)
        self.assertFalse(report["valid"])
        self.assertTrue(any("missing DealID or PositionID" in error for error in report["errors"]))

    def test_evaluation_without_candidate_is_a_valid_path_event(self):
        rows = [make_row(1, "M5_ENTRY_EVALUATION", CycleID=CYCLE, AttemptID=ATTEMPT,
                         CandidateID="", DecisionID="", DecisionStatus="", ReasonCode="")]
        report = validate_rows(SCHEMA_COLUMNS, rows)
        self.assertTrue(report["valid"], report["errors"])

    def test_run_id_consistency_is_checked(self):
        rows = valid_candidate_rows()
        rows[1]["RunID"] = "WM20261104B001"
        report = validate_rows(SCHEMA_COLUMNS, rows)
        self.assertFalse(report["valid"])
        self.assertTrue(any("more than one RunID" in error for error in report["errors"]))

    def test_source_timeframe_and_bar_timestamp_must_match_as_a_pair(self):
        rows = valid_candidate_rows()
        rows[0]["SourceBarOpenServer"] = ""
        report = validate_rows(SCHEMA_COLUMNS, rows)
        self.assertFalse(report["valid"])
        self.assertTrue(any("must both be set" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
