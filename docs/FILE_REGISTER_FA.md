# فهرست فایل‌ها و وضعیت آرشیو GitHub

## منتقل‌شده و بررسی‌شده در مخزن

### سورس‌های کامل MQ5
- src/Wyckoff_XAUUSD_W0_base.mq5
- src/Wyckoff_XAUUSD_W0_v1_01.mq5
- src/Wyckoff_XAUUSD_W0_v1_02.mq5
- src/Wyckoff_XAUUSD_W0_v1_03.mq5
- src/Wyckoff_XAUUSD_W0_v1_04.mq5
- src/Wyckoff_XAUUSD_W0_v1_05.mq5
- src/Wyckoff_XAUUSD_W0_v1_06.mq5
- src/Wyckoff_XAUUSD_W0_v1_07.mq5

سورس‌ها با خواندن همه قطعه‌های صفحات فایل (از جمله ادامه پس از خط ۱۰۰۰) بازسازی و جایگزین شدند. انتقال محتوا به معنی کامپایل یا تأیید عملکرد نیست.

### لاگ‌های کامل
- reports/20261101.log — ۱۱۳۱ خط
- reports/20261101_1.log — ۲۷۶۶ خط

### CSVهای رویداد
- events/Wyckoff_W0_events.csv — ۲۵۶۶ خط
- events/Wyckoff_W0_events_cleaned_fullrun.csv — ۱۰۰۳ خط
- events/Wyckoff_W0_events_v1_03.csv — ۲۸۷ خط
- events/Wyckoff_W0_events_v1_04.csv — ۲۸۵ خط
- events/Wyckoff_W0_events_v1_05_E12.csv — ۳۳۹ خط
- events/Wyckoff_W0_events_v1_05_E18.csv — ۳۵۶ خط
- events/Wyckoff_W0_events_v1_05_E24.csv — ۳۶۴ خط
- events/Wyckoff_W0_events_v1_06_E12.csv — ۳۳۷ خط

### مستندات
- README.md
- docs/PROJECT_STATUS_FA.md
- docs/BACKTEST_HISTORY_FA.md
- docs/FILE_REGISTER_FA.md
- docs/DEVELOPMENT_RULES_FA.md

## فایل‌های موجود در تاریخچه که هنوز به‌صورت باینری منتقل نشده‌اند
- بسته‌های ZIP پروژه و نسخه‌های v1.01 تا v1.06
- فایل تستر نسخه v1.01 با پسوند TST
- ReportTester-20181902waykof.xlsx

اتصال فعلی GitHub امکان ثبت فایل‌های متنی UTF-8 را دارد؛ اما مسیر انتقال مستقیم بایت فایل‌های باینری از فایل‌های پیوست‌شده در این محیط در دسترس نیست. فایل Excel نیز از مسیر استخراج متن، محتوای قابل خواندن ارائه نکرد.

## محدودیت آرشیو چت
این مخزن شامل جمع‌بندی فنی و فایل‌های پروژه قابل انتقال است، نه متن کامل و کلمه‌به‌کلمه تمام پیام‌های چت. برای آرشیو کامل چت، باید Export رسمی گفتگو از رابط ChatGPT گرفته و پس از بررسی اطلاعات خصوصی به مخزن اضافه شود.

## هشدار صحت
ثبت فایل در GitHub فقط انتقال محتوا را ثابت می‌کند؛ به معنی کامپایل موفق، تأیید صحت منطق، یا سودآوری اکسپرت نیست. تمام نسخه‌ها باید در MetaEditor کامپایل و با گزارش تست متناظر ممیزی شوند.


## مستندات تکمیلی نشست 2026-11-04
- docs/PROJECT_ARCHITECTURE_FA.md — معماری ده‌لایهٔ پروژه.
- docs/PROJECT_PROGRESS_ESTIMATE_FA.md — برآورد پیشرفت کلان و تفصیلی؛ درصدها تخمینی‌اند.
- docs/CHAT_AND_PROJECT_PROGRESS_FA.md — آرشیو زمانی/فنی پیشرفت و تصمیم‌های پروژه؛ خلاصه است و نه transcript لفظ‌به‌لفظ.
- docs/CHAT_AND_PROJECT_ARCHIVE_FA.md — آرشیو فنی یکپارچه و محدودیت‌های آن.
- گزارش اجرای H1STRUCT Audit — نتایج معاملهٔ واحد، قیف رویدادها و ریسک گپ/لغزش.
- گزارش‌های عمیق H1STRUCT، MultiAudit و Range-edge در reports/ و docs/ فهرست شده‌اند.

