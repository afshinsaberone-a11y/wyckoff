# برنامه راه‌اندازی Financial ML Core+

نسخه: 1.0-draft  
تاریخ: 2026-11-04  
هدف: تبدیل معماری ایجنت‌ها و پروتکل پژوهش به بسته‌های کاری قابل تحویل.

## نتیجه اولیه BOOT-001

[گزارش تطبیق هویت Baseline W0 و نسخه‌های تشخیصی](../reports/20261104_W0_BASELINE_IDENTITY_FA.md) ثبت شده است. C2-T030-SB050 به‌عنوان Baseline candidate شناخته شد؛ تطبیق نهایی تا دریافت SET دقیق اجرای تاریخی و زنجیره Build/EX5 باز است.

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

### BOOT-002 — Compile و اجرای واقعی MultiAudit
**مالک:** W0؛ اجرا/شواهد با AGENT_02؛ ممیزی AGENT_03  
**کار:**
1. Compile در MetaEditor با ثبت build و log.
2. در صورت Compile موفق، اجرای SET مبنا=5.
3. اجرای SET=10 و SET=20 با همان بازه، نماد، Expert build، مدل تیک، سرمایه، اهرم و هزینه‌ها؛ فقط متغیر مورد آزمایش عوض شود.
4. ذخیره HTML، Journal و CSV هر اجرا.
5. تطبیق نام Expert و EA_Version هر فایل خروجی.
**پذیرش:** سه خروجی قابل ردیابی و بدون mismatch هویت.  
**نکته:** اگر Compile شکست خورد، SETها اجرا نمی‌شوند و کار BLOCKED/FAILED با خطای دقیق بسته می‌شود.

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
| 1 | BOOT-001 Baseline Identity | اسناد و فایل‌های تست موجود | CONDITIONAL؛ تطبیق اولیه ثبت شد، Freeze نهایی باز است |
| 2 | BOOT-002 MultiAudit Compile/Test | دسترسی به MT5/MetaEditor | نیازمند اجرای محیطی |
| 3 | BOOT-003 Event Ledger | هویت W0 و schema | پس از طراحی/هم‌زمان با آماده‌سازی |
| 4 | BOOT-004 Data/Execution Audit | فایل‌های داده و tick | آماده ممیزی با داده در دسترس |
| 5 | BOOT-005 Label/Fold Freeze | Ledger اولیه | وابسته به تعریف outcome |
| 6 | BOOT-006 W1/W2 readiness | BOOT-001 تا 005 | قفل تا عبور Gate |
| 7 | BOOT-007 W3 | W1 و W2 معتبر | قفل |

## قانون توقف و گزارش
اگر فایل خام، دسترسی MetaEditor، تیک، یا خروجی تستر در اختیار Agent نیست، باید BLOCKED ثبت کند. هیچ Agent نباید Compile، Backtest، یا خواندن فایل‌هایی را که واقعاً اجرا/دریافت نکرده، ادعا کند.

این برنامه، صف کار است و ثبت آن در GitHub به معنی انجام هیچ‌یک از BOOT taskها نیست.
