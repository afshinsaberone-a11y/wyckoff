# راهنمای مهاجرت Legacy Event CSV به Event Ledger

نسخه: 1.0-draft  
منبع: اجرای C2 مورخ 2026-11-03  
وضعیت: کد مهاجرت و تست واحد ثبت شده‌اند؛ اجرای CI/Artifact جدید در انتظار نتیجه است.

## 1. هدف و دامنه

فایل قدیمی:
`events/Wyckoff_W0_events_v1_08_C2_SB050_T030_TIMING_B12_R12_RC12.csv`

ساختار قدیمی شامل ServerTime، EA_Version، Symbol، InitialBalance، SetupID، Direction، Event، Details، RangeHigh، RangeLow و PositionID است.

مهاجر:
`scripts/migrate_legacy_event_csv.py`

خروجی‌ها:
- `events_normalized.csv`
- `migration_manifest.json`

این ابزار فقط Event Ledger می‌سازد. این خروجی **Dataset آموزشی HMM/ML نیست**.

## 2. نگاشت شناسه‌ها

در سورس C2:
- خط 483: `g_setupCounter++`
- خط 496: بلافاصله پس از افزایش شمارنده، `RANGE_FOUND` ثبت می‌شود.
- خط 235: همان شمارنده در ستون قدیمی `SetupID` نوشته می‌شود.

بنابراین مهاجر:
- مقدار قدیمی SetupID را به `legacy_setup_id` نگاشت می‌کند.
- برای SetupID بزرگ‌تر از صفر، یک `range_id` مصنوعی اما deterministic با پیشوند LEGACY_RANGE تولید می‌کند.
- `group_id` را برابر همین Range ID می‌گذارد تا رویدادهای یک Range در splitها از هم جدا نشوند.
- شناسه‌های `cycle_id`، `attempt_id`، `candidate_id`، `decision_id` و `trade_id` را خالی باقی می‌گذارد.
- PositionID را فقط به `legacy_position_id` می‌برد؛ بدون Join تأییدشده به Order/Deal آن را trade_id نمی‌نامد.

Range ID تولیدشده یک کلید مهاجرت است که از معنای Range-level شمارنده قدیمی استفاده می‌کند؛ شناسه اصلی ثبت‌شده در سورس جدید نیست.

## 3. سیاست زمان

CSV قدیمی فقط زمان خام ServerTime را دارد. طبق سورس Event Logger، این مقدار از TimeCurrent() می‌آید؛ اما فایل CSV، timezone/offset سرور، زمان کندل منبع، زمان بسته‌شدن کندل یا زمان availability را نگه نمی‌دارد.

پس مهاجر:
- server_time_raw را بدون تغییر نگه می‌دارد.
- server_timezone را UNKNOWN ثبت می‌کند.
- event_time_utc، source_bar_open/close، available_at و decision_time را خالی نگه می‌دارد.
- timestamp را به UTC تبدیل نمی‌کند و زمان کندل منبع را حدس نمی‌زند.

## 4. ویژگی و برچسب

مهاجر:
- Feature Snapshot ایجاد نمی‌کند.
- Candidateهای Entry ایجاد نمی‌کند.
- MFE/MAE، hypothetical outcome یا actual netR تولید نمی‌کند.
- Label و right-censoring تولید نمی‌کند.
- رویدادهای ثبت‌شده را برای آموزش classification به نمونه مستقل تبدیل نمی‌کند.

برای آموزش W2 باید instrumentation جدید، نقطه تصمیم M5_ENTRY، candidate_id مستقل و outcome با افق/هزینه ازپیش‌تعریف‌شده ساخته شود.

## 5. اجرای محلی

از ریشه مخزن:

    python -m unittest discover -s scripts -p "test_legacy_event_migration.py"

    python scripts/migrate_legacy_event_csv.py       --input events/Wyckoff_W0_events_v1_08_C2_SB050_T030_TIMING_B12_R12_RC12.csv       --output-dir ./build/legacy-event-migration

خروجی در یک پوشه جدا ساخته می‌شود؛ فایل منبع تغییر نمی‌کند.

## 6. اجرای خودکار GitHub Actions

Workflow:
`.github/workflows/financial-ml-preflight.yml`

در هر اجرا:
1. Preflight قرارداد/نسخه/SET را اجرا می‌کند.
2. تست واحد مهاجر را اجرا می‌کند.
3. Event CSV قدیمی را به پوشه موقت تبدیل می‌کند.
4. manifest را کنترل می‌کند: 346 ردیف منبع/خروجی، 65 Range ID، صفر Candidate و صفر Label.
5. دو خروجی را به‌صورت Artifact با نام `legacy-event-ledger-<commit>` برای 30 روز نگه می‌دارد.

Artifact خروجی فقط در همان Workflow Run قابل دریافت است و جای فایل خام یا ثبت دائمی در مخزن را نمی‌گیرد. اگر schema یا منبع عوض شود، انتظار شمارش باید با ممیزی و تغییر نسخه به‌روزرسانی شود؛ عددها نباید برای سبز کردن CI بی‌دلیل تغییر کنند.

## 7. معیار پذیرش و محدودیت‌ها

- تعداد رویدادهای normalized با ردیف‌های منبع برابر باشد.
- Event IDها برای یک فایل و شماره ردیف deterministic باشند.
- SetupID قدیمی فقط به legacy_setup_id و Range-level group نگاشت شود.
- UTC و Candidate/Label ساختگی ایجاد نشود.
- SHA-256 منبع و خروجی در migration manifest ثبت شود.
- این کنترل فقط migration و کیفیت Event Ledger را تأیید می‌کند؛ نه کیفیت داده M1/Tick، نه اجرای معامله و نه ML edge.
