# Wyckoff W0 — XAUUSD / MetaTrader 5

پروژه پژوهشی ساخت و ارزیابی اکسپرت مبتنی بر وایکوف برای XAUUSD در MT5.

> وضعیت: توسعه و اعتبارسنجی؛ نتایج ثبت‌شده تا این مرحله زیان‌ده‌اند. استفاده روی حساب واقعی تأیید نشده است.

## آرشیو گفتگو و پیشرفت
- [آرشیو فنی و زمانی گفتگو و پیشرفت پروژه](docs/CHAT_AND_PROJECT_PROGRESS_FA.md) — خلاصهٔ تصمیم‌ها، نسخه‌ها، تست‌ها و کارهای باز؛ transcript لفظ‌به‌لفظ نیست.
- [آرشیو یکپارچه گفتگو و تصمیم‌ها](docs/CHAT_AND_PROJECT_ARCHIVE_FA.md)
- [وضعیت فعلی پروژه](docs/PROJECT_STATUS_FA.md)
- [برآورد پیشرفت با جزئیات](docs/PROJECT_PROGRESS_ESTIMATE_FA.md)
- [معماری ده‌لایه پروژه](docs/PROJECT_ARCHITECTURE_FA.md)

## مستندات مدیریتی و فنی
- [تاریخچه بک‌تست](docs/BACKTEST_HISTORY_FA.md)
- [فهرست فایل‌ها و انتقال](docs/FILE_REGISTER_FA.md)
- [قواعد توسعه و ممیزی](docs/DEVELOPMENT_RULES_FA.md)

## ساختار راهبرد
- زمینه H4 (اختیاری)، ساختار H1، ورود M5
- خرید: Accumulation/Range → Spring → Test → SOS → LPS → تأیید M5
- فروش: Distribution/Range → UTAD → Test → SOW → LPSY → تأیید M5

## آخرین ممیزی ساختار H1 — 2026-11-04
- [سورس تشخیصی چندسطحی H1STRUCT MultiAudit v1.084](src/Wyckoff_XAUUSD_W0_v1_08_C2_H1STRUCT_MULTI_AUDIT.mq5)
- [SET همراه MultiAudit با Lookback مبنا=5](sets/Wyckoff_C2_H1StructureMultiAudit_2024_2026.set)
- [SET Lookback 10](sets/Wyckoff_C2_H1STRUCT_SL10_2024_2026.set)
- [SET Lookback 20](sets/Wyckoff_C2_H1STRUCT_SL20_2024_2026.set)
- [راهنمای اجرای MultiAudit](docs/C2_H1STRUCT_MULTI_AUDIT_README_FA.md)
- [اعتبارسنجی ایستای سورس](docs/C2_H1STRUCT_MULTI_AUDIT_VALIDATION.txt)
- [تحلیل عمیق شکست‌های H1، Lookback و Pivotها](reports/20261104_H1STRUCT_MULTI_LOOKBACK_DEEP_REVIEW_FA.md)
- [گزارش اجرای H1STRUCT Audit](reports/20261104_H1STRUCT_AUDIT_RUN_ANALYSIS_FA.md)
- [آزمون خلاف‌واقع شکست لبه Range](reports/20261104_RANGE_EDGE_COUNTERFACTUAL_FA.md)

وضعیت MultiAudit: افزوده‌های تشخیصی و تطابق SET به‌صورت ایستا بررسی شده‌اند؛ هنوز در MetaEditor کامپایل و در Strategy Tester اجرا نشده‌اند. هیچ شرط معاملاتی C2 بر اساس Pivotها یا Creek/Ice تغییر نکرده است.

## ایمنی و کیفیت
هیچ نسخه‌ای در این مخزن به‌عنوان آماده معامله زنده معرفی نمی‌شود. سورس‌ها و نتایج باید به نسخه دقیق، تنظیمات و گزارش تست متناظر متصل باشند. نتیجهٔ یک معامله برای اثبات edge کافی نیست.


