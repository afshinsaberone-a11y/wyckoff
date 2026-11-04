//+------------------------------------------------------------------+
//|                       Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT.mq5  |
//| Rule-based Wyckoff prototype for MT5                             |
//| W0 v1.08-C2: H1 structure audit (diagnostics only)               |
//| C2: causal timing + 0.30 ATR retest tolerance + 0.50 ATR SL buffer |
//| NOTE: Research prototype. Validate visually and in Strategy      |
//| Tester before any demo/live use. No profitability is implied.     |
//+------------------------------------------------------------------+
#property strict
#property version   "1.084"
#property description "Wyckoff W0 v1.08-C2 multi-lookback and pivot audit; trade logic unchanged"

#include <Trade/Trade.mqh>

CTrade trade;

//------------------------------ Inputs ------------------------------
input group "=== Symbol & Timeframes ==="
input string          InpTradeSymbol             = "";       // Empty = chart symbol (allows broker suffix)
input ENUM_TIMEFRAMES InpStructureTF             = PERIOD_H4;
input ENUM_TIMEFRAMES InpSignalTF                = PERIOD_H1;
input ENUM_TIMEFRAMES InpEntryTF                 = PERIOD_M5;
input bool            InpUseH4ContextFilter      = false;    // Test false first; then compare true
input int             InpH4EMAPeriod             = 50;
input int             InpH4EMASlopeBars          = 5;

input group "=== Risk Management ==="
input double          InpRiskPercent             = 0.50;
input double          InpRewardRisk              = 2.00;
input ulong           InpMagicNumber             = 31102026;
input int             InpDeviationPoints         = 20;
input double          InpMaxSpreadPoints         = 80.0;
input double          InpMaxStopATR              = 4.0;
input int             InpStopLookbackM5          = 12;
input double          InpStopATRBuffer           = 0.50;   // C2: restore baseline stop buffer

input group "=== Range Detection ==="
input int             InpRangeLookbackBars       = 80;
input int             InpRangeMinBars            = 24;
input int             InpRangeMaxBars            = 120;
input int             InpRangeATRPeriod          = 14;
input double          InpRangeMinWidthATR        = 2.50;
input double          InpRangeMaxWidthATR        = 10.00;
input int             InpRangeMinTouches         = 2;
input double          InpRangeTouchToleranceATR  = 0.25;
input int             InpRangeMinTouchSpacing    = 5;
input int             InpRangeMaxAgeBars         = 120;

input group "=== Spring / UTAD Detection ==="
input double          InpSpringMinPenetrationATR = 0.05;
input double          InpSpringMaxPenetrationATR = 0.75;
input int             InpSpringReentryBars       = 3;
input double          InpSpringMinClosePosition  = 0.65;
input double          InpUTADMinPenetrationATR   = 0.05;
input double          InpUTADMaxPenetrationATR   = 0.75;
input int             InpUTADReentryBars         = 3;
input double          InpUTADMaxClosePosition    = 0.35;

input group "=== Test Detection ==="
input int             InpTestMinBarsAfterEvent   = 1;
input int             InpTestMaxBarsAfterEvent   = 10;
input double          InpTestMaxBreakBeyondEventATR = 0.10;
input double          InpTestSupportToleranceATR = 0.30;

input group "=== SOS / SOW Detection ==="
input int             InpStrengthSwingLookback   = 5;
input double          InpSOSMinBodyATR           = 0.50;
input double          InpSOSMinBodyShare         = 0.60;
input double          InpSOSMinClosePosition     = 0.70;
input double          InpSOWMinBodyATR           = 0.50;
input double          InpSOWMinBodyShare         = 0.60;
input double          InpSOWMaxClosePosition     = 0.30;

input group "=== LPS / LPSY Detection ==="
input double          InpLPSMinPullbackATR       = 0.15;
input double          InpLPSMaxPullbackATR       = 0.80;
input double          InpLPSInvalidationATR      = 0.20;
input int             InpLPSExpiryBars           = 12;

input group "=== M5 Entry ==="
input int             InpEntryBreakLookback      = 3;
input double          InpMinConfirmBodyShare     = 0.45;
input group "=== M5 Entry Phase Expiry (Variant C) ==="
input int             InpBreakoutExpiryBars       = 12;   // Maximum closed bars in breakout phase
input int             InpRetestExpiryBars         = 12;   // Maximum closed bars in retest phase
input int             InpRecoveryExpiryBars       = 12;   // Maximum closed bars in recovery phase
input double          InpEntryRetestToleranceATR = 0.30;  // C2: allow retest wick within 0.30 ATR
input int             InpM5ATRPeriod             = 14;

input group "=== Chart Display ==="
sinput bool           InpDrawTradingRanges       = true;
sinput bool           InpDrawWyckoffEvents       = true;
sinput bool           InpDrawEntrySignals        = true;
sinput bool           InpDrawStopTarget          = true;
sinput color          InpRangeColor              = clrSlateBlue;
sinput color          InpBuyEventColor           = clrLimeGreen;
sinput color          InpSellEventColor          = clrTomato;

input group "=== Debug & Logging ==="
sinput bool           InpEnableDebug             = true;
sinput bool           InpLogRejectedSetups       = true;
sinput bool           InpExportCSV               = true;
sinput bool           InpLogEntryEvaluation      = true;
sinput string         InpCSVFileName             = "Wyckoff_W0_events_v1_08.csv";

//------------------------------ Types --------------------------------
enum ENUM_WYCKOFF_DIRECTION
  {
   WYCKOFF_NONE = 0,
   WYCKOFF_BUY  = 1,
   WYCKOFF_SELL = -1
  };

enum ENUM_WYCKOFF_STAGE
  {
   ST_IDLE = 0,
   ST_WAIT_EVENT,
   ST_WAIT_TEST,
   ST_WAIT_STRENGTH,
   ST_WAIT_PULLBACK,
   ST_WAIT_ENTRY,
   ST_IN_POSITION
  };

enum ENUM_ENTRY_PHASE
  {
   ENTRY_PHASE_NONE = 0,
   ENTRY_PHASE_WAIT_BREAKOUT,
   ENTRY_PHASE_WAIT_RETEST,
   ENTRY_PHASE_WAIT_REJECTION
  };

struct SWyckoffSetup
  {
   ENUM_WYCKOFF_STAGE     stage;
   ENUM_WYCKOFF_DIRECTION direction;
   double                 rangeHigh;
   double                 rangeLow;
   datetime               rangeStart;
   datetime               rangeEnd;
   int                    rangeAge;
   bool                   eventCandidate;
   int                    candidateAge;
   double                 eventExtreme;
   datetime               eventTime;
   double                 testExtreme;
   datetime               testTime;
   double                 strengthBreakLevel;
   double                 strengthExtreme;
   datetime               strengthTime;
   int                    barsSinceEvent;
   int                    barsSinceTest;
   int                    barsSinceStrength;
   int                    barsSinceEntryReady;
   int                    entryBarsChecked;
   int                    entryPhaseBarsChecked;
   int                    entryDirectionalBars;
   int                    entryBodyPassBars;
   int                    entryBreakPassBars;
   int                    entryRetestTouchBars;
   int                    entryRejectionBars;
   ENUM_ENTRY_PHASE       entryPhase;
   double                 entryBreakoutLevel;
   double                 entryBreakoutExtreme;
   datetime               entryBreakoutTime;
   double                 entryRetestHigh;
   double                 entryRetestLow;
   double                 entryRetestExtreme;
   datetime               entryRetestTime;
   int                    entryRetestBars;
   double                 entryLastClose;
   double                 entryLastBreakLevel;
   double                 entryLastBodyShare;
   datetime               entryReadyTime; // Causal timing: first M5 bar may open at/after H1 confirmation close
   datetime               setupStarted;
  };

//------------------------------ Globals ------------------------------
string   g_symbol = "";
int      g_atrSignalHandle = INVALID_HANDLE;
int      g_atrEntryHandle  = INVALID_HANDLE;
int      g_emaStructureHandle = INVALID_HANDLE;
datetime g_lastSignalBar = 0;
datetime g_lastEntryBar  = 0;
int      g_csvHandle = INVALID_HANDLE;
int      g_digits = 2;
double   g_point = 0.01;
double   g_initialBalance = 0.0;
double   g_activeRiskMoney = 0.0;       // Actual fill-to-SL risk, account currency
double   g_plannedRiskMoney = 0.0;      // Pre-trade estimate (fallback only)
double   g_pendingStopPrice = 0.0;
double   g_pendingTargetPrice = 0.0;
double   g_pendingRequestPrice = 0.0;
double   g_pendingOrderVolume = 0.0;
double   g_pendingSpreadPoints = 0.0;
double   g_actualEntryVolume = 0.0;
double   g_weightedSlippagePoints = 0.0;
double   g_weightedExitSlippagePoints = 0.0;
double   g_actualExitVolume = 0.0;
ENUM_WYCKOFF_DIRECTION g_activeDirection = WYCKOFF_NONE;
string   g_csvFileName = "";
ulong    g_activePositionId = 0;
long     g_setupCounter = 0;
SWyckoffSetup g_setup;

#define EA_VERSION "1.08-C2-H1STRUCT-ML-AUDIT-SB050-T030"

//------------------------------ Utilities ----------------------------
string EffectiveCSVFileName()
  {
   string file=InpCSVFileName;
   int length=StringLen(file);
   if(length>4 && StringSubstr(file,length-4)==".csv")
      file=StringSubstr(file,0,length-4);
   return file+"_C2_SB050_T030_TIMING_B"+(string)InpBreakoutExpiryBars+
             "_R"+(string)InpRetestExpiryBars+
             "_RC"+(string)InpRecoveryExpiryBars+".csv";
  }

void DebugPrint(const string message)
  {
   if(InpEnableDebug)
      Print("[Wyckoff W0] ", message);
  }

void LogEvent(const string eventName,const string details="")
  {
   string dir = (g_setup.direction==WYCKOFF_BUY ? "BUY" :
                 g_setup.direction==WYCKOFF_SELL ? "SELL" : "NONE");
   string msg = eventName+" | "+dir+" | "+details;
   DebugPrint(msg);
   if(InpExportCSV && g_csvHandle!=INVALID_HANDLE)
     {
      FileWrite(g_csvHandle,TimeToString(TimeCurrent(),TIME_DATE|TIME_SECONDS),
                EA_VERSION,g_symbol,DoubleToString(g_initialBalance,2),
                g_setupCounter,dir,eventName,details,
                DoubleToString(g_setup.rangeHigh,g_digits),
                DoubleToString(g_setup.rangeLow,g_digits),
                (string)g_activePositionId);
      FileFlush(g_csvHandle);
     }
  }

void LogReject(const string reason,const string details="")
  {
   if(InpLogRejectedSetups)
      LogEvent(reason,details);
  }