محدودیت انتقال: این به‌روزرسانی مستندات را ثبت می‌کند. پیوست‌های باینریِ موجود در چت، از جمله HTML/Journal خام، فقط در صورت دسترسی به محتوای فایل و انتقال باینری مستقل باید به مخزن افزوده شوند؛ هیچ فایل خامی صرفاً بر اساس نام فرضاً آپلودشده تلقی نشده است.


## اسناد و شواهد Financial ML Core+ — نشست 2026-11-04

### مشخصات Agent و قراردادها
- agents/README_FA.md و فایل‌های AGENT_00، W0 تا W3 و AGENT_01 تا AGENT_04.
- agents/EXECUTION_AND_HANDOFF_MODEL_FA.md — محیط، مجوز و چرخه تحویل.
- contracts/EVENT_AND_CANDIDATE_SCHEMA_FA.md — نسخه 1.1-draft با سلسله‌مراتب شناسه‌ها.
- contracts/FEATURE_LABEL_SCHEMA_FA.md — نسخه 1.1-draft با نقطه تصمیم و جداسازی دو نوع label.
- contracts/EXPERIMENT_AND_FOLD_SCHEMA_FA.md، RESULT_AND_AUDIT_SCHEMA_FA.md و AGENT_HANDOFF_SCHEMA_FA.md.

### پروتکل و گزارش‌ها
- docs/FINANCIAL_ML_CORE_PLUS_PROTOCOL_FA.md
- docs/FINANCIAL_ML_CORE_PLUS_BOOTSTRAP_PLAN_FA.md
- reports/20261104_W0_BASELINE_IDENTITY_FA.md — تطبیق اولیه Baseline، CONDITIONAL.
- reports/20261104_FINANCIAL_ML_DATA_READINESS_AUDIT_FA.md — ممیزی Event CSV، شناسه‌ها و آمادگی داده.

### شواهد اجرای C2 که در مخزن بررسی شدند
- events/20261103.log — اجرای C2 از 2024-01-02 تا 2026-10-17 و چند اجرای تشخیصی.
- events/Wyckoff_W0_events_v1_08_C2_SB050_T030_TIMING_B12_R12_RC12.csv — Event CSV همان C2؛ 346 ردیف داده.
- گزارش C2 تا 2026-11-04 به CSV دیگری اشاره می‌کند که هنوز با همان نام در مخزن حاضر نیست.

هیچ‌یک از اسناد جدید به معنی کامپایل، تست یا آموزش مدل جدید نیست.


- reports/20261104_MULTIAUDIT_STATIC_CODE_REVIEW_FA.md — مقایسه ایستای مستقل سورس H1STRUCT Audit v1.083 و MultiAudit v1.084؛ نتیجه Static Review PASS WITH LIMITATIONS، بدون Compile/Tester.


- docs/BOOT_002_MULTIAUDIT_RUN_CARD_FA.md — دستور اجرای تکرارپذیر MultiAudit v1.084 در MT5.
- experiments/BOOT_002_RUN_MANIFEST_TEMPLATE.json — قالب ماشین‌خوان برای هویت Compile، SET، Tester و خروجی‌ها.
- reports/20261104_MULTIAUDIT_STATIC_CODE_REVIEW_FA.md — مقایسه مستقل ایستای سورس v1.083/v1.084.


- reports/20261104_BOOT_002_CI_VERIFICATION_FA.md — ثبت دو اجرای موفق GitHub Actions static preflight؛ بدون ادعای Compile/Tester.


