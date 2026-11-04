# BOOT-003 — پیاده‌سازی اولیه Event/Candidate Ledger v2

**شاخه:** `feature/w0-event-ledger-v2`  
**منبع baseline:** `src/Wyckoff_XAUUSD_W0_v1_08_C2_T030_SB050.mq5`  
**خروجی جدید:** `src/Wyckoff_XAUUSD_W0_v1_08_C2_T030_SB050_LEDGER_V2.mq5`  
**نسخهٔ EA در CSV:** `1.083-C2-TIMING-SB050-T030-LEDGER-V2`  
**وضعیت:** سورس Instrumented و تست ایستای CI افزوده شده؛ MetaEditor Compile، Strategy Tester و Replay هنوز اجرا نشده‌اند.

## 1. تضمین عدم تغییر استراتژی

این شاخه از `main` در نقطهٔ C2 ایجاد شده و فایل پایه بدون تغییر باقی مانده است. فایل v2 یک کپی مستقل از C2 است. تغییرات این نسخه به این حوزه‌ها محدود شده‌اند:

- ایجاد Event/Candidate IDها و خروجی CSV نسخهٔ ۲؛
- افزودن زمینهٔ زمان/تایم‌فریم به رویدادهای H1 و M5؛
- ثبت نتیجهٔ فیلترها و شناسه‌های سفارش/Deal/Position؛
- ثبت rejection reasonها حتی در صورت خاموش‌بودن لاگ Reject قدیمی.

هیچ آستانهٔ معاملاتی، شرط Spring/UTAD، Test، SOS/SOW، LPS/LPSY، M5 Breakout/Retest/Recovery، Stop، Target یا فرمول حجم در این کپی عمداً تغییر داده نشده است. تست ایستا حضور شرط‌های اصلی C2 را کنترل می‌کند؛ این هنوز جایگزین diff معنایی کامل یا آزمون رفتار در MT5 نیست.

## 2. قرارداد شناسه‌ها

| شناسه | زمان ساخت | قاعده |
|---|---|---|
| RunID | شروع هر اجرای Tester/Replay | ورودی دستی یکتا؛ ۸ تا ۶۴ نویسه، فقط حروف/عدد/خط تیره/زیرخط |
| RangeID | پس از یافتن Range | `RunID:Rn` |
| CycleID | اولین Spring/UTAD معتبر در Range | `RangeID:Cn` |
| AttemptID | هر تلاش مستقل Spring یا UTAD معتبر | `CycleID:An` |
| CandidateID | پس از Recovery Confirmed و پیش از PlaceTrade | `RunID:Rn:Cn:An:En` |
| DecisionID | هر تصمیم اجرایی رد/پذیرش مرتبط با Candidate | `CandidateID:Dn` |
| EventID | هر سطر CSV v2 | `RunID:EVn` |

`LegacySetupID` همان شمارندهٔ قدیمی Range/Setup است و صرفاً برای migration و Join نگه داشته می‌شود؛ هرگز CandidateID محسوب نمی‌شود. `M5_ENTRY_EVALUATION` فقط یک Event است و Candidate ایجاد نمی‌کند. دو Recovery trigger مستقل حتی در یک Attempt، CandidateID مجزا می‌گیرند.

## 3. زمان و CSV

فایل جدید با نامی مستقل از CSV قدیمی ساخته می‌شود:

`Wyckoff_W0_event_ledger_v2_<RunID>.csv`

فایل در مسیر Common Files ترمینال MT5 ذخیره می‌شود. پیش از دست‌زدن به CSV قدیمی، EA اول Optimization و سپس تکراری‌بودن نام فایل v2 را کنترل می‌کند. اگر نام فایل از قبل وجود داشته باشد، Init متوقف می‌شود تا فایل قدیمی یا دادهٔ آن Run overwrite/delete نشود. اجرای Optimization نیز عمداً متوقف می‌شود؛ برای این نسخه فقط Single Tester Run مجاز است، چون FILE_COMMON بین Optimization Agentها مشترک است.