void ResetSetup(const string reason)
  {
   if(reason!="")
      LogEvent("SETUP_RESET",reason);
   g_setup.stage=ST_IDLE;
   g_setup.direction=WYCKOFF_NONE;
   g_setup.rangeHigh=0.0;
   g_setup.rangeLow=0.0;
   g_setup.rangeStart=0;
   g_setup.rangeEnd=0;
   g_setup.rangeAge=0;
   g_setup.eventCandidate=false;
   g_setup.candidateAge=0;
   g_setup.eventExtreme=0.0;
   g_setup.eventTime=0;
   g_setup.testExtreme=0.0;
   g_setup.testTime=0;
   g_setup.strengthBreakLevel=0.0;
   g_setup.strengthExtreme=0.0;
   g_setup.strengthTime=0;
   g_setup.barsSinceEvent=0;
   g_setup.barsSinceTest=0;
   g_setup.barsSinceStrength=0;
   g_setup.barsSinceEntryReady=0;
   g_setup.entryBarsChecked=0;
   g_setup.entryPhaseBarsChecked=0;
   g_setup.entryDirectionalBars=0;
   g_setup.entryBodyPassBars=0;
   g_setup.entryBreakPassBars=0;
   g_setup.entryRetestTouchBars=0;
   g_setup.entryRejectionBars=0;
   g_setup.entryPhase=ENTRY_PHASE_NONE;
   g_setup.entryBreakoutLevel=0.0;
   g_setup.entryBreakoutExtreme=0.0;
   g_setup.entryBreakoutTime=0;
   g_setup.entryRetestHigh=0.0;
   g_setup.entryRetestLow=0.0;
   g_setup.entryRetestExtreme=0.0;
   g_setup.entryRetestTime=0;
   g_setup.entryRetestBars=0;
   g_setup.entryLastClose=0.0;
   g_setup.entryLastBreakLevel=0.0;
   g_setup.entryLastBodyShare=0.0;
   g_setup.entryReadyTime=0;
   g_setup.setupStarted=0;
  }

bool GetRates(const ENUM_TIMEFRAMES tf,const int startShift,const int count,MqlRates &rates[])
  {
   ArraySetAsSeries(rates,true);
   int copied=CopyRates(g_symbol,tf,startShift,count,rates);
   return (copied==count);
  }

bool GetATR(const int handle,double &value)
  {
   if(handle==INVALID_HANDLE)
      return false;
   double buffer[];
   ArraySetAsSeries(buffer,true);
   if(CopyBuffer(handle,0,1,1,buffer)!=1)
      return false;
   value=buffer[0];
   return (value>0.0 && MathIsValidNumber(value));
  }

// Diagnostic helper only. It does not change which ATR the strategy uses.
bool GetATRAtShift(const int handle,const int shift,double &value)
  {
   if(handle==INVALID_HANDLE || shift<0)
      return false;
   double buffer[];
   ArraySetAsSeries(buffer,true);
   if(CopyBuffer(handle,0,shift,1,buffer)!=1)
      return false;
   value=buffer[0];
   return (value>0.0 && MathIsValidNumber(value));
  }

double CandleRange(const MqlRates &bar)
  {
   return MathMax(0.0,bar.high-bar.low);
  }

double BodyShare(const MqlRates &bar)
  {
   double range=CandleRange(bar);
   if(range<=0.0) return 0.0;
   return MathAbs(bar.close-bar.open)/range;
  }

double ClosePosition(const MqlRates &bar)
  {
   double range=CandleRange(bar);
   if(range<=0.0) return 0.5;
   return (bar.close-bar.low)/range;
  }

double NormalizePrice(const double price)
  {
   double tickSize=SymbolInfoDouble(g_symbol,SYMBOL_TRADE_TICK_SIZE);
   if(tickSize<=0.0) tickSize=g_point;
   return NormalizeDouble(MathRound(price/tickSize)*tickSize,g_digits);
  }

bool IsNewBar(const ENUM_TIMEFRAMES tf,datetime &lastBarTime)
  {
   datetime current=iTime(g_symbol,tf,0);
   if(current<=0 || current==lastBarTime)
      return false;
   lastBarTime=current;
   return true;
  }

bool HasOurPosition()
  {
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong ticket=PositionGetTicket(i);
      if(ticket==0) continue;
      if(PositionGetString(POSITION_SYMBOL)==g_symbol &&
         (ulong)PositionGetInteger(POSITION_MAGIC)==InpMagicNumber)
         return true;
     }
   return false;
  }

bool SpreadIsAcceptable()
  {
   MqlTick tick;
   if(!SymbolInfoTick(g_symbol,tick)) return false;
   double spread=(tick.ask-tick.bid)/SymbolInfoDouble(g_symbol,SYMBOL_POINT);
   if(spread>InpMaxSpreadPoints)
     {
      LogReject("REJECT_SPREAD_TOO_HIGH",DoubleToString(spread,1));
      return false;
     }
   return true;
  }

bool H4ContextAllows(const ENUM_WYCKOFF_DIRECTION dir)
  {
   if(!InpUseH4ContextFilter) return true;
   if(g_emaStructureHandle==INVALID_HANDLE) return false;
   double ema[];
   ArraySetAsSeries(ema,true);
   int need=MathMax(2,InpH4EMASlopeBars+1);
   if(CopyBuffer(g_emaStructureHandle,0,1,need,ema)!=need)
      return false;
   MqlRates h4[];
   if(!GetRates(InpStructureTF,1,1,h4)) return false;
   bool falling=(ema[0]<ema[InpH4EMASlopeBars] && h4[0].close<ema[0]);
   bool rising =(ema[0]>ema[InpH4EMASlopeBars] && h4[0].close>ema[0]);
   if(dir==WYCKOFF_BUY) return falling;
   if(dir==WYCKOFF_SELL) return rising;
   return false;
  }

void DrawRange()
  {
   if(!InpDrawTradingRanges) return;
   string name="W0_RANGE_"+(string)g_setupCounter;
   ObjectDelete(0,name);
   datetime right=iTime(g_symbol,InpSignalTF,0);
   if(right<=0) right=TimeCurrent();
   if(ObjectCreate(0,name,OBJ_RECTANGLE,0,g_setup.rangeStart,g_setup.rangeHigh,right,g_setup.rangeLow))
     {
      ObjectSetInteger(0,name,OBJPROP_COLOR,InpRangeColor);
      ObjectSetInteger(0,name,OBJPROP_STYLE,STYLE_DOT);
      ObjectSetInteger(0,name,OBJPROP_WIDTH,1);
      ObjectSetInteger(0,name,OBJPROP_FILL,false);
      ObjectSetInteger(0,name,OBJPROP_BACK,true);
     }
  }

void DrawEvent(const string label,const datetime when,const double price,const bool isBuy)
  {
   if(!InpDrawWyckoffEvents) return;
   string name="W0_"+label+"_"+(string)g_setupCounter+"_"+(string)when;
   if(ObjectCreate(0,name,OBJ_TEXT,0,when,price))
     {
      ObjectSetString(0,name,OBJPROP_TEXT,label);
      ObjectSetInteger(0,name,OBJPROP_COLOR,isBuy ? InpBuyEventColor : InpSellEventColor);
      ObjectSetInteger(0,name,OBJPROP_FONTSIZE,8);
      ObjectSetInteger(0,name,OBJPROP_ANCHOR,isBuy ? ANCHOR_LOWER : ANCHOR_UPPER);
     }
  }

//------------------------------ Range detection ----------------------
bool CountSeparatedTouches(const MqlRates &rates[],const int firstIndex,const int lastIndex,
                            const bool resistance,const double level,const double tolerance,
                            const int minSpacing,const int minTouches,int &touchCount)
  {
   int count=0;
   touchCount=0;
   int lastTouchIndex=-100000;
   for(int i=lastIndex;i>=firstIndex;i--)
     {
      bool touched=false;
      if(resistance)
         touched=(rates[i].high>=level-tolerance);
      else
         touched=(rates[i].low<=level+tolerance);
      if(touched && (lastTouchIndex<0 || MathAbs(i-lastTouchIndex)>=minSpacing))
        {
         count++;
         lastTouchIndex=i;
        }
     }
   touchCount=count;
   return (count>=minTouches);
  }

bool DetectRange()
  {
   int lookback=MathMax(InpRangeMinBars,InpRangeLookbackBars);
   lookback=MathMin(lookback,InpRangeMaxBars);
   // Build the range from the configured closed bars at shifts 2..N+1.
   // The most recently closed H1 candle (shift 1) is deliberately excluded
   // from the range so it can be checked immediately as a possible Spring/UTAD.
   MqlRates rates[];
   if(!GetRates(InpSignalTF,2,lookback,rates))
      return false;
   double atr=0.0;
   if(!GetATR(g_atrSignalHandle,atr)) return false;

   double high=-DBL_MAX;
   double low=DBL_MAX;
   int highIndex=-1,lowIndex=-1;
   // All rates in this array are older than the most recently closed signal bar.
   for(int i=0;i<lookback;i++)
     {
      if(rates[i].high>high) { high=rates[i].high; highIndex=i; }
      if(rates[i].low<low)  { low=rates[i].low;  lowIndex=i; }
     }
   if(highIndex<0 || lowIndex<0 || high<=low) return false;
   double widthATR=(high-low)/atr;
   if(widthATR<InpRangeMinWidthATR || widthATR>InpRangeMaxWidthATR)
      return false;
   double atrPriorClosed=0.0;
   bool hasPriorATR=GetATRAtShift(g_atrSignalHandle,2,atrPriorClosed);
   double widthATRUsingPrior=(hasPriorATR ? (high-low)/atrPriorClosed : 0.0);
   double tolerance=atr*InpRangeTouchToleranceATR;
   int upperTouches=0,lowerTouches=0;
   if(!CountSeparatedTouches(rates,0,lookback-1,true,high,tolerance,
                             InpRangeMinTouchSpacing,InpRangeMinTouches,upperTouches))
      return false;
   if(!CountSeparatedTouches(rates,0,lookback-1,false,low,tolerance,
                             InpRangeMinTouchSpacing,InpRangeMinTouches,lowerTouches))
      return false;

   g_setupCounter++;
   g_setup.stage=ST_WAIT_EVENT;
   g_setup.direction=WYCKOFF_NONE;
   g_setup.rangeHigh=high;
   g_setup.rangeLow=low;
   g_setup.rangeStart=rates[lookback-1].time;
   g_setup.rangeEnd=rates[0].time;
   g_setup.rangeAge=0;
   g_setup.eventCandidate=false;
   g_setup.candidateAge=0;
   g_setup.eventExtreme=0.0;
   g_setup.setupStarted=TimeCurrent();
   DrawRange();
   LogEvent("RANGE_FOUND","widthATR="+DoubleToString(widthATR,2)+
            "; rangeBars="+(string)lookback+
            "; upperTouches="+(string)upperTouches+
            "; lowerTouches="+(string)lowerTouches);
   LogEvent("H1_RANGE_CONTEXT_AUDIT",
            "rangeHigh="+DoubleToString(high,g_digits)+
            "; rangeLow="+DoubleToString(low,g_digits)+
            "; widthPrice="+DoubleToString(high-low,g_digits)+
            "; atrShift1Used="+DoubleToString(atr,g_digits)+
            "; atrShift2Prior="+(hasPriorATR ? DoubleToString(atrPriorClosed,g_digits) : "NA")+
            "; widthATRShift1="+DoubleToString(widthATR,3)+
            "; widthATRShift2="+(hasPriorATR ? DoubleToString(widthATRUsingPrior,3) : "NA")+
            "; rangeStart="+TimeToString(g_setup.rangeStart,TIME_DATE|TIME_MINUTES)+
            "; rangeEnd="+TimeToString(g_setup.rangeEnd,TIME_DATE|TIME_MINUTES));
   return true;
  }

//------------------------------ Event detection ----------------------
bool DetectSpringCandidate(const MqlRates &bar,const double atr)
  {
   double penetration=(g_setup.rangeLow-bar.low)/atr;
   if(penetration<InpSpringMinPenetrationATR) return false;
   if(penetration>InpSpringMaxPenetrationATR)
     {
      LogReject("REJECT_SPRING_TOO_DEEP", "penetrationATR="+DoubleToString(penetration,2));
      ResetSetup("RANGE_INVALIDATED_SPRING_BREAK_TOO_DEEP");
      return false;
     }
   g_setup.direction=WYCKOFF_BUY;
   if(!H4ContextAllows(WYCKOFF_BUY))
     {
      LogReject("REJECT_H4_CONTEXT_BUY");
      g_setup.direction=WYCKOFF_NONE;
      return false;
     }
   g_setup.eventCandidate=true;
   g_setup.candidateAge=0;
   g_setup.eventExtreme=bar.low;
   g_setup.eventTime=bar.time;
   g_setup.barsSinceEvent=0;
   LogEvent("SPRING_CANDIDATE","penetrationATR="+DoubleToString(penetration,2));
   return true;
  }

