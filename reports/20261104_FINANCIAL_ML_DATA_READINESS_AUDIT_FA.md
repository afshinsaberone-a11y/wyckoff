# ممیزی آمادگی داده برای Financial ML Core+

تاریخ: 2026-11-04  
مالک پیشنهادی: AGENT_01  
ممیزی: AGENT_03  
وضعیت: **BLOCKED برای آموزش معتبر W1/W2/W3؛ قابل ادامه برای توسعه instrumentation و کنترل کیفیت.**

## 1. نتیجه مدیریتی

در مخزن فعلی شواهد مناسبی از سورس EA، رویدادهای تاریخی، Journal و گزارش‌های Strategy Tester وجود دارد؛ اما مجموعه داده‌ای که برای آموزش و اعتبارسنجی HMM/ML لازم است هنوز کامل نیست.

سه کمبود اصلی:
1. داده خام و قابل ردیابی OHLC M1 و تاریخچه Tick در مخزن حاضر نیست.
2. CSVهای موجود عمدتاً Event Log هستند، نه جدول Feature Snapshot و Label Outcome.
3. شناسه فعلی `SetupID` شناسه Range فعال است، نه شناسه یکتای هر تلاش/فرصت ML.

بنابراین داده موجود برای تحلیل Funnel و مهندسی ثبت رویداد مفید است، اما نباید بدون بازسازی و تکمیل به‌عنوان Dataset آماده آموزش معرفی شود.

## 2. موجودی شواهد بررسی‌شده

در درخت فایل مخزن، سورس MQ5، SET، رویداد CSV، لاگ Tester، چند فایل XLSX/CSV گزارش و مستندات فنی موجود است. موارد زیر بررسی شدند:

| فایل | داده/محتوا | کاربرد مجاز فعلی |
|---|---|---|
| `events/Wyckoff_W0_events_v1_08_C2_SB050_T030_TIMING_B12_R12_RC12.csv` | Event log نسخه C2؛ 346 ردیف داده شامل EA_INIT | تحلیل Funnel و ممیزی رخدادهای C2 |
| `events/20261103.log` | Journal چند اجرای Tester؛ اجرای کامل C2 از 2024-01-02 تا 2026-10-17 | تطبیق Expert، ورودی‌ها، رویدادها و اجرای سفارش |
| `reports/20261103.log` | لاگ طولانی‌تر شامل اجرای C2 و ابزارهای TickDiag/Session | ممیزی اجرا و مسیر توقف |
| `events/Wyckoff_W0_events.csv` | Event log قدیمی تا 2024-04-16 | تاریخچه قدیمی؛ نه baseline فعلی |
| `events/Wyckoff_W0_events_cleaned_fullrun.csv` | Event log با header wrapper و index؛ تا 2025-05-05 | نیازمند پاک‌سازی مستند و تطبیق نسخه |
| `events/Wyckoff_W0_events_v1_07_E12.csv` | Event log نسخه 1.07 | تحلیل تاریخی نسخه قدیمی، نه W0 فعلی |
| `reports/20261104_C2_T030_SB050_BACKTEST_REVIEW_FA.md` | خلاصه گزارش C2 با اشاره به CSV جداگانه | خلاصه تحلیلی؛ CSV نام‌برده در مخزن حاضر نیست |
| `reports/20261104_H1STRUCT_AUDIT_RUN_ANALYSIS_FA.md` | تحلیل واقعی H1STRUCT Audit | ممیزی ساختار؛ یک معامله ثبت‌شده |
| `src/Wyckoff_XAUUSD_W0_v1_08_C2_T030_SB050.mq5` | منطق C2 و Event logger فعلی | منبع رفتار و instrumentation |
| `src/Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT.mq5` | سورس تشخیصی MultiAudit v1.084 | بررسی ایستا؛ کامپایل/Tester تأیید نشده |

## 3. تحلیل دقیق Event CSV اجرای C2 موجود

فایل `events/Wyckoff_W0_events_v1_08_C2_SB050_T030_TIMING_B12_R12_RC12.csv` دارای:
- 346 ردیف داده (به‌همراه EA_INIT).
- EA_Version یکسان: `1.08-C2-TIMING-SB050-T030`.
- Setup/Range ID از 1 تا 65.
- پوشش رخدادها از 2024-01-02 تا آخرین رخداد 2026-10-05؛ Journal اجرای متناظر تا پایان آزمون 2026-10-16 را نشان می‌دهد.
- یک ORDER_OPENED، یک TRADE_ENTRY_DEAL و یک TRADE_CLOSED.