ستون‌های v2 دقیقاً ۲۸ فیلد دارند و با ترتیب زیر نوشته می‌شوند:

`SchemaVersion, RunID, EventID, EventSequence, EventTimeServer, ObservedAtServer, TimeBasis, SourceTimeframe, SourceBarOpenServer, Symbol, EA_Version, RangeID, CycleID, AttemptID, CandidateID, DecisionID, OrderID, DealID, PositionID, LegacySetupID, Direction, Event, DecisionStatus, ReasonCode, Details, RangeHigh, RangeLow, InitialBalance`

شناسه‌هایی که هنوز ساخته نشده‌اند (از جمله OrderID/DealID/PositionID یا LegacySetupID قبل از Range) خالی نوشته می‌شوند، نه `0` یا رشتهٔ ساختگی. برای Eventهای H1/M5، `SourceBarOpenServer` از `MqlRates.time` همان کندل می‌آید؛ `EventTimeServer` زمان واقعی ثبت رویداد در سمت بروکر را می‌گیرد و `ObservedAtServer` زمان مشاهده/پردازش EA از `TimeCurrent()` است. در رویدادهای مربوط به Deal، `EventTimeServer` از `DEAL_TIME` خوانده می‌شود تا زمان اجرای Deal از زمان رسیدن callback جدا بماند. هیچ زمان پایان کندل به‌صورت مصنوعی ساخته یا UTC حدس زده نمی‌شود. `TimeBasis` ثابت `BROKER_SERVER_RAW` است. برای رخدادهای معاملاتی که bar source ندارند، ستون‌های Source خالی می‌مانند.

## 4. Candidate و Execution funnel

Candidate دقیقاً در دو محل ساخته می‌شود: پس از `M5_BUY_RECOVERY_CONFIRMED` یا `M5_SELL_RECOVERY_CONFIRMED` و پیش از `PlaceTrade()`. در نتیجه Candidate پیش از Spread، Tick، Stop، Volume، Filling و OrderSend وجود دارد.

Rejectهای ساختاریافته شامل موارد زیرند: Spread بالا/دریافت‌نشدن Tick، محاسبه یا فاصلهٔ Stop، حداقل فاصلهٔ Stop بروکر، بودجهٔ ریسک، زیان هر لات، گام/حداقل حجم، Filling Mode، محاسبهٔ ریسک برنامه‌ریزی‌شده و شکست OrderSend. DecisionID فقط وقتی ساخته می‌شود که Candidate موجود باشد و Event نتیجهٔ رد یا پذیرش اجرایی داشته باشد.

پس از سفارش، `OrderID` از ResultOrder/transaction order، `DealID` از `trans.deal` و `PositionID` از `DEAL_POSITION_ID` ثبت می‌شوند. برای اینکه خروج SL/TP به Candidate اشتباه متصل نشود، نسخهٔ فعلی یک جدول link در حافظه نگه می‌دارد: ابتدا OrderID به Candidate متصل می‌شود؛ پس از اولین Deal ورود، PositionID نیز به همان Candidate وصل می‌شود. اگر order تیکت Deal خروج با order ورود متفاوت باشد، نگاشت PositionID و در صورت نیاز History position برای بازیابی order ورود استفاده می‌شود. هر تراکنش غیرقابل‌اتصال با رویداد `LEDGER_UNLINKED_TRADE_TRANSACTION` علامت می‌خورد و اعتبارسنج CSV آن را خطای سخت می‌داند. چند Deal برای یک Candidate (از جمله partial fill و خروج جزئی) می‌توانند تکرار شوند؛ PositionID با trade_id یکی فرض نمی‌شود.

## 5. راه اجرای MT5