bool DetectUTADCandidate(const MqlRates &bar,const double atr)
  {
   double penetration=(bar.high-g_setup.rangeHigh)/atr;
   if(penetration<InpUTADMinPenetrationATR) return false;
   if(penetration>InpUTADMaxPenetrationATR)
     {
      LogReject("REJECT_UTAD_TOO_DEEP", "penetrationATR="+DoubleToString(penetration,2));
      ResetSetup("RANGE_INVALIDATED_UTAD_BREAK_TOO_DEEP");
      return false;
     }
   g_setup.direction=WYCKOFF_SELL;
   if(!H4ContextAllows(WYCKOFF_SELL))
     {
      LogReject("REJECT_H4_CONTEXT_SELL");
      g_setup.direction=WYCKOFF_NONE;
      return false;
     }
   g_setup.eventCandidate=true;
   g_setup.candidateAge=0;
   g_setup.eventExtreme=bar.high;
   g_setup.eventTime=bar.time;
   g_setup.barsSinceEvent=0;
   LogEvent("UTAD_CANDIDATE","penetrationATR="+DoubleToString(penetration,2));
   return true;
  }

void ProcessWaitEvent(const MqlRates &bar,const double atr)
  {
   if(!g_setup.eventCandidate)
     {
      bool spring=DetectSpringCandidate(bar,atr);
      if(g_setup.stage==ST_IDLE) return; // Range was invalidated by an excessive Spring-side break.
      if(spring)
        {
         // A Spring may be confirmed on the same candle that pierced support.
         if(bar.close>g_setup.rangeLow && ClosePosition(bar)>=InpSpringMinClosePosition)
           {
            g_setup.stage=ST_WAIT_TEST;
            g_setup.eventCandidate=false;
            g_setup.barsSinceEvent=0;
            DrawEvent("SPRING",g_setup.eventTime,g_setup.eventExtreme,true);
            LogEvent("SPRING_CONFIRMED","same-bar re-entry; close="+DoubleToString(bar.close,g_digits));
           }
         return;
        }
      bool utad=DetectUTADCandidate(bar,atr);
      if(g_setup.stage==ST_IDLE) return; // Range was invalidated by an excessive UTAD-side break.
      if(utad)
        {
         // UTAD may also confirm on its initial rejection candle.
         if(bar.close<g_setup.rangeHigh && ClosePosition(bar)<=InpUTADMaxClosePosition)
           {
            g_setup.stage=ST_WAIT_TEST;
            g_setup.eventCandidate=false;
            g_setup.barsSinceEvent=0;
            DrawEvent("UTAD",g_setup.eventTime,g_setup.eventExtreme,false);
            LogEvent("UTAD_CONFIRMED","same-bar re-entry; close="+DoubleToString(bar.close,g_digits));
           }
         return;
        }
      return;
     }
   g_setup.candidateAge++;
   if(g_setup.direction==WYCKOFF_BUY)
     {
      if(bar.low<g_setup.eventExtreme) g_setup.eventExtreme=bar.low;
      double penetration=(g_setup.rangeLow-g_setup.eventExtreme)/atr;
      if(penetration>InpSpringMaxPenetrationATR)
        {
         LogReject("REJECT_SPRING_TOO_DEEP","candidatePenetrationATR="+DoubleToString(penetration,2));
         ResetSetup("RANGE_INVALIDATED_SPRING_CANDIDATE_TOO_DEEP");
         return;
        }
      if(bar.close>g_setup.rangeLow && ClosePosition(bar)>=InpSpringMinClosePosition)
        {
         g_setup.stage=ST_WAIT_TEST;
         g_setup.eventCandidate=false;
         g_setup.barsSinceEvent=0;
         DrawEvent("SPRING",g_setup.eventTime,g_setup.eventExtreme,true);
         LogEvent("SPRING_CONFIRMED","close="+DoubleToString(bar.close,g_digits));
         return;
        }
      if(g_setup.candidateAge>=InpSpringReentryBars)
        {
         LogReject("REJECT_NO_REENTRY","Spring did not close back inside range");
         g_setup.eventCandidate=false;
         g_setup.direction=WYCKOFF_NONE;
        }
     }
   else if(g_setup.direction==WYCKOFF_SELL)
     {
      if(bar.high>g_setup.eventExtreme) g_setup.eventExtreme=bar.high;
      double penetration=(g_setup.eventExtreme-g_setup.rangeHigh)/atr;
      if(penetration>InpUTADMaxPenetrationATR)
        {
         LogReject("REJECT_UTAD_TOO_DEEP","candidatePenetrationATR="+DoubleToString(penetration,2));
         ResetSetup("RANGE_INVALIDATED_UTAD_CANDIDATE_TOO_DEEP");
         return;
        }
      if(bar.close<g_setup.rangeHigh && ClosePosition(bar)<=InpUTADMaxClosePosition)
        {
         g_setup.stage=ST_WAIT_TEST;
         g_setup.eventCandidate=false;
         g_setup.barsSinceEvent=0;
         DrawEvent("UTAD",g_setup.eventTime,g_setup.eventExtreme,false);
         LogEvent("UTAD_CONFIRMED","close="+DoubleToString(bar.close,g_digits));
         return;
        }
      if(g_setup.candidateAge>=InpUTADReentryBars)
        {
         LogReject("REJECT_NO_REENTRY","UTAD did not close back inside range");
         g_setup.eventCandidate=false;
         g_setup.direction=WYCKOFF_NONE;
        }
     }
  }

//------------------------------ Test detection -----------------------
void ProcessWaitTest(const MqlRates &bar,const double atr)
  {
   g_setup.barsSinceEvent++;
   if(g_setup.barsSinceEvent>InpTestMaxBarsAfterEvent)
     {
      ResetSetup("TEST_EXPIRED");
      return;
     }
   if(g_setup.barsSinceEvent<InpTestMinBarsAfterEvent)
      return;
   if(g_setup.direction==WYCKOFF_BUY)
     {
      bool nearSupport=(bar.low<=g_setup.rangeLow+InpTestSupportToleranceATR*atr);
      bool holdsAboveSpring=(bar.low>=g_setup.eventExtreme-InpTestMaxBreakBeyondEventATR*atr);
      bool closesBackInside=(bar.close>=g_setup.rangeLow);
      if(nearSupport && holdsAboveSpring && closesBackInside)
        {
         g_setup.testExtreme=bar.low;
         g_setup.testTime=bar.time;
         g_setup.barsSinceTest=0;
         g_setup.stage=ST_WAIT_STRENGTH;
         DrawEvent("TEST",bar.time,bar.low,true);
         LogEvent("TEST_CONFIRMED","low="+DoubleToString(bar.low,g_digits)+
                  "; eventAgeBars="+(string)g_setup.barsSinceEvent);
        }
     }
   else if(g_setup.direction==WYCKOFF_SELL)
     {
      bool nearResistance=(bar.high>=g_setup.rangeHigh-InpTestSupportToleranceATR*atr);
      bool holdsBelowUTAD=(bar.high<=g_setup.eventExtreme+InpTestMaxBreakBeyondEventATR*atr);
      bool closesBackInside=(bar.close<=g_setup.rangeHigh);
      if(nearResistance && holdsBelowUTAD && closesBackInside)
        {
         g_setup.testExtreme=bar.high;
         g_setup.testTime=bar.time;
         g_setup.barsSinceTest=0;
         g_setup.stage=ST_WAIT_STRENGTH;
         DrawEvent("TEST",bar.time,bar.high,false);
         LogEvent("TEST_CONFIRMED","high="+DoubleToString(bar.high,g_digits)+
                  "; eventAgeBars="+(string)g_setup.barsSinceEvent);
        }
     }
  }

// Diagnostic-only: compare several prior-swing lookbacks and recent confirmed pivots.
// These levels are descriptive candidates, NOT authoritative Creek/Ice definitions.
void LogStrengthStructureAudit(const bool isBuy,const MqlRates &rates[],
                               const MqlRates &bar,const double atr,
                               const double bodyATR,const double share,
                               const double closePos)
  {
   int windows[4]={5,10,20,40};
   string side=(isBuy ? "HIGH" : "LOW");
   string diag="barOpen="+TimeToString(bar.time,TIME_DATE|TIME_MINUTES)+
               "; close="+DoubleToString(bar.close,g_digits)+
               "; bodyATR="+DoubleToString(bodyATR,3)+
               "; bodyShare="+DoubleToString(share,3)+
               "; closePosition="+DoubleToString(closePos,3)+
               "; referenceSide="+side+
               "; configuredLookback="+(string)InpStrengthSwingLookback;

   for(int w=0;w<4;w++)
     {
      int n=windows[w];
      if(ArraySize(rates)<=n) continue;
      double level=(isBuy ? -DBL_MAX : DBL_MAX);
      for(int i=1;i<=n;i++)
        {
         if(isBuy) level=MathMax(level,rates[i].high);
         else      level=MathMin(level,rates[i].low);
        }
      bool passed=(isBuy ? bar.close>level : bar.close<level);
      diag+="; lb"+(string)n+"Level="+DoubleToString(level,g_digits)+
            "; lb"+(string)n+"Break="+(passed ? "1" : "0");
     }

   // A pivot is considered confirmed only after two newer H1 bars exist.
   // rates[] is series-oriented: smaller indices are newer bars.
   int pivotHighCount=0,pivotLowCount=0;
   double ph1=0.0,ph2=0.0,ph3=0.0,pl1=0.0,pl2=0.0,pl3=0.0;
   datetime pht1=0,pht2=0,pht3=0,plt1=0,plt2=0,plt3=0;
   int maxIndex=MathMin(InpRangeLookbackBars-2,ArraySize(rates)-3);
   for(int i=3;i<=maxIndex;i++)
     {
      bool pivotHigh=(rates[i].high>rates[i-1].high &&
                      rates[i].high>rates[i-2].high &&
                      rates[i].high>rates[i+1].high &&
                      rates[i].high>rates[i+2].high);
      if(pivotHigh)
        {
         pivotHighCount++;
         if(pivotHighCount==1) { ph1=rates[i].high; pht1=rates[i].time; }
         else if(pivotHighCount==2) { ph2=rates[i].high; pht2=rates[i].time; }
         else if(pivotHighCount==3) { ph3=rates[i].high; pht3=rates[i].time; }
        }

      bool pivotLow=(rates[i].low<rates[i-1].low &&
                     rates[i].low<rates[i-2].low &&
                     rates[i].low<rates[i+1].low &&
                     rates[i].low<rates[i+2].low);
      if(pivotLow)
        {
         pivotLowCount++;
         if(pivotLowCount==1) { pl1=rates[i].low; plt1=rates[i].time; }
         else if(pivotLowCount==2) { pl2=rates[i].low; plt2=rates[i].time; }
         else if(pivotLowCount==3) { pl3=rates[i].low; plt3=rates[i].time; }
        }
     }

   if(isBuy)
     {
      diag+="; pivotHighCount="+(string)pivotHighCount;
      if(pivotHighCount>=3)
        {
         double zoneMin=MathMin(ph1,MathMin(ph2,ph3));
         double zoneMax=MathMax(ph1,MathMax(ph2,ph3));
         diag+="; recentPivotHigh1="+DoubleToString(ph1,g_digits)+
               "; recentPivotHigh1Time="+TimeToString(pht1,TIME_DATE|TIME_MINUTES)+
               "; recentPivotHigh2="+DoubleToString(ph2,g_digits)+
               "; recentPivotHigh2Time="+TimeToString(pht2,TIME_DATE|TIME_MINUTES)+
               "; recentPivotHigh3="+DoubleToString(ph3,g_digits)+
               "; recentPivotHigh3Time="+TimeToString(pht3,TIME_DATE|TIME_MINUTES)+
               "; recentPivotHighBandMin="+DoubleToString(zoneMin,g_digits)+
               "; recentPivotHighBandMax="+DoubleToString(zoneMax,g_digits)+
               "; recentPivotHighBandWidthATR="+DoubleToString((zoneMax-zoneMin)/atr,3)+
               "; clearsRecent3PivotHighs="+(bar.close>zoneMax ? "1" : "0");
        }
      diag+="; distanceToRangeHighATR="+DoubleToString((g_setup.rangeHigh-bar.close)/atr,3);
      LogEvent("SOS_STRENGTH_BAR_AUDIT",diag);
     }
   else
     {
      diag+="; pivotLowCount="+(string)pivotLowCount;
      if(pivotLowCount>=3)
        {
         double zoneMin=MathMin(pl1,MathMin(pl2,pl3));
         double zoneMax=MathMax(pl1,MathMax(pl2,pl3));
         diag+="; recentPivotLow1="+DoubleToString(pl1,g_digits)+
               "; recentPivotLow1Time="+TimeToString(plt1,TIME_DATE|TIME_MINUTES)+
               "; recentPivotLow2="+DoubleToString(pl2,g_digits)+
               "; recentPivotLow2Time="+TimeToString(plt2,TIME_DATE|TIME_MINUTES)+
               "; recentPivotLow3="+DoubleToString(pl3,g_digits)+
               "; recentPivotLow3Time="+TimeToString(plt3,TIME_DATE|TIME_MINUTES)+
               "; recentPivotLowBandMin="+DoubleToString(zoneMin,g_digits)+
               "; recentPivotLowBandMax="+DoubleToString(zoneMax,g_digits)+
               "; recentPivotLowBandWidthATR="+DoubleToString((zoneMax-zoneMin)/atr,3)+
               "; clearsRecent3PivotLows="+(bar.close<zoneMin ? "1" : "0");
        }
      diag+="; distanceToRangeLowATR="+DoubleToString((bar.close-g_setup.rangeLow)/atr,3);
      LogEvent("SOW_STRENGTH_BAR_AUDIT",diag);
     }
  }

