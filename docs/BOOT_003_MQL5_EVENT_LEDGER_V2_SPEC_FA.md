# مشخصات Instrumentation نسخه Event Ledger v2 برای W0

نسخه سند: 1.0-draft  
وضعیت: **طراحی و بازبینی سورس؛ هنوز در MQL5 پیاده‌سازی/کامپایل/تست نشده است.**  
محدوده: شاخه جدا از C2 و MultiAudit؛ هیچ منطق معاملاتی نباید تغییر کند.

## 1. هدف

CSV فعلی برای Event Funnel مناسب است، اما برای ML قابل استفاده مستقیم نیست. این مشخصات، شناسه‌های مستقل، زمان‌های قابل‌ردیابی، و اتصال رویداد تا سفارش/Deal را برای نسخه instrumentation بعدی تعریف می‌کند.

اصول:
- C2 baseline و MultiAudit فعلی دست‌نخورده بمانند.
- نسخه جدید در branch جدا و با شناسه EA/schema جدید ساخته شود.
- instrumentation نباید شرط تشخیص Range، Spring/UTAD، Test، SOS/SOW، LPS/LPSY، M5 breakout/retest/recovery، SL/TP یا order sizing را عوض کند.
- هیچ شناسه یا زمان گمشده‌ای به‌صورت حدسی ساخته نشود.
- قبل از آموزش ML، Event Ledger و Candidate Ledger به‌صورت جدا تولید شوند.

## 2. یافته‌های مستقیم از سورس C2

منبع: `src/Wyckoff_XAUUSD_W0_v1_08_C2_T030_SB050.mq5`.

| مکان | رفتار موجود | پیامد برای instrumentation |
|---|---|---|
| حدود خط 235 | LogEvent، g_setupCounter را در CSV به‌عنوان SetupID می‌نویسد | SetupID شناسه legacy است، نه Candidate |
| خط 483 | g_setupCounter هنگام یافتن Range افزایش می‌یابد | Range ID قابل نگاشت از شمارنده قدیمی است |
| خط 496 | بلافاصله بعد از شمارنده، RANGE_FOUND ثبت می‌شود | شناسه Range باید در همین lifecycle تثبیت شود |
| ProcessWaitTest | Test بعد از عبور شروط، state را به ST_WAIT_STRENGTH می‌برد | Test event باید به همان Range/Cycle متصل شود |
| ProcessWaitStrength | SOS/SOW از priorHigh/priorLow و Lookback فعال استفاده می‌کند | Strength event باید Lookback و rule version را ثبت کند |
| ProcessEntryBar | یک کندل بسته‌شده M5 در هر bar جدید ارزیابی می‌شود | چند M5_ENTRY_EVALUATION ممکن است یک فرصت را توصیف کنند |
| M5 recovery branch | بعد از تأیید Recovery، PlaceTrade فراخوانی می‌شود | Candidate ID باید قبل از PlaceTrade ساخته شود |
| PlaceTrade | Spread، tick، stop، حجم، filling و ارسال سفارش بررسی می‌شوند | تمام ردهای اجرایی پس از Candidate creation باید به همان Candidate متصل شوند |
| OnTradeTransaction | DEAL_POSITION_ID و Deal ticket قابل دریافت‌اند | اتصال Candidate → Order → Deal/Position ممکن است |

## 3. تعریف دقیق شناسه‌ها

شناسه‌ها برای یک Run مستقل و یکپارچه تعریف شوند:

### run_id
شناسه اجرای Tester/Replay. به‌صورت input پژوهشی اجباری تعریف شود تا هر اجرای مجدد حتی با همان تاریخ و SET شناسه جدا داشته باشد. شناسه run باید در manifest و تمام CSVها یکسان باشد.

پیشنهاد: یک مقدار دستی و یکتا برای هر Run، مثلاً `W0-LEDGER-20261104-A01`. نام EA یا تاریخ به‌تنهایی کافی نیست.

### range_id
هنگام RANGE_FOUND ساخته شود:
`{run_id}:R{range_sequence}`

legacy SetupID فعلی به‌عنوان `legacy_setup_id` نگهداری شود؛ از آن فقط در migration عقب‌رو می‌توان یک Range ID سازگار ساخت.

### cycle_id
برای یک مسیر ساختاری Wyckoff زیر یک Range. در اولین Spring/UTAD candidate معتبر که ماشین حالت چرخه را آغاز می‌کند ساخته شود:
`{range_id}:C{cycle_sequence}`

اگر چرخه هیچ‌وقت وارد فاز ساختاری نشود، Range event باقی می‌ماند ولی cycle_id می‌تواند خالی بماند. اگر semantics چرخه در مسیر state machine هنوز مبهم باشد، آن را خالی نگه دارید؛ شناسه صوری نسازید.

