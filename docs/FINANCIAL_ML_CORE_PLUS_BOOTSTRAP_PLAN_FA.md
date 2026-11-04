# برنامه راه‌اندازی Financial ML Core+

نسخه: 1.0-draft  
تاریخ: 2026-11-04  
هدف: تبدیل معماری ایجنت‌ها و پروتکل پژوهش به بسته‌های کاری قابل تحویل.

## نتیجه اولیه BOOT-001

[گزارش تطبیق هویت Baseline W0](../reports/20261104_W0_BASELINE_IDENTITY_FA.md) و [گزارش بازسازی SET مرجع C2](../reports/20261104_W0_C2_SET_RECONSTRUCTION_FA.md) ثبت شده‌اند. C2-T030-SB050 به‌عنوان Baseline candidate شناسایی شده؛ هر 67 مقدار ورودی از Journal بازسازی و با سورس/Journal دقیقاً منطبق است. فایل اصلی SET و hash باینری EX5 تاریخی در دسترس نیستند؛ بنابراین Freeze نهایی هنوز CONDITIONAL است.

## تصمیم پیش از شروع: هویت Baseline را اشتباه نگیریم

در مخزن، این خانواده فایل‌ها و اجراها وجود دارند و نباید یکی فرض شوند:
- C2 پایه و نسخه‌های timing/risk با تنظیمات خاص.
- H1STRUCT Audit که برای بررسی ساختار H1 اجرا شده است.
- H1STRUCT MultiAudit که ابزار تشخیصی Lookback/Pivot است و در وضعیت ثبت‌شده هنوز کامپایل و اجرای Tester آن تأیید نشده است.

بنابراین اولین کار، انتخاب خودکار یکی از نام‌ها نیست. باید Expert name در گزارش Strategy Tester، مقدار EA_Version در CSV، فایل سورس، Commit، فایل SET و مشخصات حساب/بازه به هم متصل شوند. Baseline پژوهشی W0 فقط پس از این تطبیق Freeze می‌شود. H1STRUCT Audit یک نسخه تشخیصی است و نباید بدون تصمیم ثبت‌شده جایگزین C2 پایه شود.

## بسته‌های کاری

### BOOT-001 — تثبیت هویت و نسخه Baseline
**مالک:** AGENT_00 با همکاری W0 و AGENT_04  
**ورودی:** سورس‌ها، SETها، Journal، HTML و CSV تست‌های موجود.  
**کار:** ساخت جدول تطبیق Expert name، EA_Version، فایل سورس، Commit، config hash، data/test range و account spec.  
**پذیرش:** هیچ گزارش یا CSV به نسخه اشتباه نسبت داده نشده باشد؛ Baseline candidate و موارد تشخیصی از هم جدا باشند.  
**خروجی:** reports/W0_BASELINE_IDENTITY_FA.md و manifest ماشین‌خوان.

### BOOT-002 — Compile و چهار اجرای کنترل/حساسیت H1STRUCT
**کارت اجرای دقیق:** [BOOT-002 چهار Run](BOOT_002_MULTIAUDIT_RUN_CARD_FA.md)؛ قالب manifest ماشینی: [BOOT_002_RUN_MANIFEST_TEMPLATE.json](../experiments/BOOT_002_RUN_MANIFEST_TEMPLATE.json).
**مالک:** W0؛ اجرا/شواهد با AGENT_02؛ ممیزی AGENT_03.  
**کار:** دو Compile با MetaEditor build یکسان (v1.083 و v1.084)، سپس چهار Run در یک بازه و شرایط ثابت: A) H1STRUCT v1.083/LB5، B) MultiAudit v1.084/LB5، C) MultiAudit/LB10، D) MultiAudit/LB20. A/B جفت کنترل عدم‌تداخل diagnostics هستند؛ C/D حساسیت قانون فعال SOS/SOW هستند، چون Lookback در priorHigh/priorLow استفاده می‌شود.  
**پذیرش:** دو EX5 با SHA-256، چهار بسته HTML/Journal/CSV، تطبیق Expert/EA_VERSION، یکسانی تاریخ و شرایط، و Audit مستقل A/B و C/D.  
**نکته:** اگر Compile شکست خورد، Testerها اجرا نمی‌شوند. Preflight موفق فقط static validation است و جای Compile/Tester را نمی‌گیرد.