//------------------------------ SOS / SOW ----------------------------
void ProcessWaitStrength(const MqlRates &rates[],const double atr)
  {
   int lookback=MathMax(2,InpStrengthSwingLookback);
   if(ArraySize(rates)<lookback+2) return;
   MqlRates bar=rates[0];
   // Strength must occur after the confirmed Test, using only closed bars.
   if(g_setup.testTime<=0 || bar.time<=g_setup.testTime)
      return;

   g_setup.barsSinceTest++;
   double elapsedHours=(double)(bar.time-g_setup.testTime)/3600.0;

   double bodyATR=MathAbs(bar.close-bar.open)/atr;
   double share=BodyShare(bar);
   double closePos=ClosePosition(bar);

   if(g_setup.direction==WYCKOFF_BUY)
     {
      double priorHigh=-DBL_MAX;
      for(int i=1;i<=lookback;i++) priorHigh=MathMax(priorHigh,rates[i].high);
      bool strong=(bar.close>bar.open && bodyATR>=InpSOSMinBodyATR &&
                   share>=InpSOSMinBodyShare && closePos>=InpSOSMinClosePosition);
      if(!strong) return;
      LogStrengthStructureAudit(true,rates,bar,atr,bodyATR,share,closePos);

      // A bullish SOS may break the range ceiling, but its reference swing
      // must not be below the range floor and the strength candle must have
      // reclaimed the range. This blocks inverted SOS records.
      if(priorHigh<g_setup.rangeLow || bar.close<=g_setup.rangeLow)
        {
         LogReject("REJECT_SOS_WRONG_SIDE_OF_RANGE",
                   "break="+DoubleToString(priorHigh,g_digits)+
                   "; close="+DoubleToString(bar.close,g_digits)+
                   "; rangeLow="+DoubleToString(g_setup.rangeLow,g_digits));
         ResetSetup("SOS_WRONG_SIDE_OF_RANGE");
         return;
        }
      if(bar.close>priorHigh)
        {
         g_setup.strengthBreakLevel=priorHigh;
         g_setup.strengthExtreme=bar.high;
         g_setup.strengthTime=bar.time;
         g_setup.barsSinceStrength=0;
         g_setup.stage=ST_WAIT_PULLBACK;
         DrawEvent("SOS",bar.time,bar.high,true);
         string sosClass=(bar.close>g_setup.rangeHigh ? "RANGE_EDGE_BREAK" : "INTERNAL_SWING_BREAK");
         double remainingToRangeEdgeATR=(g_setup.rangeHigh-bar.close)/atr;
         LogEvent("SOS_CONFIRMED","break="+DoubleToString(priorHigh,g_digits)+
                  "; bodyATR="+DoubleToString(bodyATR,2)+
                  "; structureClass="+sosClass+
                  "; close="+DoubleToString(bar.close,g_digits)+
                  "; rangeHigh="+DoubleToString(g_setup.rangeHigh,g_digits)+
                  "; remainingToRangeHighATR="+DoubleToString(remainingToRangeEdgeATR,3)+
                  "; barsAfterTest="+(string)g_setup.barsSinceTest+
                  "; elapsedHoursAfterTest="+DoubleToString(elapsedHours,1));
        }
     }
   else if(g_setup.direction==WYCKOFF_SELL)
     {
      double priorLow=DBL_MAX;
      for(int i=1;i<=lookback;i++) priorLow=MathMin(priorLow,rates[i].low);
      bool strong=(bar.close<bar.open && bodyATR>=InpSOWMinBodyATR &&
                   share>=InpSOWMinBodyShare && closePos<=InpSOWMaxClosePosition);
      if(!strong) return;
      LogStrengthStructureAudit(false,rates,bar,atr,bodyATR,share,closePos);

      // A bearish SOW may break the range floor, but its reference swing
      // must not be above the range ceiling and the candle must close below it.
      if(priorLow>g_setup.rangeHigh || bar.close>=g_setup.rangeHigh)
        {
         LogReject("REJECT_SOW_WRONG_SIDE_OF_RANGE",
                   "break="+DoubleToString(priorLow,g_digits)+
                   "; close="+DoubleToString(bar.close,g_digits)+
                   "; rangeHigh="+DoubleToString(g_setup.rangeHigh,g_digits));
         ResetSetup("SOW_WRONG_SIDE_OF_RANGE");
         return;
        }
      if(bar.close<priorLow)
        {
         g_setup.strengthBreakLevel=priorLow;
         g_setup.strengthExtreme=bar.low;
         g_setup.strengthTime=bar.time;
         g_setup.barsSinceStrength=0;
         g_setup.stage=ST_WAIT_PULLBACK;
         DrawEvent("SOW",bar.time,bar.low,false);
         string sowClass=(bar.close<g_setup.rangeLow ? "RANGE_EDGE_BREAK" : "INTERNAL_SWING_BREAK");
         double remainingToRangeEdgeATR=(bar.close-g_setup.rangeLow)/atr;
         LogEvent("SOW_CONFIRMED","break="+DoubleToString(priorLow,g_digits)+
                  "; bodyATR="+DoubleToString(bodyATR,2)+
                  "; structureClass="+sowClass+
                  "; close="+DoubleToString(bar.close,g_digits)+
                  "; rangeLow="+DoubleToString(g_setup.rangeLow,g_digits)+
                  "; remainingToRangeLowATR="+DoubleToString(remainingToRangeEdgeATR,3)+
                  "; barsAfterTest="+(string)g_setup.barsSinceTest+
                  "; elapsedHoursAfterTest="+DoubleToString(elapsedHours,1));
        }
     }
  }

//------------------------------ LPS / LPSY ---------------------------
string EntryPhaseName(const ENUM_ENTRY_PHASE phase)
  {
   switch(phase)
     {
      case ENTRY_PHASE_WAIT_BREAKOUT: return "WAIT_BREAKOUT";
      case ENTRY_PHASE_WAIT_RETEST: return "WAIT_RETEST";
      case ENTRY_PHASE_WAIT_REJECTION: return "WAIT_REJECTION";
      default: return "NONE";
     }
  }

// Causal timing fix: readyTime is the close time of the H1 bar that
// confirmed LPS/LPSY. Only M5 candles whose opening time is at or after
// this timestamp may be evaluated for the entry sequence.
void InitializeEntryWait(const datetime readyTime)
  {
   g_setup.stage=ST_WAIT_ENTRY;
   g_setup.entryReadyTime=readyTime;
   g_setup.entryPhase=ENTRY_PHASE_WAIT_BREAKOUT;
   g_setup.barsSinceEntryReady=0;
   g_setup.entryBarsChecked=0;
   g_setup.entryPhaseBarsChecked=0;
   g_setup.entryDirectionalBars=0;
   g_setup.entryBodyPassBars=0;
   g_setup.entryBreakPassBars=0;
   g_setup.entryRetestTouchBars=0;
   g_setup.entryRejectionBars=0;
   g_setup.entryBreakoutLevel=0.0;
   g_setup.entryBreakoutExtreme=0.0;
   g_setup.entryBreakoutTime=0;
   g_setup.entryRetestHigh=0.0;
   g_setup.entryRetestLow=0.0;
   g_setup.entryRetestExtreme=0.0;
   g_setup.entryRetestTime=0;
   g_setup.entryRetestBars=0;
   g_setup.entryLastClose=0.0;
   g_setup.entryLastBreakLevel=0.0;
   g_setup.entryLastBodyShare=0.0;
  }