### attempt_id
برای هر تلاش مستقل Spring یا UTAD ساخته شود:
`{cycle_id}:A{attempt_sequence}`

Candidateهای ناموفق و تلاش‌های مجدد باید attempt_id جدا داشته باشند. رویدادهای confirm/test/strength/LPS مربوط به همان مسیر، attempt_id جاری را حمل کنند.

### candidate_id
برای هر کندل Recovery که شرط ورود M5 را تکمیل می‌کند، دقیقاً یک Candidate مستقل ساخته شود:
`{run_id}:{range_sequence}:{cycle_sequence}:{attempt_sequence}:E{entry_sequence}`

نقطه ساخت ID: در شاخه BUY پس از LogEvent مربوط به M5_BUY_RECOVERY_CONFIRMED و درست پیش از فراخوانی PlaceTrade؛ در شاخه SELL در نقطه قرینه پس از M5_SELL_RECOVERY_CONFIRMED و پیش از PlaceTrade.

این کار تضمین می‌کند Candidate قبل از بررسی Spread، tick، stop، حجم، filling و OrderSend موجود باشد. پس حتی اگر معامله‌ای باز نشود، Candidate و rejection reason باقی می‌مانند.

اگر در کندل بعدی Recovery دوباره تأیید شود و PlaceTrade قبلی fail شده باشد، این یک entry trigger جدید است و candidate_id جدید می‌گیرد؛ در عین حال cycle_id و attempt_id ساختاری می‌توانند ثابت بمانند.

### decision_id
برای هر ارزیابی مجزای تصمیم/فیلتر زیر Candidate ساخته شود؛ هر decision باید نوع، زمان و نتیجه خودش را داشته باشد:
`{candidate_id}:D{decision_sequence}`

### order_id / deal_id / trade_id
- order_id از ticket واقعی سفارش پذیرفته‌شده گرفته شود.
- deal_id از trans.deal در OnTradeTransaction ثبت شود.
- position_id از DEAL_POSITION_ID ثبت شود.
- trade_id داخلی فقط وقتی ساخته شود که تعریف trade lifecycle و اتصال partial fills/exit deals روشن باشد؛ می‌توان در نسخه اول position_id را جدا نگه داشت و trade_id را null گذاشت.
- هرگز PositionID legacy را بدون Join به‌عنوان trade_id قطعی معرفی نکن.

## 4. Candidate universe برای W2 نسخه اول

نقطه تصمیم مدل W2 برابر M5_ENTRY است: نخستین کندل Recovery که قواعد W0 را پاس می‌کند و موتور آماده فراخوانی PlaceTrade است.

**یک candidate_id برای هر recovery trigger مستقل**، نه برای هر M5_ENTRY_EVALUATION.

رفتارهای زیر باید Candidate داشته باشند:
- Recovery معتبر شد و سفارش اجرا شد.
- Recovery معتبر شد، ولی Spread زیاد بود.
- Recovery معتبر شد، اما SymbolInfoTick موجود نبود.
- محاسبه stop شکست خورد یا حد ضرر بیش از MaxStopATR بود.
- حجم کمتر از حداقل بروکر شد.
- filling mode در دسترس نبود.
- محاسبه planned risk شکست خورد.
- OrderSend رد شد یا retcode پذیرفته نشد.
- Order پذیرفته شد ولی بعداً partial fill یا خروج رخ داد.

رویدادهای M5 قبل از Recovery مانند breakout/retest، eventهای مسیر هستند و به range/cycle/attempt متصل می‌شوند، اما candidate_id نهایی M5_ENTRY هنوز ندارند. برای آن‌ها یک M5 path ID اختیاری می‌توان تعریف کرد؛ نباید با candidate_id اشتباه شود.

## 5. تفسیر M5_ENTRY_EVALUATION موجود

در سورس فعلی، ProcessEntryBar هر M5 bar بسته‌شده را ارزیابی می‌کند و ممکن است M5_ENTRY_EVALUATION ثبت کند. این رخداد:
- می‌تواند چندین بار در یک entry path ثبت شود.
- لزوماً یک Recovery trigger یا ارسال سفارش نیست.
- ممکن است یک کندل pre-ready را اصلاً ارزیابی نکند.
- در مسیر موفق، به‌دلیل return پس از sequenceComplete ممکن است آخرین evaluation log اصلاً نوشته نشود.

بنابراین 57 رخداد M5_ENTRY_EVALUATION در CSV قدیمی برابر 57 Candidate مستقل نیست. در v2 باید event_id برای هر evaluation و candidate_id فقط برای trigger معتبر ساخته شود.