### BOOT-003 — طراحی و پیاده‌سازی Event/Candidate Ledger
**مالک:** AGENT_01 و W0  
**کار:** افزودن شناسه‌های پایدار و ثبت Range، Spring/UTAD، Test، SOS/SOW، LPS/LPSY، Candidateهای M5، ردها، انقضاها، ابطال‌ها، سفارش‌ها و Dealها.  
**پذیرش:** Candidate اجرا‌نشده هم در Ledger وجود داشته باشد؛ هر Candidate تا تصمیم و outcome قابل ردیابی باشد؛ feature snapshot از label جدا باشد.  
**خروجی:** schema-validated CSV/Parquet و نمونه audit trail.

### BOOT-004 — ممیزی داده و پوشش اجرا
**مالک:** AGENT_01 و AGENT_02  
**کار:** تعیین دقیق پوشش M1/tick، زمان‌های missing، spread صفر/مفقود، اختلاف tick، gap، bid/ask، و فرض اجرای SL/TP.  
**پذیرش:** گزارش quality با تفکیک بازه‌های معتبر و نامعتبر؛ بدون پرکردن خاموش داده مفقود.  
**خروجی:** Data Quality و Execution Assumption Report.

### BOOT-005 — Freeze برچسب و Foldها
**مالک:** AGENT_04؛ تأیید AGENT_03  
**کار:** تعریف outcome horizon، barrier، هزینه‌ها، MFE/MAE، censoring، Purge، Embargo و Foldهای زمانی.  
**پذیرش:** label windows قابل محاسبه و overlapها قابل شناسایی باشند؛ هیچ split تصادفی استفاده نشود.  
**خروجی:** label manifest و fold manifest نسخه‌بندی‌شده.

### BOOT-006 — Gate آمادگی W1/W2
**مالک:** AGENT_03 و AGENT_04  
**شرط:** BOOT-001 تا BOOT-005 کامل و ممیزی قابل قبول باشند.  
**نتیجه:** اگر PASS/شرط‌های CONDITIONAL رعایت‌شده، W1 و W2 اجازه شروع آزمایش در Foldهای مجاز می‌گیرند. در غیر این صورت توسعه فقط روی داده آزمایشی/کد و بدون ادعای نتیجه معتبر ادامه می‌یابد.

### BOOT-007 — W3 و مقایسه چهاربازویی
**مالک:** W3، AGENT_02 و AGENT_03  
**شرط:** W1 و W2 مستقل و Freeze شده باشند.  
**کار:** ادغام خروجی‌های هم‌تراز، مقایسه W0/W1/W2/W3، محاسبه اثرهای اصلی و تعامل و گزارش uncertainty.  
**پذیرش:** شواهد out-of-fold و OOS بدون tuning مجدد؛ گزارش همه نسخه‌ها، حتی نتایج منفی.

## صف اجرای پیشنهادی