void ProcessWaitPullback(const MqlRates &bar,const double atr)
  {
   g_setup.barsSinceStrength++;
   if(g_setup.barsSinceStrength>InpLPSExpiryBars)
     {
      ResetSetup("LPS_LPSY_EXPIRED");
      return;
     }
   if(g_setup.direction==WYCKOFF_BUY)
     {
      double pullback=(g_setup.strengthExtreme-bar.low)/atr;
      bool depthOK=(pullback>=InpLPSMinPullbackATR && pullback<=InpLPSMaxPullbackATR);
      bool holdsLevel=(bar.low>=g_setup.strengthBreakLevel-InpLPSInvalidationATR*atr &&
                       bar.close>=g_setup.strengthBreakLevel);
      if(depthOK && holdsLevel)
        {
         InitializeEntryWait(bar.time+(datetime)PeriodSeconds(InpSignalTF));
         DrawEvent("LPS",bar.time,bar.low,true);
         string lpsContext=(bar.close>g_setup.rangeHigh ? "ABOVE_RANGE_HIGH" : "INSIDE_RANGE");
         double remainingToRangeEdgeATR=(g_setup.rangeHigh-bar.close)/atr;
         LogEvent("LPS_CONFIRMED","pullbackATR="+DoubleToString(pullback,2)+
                  "; entryReadyTime="+TimeToString(g_setup.entryReadyTime,TIME_DATE|TIME_MINUTES)+
                  "; structureContext="+lpsContext+
                  "; rangeHigh="+DoubleToString(g_setup.rangeHigh,g_digits)+
                  "; remainingToRangeHighATR="+DoubleToString(remainingToRangeEdgeATR,3));
        }
      else if(bar.close<g_setup.strengthBreakLevel-InpLPSInvalidationATR*atr)
        {
         LogReject("REJECT_LPS_INVALIDATED");
         ResetSetup("LPS invalidated");
        }
     }
   else if(g_setup.direction==WYCKOFF_SELL)
     {
      double pullback=(bar.high-g_setup.strengthExtreme)/atr;
      bool depthOK=(pullback>=InpLPSMinPullbackATR && pullback<=InpLPSMaxPullbackATR);
      bool holdsLevel=(bar.high<=g_setup.strengthBreakLevel+InpLPSInvalidationATR*atr &&
                       bar.close<=g_setup.strengthBreakLevel);
      if(depthOK && holdsLevel)
        {
         InitializeEntryWait(bar.time+(datetime)PeriodSeconds(InpSignalTF));
         DrawEvent("LPSY",bar.time,bar.high,false);
         string lpsyContext=(bar.close<g_setup.rangeLow ? "BELOW_RANGE_LOW" : "INSIDE_RANGE");
         double remainingToRangeEdgeATR=(bar.close-g_setup.rangeLow)/atr;
         LogEvent("LPSY_CONFIRMED","pullbackATR="+DoubleToString(pullback,2)+
                  "; entryReadyTime="+TimeToString(g_setup.entryReadyTime,TIME_DATE|TIME_MINUTES)+
                  "; structureContext="+lpsyContext+
                  "; rangeLow="+DoubleToString(g_setup.rangeLow,g_digits)+
                  "; remainingToRangeLowATR="+DoubleToString(remainingToRangeEdgeATR,3));
        }
      else if(bar.close>g_setup.strengthBreakLevel+InpLPSInvalidationATR*atr)
        {
         LogReject("REJECT_LPSY_INVALIDATED");
         ResetSetup("LPSY invalidated");
        }
     }
  }

//------------------------------ Risk / order sizing ------------------
int VolumeDigits(const double step)
  {
   for(int d=0;d<=8;d++)
      if(MathAbs(step-NormalizeDouble(step,d))<1e-10)
         return d;
   return 2;
  }

bool CalculateRiskVolume(const ENUM_ORDER_TYPE orderType,const double entry,
                         const double stop,double &volume)
  {
   double equity=AccountInfoDouble(ACCOUNT_EQUITY);
   double riskMoney=equity*InpRiskPercent/100.0;
   if(riskMoney<=0.0) return false;
   double oneLotProfit=0.0;
   if(!OrderCalcProfit(orderType,g_symbol,1.0,entry,stop,oneLotProfit))
     {
      LogReject("REJECT_ORDER_CALC_PROFIT_FAILED",(string)GetLastError());
      return false;
     }
   double lossPerLot=MathAbs(oneLotProfit);
   if(lossPerLot<=0.0) return false;
   double rawVolume=riskMoney/lossPerLot;
   double minVol=SymbolInfoDouble(g_symbol,SYMBOL_VOLUME_MIN);
   double maxVol=SymbolInfoDouble(g_symbol,SYMBOL_VOLUME_MAX);
   double step=SymbolInfoDouble(g_symbol,SYMBOL_VOLUME_STEP);
   if(step<=0.0) return false;
   double normalized=MathFloor(rawVolume/step)*step;
   if(normalized>maxVol) normalized=maxVol;
   if(normalized<minVol)
     {
      LogReject("REJECT_VOLUME_BELOW_MIN", "raw="+DoubleToString(rawVolume,4)+
                "; min="+DoubleToString(minVol,4));
      return false;
     }
   volume=NormalizeDouble(normalized,(int)VolumeDigits(step));
   return true;
  }

bool FindM5Stop(const ENUM_WYCKOFF_DIRECTION dir,double &stop,double &atrM5)
  {
   if(!GetATR(g_atrEntryHandle,atrM5)) return false;
   int n=MathMax(3,InpStopLookbackM5);
   MqlRates rates[];
   if(!GetRates(InpEntryTF,1,n,rates)) return false;
   if(dir==WYCKOFF_BUY)
     {
      double low=DBL_MAX;
      for(int i=0;i<n;i++) low=MathMin(low,rates[i].low);
      stop=NormalizePrice(low-InpStopATRBuffer*atrM5);
     }
   else
     {
      double high=-DBL_MAX;
      for(int i=0;i<n;i++) high=MathMax(high,rates[i].high);
      stop=NormalizePrice(high+InpStopATRBuffer*atrM5);
     }
   return true;
  }

bool PlaceTrade(const ENUM_WYCKOFF_DIRECTION dir,const MqlRates &entryBar)
  {
   if(!SpreadIsAcceptable()) return false;
   MqlTick tick;
   if(!SymbolInfoTick(g_symbol,tick)) return false;
   double entry=(dir==WYCKOFF_BUY ? tick.ask : tick.bid);
   double stop=0.0,atrM5=0.0;
   if(!FindM5Stop(dir,stop,atrM5))
     {
      LogReject("REJECT_STOP_CALC_FAILED");
      return false;
     }
   double distance=(dir==WYCKOFF_BUY ? entry-stop : stop-entry);
   if(distance<=0.0 || distance>InpMaxStopATR*atrM5)
     {
      LogReject("REJECT_STOP_TOO_LARGE","stopATR="+DoubleToString(distance/atrM5,2));
      return false;
     }
   double target=(dir==WYCKOFF_BUY ? entry+InpRewardRisk*distance : entry-InpRewardRisk*distance);
   stop=NormalizePrice(stop);
   target=NormalizePrice(target);
   long stopsLevel=(long)SymbolInfoInteger(g_symbol,SYMBOL_TRADE_STOPS_LEVEL);
   double minBrokerDistance=(double)stopsLevel*g_point;
   if(distance<minBrokerDistance || MathAbs(target-entry)<minBrokerDistance)
     {
      LogReject("REJECT_BROKER_STOPS_LEVEL", "minimumDistance="+DoubleToString(minBrokerDistance,g_digits));
      return false;
     }
   double volume=0.0;
   ENUM_ORDER_TYPE type=(dir==WYCKOFF_BUY ? ORDER_TYPE_BUY : ORDER_TYPE_SELL);
   if(!CalculateRiskVolume(type,entry,stop,volume)) return false;

   trade.SetExpertMagicNumber(InpMagicNumber);
   trade.SetDeviationInPoints(InpDeviationPoints);
   if(!trade.SetTypeFillingBySymbol(g_symbol))
     {
      LogReject("REJECT_FILLING_MODE_UNAVAILABLE");
      return false;
     }
   double plannedLoss=0.0;
   if(!OrderCalcProfit(type,g_symbol,volume,entry,stop,plannedLoss) || MathAbs(plannedLoss)<=0.0)
     {
      LogReject("REJECT_PLANNED_RISK_CALC_FAILED",(string)GetLastError());
      return false;
     }
   // Use the actual risk of the rounded lot size, not the requested risk budget,
   // so the realized R multiple remains consistent with the executed volume.
   g_plannedRiskMoney=MathAbs(plannedLoss);
   g_activeRiskMoney=0.0;
   g_pendingStopPrice=stop;
   g_pendingTargetPrice=target;
   g_pendingRequestPrice=entry;
   g_activeDirection=dir;
   g_pendingOrderVolume=volume;
   g_pendingSpreadPoints=(tick.ask-tick.bid)/g_point;
   g_actualEntryVolume=0.0;
   g_weightedSlippagePoints=0.0;
   g_weightedExitSlippagePoints=0.0;
   g_actualExitVolume=0.0;
   g_activePositionId=0;
   bool sent=false;
   if(dir==WYCKOFF_BUY)
      sent=trade.Buy(volume,g_symbol,0.0,stop,target,"Wyckoff W0 BUY");
   else
      sent=trade.Sell(volume,g_symbol,0.0,stop,target,"Wyckoff W0 SELL");

   uint retcode=trade.ResultRetcode();
   bool accepted=(retcode==TRADE_RETCODE_DONE ||
                  retcode==TRADE_RETCODE_DONE_PARTIAL ||
                  retcode==TRADE_RETCODE_PLACED);
   if(!sent || !accepted)
     {
      g_activeRiskMoney=0.0;
      g_plannedRiskMoney=0.0;
      g_pendingStopPrice=0.0;
      g_pendingTargetPrice=0.0;
      g_pendingRequestPrice=0.0;
      g_pendingOrderVolume=0.0;
      g_pendingSpreadPoints=0.0;
      g_actualEntryVolume=0.0;
      g_weightedSlippagePoints=0.0;
      g_weightedExitSlippagePoints=0.0;
      g_actualExitVolume=0.0;
      g_activeDirection=WYCKOFF_NONE;
      g_activePositionId=0;
      LogReject("ORDER_SEND_FAILED",trade.ResultRetcodeDescription()+
                "; retcode="+(string)retcode);
      return false;
     }
   LogEvent("ORDER_OPENED","volume="+DoubleToString(volume,2)+
            "; entry="+DoubleToString(entry,g_digits)+
            "; SL="+DoubleToString(stop,g_digits)+
            "; TP="+DoubleToString(target,g_digits)+
            "; plannedRiskMoney="+DoubleToString(g_plannedRiskMoney,2)+
            "; quoteSpreadPoints="+DoubleToString(g_pendingSpreadPoints,1)+
            "; RR="+DoubleToString(InpRewardRisk,2));
   if(InpDrawEntrySignals)
      DrawEvent(dir==WYCKOFF_BUY ? "BUY_ENTRY" : "SELL_ENTRY",entryBar.time,entry,dir==WYCKOFF_BUY);
   if(InpDrawStopTarget)
     {
      string slName="W0_SL_"+(string)g_setupCounter+"_"+(string)entryBar.time;
      string tpName="W0_TP_"+(string)g_setupCounter+"_"+(string)entryBar.time;
      ObjectCreate(0,slName,OBJ_HLINE,0,0,stop);
      ObjectSetInteger(0,slName,OBJPROP_COLOR,clrTomato);
      ObjectCreate(0,tpName,OBJ_HLINE,0,0,target);
      ObjectSetInteger(0,tpName,OBJPROP_COLOR,clrLimeGreen);
     }
   g_setup.stage=ST_IN_POSITION;
   return true;
  }

//------------------------------ M5 entry -----------------------------
void LogEntryPhaseExpiryAndReset(const string eventName,const int phaseLimit)
  {
   string diag="phase="+EntryPhaseName(g_setup.entryPhase)+
               "; phaseChecked="+(string)g_setup.entryPhaseBarsChecked+
               "; phaseLimit="+(string)phaseLimit+
               "; totalChecked="+(string)g_setup.entryBarsChecked+
               "; directionalBars="+(string)g_setup.entryDirectionalBars+
               "; bodyPassBars="+(string)g_setup.entryBodyPassBars+
               "; breakoutPassBars="+(string)g_setup.entryBreakPassBars+
               "; retestTouches="+(string)g_setup.entryRetestTouchBars+
               "; retestBars="+(string)g_setup.entryRetestBars+
               "; recoveryBars="+(string)g_setup.entryRejectionBars+
               "; breakoutLevel="+DoubleToString(g_setup.entryBreakoutLevel,g_digits)+
               "; breakoutTime="+TimeToString(g_setup.entryBreakoutTime,TIME_DATE|TIME_MINUTES)+
               "; retestTime="+TimeToString(g_setup.entryRetestTime,TIME_DATE|TIME_MINUTES)+
               "; lastClose="+DoubleToString(g_setup.entryLastClose,g_digits)+
               "; lastLevel="+DoubleToString(g_setup.entryLastBreakLevel,g_digits)+
               "; lastBodyShare="+DoubleToString(g_setup.entryLastBodyShare,3);
   LogEvent(eventName,diag);
   ResetSetup(eventName);
  }