## Financial ML Core+\n- [گزارش اجرای موفق مهاجرت 346 Event](reports/20261104_LEGACY_EVENT_LEDGER_MIGRATION_RUN_FA.md)
- [راهنمای مهاجرت Legacy Event CSV](docs/LEGACY_EVENT_LEDGER_MIGRATION_FA.md)\n- [اسکریپت مهاجرت Event Ledger](scripts/migrate_legacy_event_csv.py)
- [ممیزی آمادگی داده و شناسه Candidateها](reports/20261104_FINANCIAL_ML_DATA_READINESS_AUDIT_FA.md)
- [بازبینی ایستای مستقل MultiAudit v1.084](reports/20261104_MULTIAUDIT_STATIC_CODE_REVIEW_FA.md)
- [کارت اجرای MT5 برای BOOT-002](docs/BOOT_002_MULTIAUDIT_RUN_CARD_FA.md)
- [اسکریپت Preflight خودکار](scripts/validate_financial_ml_preflight.py)
- [GitHub Actions Preflight workflow](.github/workflows/financial-ml-preflight.yml)
- [قالب JSON ثبت Runهای BOOT-002](experiments/BOOT_002_RUN_MANIFEST_TEMPLATE.json)
- [گزارش اولین Preflight موفق](experiments/BOOT_002_STATIC_PREFLIGHT_RUN_001.json)
- [گزارش Preflight پیشرفته 24/24](experiments/BOOT_002_STATIC_PREFLIGHT_RUN_002.json)
- [گزارش دو Preflight متوالی 27/27](experiments/BOOT_002_STATIC_PREFLIGHT_RUN_003.json)
- [Manifest اجرای BOOT-003 Legacy Event Migration](experiments/BOOT_003_LEGACY_EVENT_MIGRATION_RUN_001.json)
- [آخرین اجرای CI با 27/27](https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41858859791)
- [گزارش دو اجرای موفق GitHub Actions](reports/20261104_BOOT_002_CI_VERIFICATION_FA.md)
- [اجرای GitHub Actions](https://github.com/afshinsaberone-a11y/wyckoff/actions/runs/41856290720)
- [گزارش بازسازی SET مرجع C2 از Journal](reports/20261104_W0_C2_SET_RECONSTRUCTION_FA.md)
- [گزارش تطبیق هویت Baseline W0 و BOOT-001](reports/20261104_W0_BASELINE_IDENTITY_FA.md)
- [پروتکل رسمی Financial ML Core+](docs/FINANCIAL_ML_CORE_PLUS_PROTOCOL_FA.md)
- [رجیستری ۹ نقش ایجنت‌ها](agents/README_FA.md)
- [قرارداد Event و Candidate](contracts/EVENT_AND_CANDIDATE_SCHEMA_FA.md)
- [قرارداد Feature و Label](contracts/FEATURE_LABEL_SCHEMA_FA.md)
- [قرارداد Experiment و Walk-Forward](contracts/EXPERIMENT_AND_FOLD_SCHEMA_FA.md)
- [قرارداد Result و Audit](contracts/RESULT_AND_AUDIT_SCHEMA_FA.md)

وضعیت: مشخصات و System Prompt نقش‌ها ثبت شده‌اند؛ ایجنت‌ها هنوز به‌صورت سرویس مستقل مستقر نشده‌اند. W1/W2/W3 تا تکمیل W0، Event Ledger و Label/Fold validation نباید وارد آموزش/آزمون نهایی شوند.

- [برنامه راه‌اندازی و بسته‌های کاری BOOT-001 تا BOOT-007](docs/FINANCIAL_ML_CORE_PLUS_BOOTSTRAP_PLAN_FA.md)
- [مدل استقرار و تحویل بین ایجنت‌ها](agents/EXECUTION_AND_HANDOFF_MODEL_FA.md)
- [قرارداد Agent Handoff](contracts/AGENT_HANDOFF_SCHEMA_FA.md)