| ترتیب | Task | وابستگی | وضعیت شروع |
|---:|---|---|---|
| 1 | BOOT-001 Baseline Identity | Journal، سورس، SET بازسازی‌شده | CONDITIONAL؛ 67/67 ورودی بازیابی شد؛ EX5 hash تاریخی در دسترس نیست |
| 2 | BOOT-002 H1STRUCT/MultiAudit | دسترسی MT5/MetaEditor | Static Preflight پیشرفته PASS؛ دو Compile و چهار MT5 Run هنوز NOT RUN |
| 3 | BOOT-003 Event Ledger | هویت W0 و schema | قرارداد ID به‌روزرسانی شد؛ instrumentation در سورس هنوز اجرا نشده |
| 4 | BOOT-004 Data/Execution Audit | فایل‌های داده و tick | ممیزی Event Log انجام شد؛ OHLC/Tick خام در مخزن یافت نشد؛ CONDITIONAL/BLOCKED |
| 5 | BOOT-005 Label/Fold Freeze | Ledger اولیه | وابسته به تعریف outcome |
| 6 | BOOT-006 W1/W2 readiness | BOOT-001 تا 005 | قفل تا عبور Gate |
| 7 | BOOT-007 W3 | W1 و W2 معتبر | قفل |

## قانون توقف و گزارش
اگر فایل خام، دسترسی MetaEditor، تیک، یا خروجی تستر در اختیار Agent نیست، باید BLOCKED ثبت کند. هیچ Agent نباید Compile، Backtest، یا خواندن فایل‌هایی را که واقعاً اجرا/دریافت نکرده، ادعا کند.

این برنامه، صف کار است و ثبت آن در GitHub به معنی انجام هیچ‌یک از BOOT taskها نیست.


## نتیجه ممیزی آمادگی داده و اصلاح قرارداد شناسه — 2026-11-04

[گزارش ممیزی آمادگی داده Financial ML](../reports/20261104_FINANCIAL_ML_DATA_READINESS_AUDIT_FA.md) ثبت شد. Event CSV اجرای C2 مورخ 2026-11-03 دارای 346 ردیف داده و 65 Range است؛ این اجرای مشخص تا 2026-10-17 ادامه دارد و نباید با اجرای جداگانه‌ای که گزارش C2 مورخ 2026-11-04 تا 2026-11-04 توصیف می‌کند ادغام شود. CSV جداگانه‌ای که در گزارش دوم نام برده شده، در مخزن حاضر نیست.

بررسی سورس نشان داد `g_setupCounter` هنگام RANGE_FOUND افزایش می‌یابد؛ پس SetupID قدیمی شناسه Range/ماشین حالت است، نه شناسه یکتای هر Candidate. قراردادهای Event/Candidate و Feature/Label به schema نسخه 1.1-draft ارتقا یافتند: `range_id`، `cycle_id`، `attempt_id`، `candidate_id` و `legacy_setup_id` جدا هستند. W2 در نسخه اول باید نقطه تصمیم M5_ENTRY را Freeze کند.

### وضعیت Gateها پس از این ممیزی
- BOOT-001: CONDITIONAL؛ SET بازسازی‌شده 67/67 با Journal و سورس منطبق است؛ EX5 hash/Build تاریخی موجود نیست.
- BOOT-002: Static Preflight پیشرفته PASS؛ دو Compile و چهار Run (v1.083/LB5، v1.084/LB5/10/20) در MT5 هنوز انجام نشده‌اند.
- BOOT-003: طراحی قرارداد/شناسه بهتر شد؛ instrumentation در سورس و Compile/Replay هنوز انجام نشده.
- BOOT-004: Event Log بررسی شد؛ داده خام M1/Tick و بسته کامل CSV اجرای 2026-11-04 در مخزن موجود نیست.
- BOOT-005 تا BOOT-007: قفل؛ W1/W2/W3 هنوز نباید روی این Event CSV آموزش/ارزیابی شوند.


## نتیجه بازبینی ایستای MultiAudit v1.084 — 2026-11-04

[گزارش بازبینی مستقل سورس MultiAudit](../reports/20261104_MULTIAUDIT_STATIC_CODE_REVIEW_FA.md) اضافه شد. مقایسه خطی v1.083 با v1.084 نشان داد 117 خط افزوده و فقط 4 خط حذف شده‌اند؛ چهار حذف فقط metadata نسخه/نام/توضیح/EA_VERSION هستند. در این مقایسه هیچ خط اجرایی پایه حذف نشده است. افزوده‌ها شامل تابع تشخیصی Lookback/Pivot، دو فراخوانی در مسیر Strength و افزایش تعداد barهای درخواستی هنگام ST_WAIT_STRENGTH هستند.