void ProcessEntryBar()
  {
   if(g_setup.stage!=ST_WAIT_ENTRY) return;

   // One fully closed M5 candle is evaluated per new M5 bar.
   int lookback=MathMax(1,InpEntryBreakLookback);
   MqlRates rates[];
   if(!GetRates(InpEntryTF,1,lookback+1,rates)) return;

   double atrEntry=0.0;
   if(!GetATR(g_atrEntryHandle,atrEntry) || atrEntry<=0.0) return;

   MqlRates bar=rates[0];

   // Causal timing guard:
   // The H1 LPS/LPSY candle is known to be closed only at entryReadyTime.
   // Reject an M5 candle that opened before that instant. In particular,
   // the M5 candle ending exactly at the H1 boundary must not be used as
   // an entry candle because it formed while the H1 setup was unconfirmed.
   // Do this before evaluating signals or incrementing any phase counters.
   if(g_setup.entryReadyTime>0 && bar.time<g_setup.entryReadyTime)
     {
      if(InpLogEntryEvaluation)
         LogEvent("M5_ENTRY_SKIPPED_PRE_READY",
                  "barOpen="+TimeToString(bar.time,TIME_DATE|TIME_MINUTES)+
                  "; readyTime="+TimeToString(g_setup.entryReadyTime,TIME_DATE|TIME_MINUTES));
      return;
     }

   double share=BodyShare(bar);
   bool directionPass=false;
   bool bodyPass=(share>=InpMinConfirmBodyShare);
   bool breakoutPass=false;
   bool retestTouch=false;
   bool rejectionPass=false;
   double level=0.0;
   double distanceToLevelPoints=0.0;
   double distanceToLevelATR=0.0;
   double tolerance=InpEntryRetestToleranceATR*atrEntry;
   bool sequenceComplete=false;

   g_setup.entryBarsChecked++;
   g_setup.barsSinceEntryReady=g_setup.entryBarsChecked;
   g_setup.entryPhaseBarsChecked++;
   g_setup.entryLastClose=bar.close;
   g_setup.entryLastBodyShare=share;

   // Do not accept a later entry once price has closed outside the original
   // Wyckoff trading range on the adverse side.
   if(g_setup.direction==WYCKOFF_BUY && bar.close<=g_setup.rangeLow)
     {
      LogReject("REJECT_ENTRY_OUTSIDE_RANGE","BUY close="+DoubleToString(bar.close,g_digits)+
                "; rangeLow="+DoubleToString(g_setup.rangeLow,g_digits));
      ResetSetup("ENTRY_INVALIDATED_BELOW_RANGE_LOW");
      return;
     }
   if(g_setup.direction==WYCKOFF_SELL && bar.close>=g_setup.rangeHigh)
     {
      LogReject("REJECT_ENTRY_OUTSIDE_RANGE","SELL close="+DoubleToString(bar.close,g_digits)+
                "; rangeHigh="+DoubleToString(g_setup.rangeHigh,g_digits));
      ResetSetup("ENTRY_INVALIDATED_ABOVE_RANGE_HIGH");
      return;
     }

   if(g_setup.direction==WYCKOFF_BUY)
     {
      directionPass=(bar.close>bar.open);
      if(directionPass) g_setup.entryDirectionalBars++;
      if(bodyPass) g_setup.entryBodyPassBars++;

      if(g_setup.entryPhase==ENTRY_PHASE_WAIT_BREAKOUT)
        {
         double priorHigh=-DBL_MAX;
         for(int i=1;i<=lookback;i++) priorHigh=MathMax(priorHigh,rates[i].high);
         level=priorHigh;
         g_setup.entryLastBreakLevel=level;
         distanceToLevelPoints=(bar.close-level)/g_point;
         distanceToLevelATR=(bar.close-level)/atrEntry;
         breakoutPass=(directionPass && bodyPass && bar.close>level);
         if(breakoutPass)
           {
            g_setup.entryBreakPassBars++;
            g_setup.entryBreakoutLevel=level;
            g_setup.entryBreakoutExtreme=bar.high;
            g_setup.entryBreakoutTime=bar.time;
            g_setup.entryRetestBars=0;
            g_setup.entryPhase=ENTRY_PHASE_WAIT_RETEST;
            g_setup.entryPhaseBarsChecked=0;
            DrawEvent("M5_BREAKOUT",bar.time,bar.high,true);
            LogEvent("M5_BREAKOUT_CONFIRMED","level="+DoubleToString(level,g_digits)+
                     "; close="+DoubleToString(bar.close,g_digits)+
                     "; distanceATR="+DoubleToString(distanceToLevelATR,3)+
                     "; bodyShare="+DoubleToString(share,3));
           }
        }
      else if(g_setup.entryPhase==ENTRY_PHASE_WAIT_RETEST)
        {
         level=g_setup.entryBreakoutLevel;
         g_setup.entryRetestBars++;
         distanceToLevelPoints=(bar.low-level)/g_point;
         distanceToLevelATR=(bar.low-level)/atrEntry;
         // A BUY retest may close a little below the breakout level, but
         // the entire retest candle must remain inside the ATR tolerance.
         // The next candle must reclaim both the level and retest high.
         bool lostLevel=(bar.low<level-tolerance || bar.close<level-tolerance);
         retestTouch=(bar.low<=level+tolerance && bar.low>=level-tolerance &&
                      bar.close>=level-tolerance);
         if(lostLevel)
           {
            LogReject("REJECT_M5_BREAKOUT_RETEST_FAILED","BUY low="+DoubleToString(bar.low,g_digits)+
                      "; close="+DoubleToString(bar.close,g_digits)+
                      "; breakoutLevel="+DoubleToString(level,g_digits)+
                      "; penetrationATR="+DoubleToString((level-bar.low)/atrEntry,3)+
                      "; toleranceATR="+DoubleToString(InpEntryRetestToleranceATR,2));
            ResetSetup("M5_BREAKOUT_LEVEL_LOST_BEFORE_RETEST");
            return;
           }
         if(retestTouch)
           {
            g_setup.entryRetestTouchBars++;
            g_setup.entryRetestHigh=bar.high;
            g_setup.entryRetestLow=bar.low;
            g_setup.entryRetestExtreme=bar.low;
            g_setup.entryRetestTime=bar.time;
            g_setup.entryPhase=ENTRY_PHASE_WAIT_REJECTION;
            g_setup.entryPhaseBarsChecked=0;
            DrawEvent("M5_RETEST",bar.time,bar.low,true);
            LogEvent("M5_RETEST_CONFIRMED","breakoutLevel="+DoubleToString(level,g_digits)+
                     "; retestLow="+DoubleToString(bar.low,g_digits)+
                     "; retestClose="+DoubleToString(bar.close,g_digits)+
                     "; retestDepthATR="+DoubleToString((level-bar.low)/atrEntry,3));
           }
        }
      else if(g_setup.entryPhase==ENTRY_PHASE_WAIT_REJECTION)
        {
         level=g_setup.entryBreakoutLevel;
         distanceToLevelPoints=(bar.close-level)/g_point;
         distanceToLevelATR=(bar.close-level)/atrEntry;
         g_setup.entryRejectionBars++;
         if(bar.low<level-tolerance || bar.close<level-tolerance)
           {
            LogReject("REJECT_M5_RETEST_SUPPORT_LOST","BUY low="+DoubleToString(bar.low,g_digits)+
                      "; close="+DoubleToString(bar.close,g_digits)+
                      "; breakoutLevel="+DoubleToString(level,g_digits)+
                      "; penetrationATR="+DoubleToString((level-bar.low)/atrEntry,3)+
                      "; toleranceATR="+DoubleToString(InpEntryRetestToleranceATR,2));
            ResetSetup("M5_RETEST_SUPPORT_LOST");
            return;
           }
         // Recovery is confirmed by a directional body closing back above
         // the broken resistance. Clearing the entire retest candle high is
         // deliberately NOT required; that is a separate, stricter condition.
         rejectionPass=(directionPass && bodyPass && bar.time>g_setup.entryRetestTime &&
                        bar.close>level);
         if(rejectionPass)
           {
            LogEvent("M5_BUY_RECOVERY_CONFIRMED","close="+DoubleToString(bar.close,g_digits)+
                     "; breakoutLevel="+DoubleToString(level,g_digits)+
                     "; retestHigh="+DoubleToString(g_setup.entryRetestHigh,g_digits)+
                     "; clearedRetestHigh="+(bar.close>g_setup.entryRetestHigh ? "1" : "0")+
                     "; bodyShare="+DoubleToString(share,3));
            sequenceComplete=PlaceTrade(WYCKOFF_BUY,bar);
           }
        }
     }
   else if(g_setup.direction==WYCKOFF_SELL)
     {
      directionPass=(bar.close<bar.open);
      if(directionPass) g_setup.entryDirectionalBars++;
      if(bodyPass) g_setup.entryBodyPassBars++;

      if(g_setup.entryPhase==ENTRY_PHASE_WAIT_BREAKOUT)
        {
         double priorLow=DBL_MAX;
         for(int i=1;i<=lookback;i++) priorLow=MathMin(priorLow,rates[i].low);
         level=priorLow;
         g_setup.entryLastBreakLevel=level;
         distanceToLevelPoints=(level-bar.close)/g_point;
         distanceToLevelATR=(level-bar.close)/atrEntry;
         breakoutPass=(directionPass && bodyPass && bar.close<level);
         if(breakoutPass)
           {
            g_setup.entryBreakPassBars++;
            g_setup.entryBreakoutLevel=level;
            g_setup.entryBreakoutExtreme=bar.low;
            g_setup.entryBreakoutTime=bar.time;
            g_setup.entryRetestBars=0;
            g_setup.entryPhase=ENTRY_PHASE_WAIT_RETEST;
            g_setup.entryPhaseBarsChecked=0;
            DrawEvent("M5_BREAKOUT",bar.time,bar.low,false);
            LogEvent("M5_BREAKOUT_CONFIRMED","level="+DoubleToString(level,g_digits)+
                     "; close="+DoubleToString(bar.close,g_digits)+
                     "; distanceATR="+DoubleToString(distanceToLevelATR,3)+
                     "; bodyShare="+DoubleToString(share,3));
           }
        }
      else if(g_setup.entryPhase==ENTRY_PHASE_WAIT_RETEST)
        {
         level=g_setup.entryBreakoutLevel;
         g_setup.entryRetestBars++;
         distanceToLevelPoints=(level-bar.high)/g_point;
         distanceToLevelATR=(level-bar.high)/atrEntry;
         // SELL mirror: allow a small close above the broken support, but
         // reject a move beyond the ATR tolerance. Confirmation must reclaim
         // the level and retest low in the bearish direction.
         bool lostLevel=(bar.high>level+tolerance || bar.close>level+tolerance);
         retestTouch=(bar.high>=level-tolerance && bar.high<=level+tolerance &&
                      bar.close<=level+tolerance);
         if(lostLevel)
           {
            LogReject("REJECT_M5_BREAKOUT_RETEST_FAILED","SELL high="+DoubleToString(bar.high,g_digits)+
                      "; close="+DoubleToString(bar.close,g_digits)+
                      "; breakoutLevel="+DoubleToString(level,g_digits)+
                      "; penetrationATR="+DoubleToString((bar.high-level)/atrEntry,3)+
                      "; toleranceATR="+DoubleToString(InpEntryRetestToleranceATR,2));
            ResetSetup("M5_BREAKOUT_LEVEL_LOST_BEFORE_RETEST");
            return;
           }
         if(retestTouch)
           {
            g_setup.entryRetestTouchBars++;
            g_setup.entryRetestHigh=bar.high;
            g_setup.entryRetestLow=bar.low;
            g_setup.entryRetestExtreme=bar.high;
            g_setup.entryRetestTime=bar.time;
            g_setup.entryPhase=ENTRY_PHASE_WAIT_REJECTION;
            g_setup.entryPhaseBarsChecked=0;
            DrawEvent("M5_RETEST",bar.time,bar.high,false);
            LogEvent("M5_RETEST_CONFIRMED","breakoutLevel="+DoubleToString(level,g_digits)+
                     "; retestHigh="+DoubleToString(bar.high,g_digits)+
                     "; retestClose="+DoubleToString(bar.close,g_digits)+
                     "; retestDepthATR="+DoubleToString((bar.high-level)/atrEntry,3));
           }
        }
      else if(g_setup.entryPhase==ENTRY_PHASE_WAIT_REJECTION)
        {
         level=g_setup.entryBreakoutLevel;
         distanceToLevelPoints=(level-bar.close)/g_point;
         distanceToLevelATR=(level-bar.close)/atrEntry;
         g_setup.entryRejectionBars++;
         if(bar.high>level+tolerance || bar.close>level+tolerance)
           {
            LogReject("REJECT_M5_RETEST_RESISTANCE_LOST","SELL high="+DoubleToString(bar.high,g_digits)+
                      "; close="+DoubleToString(bar.close,g_digits)+
                      "; breakoutLevel="+DoubleToString(level,g_digits)+
                      "; penetrationATR="+DoubleToString((bar.high-level)/atrEntry,3)+
                      "; toleranceATR="+DoubleToString(InpEntryRetestToleranceATR,2));
            ResetSetup("M5_RETEST_RESISTANCE_LOST");
            return;
           }
         // Recovery is confirmed by a directional body closing back below
         // the broken support. Clearing the entire retest candle low is
         // deliberately NOT required; that is a separate, stricter condition.
         rejectionPass=(directionPass && bodyPass && bar.time>g_setup.entryRetestTime &&
                        bar.close<level);
         if(rejectionPass)
           {
            LogEvent("M5_SELL_RECOVERY_CONFIRMED","close="+DoubleToString(bar.close,g_digits)+
                     "; breakoutLevel="+DoubleToString(level,g_digits)+
                     "; retestLow="+DoubleToString(g_setup.entryRetestLow,g_digits)+
                     "; clearedRetestLow="+(bar.close<g_setup.entryRetestLow ? "1" : "0")+
                     "; bodyShare="+DoubleToString(share,3));
            sequenceComplete=PlaceTrade(WYCKOFF_SELL,bar);
           }
        }
     }

   if(InpLogEntryEvaluation)
     {
      string eval="bar="+TimeToString(bar.time,TIME_DATE|TIME_MINUTES)+
                  "; phase="+EntryPhaseName(g_setup.entryPhase)+
                  "; checked="+(string)g_setup.entryBarsChecked+
                  "; phaseChecked="+(string)g_setup.entryPhaseBarsChecked+
                  "; O="+DoubleToString(bar.open,g_digits)+
                  "; H="+DoubleToString(bar.high,g_digits)+
                  "; L="+DoubleToString(bar.low,g_digits)+
                  "; C="+DoubleToString(bar.close,g_digits)+
                  "; level="+DoubleToString(level,g_digits)+
                  "; directionPass="+(directionPass ? "1" : "0")+
                  "; bodyPass="+(bodyPass ? "1" : "0")+
                  "; breakoutPass="+(breakoutPass ? "1" : "0")+
                  "; retestTouch="+(retestTouch ? "1" : "0")+
                  "; rejectionPass="+(rejectionPass ? "1" : "0")+
                  "; bodyShare="+DoubleToString(share,3)+
                  "; distanceToLevelPoints="+DoubleToString(distanceToLevelPoints,1)+
                  "; distanceToLevelATR="+DoubleToString(distanceToLevelATR,3)+
                  "; retestToleranceATR="+DoubleToString(InpEntryRetestToleranceATR,2);
      LogEvent("M5_ENTRY_EVALUATION",eval);
     }

   if(sequenceComplete) return;
   if(g_setup.stage==ST_WAIT_ENTRY)
     {
      // The confirmation candle completes the current phase. The next phase
      // starts counting on the next fully closed M5 candle.
      if(g_setup.entryPhase==ENTRY_PHASE_WAIT_BREAKOUT &&
         g_setup.entryPhaseBarsChecked>=InpBreakoutExpiryBars)
         LogEntryPhaseExpiryAndReset("BREAKOUT_PHASE_EXPIRED",InpBreakoutExpiryBars);
      else if(g_setup.entryPhase==ENTRY_PHASE_WAIT_RETEST &&
              g_setup.entryPhaseBarsChecked>=InpRetestExpiryBars)
         LogEntryPhaseExpiryAndReset("RETEST_PHASE_EXPIRED",InpRetestExpiryBars);
      else if(g_setup.entryPhase==ENTRY_PHASE_WAIT_REJECTION &&
              g_setup.entryPhaseBarsChecked>=InpRecoveryExpiryBars)
         LogEntryPhaseExpiryAndReset("RECOVERY_PHASE_EXPIRED",InpRecoveryExpiryBars);
     }
  }