## 6. قرارداد زمان

زمان‌های موجود باید با basis مشخص ذخیره شوند:
- `event_time_server`: زمان واقعی ثبت/وقوع رویداد طبق قواعد همان event.
- `source_bar_open_server`: مقدار MqlRates.time برای کندل منبع.
- `observed_at_server`: زمان TimeCurrent وقتی EA کندل بسته‌شده را پردازش می‌کند.
- `decision_time_server`: زمان ارزیابی/تصمیم.
- `time_basis`: ثابت `BROKER_SERVER_RAW` تا وقتی timezone/offset با داده معتبر مشخص شود.

از تبدیل خودکار به UTC خودداری شود. زمان پایان bar به شکل اسمی از PeriodSeconds محاسبه نشود و به‌عنوان close قطعی معرفی نشود؛ observation time واقعی ثبت شود. برای هر رخداد، source timeframe و source bar time ثبت شود.

## 7. CSV schema نسخه 2

Header پیشنهادی:

```text
SchemaVersion,RunID,EventID,EventSequence,EventTimeServer,ObservedAtServer,TimeBasis,SourceTimeframe,SourceBarOpenServer,Symbol,EA_Version,RangeID,CycleID,AttemptID,CandidateID,DecisionID,OrderID,DealID,PositionID,LegacySetupID,Direction,Event,DecisionStatus,ReasonCode,Details,RangeHigh,RangeLow,InitialBalance
```

قواعد:
- هر ردیف event یک event_id یکتا و event_sequence ترتیبی دارد.
- فیلدهای شناسه‌ای که هنوز ساخته نشده‌اند خالی‌اند، نه صفر یا رشته جعلی.
- Details فقط توضیح انسانی است؛ فیلدهای اصلی باید ستون مستقل داشته باشند.
- CSV schema version در هر ردیف و manifest ثبت شود.
- schema جدید در فایل جدا ذخیره شود؛ روی CSV legacy append نشود.
- تمام eventهای رد، انقضا، ابطال، order failure، partial fill و close log شوند.

## 8. ترتیب implementation پیشنهادی

1. ساخت branch مجزا، مثلاً `feature/w0-event-ledger-v2`.
2. افزودن input پژوهشی RunID و version/schema metadata.
3. افزودن counters و فیلدهای range/cycle/attempt/candidate/decision.
4. ایجاد توابع LogEventV2 و LogCandidateDecision که ستون‌های ساختاری را جدا بنویسند.
5. ثبت source timeframe/bar time در call siteهای H1 و M5.
6. ایجاد Candidate درست پیش از PlaceTrade، نه بعد از موفقیت سفارش.
7. پیوند order/deal/position در OnTradeTransaction.
8. افزودن replay tests برای یک Range با دو attempt، یک candidate ردشده به‌علت spread، یک order failed و یک معامله با partial fill.
9. اثبات با diff که predicateهای معاملاتی تغییر نکرده‌اند.
10. MetaEditor Compile، سپس یک Replay کوتاه و بعد Tester محدود؛ تنها پس از Audit به تست کامل بروید.

## 9. تست‌های پذیرش instrumentation

- یک Range چند event دارد اما range_id ثابت است.
- دو attempt در یک Range attempt_id متفاوت دارند.
- یک attempt chain واحد cycle_id و attempt_id ثابت را حفظ می‌کند.
- چند M5_ENTRY_EVALUATION یک candidate_id نمی‌سازند.
- هر Recovery trigger یک candidate_id تازه می‌سازد.
- Spread rejection پیش از order ارسال، Candidate را حذف نمی‌کند.
- order/deal/position به Candidate درست پیوند می‌خورند.
- event_idها در RunID یکسان یکتا و تکرارپذیرند.
- تمام times به‌عنوان broker server raw ثبت می‌شوند؛ UTC یا source close ساختگی ندارند.
- event log قدیمی و schema v2 از هم جدا باقی می‌مانند.
- رفتار معاملات در مقایسه replay با baseline تغییر نکرده است.

## 10. محدودیت و Gate

این سند فقط مشخصات است. در وضعیت فعلی:
- سورس C2، H1STRUCT و MultiAudit تغییر نکرده‌اند.
- هیچ instrumented MQ5 جدیدی کامپایل نشده است.
- هیچ Candidate ML واقعی از Event CSV قدیمی ساخته نشده است.
- W1/W2/W3 همچنان تا تکمیل Data/Label/Validation قفل هستند.

BOOT-003 می‌تواند بخش Event migration را با artifact موجود PASS کند، اما Event/Candidate Ledger کامل فقط پس از implementation، Compile، Replay و Audit مستقل COMPLETE خواهد شد.
