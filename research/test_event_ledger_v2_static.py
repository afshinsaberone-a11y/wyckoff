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

    def test_v2_ledger_open_succeeds_before_legacy_csv_is_deleted(self):
        ledger_open = SOURCE.index('g_ledgerHandle=FileOpen(g_ledgerFileName,')
        legacy_delete = SOURCE.index('if(FileIsExist(g_csvFileName,FILE_COMMON))')
        self.assertLess(ledger_open, legacy_delete)

    def test_run_id_collision_is_checked_before_legacy_csv_delete(self):
        collision = SOURCE.index('if(FileIsExist(g_ledgerFileName,FILE_COMMON))')
        legacy_delete = SOURCE.index('if(FileIsExist(g_csvFileName,FILE_COMMON))')
        self.assertLess(collision, legacy_delete)
        self.assertIn('use a new unique RunID', SOURCE)

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
        self.assertIn('decisionID=rowCandidateID+":D"+(string)g_ledgerDecisionSequence;', SOURCE)
        self.assertIn('reasonCode=(status=="REJECTED" ? eventName : "ORDER_ACCEPTED");', SOURCE)

    def test_decision_status_is_only_set_for_candidate_linked_events(self):
        writer_start = SOURCE.index('void LedgerWriteEvent(')
        writer_end = SOURCE.index('datetime eventTime=', writer_start)
        writer = SOURCE[writer_start:writer_end]
        self.assertIn('string eventDecisionStatus=LedgerDecisionStatus(eventName);', writer)
        self.assertIn('if(rowCandidateID!="" && eventDecisionStatus!="")', writer)
        self.assertIn('status=eventDecisionStatus;', writer)

    def test_trade_links_are_persisted_by_order_and_position(self):
        self.assertIn("struct SLedgerTradeLink", SOURCE)
        self.assertIn("int LedgerFindOrderLink(const ulong orderTicket)", SOURCE)
        self.assertIn("int LedgerFindPositionLink(const ulong positionID)", SOURCE)
        self.assertIn("int LedgerFindTradeLink(const ulong orderTicket,const ulong positionID)", SOURCE)
        self.assertIn("void LedgerRegisterOrderLink(const ulong orderTicket)", SOURCE)
        self.assertIn("void LedgerBindPosition(const int index,const ulong positionID)", SOURCE)
        self.assertIn("LedgerRegisterOrderLink(resultOrderTicket);", SOURCE)
        self.assertIn("LedgerBindPosition(ledgerTradeLinkIndex,(ulong)positionId);", SOURCE)

    def test_unlinked_transactions_are_never_attached_to_current_candidate(self):
        self.assertIn("LEDGER_UNLINKED_TRADE_TRANSACTION", SOURCE)
        self.assertIn("Never attach an unrelated currently-active Candidate to an unmatched deal.", SOURCE)
        self.assertIn("LedgerWriteEvent(eventName,details,tradeLinkIndex,transactionContext,", SOURCE)
        self.assertIn("rowCandidateID=g_ledgerTradeLinks[tradeLinkIndex].candidateID;", SOURCE)

    def test_deal_fields_are_read_before_position_history_lookup(self):
        deal_read = SOURCE.index('double dealPrice=HistoryDealGetDouble(trans.deal,DEAL_PRICE);')
        link_lookup = SOURCE.index('int ledgerTradeLinkIndex=LedgerFindTradeLink(trans.order,(ulong)positionId);')
        self.assertLess(deal_read, link_lookup)
        self.assertIn('HistorySelectByPosition(positionID)', SOURCE)

    def test_order_deal_position_linkage_uses_mt5_transaction_values(self):
        self.assertIn('ulong resultOrderTicket=trade.ResultOrder();', SOURCE)
        self.assertIn('g_ledgerOrderID=(resultOrderTicket>0 ? (string)resultOrderTicket : "");', SOURCE)
        self.assertIn('g_ledgerOrderID=(string)trans.order;', SOURCE)
        self.assertIn('g_ledgerDealID=(string)trans.deal;', SOURCE)
        self.assertIn('HistoryDealGetInteger(trans.deal,DEAL_POSITION_ID)', SOURCE)
        self.assertIn('positionId>0 ? (string)positionId : ""', SOURCE)

    def test_deal_event_time_uses_history_deal_time_and_observed_time_is_separate(self):
        self.assertIn('datetime dealTime=(datetime)HistoryDealGetInteger(trans.deal,DEAL_TIME);', SOURCE)
        self.assertIn('eventTimeOverride>0 ? eventTimeOverride : TimeCurrent()', SOURCE)
        self.assertIn('TimeToString(TimeCurrent(),TIME_DATE|TIME_SECONDS)', SOURCE)
        self.assertEqual(SOURCE.count('ledgerTradeLinkIndex,true,trans.order,trans.deal,(ulong)positionId,dealTime);'), 2)

    def test_order_link_is_registered_only_after_server_acceptance(self):
        place = SOURCE[SOURCE.index('bool PlaceTrade('):SOURCE.index('//------------------------------ M5 entry')]
        accepted_check = place.index('if(!sent || !accepted)')
        register_link = place.index('LedgerRegisterOrderLink(resultOrderTicket);')
        self.assertLess(accepted_check, register_link)
        self.assertIn('g_ledgerOrderID="";', place)

    def test_event_time_is_observation_time_not_relabelled_bar_open(self):
        self.assertIn('datetime eventTime=(eventTimeOverride>0 ? eventTimeOverride : TimeCurrent());', SOURCE)
        self.assertIn('TimeToString(g_ledgerSourceBarOpen,TIME_DATE|TIME_SECONDS)', SOURCE)

    def test_missing_attempt_does_not_fabricate_candidate_hierarchy(self):
        candidate_body = SOURCE[SOURCE.index('void LedgerBeginCandidate'):SOURCE.index('void LedgerResetActiveIDs')]
        self.assertNotIn('LedgerBeginAttempt();', candidate_body)
        self.assertIn('LEDGER_IDENTITY_ERROR', candidate_body)

    def test_legacy_csv_filename_is_isolated_from_c2_output(self):
        self.assertIn('return file+"_LEDGER_V2_C2_SB050_T030_TIMING_B"', SOURCE)

    def test_unavailable_identifiers_are_blank_not_zero(self):
        self.assertIn('string legacySetupID=(rowRangeID!="" && rowLegacySetupCounter>0 ? (string)rowLegacySetupCounter : "");', SOURCE)
        self.assertIn('resultOrderTicket>0 ? (string)resultOrderTicket : ""', SOURCE)
        self.assertIn('positionId>0 ? (string)positionId : ""', SOURCE)

    def test_h1_and_m5_source_bar_context_is_explicit(self):
        self.assertIn('LedgerSetSource(InpSignalTF,bar.time);', SOURCE)
        self.assertIn('LedgerSetSource(InpEntryTF,bar.time);', SOURCE)
        self.assertIn('g_ledgerSourceBarOpen>0 ? EnumToString(g_ledgerSourceTF) : ""', SOURCE)
        self.assertIn('TimeToString(g_ledgerSourceBarOpen,TIME_DATE|TIME_SECONDS)', SOURCE)

    def test_legacy_and_v2_csv_are_separate(self):
        self.assertIn('return file+"_LEDGER_V2_C2_SB050_T030_TIMING_B"', SOURCE)
        self.assertIn('return base+"_"+g_ledgerRunID+".csv";', SOURCE)
        self.assertIn("LedgerWriteEvent(eventName,details,tradeLinkIndex,transactionContext,", SOURCE)

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
