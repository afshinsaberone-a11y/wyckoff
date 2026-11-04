from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "src" / "Wyckoff_XAUUSD_W0_v1_08_C2_T030_SB050_LEDGER_V2.mq5"
SOURCE = SOURCE_PATH.read_text(encoding="utf-8")

EXPECTED_HEADER = [
    "SchemaVersion", "RunID", "EventID", "EventSequence",
    "EventTimeServer", "ObservedAtServer", "TimeBasis", "SourceTimeframe",
    "SourceBarOpenServer", "Symbol", "EA_Version", "RangeID", "CycleID",
    "AttemptID", "CandidateID", "DecisionID", "OrderID", "DealID", "PositionID",
    "LegacySetupID", "Direction", "Event", "DecisionStatus", "ReasonCode",
    "Details", "RangeHigh", "RangeLow", "InitialBalance",
]


class EventLedgerV2StaticTests(unittest.TestCase):
    def test_schema_header_has_exact_order_and_width(self):
        match = re.search(
            r'FileWrite\(g_ledgerHandle,"SchemaVersion",(.*?)\);\s*FileFlush',
            SOURCE,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match, "v2 CSV header writer was not found")
        actual = re.findall(r'"([^"]+)"', match.group(0))
        self.assertEqual(actual, EXPECTED_HEADER)
        self.assertEqual(len(actual), 28)

    def test_unique_run_id_is_mandatory_and_filename_is_run_scoped(self):
        self.assertIn('InpLedgerRunID              = "UNASSIGNED"', SOURCE)
        self.assertIn('requestedRunID!="UNASSIGNED"', SOURCE)
        self.assertIn('StringLen(requestedRunID)<=64', SOURCE)
        self.assertIn('base+"_"+g_ledgerRunID+".csv"', SOURCE)
        self.assertIn('if(FileIsExist(g_ledgerFileName,FILE_COMMON))', SOURCE)

    def test_event_ids_and_sequence_are_monotonic_per_run(self):
        self.assertIn('g_ledgerEventSequence++;', SOURCE)
        self.assertIn('g_ledgerRunID+":EV"+(string)g_ledgerEventSequence', SOURCE)
        self.assertIn('"BROKER_SERVER_RAW"', SOURCE)

    def test_range_cycle_attempt_identity_creation_points(self):
        self.assertIn('LedgerBeginRange();', SOURCE)
        self.assertIn('LedgerBeginAttempt();', SOURCE)
        self.assertIn('g_ledgerRangeID=g_ledgerRunID+":R"+(string)g_ledgerRangeSequence;', SOURCE)
        self.assertIn('g_ledgerCycleID=g_ledgerRangeID+":C"+(string)g_ledgerCycleSequence;', SOURCE)
        self.assertIn('g_ledgerAttemptID=g_ledgerCycleID+":A"+(string)g_ledgerAttemptSequence;', SOURCE)

    def test_candidate_is_created_only_at_each_recovery_trigger(self):
        self.assertEqual(SOURCE.count('LedgerBeginCandidate(WYCKOFF_BUY,bar.time);'), 1)
        self.assertEqual(SOURCE.count('LedgerBeginCandidate(WYCKOFF_SELL,bar.time);'), 1)
        buy_confirm = SOURCE.index('LogEvent("M5_BUY_RECOVERY_CONFIRMED"')
        buy_candidate = SOURCE.index('LedgerBeginCandidate(WYCKOFF_BUY,bar.time);')
        buy_order = SOURCE.index('sequenceComplete=PlaceTrade(WYCKOFF_BUY,bar);')
        sell_confirm = SOURCE.index('LogEvent("M5_SELL_RECOVERY_CONFIRMED"')
        sell_candidate = SOURCE.index('LedgerBeginCandidate(WYCKOFF_SELL,bar.time);')
        sell_order = SOURCE.index('sequenceComplete=PlaceTrade(WYCKOFF_SELL,bar);')
        self.assertLess(buy_confirm, buy_candidate)
        self.assertLess(buy_candidate, buy_order)
        self.assertLess(sell_confirm, sell_candidate)
        self.assertLess(sell_candidate, sell_order)
        self.assertIn('LedgerWriteEvent("CANDIDATE_CREATED"', SOURCE)

    def test_m5_evaluation_is_not_used_as_candidate_identity(self):
        self.assertEqual(SOURCE.count('LedgerBeginCandidate('), 3)  # definition + BUY + SELL
        self.assertIn('LogEvent("M5_ENTRY_EVALUATION",eval);', SOURCE)

    def test_execution_rejections_are_structured_and_candidate_linkable(self):
        required = [
            "REJECT_SPREAD_TOO_HIGH",
            "REJECT_TICK_UNAVAILABLE",
            "REJECT_STOP_CALC_FAILED",
            "REJECT_STOP_TOO_LARGE",
            "REJECT_BROKER_STOPS_LEVEL",
            "REJECT_RISK_BUDGET_INVALID",
            "REJECT_RISK_PER_LOT_INVALID",
            "REJECT_VOLUME_STEP_INVALID",
            "REJECT_VOLUME_BELOW_MIN",
            "REJECT_FILLING_MODE_UNAVAILABLE",
            "REJECT_PLANNED_RISK_CALC_FAILED",
            "ORDER_SEND_FAILED",
        ]
        for reason in required:
            with self.subTest(reason=reason):
                self.assertIn(reason, SOURCE)
        self.assertIn('StringFind(eventName,"REJECT_")==0', SOURCE)
        self.assertIn('decisionID=g_ledgerCandidateID+":D"+(string)g_ledgerDecisionSequence;', SOURCE)
        self.assertIn('reasonCode=(status=="REJECTED" ? eventName : "ORDER_ACCEPTED");', SOURCE)

    def test_order_deal_position_linkage_uses_mt5_transaction_values(self):
        self.assertIn('ulong resultOrderTicket=trade.ResultOrder();', SOURCE)
        self.assertIn('g_ledgerOrderID=(resultOrderTicket>0 ? (string)resultOrderTicket : "");', SOURCE)
        self.assertIn('g_ledgerOrderID=(string)trans.order;', SOURCE)
        self.assertIn('g_ledgerDealID=(string)trans.deal;', SOURCE)
        self.assertIn('HistoryDealGetInteger(trans.deal,DEAL_POSITION_ID)', SOURCE)
        self.assertIn('g_ledgerPositionID=(string)positionId;', SOURCE)

    def test_unavailable_identifiers_are_blank_not_zero(self):
        self.assertIn('string legacySetupID=(g_setupCounter>0 ? (string)g_setupCounter : "");', SOURCE)
        self.assertIn('resultOrderTicket>0 ? (string)resultOrderTicket : ""', SOURCE)
        self.assertIn('positionId>0 ? (string)positionId : ""', SOURCE)

    def test_h1_and_m5_source_bar_context_is_explicit(self):
        self.assertIn('LedgerSetSource(InpSignalTF,bar.time);', SOURCE)
        self.assertIn('LedgerSetSource(InpEntryTF,bar.time);', SOURCE)
        self.assertIn('g_ledgerSourceBarOpen>0 ? EnumToString(g_ledgerSourceTF) : ""', SOURCE)
        self.assertIn('TimeToString(g_ledgerSourceBarOpen,TIME_DATE|TIME_SECONDS)', SOURCE)

    def test_legacy_and_v2_csv_are_separate(self):
        self.assertIn('return file+"_C2_SB050_T030_TIMING_B"', SOURCE)
        self.assertIn('return base+"_"+g_ledgerRunID+".csv";', SOURCE)
        self.assertIn('LedgerWriteEvent(eventName,details);', SOURCE)

    def test_key_c2_trade_predicates_remain_present(self):
        anchors = [
            'breakoutPass=(directionPass && bodyPass && bar.close>level);',
            'breakoutPass=(directionPass && bodyPass && bar.close<level);',
            'rejectionPass=(directionPass && bodyPass && bar.time>g_setup.entryRetestTime &&',
            'bar.close>level);',
            'bar.close<level);',
            'distance<=0.0 || distance>InpMaxStopATR*atrM5',
            'CalculateRiskVolume(type,entry,stop,volume)',
            'trade.Buy(volume,g_symbol,0.0,stop,target,"Wyckoff W0 BUY")',
            'trade.Sell(volume,g_symbol,0.0,stop,target,"Wyckoff W0 SELL")',
        ]
        for anchor in anchors:
            with self.subTest(anchor=anchor):
                self.assertIn(anchor, SOURCE)

    def test_single_tester_run_guard_prevents_shared_optimization_writes(self):
        self.assertIn('MQLInfoInteger(MQL_OPTIMIZATION)', SOURCE)
        self.assertIn('Event Ledger v2 requires a single Tester run', SOURCE)
        self.assertIn('FILE_WRITE|FILE_CSV|FILE_SHARE_READ|FILE_ANSI|FILE_COMMON', SOURCE)


if __name__ == "__main__":
    unittest.main(verbosity=2)
