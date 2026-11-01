//+------------------------------------------------------------------+
//|                                      Wyckoff_XAUUSD_W0_v1_05.mq5 |
//| Rule-based Wyckoff prototype for MT5                             |
//| W0 v1.05: exact entry-expiry accounting, M5 trigger telemetry, |
//| actual-fill risk and transaction-cost reconciliation             |
//| NOTE: Research prototype. Validate visually and in Strategy      |
//| Tester before any demo/live use. No profitability is implied.     |
//+------------------------------------------------------------------+
#property strict
#property version   "1.05"
#property description "Rule-based Wyckoff W0 prototype for XAUUSD"

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
input double          InpRewardRisk               = 2.00;
input ulong           InpMagicNumber             = 31102026;
input int             InpDeviationPoints         = 20;
input double          InpMaxSpreadPoints         = 80.0;
input double          InpMaxStopATR              = 4.0;
input int             InpStopLookbackM5           = 12;
input double          InpStopATRBuffer            = 0.20;

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
input int             InpEntryExpiryBars         = 12;
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
sinput bool           InpLogEntryEvaluation     = true;
sinput string          InpCSVFileName             = "Wyckoff_W0_events_v1_05.csv";

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
   int                    barsSinceStrength;
   int                    barsSinceEntryReady;
   int                    entryBarsChecked;
   int                    entryDirectionalBars;
   int                    entryBodyPassBars;
   int                    entryBreakPassBars;
   double                 entryLastClose;
   double                 entryLastBreakLevel;
   double                 entryLastBodyShare;
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
 double   g_plannedRiskMoney = 0.0;     // Pre-trade estimate (fallback only)
 double   g_pendingStopPrice = 0.0;
 double   g_pendingRequestPrice = 0.0;
 double   g_pendingOrderVolume = 0.0;
 double   g_pendingSpreadPoints = 0.0;
 double   g_actualEntryVolume = 0.0;
 double   g_weightedSlippagePoints = 0.0;
 string   g_csvFileName = "";
 ulong    g_activePositionId = 0;
long     g_setupCounter = 0;
SWyckoffSetup g_setup;

#define EA_VERSION "1.05"

//------------------------------ Utilities ----------------------------
string EffectiveCSVFileName()
  {
   string file=InpCSVFileName;
   int length=StringLen(file);
   if(length>4 && StringSubstr(file,length-4)==".csv")
      file=StringSubstr(file,0,length-4);
   return file+"_E"+(string)InpEntryExpiryBars+".csv";
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
   g_setup.barsSinceStrength=0;
   g_setup.barsSinceEntryReady=0;
   g_setup.entryBarsChecked=0;
   g_setup.entryDirectionalBars=0;
   g_setup.entryBodyPassBars=0;
   g_setup.entryBreakPassBars=0;
   g_setup.entryLastClose=0.0;
   g_setup.entryLastBreakLevel=0.0;
   g_setup.entryLastBodyShare=0.0;
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
   // Build the range from the 80 (or configured) closed bars at shifts 2..N+1.
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
         g_setup.stage=ST_WAIT_STRENGTH;
         DrawEvent("TEST",bar.time,bar.low,true);
         LogEvent("TEST_CONFIRMED","low="+DoubleToString(bar.low,g_digits));
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
         g_setup.stage=ST_WAIT_STRENGTH;
         DrawEvent("TEST",bar.time,bar.high,false);
         LogEvent("TEST_CONFIRMED","high="+DoubleToString(bar.high,g_digits));
        }
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

      // A bullish SOS may break the range ceiling, but its reference swing
      // must not be below the range floor and the strength candle must have
      // reclaimed the range. This blocks the inverted SOS records observed
      // in v1.03 (break levels below RangeLow).
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
         LogEvent("SOS_CONFIRMED","break="+DoubleToString(priorHigh,g_digits)+
                  "; bodyATR="+DoubleToString(bodyATR,2));
        }
     }
   else if(g_setup.direction==WYCKOFF_SELL)
     {
      double priorLow=DBL_MAX;
      for(int i=1;i<=lookback;i++) priorLow=MathMin(priorLow,rates[i].low);
      bool strong=(bar.close<bar.open && bodyATR>=InpSOWMinBodyATR &&
                   share>=InpSOWMinBodyShare && closePos<=InpSOWMaxClosePosition);
      if(!strong) return;

      // A bearish SOW may break the range floor, but its reference swing
      // must not be above the range ceiling and the candle must close back
      // below the range ceiling. This rejects inverted SOW levels in v1.03.
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
         LogEvent("SOW_CONFIRMED","break="+DoubleToString(priorLow,g_digits)+
                  "; bodyATR="+DoubleToString(bodyATR,2));
        }
     }
  }