1. فایل `..._LEDGER_V2.mq5` را در MetaEditor باز و Compile کنید؛ خطا و Warning را ذخیره کنید.
2. در Strategy Tester، یک RunID جدید مانند `WM20261104A001` تنظیم کنید. مقدار پیش‌فرض `UNASSIGNED` عمداً باعث توقف Init می‌شود.
3. ابتدا یک بازهٔ کوتاه single-run با همان Symbol، Timeframe، تاریخ و تنظیمات مرجع C2 اجرا کنید.
4. هر دو فایل CSV (legacy و v2) را Export کنید و manifest شامل RunID، SHA-256 سورس/EX5/SET، بازه و تنظیمات را ثبت کنید.
5. سطرهای `CANDIDATE_CREATED` را با Recovery eventها تطبیق دهید؛ برای Candidateهای ردشده باید DecisionID و ReasonCode حاضر باشد.
6. برای سفارش‌های پذیرفته‌شده، OrderID → DealID → PositionID و partial fill/close را با History/OnTradeTransaction تطبیق دهید.
7. سپس Replay A/B انجام شود: C2 پایه در برابر C2+Ledger v2 با داده، تنظیمات و مدل اجرای یکسان. تعداد/زمان/جهت سیگنال‌ها و سفارش‌ها باید برابر باشند.

## 6. اعتبارسنج مستقل خروجی CSV

اسکریپت `research/event_ledger_v2_validator.py` فایل خروجی MT5 را با schema دقیق ۲۸ ستونی کنترل می‌کند: عرض واقعی هر ردیف، یکتایی و پیوستگی EventSequence/EventID، ترتیب ساخت Candidate بلافاصله بعد از Recovery هم‌جهت، تو در تو بودن Range/Cycle/Attempt/Candidate/Decision ID، تعداد دقیق یک `CANDIDATE_CREATED` برای هر Candidate، زمان‌های broker-server، وضعیت Decision، و اتصال Deal/Position به Candidate. تراکنش بدون اتصال به Candidate خطای سخت است؛ OrderID ناموجود در یک Deal warning است و به‌صورت خودکار جعل نمی‌شود.

پس از کپی CSV از Common Files ترمینال MT5 به پوشهٔ پروژه، اجرا کنید:

```powershell
python research/event_ledger_v2_validator.py `
  runs/BOOT-003/WM20261104A001_event_ledger_v2.csv `
  --expected-run-id WM20261104A001 `
  --output-json runs/BOOT-003/WM20261104A001_ledger_validation.json
```

خروجی با کد ۰ معتبر، کد ۲ نامعتبر و کد ۳ خطای نوشتن گزارش JSON را اعلام می‌کند. این Validator فقط ساختار و پیوند هویتی را می‌سنجد؛ درست‌بودن قیمت، منطق و نتیجهٔ معامله را اثبات نمی‌کند.
## 7. تست‌های ایستا و محدودیت

فایل `research/test_event_ledger_v2_static.py` ترتیب Schema، محل Candidate creation، ReasonCodeها، نگاشت پایدار Order/Position، زمان‌های خام و حضور predicateهای اصلی C2 را کنترل می‌کند. فایل `research/test_event_ledger_v2_validator.py` نیز Validator خروجی را با داده‌های مصنوعی مثبت/منفی می‌آزماید. Workflow اختصاصی GitHub Actions هر دو مجموعه را اجرا می‌کند.

**این تست‌ها Compile MQL5 نیستند.** در این Commit هنوز موارد زیر PASS نشده‌اند:

- MetaEditor compile؛
- اجرای EA روی MT5 / WMMarkets؛
- تطبیق واقعی CSV با معاملات Tester؛
- اثبات عدم تغییر رفتار با Replay A/B؛
- ممیزی مستقل ترتیب callbackها، خصوصاً partial fills.

تا عبور این Gateها BOOT-003 کامل نیست و Event Ledger v2 نباید برای آموزش W1/W2/W3 استفاده شود.