//------------------------------ H1 state machine ---------------------
void ProcessSignalBar()
  {
   if(HasOurPosition())
     {
      g_setup.stage=ST_IN_POSITION;
      return;
     }
   if(g_setup.stage==ST_IN_POSITION)
     {
      ResetSetup("POSITION_CLOSED");
      return;
     }
   double atr=0.0;
   if(!GetATR(g_atrSignalHandle,atr)) return;
   int need=MathMax(InpStrengthSwingLookback+2,4);
   if(g_setup.stage==ST_WAIT_STRENGTH)
      need=MathMax(need,MathMax(42,InpRangeLookbackBars+2));
   MqlRates rates[];
   if(!GetRates(InpSignalTF,1,need,rates)) return;
   MqlRates bar=rates[0];

   if(g_setup.stage==ST_IDLE)
     {
      // Do not lose a Spring/UTAD that appears on the first candle after
      // the range window. DetectRange uses bars from shift 2 onward; process
      // the latest closed candle (shift 1) immediately against those levels.
      if(DetectRange())
         ProcessWaitEvent(bar,atr);
      return;
     }

   g_setup.rangeAge++;
   if(g_setup.rangeAge>InpRangeMaxAgeBars)
     {
      if(g_setup.stage==ST_WAIT_STRENGTH && g_setup.testTime>0)
         LogEvent("H1_STRENGTH_NOT_FOUND_BEFORE_RANGE_EXPIRY",
                  "barsAfterTest="+(string)g_setup.barsSinceTest+
                  "; elapsedHoursAfterTest="+DoubleToString((double)(TimeCurrent()-g_setup.testTime)/3600.0,1));
      ResetSetup("RANGE_EXPIRED");
      return;
     }

   switch(g_setup.stage)
     {
      case ST_WAIT_EVENT:
         ProcessWaitEvent(bar,atr);
         break;
      case ST_WAIT_TEST:
         ProcessWaitTest(bar,atr);
         break;
      case ST_WAIT_STRENGTH:
         ProcessWaitStrength(rates,atr);
         break;
      case ST_WAIT_PULLBACK:
         ProcessWaitPullback(bar,atr);
         break;
      case ST_WAIT_ENTRY:
         // Entry trigger is evaluated only on a newly closed M5 candle.
         break;
      default:
         break;
     }
  }

//------------------------------ MT5 events ---------------------------
int OnInit()
  {
   if(InpRiskPercent<=0.0 || InpRewardRisk<=0.0 || InpRangeLookbackBars<InpRangeMinBars ||
      InpRangeMinBars<10 || InpRangeMaxBars<InpRangeMinBars || InpRangeATRPeriod<2 ||
      InpM5ATRPeriod<2 || InpEntryBreakLookback<1 || InpStopLookbackM5<2 ||
      InpStrengthSwingLookback<2 || InpBreakoutExpiryBars<1 ||
      InpRetestExpiryBars<1 || InpRecoveryExpiryBars<1 ||
      InpMaxSpreadPoints<=0.0 || InpMaxStopATR<=0.0 ||
      InpEntryRetestToleranceATR<=0.0 || InpEntryRetestToleranceATR>2.0)
     {
      Print("[Wyckoff W0] Invalid input parameters. Check risk, range, ATR and entry settings.");
      return INIT_PARAMETERS_INCORRECT;
     }
   g_symbol=(InpTradeSymbol=="" ? _Symbol : InpTradeSymbol);
   g_initialBalance=AccountInfoDouble(ACCOUNT_BALANCE);
   if(!SymbolSelect(g_symbol,true))
     {
      Print("[Wyckoff W0] Cannot select symbol: ",g_symbol);
      return INIT_FAILED;
     }
   g_digits=(int)SymbolInfoInteger(g_symbol,SYMBOL_DIGITS);
   g_point=SymbolInfoDouble(g_symbol,SYMBOL_POINT);
   if(g_digits<0 || g_point<=0.0)
     {
      Print("[Wyckoff W0] Invalid symbol properties for ",g_symbol);
      return INIT_FAILED;
     }
   g_atrSignalHandle=iATR(g_symbol,InpSignalTF,InpRangeATRPeriod);
   g_atrEntryHandle=iATR(g_symbol,InpEntryTF,InpM5ATRPeriod);
   if(InpUseH4ContextFilter)
      g_emaStructureHandle=iMA(g_symbol,InpStructureTF,InpH4EMAPeriod,0,MODE_EMA,PRICE_CLOSE);
   if(g_atrSignalHandle==INVALID_HANDLE || g_atrEntryHandle==INVALID_HANDLE ||
      (InpUseH4ContextFilter && g_emaStructureHandle==INVALID_HANDLE))
     {
      Print("[Wyckoff W0] Failed to create indicator handle. Error=",GetLastError());
      return INIT_FAILED;
     }
   trade.SetExpertMagicNumber(InpMagicNumber);
   trade.SetDeviationInPoints(InpDeviationPoints);
   g_csvFileName=EffectiveCSVFileName();
   if(InpExportCSV && (bool)MQLInfoInteger(MQL_OPTIMIZATION))
     {
      // FILE_COMMON is shared by optimization agents; do not let concurrent passes
      // overwrite or interleave each other's event streams.
      Print("[Wyckoff W0] CSV export is disabled during Optimization. Run a single test to create the CSV.");
     }
   else if(InpExportCSV)
     {
      // Store the CSV in the common terminal Files directory. Start each single test
      // with a fresh file so previous runs cannot be appended accidentally.
      string commonFilesPath=TerminalInfoString(TERMINAL_COMMONDATA_PATH)+"\\Files\\"+g_csvFileName;
      bool canStartCSV=true;
      if(FileIsExist(g_csvFileName,FILE_COMMON))
        {
         ResetLastError();
         if(!FileDelete(g_csvFileName,FILE_COMMON))
           {
            Print("[Wyckoff W0] CSV start aborted: previous file could not be removed. Error=",GetLastError(),
                  "; close any program that may have the CSV open: ",commonFilesPath);
            canStartCSV=false;
           }
        }
      if(canStartCSV)
        {
         ResetLastError();
         g_csvHandle=FileOpen(g_csvFileName,
                              FILE_READ|FILE_WRITE|FILE_CSV|FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_ANSI|FILE_COMMON,',');
         if(g_csvHandle==INVALID_HANDLE)
            Print("[Wyckoff W0] CSV open failed. Error=",GetLastError(),"; expected path: ",commonFilesPath);
         else
           {
            FileWrite(g_csvHandle,"ServerTime","EA_Version","Symbol","InitialBalance",
                      "SetupID","Direction","Event","Details","RangeHigh","RangeLow","PositionID");
            FileFlush(g_csvHandle);
            Print("[Wyckoff W0] CSV logging enabled (fresh file). File: ",commonFilesPath);
           }
        }
     }
   g_lastSignalBar=iTime(g_symbol,InpSignalTF,0);
   g_lastEntryBar=iTime(g_symbol,InpEntryTF,0);
   ResetSetup("");
   if(InpExportCSV && g_csvHandle!=INVALID_HANDLE)
      LogEvent("EA_INIT","CSV logging started; initialBalance="+DoubleToString(g_initialBalance,2)+
                "; accountCurrency="+AccountInfoString(ACCOUNT_CURRENCY)+
                "; minVolume="+DoubleToString(SymbolInfoDouble(g_symbol,SYMBOL_VOLUME_MIN),2)+
                "; volumeStep="+DoubleToString(SymbolInfoDouble(g_symbol,SYMBOL_VOLUME_STEP),2));
   DebugPrint("v1.08-C2 timing initialized on "+g_symbol+"; StopATRBuffer="+DoubleToString(InpStopATRBuffer,2)+
              "; RetestToleranceATR="+DoubleToString(InpEntryRetestToleranceATR,2)+"; SignalTF="+EnumToString(InpSignalTF)+
              "; EntryTF="+EnumToString(InpEntryTF)+
              "; Risk="+DoubleToString(InpRiskPercent,2)+"%; RR="+DoubleToString(InpRewardRisk,2));
   return INIT_SUCCEEDED;
  }