وضعیت Gate:
- Static source review: PASS WITH LIMITATIONS.
- MetaEditor Compile: NOT RUN.
- MT5 Strategy Tester: NOT RUN.
- BOOT-002: هنوز باز است؛ طراحی چهار Run A/B/C/D در Run Card v2 ثبت شده است.


## Preflight خودکار مخزن

اسکریپت [validate_financial_ml_preflight.py](../scripts/validate_financial_ml_preflight.py) و workflow [financial-ml-preflight.yml](../.github/workflows/financial-ml-preflight.yml) اضافه شده‌اند. این کنترل‌ها حفظ خطوط پایه v1.083 در v1.084، شناسه نسخه، وجود توابع Audit و تطابق 67 ورودی با سه SET و تفاوت مجاز فقط Lookback/CSV filename را بررسی می‌کنند.

Preflight یک کنترل ایستای repository است؛ حتی در صورت PASS، BOOT-002 تا وقتی دو MetaEditor Compile و چهار اجرای MT5 ثبت نشده‌اند COMPLETE نخواهد شد.


## شاهد اجرای خودکار Preflight — 2026-11-04

اولین GitHub Actions workflow با شناسه Run `41856290720` روی Commit `ec3f92cb94737f63f73c9276827b5f5dac934aaf` با نتیجه `success` تمام شد. Job: `static-preflight`. [مشاهده اجرای CI](https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41856290720).

گزارش ماشین‌خوان: [BOOT_002_STATIC_PREFLIGHT_RUN_001.json](../experiments/BOOT_002_STATIC_PREFLIGHT_RUN_001.json).

این نتیجه فقط تأیید می‌کند کنترل‌های repository/static در آن Commit پاس شده‌اند: هویت v1.084، حفظ خطوط مبنای v1.083، تابع تشخیصی بدون سفارش، شناسه رویدادها، تطابق 67 ورودی با SETها و اختلاف مجاز فقط Lookback/نام CSV. این موفقیت هیچ Compile MQL5 یا اجرای MT5 را تأیید نمی‌کند؛ BOOT-002 هنوز باز است.


## تکرارپذیری Preflight — دو اجرای موفق

گزارش [دو اجرای موفق GitHub Actions](../reports/20261104_BOOT_002_CI_VERIFICATION_FA.md) ثبت شد:
- Run 41856290720 روی Commit `ec3f92cb94737f63f73c9276827b5f5dac934aaf`.
- Run 41856507674 روی Commit `3e2a6138131ef08531ea743378906a31ef35232c`.

هر دو Job با conclusion=success پایان یافتند. این فقط تکرارپذیری کنترل‌های repository/static را تأیید می‌کند؛ BOOT-002 تا Compile واقعی و سه MT5 Run باز است.


## Preflight پیشرفته با 24 کنترل — PASS

در Run [41858327181](https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41858327181) روی Commit `eb43035187a2f4e2ab2dfbd8aebea838c555949a`، Job `static-preflight` با نتیجه success پایان یافت: 24 کنترل PASS و صفر FAIL. این نسخه علاوه بر کنترل‌های MultiAudit، Journal UTF-16، C2 source/SET/Journal با 67 ورودی، برابری SET کنترل H1STRUCT و MultiAudit/LB5 به‌جز CSV filename، و استفاده فعال Lookback در SOS/SOW را کنترل می‌کند.

[Manifest ماشینی این Run](../experiments/BOOT_002_STATIC_PREFLIGHT_RUN_002.json).

این فقط Static Preflight است. BOOT-002 همچنان نیازمند دو Compile واقعی و چهار MT5 Run است.