شمارش رخدادها در همین CSV:
| Event | Count |
|---|---:|
| RANGE_FOUND | 65 |
| SPRING_CANDIDATE / SPRING_CONFIRMED | 20 / 15 |
| UTAD_CANDIDATE / UTAD_CONFIRMED | 14 / 7 |
| TEST_CONFIRMED | 15 |
| SOS_CONFIRMED / SOW_CONFIRMED | 6 / 2 |
| LPS_CONFIRMED / LPSY_CONFIRMED | 4 / 2 |
| M5_BREAKOUT_CONFIRMED | 3 |
| M5_RETEST_CONFIRMED | 2 |
| M5_BUY_RECOVERY_CONFIRMED | 1 |
| ORDER_OPENED / TRADE_ENTRY_DEAL / TRADE_CLOSED | 1 / 1 / 1 |

این شمارش مربوط به اجرای C2 در Journal مورخ 2026-11-03 با بازه 2024-01-02 تا 2026-10-17 است؛ با اجرای دیگری که گزارش 2026-11-04 برای بازه تا 2026-11-04 توصیف می‌کند ادغام نشود.

### 3.1 اختلاف بازه‌های تست را حفظ کن

گزارش `20261104_C2_T030_SB050_BACKTEST_REVIEW_FA.md` به CSV دیگری اشاره می‌کند:
`Wyckoff_C2_H1StructureAudit_2024_2026_C2_SB050_T030_TIMING_B12_R12_RC12.csv`.

این فایل با همین نام در درخت فعلی مخزن پیدا نشد. گزارش 2026-11-04 بازه آزمون را تا 2026-11-04 ذکر می‌کند، در حالی که Journal C2 آرشیوشده در 2026-11-03 تا 2026-10-17 تست کرده است. شمارش‌های این دو run نباید با هم یکی گرفته شوند. قبل از تجمیع، CSV خامِ نام‌برده و Journal/HTML همان اجرای 2026-11-04 باید وارد مخزن و با EA_Version تطبیق داده شوند.

## 4. محدودیت‌های بنیادی CSV فعلی

ساختار موجود عمدتاً شامل:
`ServerTime, EA_Version, Symbol, InitialBalance, SetupID, Direction, Event, Details, RangeHigh, RangeLow, PositionID`.

فیلدهای مهمِ غایب:
- range_id مستقل و parent cycle ID
- candidate_id و attempt_id
- event source bar time و source bar close time
- available_at و decision_time مستقل
- snapshot کامل ویژگی‌ها در زمان تصمیم
- OHLC/ATR/volume/spread در زمان هر Candidate
- تعریف label، horizon، MFE، MAE و right-censoring
- hypothetical outcome برای فرصت‌های اجرا‌نشده
- data/config/code hash و tester build در هر ردیف یا manifest
- دلیل رد استانداردشده با stage و rejection severity

Event logger فعلی در سورس، timestamp ثبت را از `TimeCurrent()` می‌نویسد. برای رویدادهای مبتنی بر کندل باید زمان کندل منبع، بسته‌شدن کندل، زمان دسترس‌پذیری و زمان تصمیم جدا ثبت شوند؛ `ServerTime` به‌تنهایی جای همه این مفاهیم را نمی‌گیرد.

## 5. مسئله شناسه: SetupID فعلی شناسه Candidate نیست

در سورس C2:
- `g_setupCounter++` در تابع تشخیص/ایجاد Range رخ می‌دهد.
- مقدار `g_setupCounter` سپس در Event CSV به‌عنوان `SetupID` ذخیره می‌شود.
- داخل همان Range ممکن است بیش از یک Spring/UTAD candidate یا rejection رخ دهد.
- M5 نیز چندین مرحله ارزیابی و تلاش ورود دارد.

پس `SetupID` فعلی عملاً به Range/ماشین حالت فعال نزدیک‌تر است؛ نه شناسه مستقل هر نمونه ML. اگر دو تلاش Spring یا دو Candidate M5 با یک SetupID ادغام شوند، ویژگی‌ها و labelهای دو فرصت متفاوت مخلوط می‌شوند.