- reports/20261104_W0_C2_SET_RECONSTRUCTION_FA.md — بازسازی SET اجرای C2 از 67 مقدار Journal و تطبیق کامل با سورس/Journal.
- experiments/W0_C2_BASELINE_RUN_20261103.json — manifest شواهد اجرای تاریخی C2 و محدودیت‌های EX5/SET اصلی.
- experiments/BOOT_002_STATIC_PREFLIGHT_RUN_002.json — GitHub Actions Preflight پیشرفته، 24 PASS / 0 FAIL.
- docs/BOOT_002_MULTIAUDIT_RUN_CARD_FA.md — نسخه 2.0، چهار Run A/B/C/D با جفت کنترل و دو حساسیت Lookback.


- experiments/BOOT_002_STATIC_PREFLIGHT_RUN_003.json — ثبت دو اجرای GitHub Actions موفق با 27 PASS / 0 FAIL روی طراحی چهار Run.
- docs/BOOT_002_MULTIAUDIT_RUN_CARD_FA.md v2.0 — چهار Run کنترل/حساسیت؛ Lookback10/20 به‌عنوان تغییر فعال شرط SOS/SOW.


### Legacy Event Ledger migration
- docs/LEGACY_EVENT_LEDGER_MIGRATION_FA.md — قواعد نگاشت، زمان و محدودیت‌های مهاجرت.
- scripts/migrate_legacy_event_csv.py — مبدل محافظه‌کار Event CSV به CSV normalized + manifest.
- scripts/test_legacy_event_migration.py — تست واحد شناسه‌ها، timestamp و عدم جعل Candidate/Label.


- reports/20261104_LEGACY_EVENT_LEDGER_MIGRATION_RUN_FA.md — گزارش 346/346 ردیف، 65 Range group و 5 تست واحد موفق.
- experiments/BOOT_003_LEGACY_EVENT_MIGRATION_RUN_001.json — جزئیات CI و Artifact اجرای BOOT-003.
- docs/LEGACY_EVENT_LEDGER_MIGRATION_FA.md — راهنمای مهاجرت، شناسه‌ها و محدودیت زمان.


- docs/BOOT_003_MQL5_EVENT_LEDGER_V2_SPEC_FA.md — قرارداد اجرایی instrumentation v2 برای Run/Range/Cycle/Attempt/Candidate/Decision و زمان‌های point-in-time.
- contracts/EVENT_AND_CANDIDATE_SCHEMA_FA.md v1.2-draft — هویت و event/candidate row schema.
- contracts/FEATURE_LABEL_SCHEMA_FA.md v1.2-draft — feature/label point-in-time و server time basis.


## شروع موازی ایجنت‌ها — 2026-11-04
- docs/PARALLEL_AGENT_LEARNING_SPRINT_FA.md — ماتریس ۹ مسیر کاری، وابستگی‌ها و Gateها.
- experiments/PARALLEL_AGENT_SPRINT_20261104.json — Manifest ماشین‌خوان Issueها/Branchها و وضعیت اجرا.
- docs/W1_HMM_REGIME_RESEARCH_STARTER_FA.md — بسته یادگیری HMM و forward filtering.
- docs/W2_ML_CANDIDATE_SCORING_STARTER_FA.md — بسته یادگیری Candidate Scoring.
- docs/W3_HYBRID_INTEGRATION_STARTER_FA.md — معماری W3 و طرح آزمایش 2×2.


## Sprint موازی ۹ نقش — خروجی‌های شروع
- reports/20261104_PARALLEL_AGENT_START_REPORT_FA.md — وضعیت Issueها، branchها، prototypeها و CI.
- research/w1_forward_filter.py و research/test_w1_forward_filter.py — HMM causal filter prototype و tests در branch W1.
- research/w2_candidate_validator.py و research/test_w2_candidate_validator.py — Candidate chronology/purge/embargo prototype و tests در branch W2.
- contracts/W3_HMM_ML_INTERFACE_V1.schema.json، research/w3_interface_validator.py و research/test_w3_interface_validator.py — interface contract و fail-closed validator در branch W3.
- .github/workflows/parallel-agent-learning-tests.yml — workflow اختصاصی W1/W2/W3.