string DealReasonName(const long reason)
  {
   switch((ENUM_DEAL_REASON)reason)
     {
      case DEAL_REASON_SL: return "SL";
      case DEAL_REASON_TP: return "TP";
      case DEAL_REASON_SO: return "STOP_OUT";
      case DEAL_REASON_EXPERT: return "EXPERT";
      case DEAL_REASON_CLIENT: return "CLIENT";
      case DEAL_REASON_MOBILE: return "MOBILE";
      case DEAL_REASON_WEB: return "WEB";
      case DEAL_REASON_ROLLOVER: return "ROLLOVER";
      case DEAL_REASON_VMARGIN: return "VARIATION_MARGIN";
      case DEAL_REASON_SPLIT: return "SPLIT";
      default: return "OTHER";
     }
  }

void OnTradeTransaction(const MqlTradeTransaction &trans,
                        const MqlTradeRequest &request,
                        const MqlTradeResult &result)
  {
   if(trans.type!=TRADE_TRANSACTION_DEAL_ADD || trans.deal==0)
      return;
   if(!HistoryDealSelect(trans.deal))
      return;

   string dealSymbol=HistoryDealGetString(trans.deal,DEAL_SYMBOL);
   long dealMagic=HistoryDealGetInteger(trans.deal,DEAL_MAGIC);
   if(dealSymbol!=g_symbol || (ulong)dealMagic!=InpMagicNumber)
      return;

   long entryType=HistoryDealGetInteger(trans.deal,DEAL_ENTRY);
   long positionId=HistoryDealGetInteger(trans.deal,DEAL_POSITION_ID);
   double dealPrice=HistoryDealGetDouble(trans.deal,DEAL_PRICE);
   double dealVolume=HistoryDealGetDouble(trans.deal,DEAL_VOLUME);
   long dealReason=HistoryDealGetInteger(trans.deal,DEAL_REASON);
   long dealType=HistoryDealGetInteger(trans.deal,DEAL_TYPE);

   if(entryType==DEAL_ENTRY_IN)
     {
      g_activePositionId=(ulong)positionId;
      double stopPrice=g_pendingStopPrice;
      if(PositionSelect(g_symbol) &&
         (ulong)PositionGetInteger(POSITION_MAGIC)==InpMagicNumber)
        {
         double positionSL=PositionGetDouble(POSITION_SL);
         if(positionSL>0.0) stopPrice=positionSL;
        }
      ENUM_ORDER_TYPE orderType=(dealType==DEAL_TYPE_BUY ? ORDER_TYPE_BUY : ORDER_TYPE_SELL);
      double fillRisk=0.0;
      bool riskOK=(stopPrice>0.0 &&
                   OrderCalcProfit(orderType,g_symbol,dealVolume,dealPrice,stopPrice,fillRisk));
      if(riskOK)
         g_activeRiskMoney+=MathAbs(fillRisk);
      else if(g_pendingOrderVolume>0.0)
         g_activeRiskMoney+=g_plannedRiskMoney*(dealVolume/g_pendingOrderVolume);

      double slipPoints=0.0;
      if(g_point>0.0)
        {
         if(dealType==DEAL_TYPE_BUY)
            slipPoints=(dealPrice-g_pendingRequestPrice)/g_point;
         else if(dealType==DEAL_TYPE_SELL)
            slipPoints=(g_pendingRequestPrice-dealPrice)/g_point;
        }
      g_weightedSlippagePoints+=slipPoints*dealVolume;
      g_actualEntryVolume+=dealVolume;

      LogEvent("TRADE_ENTRY_DEAL","positionID="+(string)positionId+
               "; actualPrice="+DoubleToString(dealPrice,g_digits)+
               "; volume="+DoubleToString(dealVolume,2)+
               "; stopPrice="+DoubleToString(stopPrice,g_digits)+
               "; actualRiskMoney="+DoubleToString(g_activeRiskMoney,2)+
               "; riskCalc="+(riskOK ? "FILL_TO_SL" : "PLANNED_FALLBACK")+
               "; quoteSpreadPoints="+DoubleToString(g_pendingSpreadPoints,1)+
               "; slippagePoints="+DoubleToString(slipPoints,1));
      return;
     }

   if(entryType==DEAL_ENTRY_OUT || entryType==DEAL_ENTRY_OUT_BY || entryType==DEAL_ENTRY_INOUT)
     {
      double grossProfit=0.0;
      double totalSwap=0.0;
      double totalCommission=0.0;
      double totalFee=0.0;
      if(HistorySelectByPosition((ulong)positionId))
        {
         int total=HistoryDealsTotal();
         for(int i=0;i<total;i++)
           {
            ulong ticket=HistoryDealGetTicket(i);
            if(ticket==0) continue;
            if(HistoryDealGetInteger(ticket,DEAL_POSITION_ID)!=positionId) continue;
            grossProfit+=HistoryDealGetDouble(ticket,DEAL_PROFIT);
            totalSwap+=HistoryDealGetDouble(ticket,DEAL_SWAP);
            totalCommission+=HistoryDealGetDouble(ticket,DEAL_COMMISSION);
            totalFee+=HistoryDealGetDouble(ticket,DEAL_FEE);
           }
        }
      double totalCosts=totalSwap+totalCommission+totalFee;
      double netProfit=grossProfit+totalCosts;
      bool stillOpen=HasOurPosition();
      double realizedR=(g_activeRiskMoney>0.0 ? netProfit/g_activeRiskMoney : 0.0);
      double avgEntrySlippage=(g_actualEntryVolume>0.0 ?
                               g_weightedSlippagePoints/g_actualEntryVolume : 0.0);
      double exitReferencePrice=0.0;
      double exitSlippagePoints=0.0;
      string exitSlippageBasis="UNAVAILABLE";
      if(dealReason==DEAL_REASON_SL && g_pendingStopPrice>0.0)
        {
         exitReferencePrice=g_pendingStopPrice;
         exitSlippageBasis="SL";
        }
      else if(dealReason==DEAL_REASON_TP && g_pendingTargetPrice>0.0)
        {
         exitReferencePrice=g_pendingTargetPrice;
         exitSlippageBasis="TP";
        }
      if(exitReferencePrice>0.0 && g_point>0.0)
        {
         // Positive = adverse execution relative to the stored stop/target.
         if(g_activeDirection==WYCKOFF_BUY)
            exitSlippagePoints=(exitReferencePrice-dealPrice)/g_point;
         else if(g_activeDirection==WYCKOFF_SELL)
            exitSlippagePoints=(dealPrice-exitReferencePrice)/g_point;
         g_weightedExitSlippagePoints+=exitSlippagePoints*dealVolume;
         g_actualExitVolume+=dealVolume;
        }
      double avgExitSlippage=(g_actualExitVolume>0.0 ?
                              g_weightedExitSlippagePoints/g_actualExitVolume : 0.0);
      string eventName=(stillOpen ? "TRADE_PARTIAL_EXIT" : "TRADE_CLOSED");
      LogEvent(eventName,"positionID="+(string)positionId+
               "; exitDealPrice="+DoubleToString(dealPrice,g_digits)+
               "; exitReferencePrice="+DoubleToString(exitReferencePrice,g_digits)+
               "; exitSlippageBasis="+exitSlippageBasis+
               "; exitSlippagePoints="+(exitSlippageBasis=="UNAVAILABLE" ? "NA" : DoubleToString(exitSlippagePoints,1))+
               "; avgExitSlippagePoints="+(g_actualExitVolume>0.0 ? DoubleToString(avgExitSlippage,1) : "NA")+
               "; exitDealVolume="+DoubleToString(dealVolume,2)+
               "; grossProfit="+DoubleToString(grossProfit,2)+
               "; swap="+DoubleToString(totalSwap,2)+
               "; commission="+DoubleToString(totalCommission,2)+
               "; fee="+DoubleToString(totalFee,2)+
               "; totalCosts="+DoubleToString(totalCosts,2)+
               "; netProfit="+DoubleToString(netProfit,2)+
               "; actualInitialRiskMoney="+DoubleToString(g_activeRiskMoney,2)+
               "; realizedR="+DoubleToString(realizedR,3)+
               "; quoteSpreadPoints="+DoubleToString(g_pendingSpreadPoints,1)+
               "; avgEntrySlippagePoints="+DoubleToString(avgEntrySlippage,1)+
               "; reason="+DealReasonName(dealReason));
      if(!stillOpen)
        {
         g_activePositionId=0;
         g_activeRiskMoney=0.0;
         g_plannedRiskMoney=0.0;
         g_pendingStopPrice=0.0;
         g_pendingTargetPrice=0.0;
         g_pendingRequestPrice=0.0;
         g_pendingOrderVolume=0.0;
         g_pendingSpreadPoints=0.0;
         g_actualEntryVolume=0.0;
         g_weightedSlippagePoints=0.0;
         g_weightedExitSlippagePoints=0.0;
         g_actualExitVolume=0.0;
         g_activeDirection=WYCKOFF_NONE;
        }
     }
  }

void OnDeinit(const int reason)
  {
   if(g_atrSignalHandle!=INVALID_HANDLE) IndicatorRelease(g_atrSignalHandle);
   if(g_atrEntryHandle!=INVALID_HANDLE) IndicatorRelease(g_atrEntryHandle);
   if(g_emaStructureHandle!=INVALID_HANDLE) IndicatorRelease(g_emaStructureHandle);
   if(g_csvHandle!=INVALID_HANDLE)
     {
      FileFlush(g_csvHandle);
      FileClose(g_csvHandle);
      g_csvHandle=INVALID_HANDLE;
     }
   DebugPrint("Deinitialized. Reason="+(string)reason);
  }

void OnTick()
  {
   if(HasOurPosition())
     {
      g_setup.stage=ST_IN_POSITION;
      return;
     }
   if(IsNewBar(InpSignalTF,g_lastSignalBar))
      ProcessSignalBar();
   if(IsNewBar(InpEntryTF,g_lastEntryBar))
      ProcessEntryBar();
  }
//+------------------------------------------------------------------+