شناسه‌های لازم از این پس:
- `range_id`: محدوده تشخیص داده‌شده.
- `cycle_id`: یک چرخه ساختاری Wyckoff زیر یک Range (Spring/UTAD تا Test/Strength/LPS).
- `attempt_id`: یک تلاش مستقل Spring/UTAD یا مرحله بازآزمایی، در صورت تکرار.
- `candidate_id`: یک تصمیم/فرصت قابل امتیازدهی در نقطه تصمیم ازپیش‌تعریف‌شده.
- `trade_id`: معامله واقعی یا شبیه‌سازی‌شده.
- `legacy_setup_id`: مقدار فعلی SetupID برای نگاشت عقب‌رو؛ آن را به‌صورت خودکار candidate_id فرض نکن.

برای Split و Uncertainty، candidateهای وابسته از یک Range یا cycle باید با group_id مشترک قابل شناسایی باشند.

## 6. چه چیزی می‌توان از داده فعلی انجام داد؟

**مجاز:**
- شمارش و تحلیل Funnel رویدادها.
- مقایسه زمان و فاصله بین مراحل روی CSV/Journal موجود.
- تطبیق رویدادهای کد و گزارش Tester.
- طراحی و تست parser، schema و Event Ledger instrumentation.
- بررسی خطاهای ثبت شناسه و زمان.

**غیرمجاز به‌عنوان نتیجه معتبر ML:**
- آموزش مدل سودآوری روی 346 ردیف Event CSV.
- استفاده از فقط یک معامله اجراشده برای برچسب سود/زیان.
- ساخت outcome فرضی بدون OHLC/Tick و execution assumptions.
- تلقی 57 رویداد M5_ENTRY_EVALUATION به‌عنوان 57 معامله یا 57 Candidate مستقل.
- ادغام رویدادهای نسخه‌های 1.07، C2، H1STRUCT و MultiAudit بدون run manifest و کلیدهای نگاشت.
- ساخت HMM بر اساس Event ID یا داده ناقص رویداد به‌جای دنباله زمانی ویژگی‌های بازار.

## 7. داده و artifactهای لازم برای رفع Block

| نیاز | چرا لازم است | وضعیت مخزن |
|---|---|---|
| XAUUSD_M1 خام و manifest | ساخت M5/H1/H4 و ویژگی‌های زمانی | یافت نشد |
| Tick/Bid/Ask یا فایل اجرای معتبر | Spread، gap، fill و برچسب after-cost | فایل خام مستقل یافت نشد؛ Journalهای منتخب موجودند |
| CSV اجرای C2 تا 2026-11-04 که در گزارش نام‌برده شده | تطبیق آمار اجرای جدید | یافت نشد |
| HTML و Journal کامل هر اجرای مستقل | هویت Expert، پارامترها و اجرای سفارش | بخشی از Journalها موجود؛ بسته کامل هر run نیست |
| Event/Candidate Ledger با IDهای جدا | نمونه آموزشی بدون ادغام تلاش‌ها | هنوز ساخته نشده |
| Feature Snapshot point-in-time | ورودی معتبر HMM/ML | موجود نیست |
| Label/Outcome table | هدف آموزش و ارزیابی | موجود نیست |
| Fold manifest و purge/embargo records | کنترل leakage | هنوز ساخته نشده |

## 8. اقدام اصلاحی پیشنهادی

1. قرارداد Event/Candidate را به schema با سلسله‌مراتب ID ارتقا بده.
2. Event logger را additive و در branch جدا instrument کن؛ هیچ predicate معاملاتی تغییر نکند.
3. رویداد و Candidate را در جدول‌های جدا با source bar time، available_at و decision_time ثبت کن.
4. تمام رد، انقضا، ابطال، عدم اجرای سفارش و رویدادهای پس از ورود را حفظ کن.
5. برای هر Candidate در یک نقطه تصمیم ثابت، feature snapshot ایجاد کن.
6. outcome را در فرآیند جداگانه با M1/Tick و cost model محاسبه کن.
7. Auditor قبل از ساخت Foldها، schema و completeness را کنترل کند.

## 9. تصمیم آمادگی

- Event Funnel Audit: **قابل انجام**
- Data/Execution completeness: **CONDITIONAL**
- Candidate/Feature/Label dataset: **BLOCKED**
- W1 HMM training: **BLOCKED**
- W2 ML training: **BLOCKED**
- W3 Hybrid: **BLOCKED**

ثبت این گزارش به معنی تولید Dataset جدید، اجرای کد یا آموزش مدل نیست.