//------------------------------ LPS / LPSY ---------------------------
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
         g_setup.stage=ST_WAIT_ENTRY;
         g_setup.barsSinceEntryReady=0;
         g_setup.entryBarsChecked=0;
         g_setup.entryDirectionalBars=0;
         g_setup.entryBodyPassBars=0;
         g_setup.entryBreakPassBars=0;
         g_setup.entryLastClose=0.0;
         g_setup.entryLastBreakLevel=0.0;
         g_setup.entryLastBodyShare=0.0;
         DrawEvent("LPS",bar.time,bar.low,true);
         LogEvent("LPS_CONFIRMED","pullbackATR="+DoubleToString(pullback,2));
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
         g_setup.stage=ST_WAIT_ENTRY;
         g_setup.barsSinceEntryReady=0;
         g_setup.entryBarsChecked=0;
         g_setup.entryDirectionalBars=0;
         g_setup.entryBodyPassBars=0;
         g_setup.entryBreakPassBars=0;
         g_setup.entryLastClose=0.0;
         g_setup.entryLastBreakLevel=0.0;
         g_setup.entryLastBodyShare=0.0;
         DrawEvent("LPSY",bar.time,bar.high,false);
         LogEvent("LPSY_CONFIRMED","pullbackATR="+DoubleToString(pullback,2));
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
   g_pendingRequestPrice=entry;
   g_pendingOrderVolume=volume;
   g_pendingSpreadPoints=(tick.ask-tick.bid)/g_point;
   g_actualEntryVolume=0.0;
   g_weightedSlippagePoints=0.0;
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
      g_pendingRequestPrice=0.0;
      g_pendingOrderVolume=0.0;
      g_pendingSpreadPoints=0.0;
      g_actualEntryVolume=0.0;
      g_weightedSlippagePoints=0.0;
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
void LogEntryExpiryAndReset()
  {
   string diag="checked="+(string)g_setup.entryBarsChecked+
               "; directionalBars="+(string)g_setup.entryDirectionalBars+
               "; bodyPassBars="+(string)g_setup.entryBodyPassBars+
               "; breakPassBars="+(string)g_setup.entryBreakPassBars+
               "; lastClose="+DoubleToString(g_setup.entryLastClose,g_digits)+
               "; lastBreakLevel="+DoubleToString(g_setup.entryLastBreakLevel,g_digits)+
               "; lastBodyShare="+DoubleToString(g_setup.entryLastBodyShare,3);
   LogEvent("ENTRY_TRIGGER_EXPIRED",diag);
   ResetSetup("ENTRY_TRIGGER_EXPIRED");
  }

void ProcessEntryBar()
  {
   if(g_setup.stage!=ST_WAIT_ENTRY) return;

   // Count only bars that were actually copied and evaluated. A transient
   // CopyRates failure must not consume the setup's expiry allowance.
   int count=MathMax(3,InpEntryBreakLookback)+2;
   MqlRates rates[];
   if(!GetRates(InpEntryTF,1,count,rates)) return;
   MqlRates bar=rates[0];
   double share=BodyShare(bar);
   g_setup.entryBarsChecked++;
   g_setup.barsSinceEntryReady=g_setup.entryBarsChecked;
   g_setup.entryLastClose=bar.close;
   g_setup.entryLastBodyShare=share;

   // Invalidate any entry trigger that has closed back outside the original
   // trading range in the wrong direction.
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

   double atrEntry=0.0;
   GetATR(g_atrEntryHandle,atrEntry);